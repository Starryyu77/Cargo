# Project: CARGO - AI Interpreter 意图识别层设计文档

> **文档版本**: v1.0  
> **创建日期**: 2024  
> **文档类型**: 技术设计文档  
> **适用范围**: Project: CARGO 游戏AI系统

---

## 文档概述

本文档详细描述了Project: CARGO游戏中AI Interpreter意图识别中间件的完整设计方案，包括：

1. 系统架构设计
2. 核心意图识别逻辑（Python伪代码）
3. 三层危险指令检测系统
4. 模糊指令处理与置信度机制
5. 结构化输出Schema定义
6. 物理状态机交互接口

---

## 1. 系统架构概览

```
┌─────────────────────────────────────────────────────────────────────────┐
│                        AI Interpreter 中间件架构                          │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  ┌──────────────┐     ┌──────────────┐     ┌──────────────┐            │
│  │  玩家输入     │────▶│  预处理层    │────▶│  语义解析层  │            │
│  │  (自然语言)   │     │  分词/标准化  │     │  NER/意图分类 │            │
│  └──────────────┘     └──────────────┘     └──────────────┘            │
│                                                    │                    │
│                                                    ▼                    │
│  ┌──────────────┐     ┌──────────────┐     ┌──────────────┐            │
│  │ 物理世界     │◀────│  执行引擎    │◀────│  安全检测层  │            │
│  │ 状态更新     │     │  指令执行    │     │  三层校验    │            │
│  └──────────────┘     └──────────────┘     └──────────────┘            │
│                                                    │                    │
│                                                    ▼                    │
│                                          ┌──────────────┐              │
│                                          │  输出格式化  │─────────────▶│
│                                          │  结构化输出  │   返回结果    │
│                                          └──────────────┘              │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

## 2. 核心数据结构定义

```python
from dataclasses import dataclass, field
from typing import Optional, Dict, List, Any, Union
from enum import Enum

class ActionType(Enum):
    """游戏内可执行的动作类型"""
    MOVE = "move"                    # 移动
    INTERACT = "interact"            # 交互（按下、拉动等）
    USE_ITEM = "use_item"            # 使用物品
    EXAMINE = "examine"              # 检查/观察
    COMMUNICATE = "communicate"      # 交流
    WAIT = "wait"                    # 等待
    CANCEL = "cancel"                # 取消当前动作

class DangerLevel(Enum):
    """危险等级"""
    NONE = "none"           # 无危险
    LOW = "low"             # 低风险
    MEDIUM = "medium"       # 中等风险
    HIGH = "high"           # 高风险
    CRITICAL = "critical"   # 致命风险

class ConfidenceLevel(Enum):
    """置信度等级"""
    HIGH = "high"       # > 0.8
    MEDIUM = "medium"   # 0.5 - 0.8
    LOW = "low"         # < 0.5

@dataclass
class GameContext:
    """游戏上下文"""
    jack_position: tuple[float, float, float]  # Jack的3D位置
    jack_state: str                            # Jack当前状态
    nearby_objects: List[Dict[str, Any]]       # 附近可交互物体
    environment_state: Dict[str, Any]          # 环境状态（温度、光照等）
    inventory: List[str]                       # Jack携带的物品
    current_objective: Optional[str]           # 当前任务目标
    recent_actions: List[str]                  # 最近执行的动作（用于上下文）
    danger_zones: List[Dict[str, Any]]         # 危险区域信息

@dataclass
class ParsedIntent:
    """解析后的意图"""
    action: ActionType
    target: Optional[str]
    target_type: Optional[str]  # "object", "location", "npc", "self"
    parameters: Dict[str, Any]
    raw_text: str

@dataclass
class SafetyCheckResult:
    """安全检测结果"""
    passed: bool
    danger_level: DangerLevel
    violations: List[str]
    warnings: List[str]
    mitigation_suggestions: List[str]

@dataclass
class InstructionResult:
    """最终指令结果"""
    action: str
    target_id: Optional[str]
    parameters: Dict[str, Any]
    confidence: float
    danger_level: DangerLevel
    requires_clarification: bool
    clarification_prompt: Optional[str]
    rejection_reason: Optional[str]
    alternative_suggestions: List[str]
```

## 3. 核心意图识别逻辑

```python
class AIInterpreter:
    """
    Project: CARGO 意图识别中间件
    
    职责：
    1. 将玩家自然语言转换为结构化游戏指令
    2. 执行多层安全检测
    3. 处理模糊指令与澄清请求
    4. 与物理状态机交互
    """
    
    def __init__(self, llm_client, game_state_manager):
        self.llm = llm_client
        self.state_manager = game_state_manager
        
        # 初始化各层检测器
        self.syntax_checker = SyntaxSafetyChecker()
        self.semantic_checker = SemanticSafetyChecker()
        self.state_checker = StateSafetyChecker()
        
        # 置信度阈值配置
        self.CONFIDENCE_HIGH = 0.8
        self.CONFIDENCE_MEDIUM = 0.5
        
    def interpret_instruction(
        self, 
        player_input: str, 
        context: GameContext
    ) -> InstructionResult:
        """
        主入口：将玩家自然语言转换为结构化游戏指令
        
        处理流程：
        1. 输入预处理
        2. 语义解析（提取动作、目标、参数）
        3. 三层安全检测
        4. 置信度评估
        5. 生成结构化输出
        """
        
        # ========== Step 1: 输入预处理 ==========
        cleaned_input = self._preprocess_input(player_input)
        
        # ========== Step 2: 语义解析 ==========
        parsed_intent = self._parse_semantic(cleaned_input, context)
        
        # 解析失败处理
        if parsed_intent is None:
            return InstructionResult(
                action="none",
                target_id=None,
                parameters={},
                confidence=0.0,
                danger_level=DangerLevel.NONE,
                requires_clarification=True,
                clarification_prompt="我没有理解您的指令，请尝试用更具体的描述。",
                rejection_reason="语义解析失败",
                alternative_suggestions=[]
            )
        
        # ========== Step 3: 三层安全检测 ==========
        safety_result = self._safety_check(parsed_intent, context)
        
        # 严重危险直接拒绝
        if safety_result.danger_level == DangerLevel.CRITICAL:
            return InstructionResult(
                action=parsed_intent.action.value,
                target_id=parsed_intent.target,
                parameters=parsed_intent.parameters,
                confidence=1.0,
                danger_level=DangerLevel.CRITICAL,
                requires_clarification=False,
                clarification_prompt=None,
                rejection_reason=f"检测到致命危险: {'; '.join(safety_result.violations)}",
                alternative_suggestions=safety_result.mitigation_suggestions
            )
        
        # ========== Step 4: 置信度评估 ==========
        confidence = self._calculate_confidence(parsed_intent, context)
        
        # ========== Step 5: 根据置信度生成输出 ==========
        return self._generate_output(
            parsed_intent, 
            safety_result, 
            confidence, 
            context
        )
    
    def _preprocess_input(self, player_input: str) -> str:
        """
        输入预处理
        - 去除多余空格
        - 统一标点符号
        - 简繁转换（如需要）
        """
        cleaned = player_input.strip()
        cleaned = cleaned.replace("，", ",").replace("。", ".")
        return cleaned
    
    def _parse_semantic(
        self, 
        cleaned_input: str, 
        context: GameContext
    ) -> Optional[ParsedIntent]:
        """
        语义解析：提取动作、目标、参数
        
        使用LLM进行结构化提取，同时结合规则匹配作为fallback
        """
        # 尝试规则匹配（快速路径）
        rule_match = self._rule_based_parsing(cleaned_input, context)
        if rule_match:
            return rule_match
        
        # LLM结构化提取
        prompt = self._build_parsing_prompt(cleaned_input, context)
        
        try:
            llm_response = self.llm.generate_structured(
                prompt=prompt,
                schema=self._get_intent_schema()
            )
            
            return ParsedIntent(
                action=ActionType(llm_response["action"]),
                target=llm_response.get("target"),
                target_type=llm_response.get("target_type"),
                parameters=llm_response.get("parameters", {}),
                raw_text=cleaned_input
            )
        except Exception as e:
            # LLM解析失败，尝试模糊匹配
            return self._fuzzy_parsing(cleaned_input, context)
    
    def _rule_based_parsing(
        self, 
        input_text: str, 
        context: GameContext
    ) -> Optional[ParsedIntent]:
        """
        基于规则的快速解析
        """
        # 移动类指令
        move_patterns = [
            (r"去(.*?)(那里|那边|位置)?", ActionType.MOVE),
            (r"走到(.*?)", ActionType.MOVE),
            (r"靠近(.*?)", ActionType.MOVE),
            (r"离开(.*?)", ActionType.MOVE),
        ]
        
        for pattern, action in move_patterns:
            match = re.search(pattern, input_text)
            if match:
                target = match.group(1).strip()
                return ParsedIntent(
                    action=action,
                    target=target,
                    target_type="location",
                    parameters={"direction": "toward" if "去" in input_text else "away"},
                    raw_text=input_text
                )
        
        # 交互类指令
        interact_patterns = [
            (r"按(下)?(.*?)", "press"),
            (r"拉(动)?(.*?)", "pull"),
            (r"打开(.*?)", "open"),
            (r"关闭(.*?)", "close"),
            (r"拿(起)?(.*?)", "pickup"),
            (r"放下(.*?)", "drop"),
        ]
        
        for pattern, interact_type in interact_patterns:
            match = re.search(pattern, input_text)
            if match:
                target = match.group(2).strip() if match.lastindex > 1 else match.group(1).strip()
                return ParsedIntent(
                    action=ActionType.INTERACT,
                    target=target,
                    target_type="object",
                    parameters={"interact_type": interact_type},
                    raw_text=input_text
                )
        
        # 检查类指令
        examine_patterns = [
            r"看看(.*?)",
            r"检查(.*?)",
            r"观察(.*?)",
        ]
        
        for pattern in examine_patterns:
            match = re.search(pattern, input_text)
            if match:
                target = match.group(1).strip() or "周围"
                return ParsedIntent(
                    action=ActionType.EXAMINE,
                    target=target,
                    target_type="object" if target != "周围" else "location",
                    parameters={},
                    raw_text=input_text
                )
        
        return None
    
    def _fuzzy_parsing(
        self, 
        input_text: str, 
        context: GameContext
    ) -> Optional[ParsedIntent]:
        """
        模糊匹配解析（兜底方案）
        """
        # 计算与已知指令的相似度
        known_instructions = self._get_known_instructions()
        
        best_match = None
        best_score = 0.0
        
        for instruction in known_instructions:
            score = self._calculate_similarity(input_text, instruction["pattern"])
            if score > best_score and score > 0.6:  # 相似度阈值
                best_score = score
                best_match = instruction
        
        if best_match:
            return ParsedIntent(
                action=ActionType(best_match["action"]),
                target=best_match.get("default_target"),
                target_type=best_match.get("target_type"),
                parameters=best_match.get("parameters", {}),
                raw_text=input_text
            )
        
        return None
    
    def _safety_check(
        self, 
        parsed_intent: ParsedIntent, 
        context: GameContext
    ) -> SafetyCheckResult:
        """
        三层安全检测
        """
        all_violations = []
        all_warnings = []
        all_suggestions = []
        
        # Level 1: 语法层检测
        syntax_result = self.syntax_checker.check(parsed_intent)
        all_violations.extend(syntax_result.violations)
        all_warnings.extend(syntax_result.warnings)
        all_suggestions.extend(syntax_result.suggestions)
        
        # Level 2: 语义层检测
        semantic_result = self.semantic_checker.check(parsed_intent, context)
        all_violations.extend(semantic_result.violations)
        all_warnings.extend(semantic_result.warnings)
        all_suggestions.extend(semantic_result.suggestions)
        
        # Level 3: 状态层检测
        state_result = self.state_checker.check(parsed_intent, context)
        all_violations.extend(state_result.violations)
        all_warnings.extend(state_result.warnings)
        all_suggestions.extend(state_result.suggestions)
        
        # 综合评估危险等级
        danger_level = self._assess_danger_level(
            all_violations, all_warnings
        )
        
        return SafetyCheckResult(
            passed=len(all_violations) == 0,
            danger_level=danger_level,
            violations=all_violations,
            warnings=all_warnings,
            mitigation_suggestions=all_suggestions
        )
    
    def _calculate_confidence(
        self, 
        parsed_intent: ParsedIntent, 
        context: GameContext
    ) -> float:
        """
        计算置信度分数
        """
        scores = []
        
        # 1. 目标存在性分数
        target_exists = self._check_target_exists(parsed_intent.target, context)
        scores.append(1.0 if target_exists else 0.3)
        
        # 2. 动作-目标匹配分数
        action_target_match = self._check_action_target_match(
            parsed_intent.action, 
            parsed_intent.target_type
        )
        scores.append(action_target_match)
        
        # 3. 上下文一致性分数
        context_consistency = self._check_context_consistency(
            parsed_intent, context
        )
        scores.append(context_consistency)
        
        # 4. 解析方法分数（规则匹配置信度更高）
        parsing_method_score = 0.9 if "规则匹配" in str(parsed_intent) else 0.7
        scores.append(parsing_method_score)
        
        # 加权平均
        weights = [0.3, 0.25, 0.25, 0.2]
        confidence = sum(s * w for s, w in zip(scores, weights))
        
        return round(confidence, 3)
    
    def _generate_output(
        self,
        parsed_intent: ParsedIntent,
        safety_result: SafetyCheckResult,
        confidence: float,
        context: GameContext
    ) -> InstructionResult:
        """
        根据置信度和安全检测结果生成最终输出
        """
        # 高置信度：直接执行
        if confidence >= self.CONFIDENCE_HIGH:
            return InstructionResult(
                action=parsed_intent.action.value,
                target_id=parsed_intent.target,
                parameters=parsed_intent.parameters,
                confidence=confidence,
                danger_level=safety_result.danger_level,
                requires_clarification=False,
                clarification_prompt=None,
                rejection_reason=None,
                alternative_suggestions=[]
            )
        
        # 中置信度：请求澄清
        elif confidence >= self.CONFIDENCE_MEDIUM:
            clarification_prompt = self._generate_clarification_prompt(
                parsed_intent, context
            )
            return InstructionResult(
                action=parsed_intent.action.value,
                target_id=parsed_intent.target,
                parameters=parsed_intent.parameters,
                confidence=confidence,
                danger_level=safety_result.danger_level,
                requires_clarification=True,
                clarification_prompt=clarification_prompt,
                rejection_reason=None,
                alternative_suggestions=self._generate_alternatives(
                    parsed_intent, context
                )
            )
        
        # 低置信度：拒绝
        else:
            return InstructionResult(
                action="none",
                target_id=None,
                parameters={},
                confidence=confidence,
                danger_level=DangerLevel.NONE,
                requires_clarification=True,
                clarification_prompt="我没有完全理解您的意思，请尝试用更具体的描述。",
                rejection_reason="置信度过低",
                alternative_suggestions=self._generate_alternatives(
                    parsed_intent, context
                )
            )
```

# Project: CARGO - AI Interpreter 意图识别层设计文档

> **文档版本**: v1.0  
> **创建日期**: 2024  
> **文档类型**: 技术设计文档  
> **适用范围**: Project: CARGO 游戏AI系统

---

## 文档概述

本文档详细描述了Project: CARGO游戏中AI Interpreter意图识别中间件的完整设计方案，包括：

1. 系统架构设计
2. 核心意图识别逻辑（Python伪代码）
3. 三层危险指令检测系统
4. 模糊指令处理与置信度机制
5. 结构化输出Schema定义
6. 物理状态机交互接口

---

## 1. 系统架构概览

```
┌─────────────────────────────────────────────────────────────────────────┐
│                        AI Interpreter 中间件架构                          │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  ┌──────────────┐     ┌──────────────┐     ┌──────────────┐            │
│  │  玩家输入     │────▶│  预处理层    │────▶│  语义解析层  │            │
│  │  (自然语言)   │     │  分词/标准化  │     │  NER/意图分类 │            │
│  └──────────────┘     └──────────────┘     └──────────────┘            │
│                                                    │                    │
│                                                    ▼                    │
│  ┌──────────────┐     ┌──────────────┐     ┌──────────────┐            │
│  │ 物理世界     │◀────│  执行引擎    │◀────│  安全检测层  │            │
│  │ 状态更新     │     │  指令执行    │     │  三层校验    │            │
│  └──────────────┘     └──────────────┘     └──────────────┘            │
│                                                    │                    │
│                                                    ▼                    │
│                                          ┌──────────────┐              │
│                                          │  输出格式化  │─────────────▶│
│                                          │  结构化输出  │   返回结果    │
│                                          └──────────────┘              │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

## 2. 核心数据结构定义

```python
from dataclasses import dataclass, field
from typing import Optional, Dict, List, Any, Union
from enum import Enum

class ActionType(Enum):
    """游戏内可执行的动作类型"""
    MOVE = "move"                    # 移动
    INTERACT = "interact"            # 交互（按下、拉动等）
    USE_ITEM = "use_item"            # 使用物品
    EXAMINE = "examine"              # 检查/观察
    COMMUNICATE = "communicate"      # 交流
    WAIT = "wait"                    # 等待
    CANCEL = "cancel"                # 取消当前动作

class DangerLevel(Enum):
    """危险等级"""
    NONE = "none"           # 无危险
    LOW = "low"             # 低风险
    MEDIUM = "medium"       # 中等风险
    HIGH = "high"           # 高风险
    CRITICAL = "critical"   # 致命风险

class ConfidenceLevel(Enum):
    """置信度等级"""
    HIGH = "high"       # > 0.8
    MEDIUM = "medium"   # 0.5 - 0.8
    LOW = "low"         # < 0.5

@dataclass
class GameContext:
    """游戏上下文"""
    jack_position: tuple[float, float, float]  # Jack的3D位置
    jack_state: str                            # Jack当前状态
    nearby_objects: List[Dict[str, Any]]       # 附近可交互物体
    environment_state: Dict[str, Any]          # 环境状态（温度、光照等）
    inventory: List[str]                       # Jack携带的物品
    current_objective: Optional[str]           # 当前任务目标
    recent_actions: List[str]                  # 最近执行的动作（用于上下文）
    danger_zones: List[Dict[str, Any]]         # 危险区域信息

@dataclass
class ParsedIntent:
    """解析后的意图"""
    action: ActionType
    target: Optional[str]
    target_type: Optional[str]  # "object", "location", "npc", "self"
    parameters: Dict[str, Any]
    raw_text: str

@dataclass
class SafetyCheckResult:
    """安全检测结果"""
    passed: bool
    danger_level: DangerLevel
    violations: List[str]
    warnings: List[str]
    mitigation_suggestions: List[str]

@dataclass
class InstructionResult:
    """最终指令结果"""
    action: str
    target_id: Optional[str]
    parameters: Dict[str, Any]
    confidence: float
    danger_level: DangerLevel
    requires_clarification: bool
    clarification_prompt: Optional[str]
    rejection_reason: Optional[str]
    alternative_suggestions: List[str]
```

## 3. 核心意图识别逻辑

```python
class AIInterpreter:
    """
    Project: CARGO 意图识别中间件
    
    职责：
    1. 将玩家自然语言转换为结构化游戏指令
    2. 执行多层安全检测
    3. 处理模糊指令与澄清请求
    4. 与物理状态机交互
    """
    
    def __init__(self, llm_client, game_state_manager):
        self.llm = llm_client
        self.state_manager = game_state_manager
        
        # 初始化各层检测器
        self.syntax_checker = SyntaxSafetyChecker()
        self.semantic_checker = SemanticSafetyChecker()
        self.state_checker = StateSafetyChecker()
        
        # 置信度阈值配置
        self.CONFIDENCE_HIGH = 0.8
        self.CONFIDENCE_MEDIUM = 0.5
        
    def interpret_instruction(
        self, 
        player_input: str, 
        context: GameContext
    ) -> InstructionResult:
        """
        主入口：将玩家自然语言转换为结构化游戏指令
        
        处理流程：
        1. 输入预处理
        2. 语义解析（提取动作、目标、参数）
        3. 三层安全检测
        4. 置信度评估
        5. 生成结构化输出
        """
        
        # ========== Step 1: 输入预处理 ==========
        cleaned_input = self._preprocess_input(player_input)
        
        # ========== Step 2: 语义解析 ==========
        parsed_intent = self._parse_semantic(cleaned_input, context)
        
        # 解析失败处理
        if parsed_intent is None:
            return InstructionResult(
                action="none",
                target_id=None,
                parameters={},
                confidence=0.0,
                danger_level=DangerLevel.NONE,
                requires_clarification=True,
                clarification_prompt="我没有理解您的指令，请尝试用更具体的描述。",
                rejection_reason="语义解析失败",
                alternative_suggestions=[]
            )
        
        # ========== Step 3: 三层安全检测 ==========
        safety_result = self._safety_check(parsed_intent, context)
        
        # 严重危险直接拒绝
        if safety_result.danger_level == DangerLevel.CRITICAL:
            return InstructionResult(
                action=parsed_intent.action.value,
                target_id=parsed_intent.target,
                parameters=parsed_intent.parameters,
                confidence=1.0,
                danger_level=DangerLevel.CRITICAL,
                requires_clarification=False,
                clarification_prompt=None,
                rejection_reason=f"检测到致命危险: {'; '.join(safety_result.violations)}",
                alternative_suggestions=safety_result.mitigation_suggestions
            )
        
        # ========== Step 4: 置信度评估 ==========
        confidence = self._calculate_confidence(parsed_intent, context)
        
        # ========== Step 5: 根据置信度生成输出 ==========
        return self._generate_output(
            parsed_intent, 
            safety_result, 
            confidence, 
            context
        )
    
    def _preprocess_input(self, player_input: str) -> str:
        """
        输入预处理
        - 去除多余空格
        - 统一标点符号
        - 简繁转换（如需要）
        """
        cleaned = player_input.strip()
        cleaned = cleaned.replace("，", ",").replace("。", ".")
        return cleaned
    
    def _parse_semantic(
        self, 
        cleaned_input: str, 
        context: GameContext
    ) -> Optional[ParsedIntent]:
        """
        语义解析：提取动作、目标、参数
        
        使用LLM进行结构化提取，同时结合规则匹配作为fallback
        """
        # 尝试规则匹配（快速路径）
        rule_match = self._rule_based_parsing(cleaned_input, context)
        if rule_match:
            return rule_match
        
        # LLM结构化提取
        prompt = self._build_parsing_prompt(cleaned_input, context)
        
        try:
            llm_response = self.llm.generate_structured(
                prompt=prompt,
                schema=self._get_intent_schema()
            )
            
            return ParsedIntent(
                action=ActionType(llm_response["action"]),
                target=llm_response.get("target"),
                target_type=llm_response.get("target_type"),
                parameters=llm_response.get("parameters", {}),
                raw_text=cleaned_input
            )
        except Exception as e:
            # LLM解析失败，尝试模糊匹配
            return self._fuzzy_parsing(cleaned_input, context)
    
    def _rule_based_parsing(
        self, 
        input_text: str, 
        context: GameContext
    ) -> Optional[ParsedIntent]:
        """
        基于规则的快速解析
        """
        # 移动类指令
        move_patterns = [
            (r"去(.*?)(那里|那边|位置)?", ActionType.MOVE),
            (r"走到(.*?)", ActionType.MOVE),
            (r"靠近(.*?)", ActionType.MOVE),
            (r"离开(.*?)", ActionType.MOVE),
        ]
        
        for pattern, action in move_patterns:
            match = re.search(pattern, input_text)
            if match:
                target = match.group(1).strip()
                return ParsedIntent(
                    action=action,
                    target=target,
                    target_type="location",
                    parameters={"direction": "toward" if "去" in input_text else "away"},
                    raw_text=input_text
                )
        
        # 交互类指令
        interact_patterns = [
            (r"按(下)?(.*?)", "press"),
            (r"拉(动)?(.*?)", "pull"),
            (r"打开(.*?)", "open"),
            (r"关闭(.*?)", "close"),
            (r"拿(起)?(.*?)", "pickup"),
            (r"放下(.*?)", "drop"),
        ]
        
        for pattern, interact_type in interact_patterns:
            match = re.search(pattern, input_text)
            if match:
                target = match.group(2).strip() if match.lastindex > 1 else match.group(1).strip()
                return ParsedIntent(
                    action=ActionType.INTERACT,
                    target=target,
                    target_type="object",
                    parameters={"interact_type": interact_type},
                    raw_text=input_text
                )
        
        # 检查类指令
        examine_patterns = [
            r"看看(.*?)",
            r"检查(.*?)",
            r"观察(.*?)",
        ]
        
        for pattern in examine_patterns:
            match = re.search(pattern, input_text)
            if match:
                target = match.group(1).strip() or "周围"
                return ParsedIntent(
                    action=ActionType.EXAMINE,
                    target=target,
                    target_type="object" if target != "周围" else "location",
                    parameters={},
                    raw_text=input_text
                )
        
        return None
    
    def _fuzzy_parsing(
        self, 
        input_text: str, 
        context: GameContext
    ) -> Optional[ParsedIntent]:
        """
        模糊匹配解析（兜底方案）
        """
        # 计算与已知指令的相似度
        known_instructions = self._get_known_instructions()
        
        best_match = None
        best_score = 0.0
        
        for instruction in known_instructions:
            score = self._calculate_similarity(input_text, instruction["pattern"])
            if score > best_score and score > 0.6:  # 相似度阈值
                best_score = score
                best_match = instruction
        
        if best_match:
            return ParsedIntent(
                action=ActionType(best_match["action"]),
                target=best_match.get("default_target"),
                target_type=best_match.get("target_type"),
                parameters=best_match.get("parameters", {}),
                raw_text=input_text
            )
        
        return None
    
    def _safety_check(
        self, 
        parsed_intent: ParsedIntent, 
        context: GameContext
    ) -> SafetyCheckResult:
        """
        三层安全检测
        """
        all_violations = []
        all_warnings = []
        all_suggestions = []
        
        # Level 1: 语法层检测
        syntax_result = self.syntax_checker.check(parsed_intent)
        all_violations.extend(syntax_result.violations)
        all_warnings.extend(syntax_result.warnings)
        all_suggestions.extend(syntax_result.suggestions)
        
        # Level 2: 语义层检测
        semantic_result = self.semantic_checker.check(parsed_intent, context)
        all_violations.extend(semantic_result.violations)
        all_warnings.extend(semantic_result.warnings)
        all_suggestions.extend(semantic_result.suggestions)
        
        # Level 3: 状态层检测
        state_result = self.state_checker.check(parsed_intent, context)
        all_violations.extend(state_result.violations)
        all_warnings.extend(state_result.warnings)
        all_suggestions.extend(state_result.suggestions)
        
        # 综合评估危险等级
        danger_level = self._assess_danger_level(
            all_violations, all_warnings
        )
        
        return SafetyCheckResult(
            passed=len(all_violations) == 0,
            danger_level=danger_level,
            violations=all_violations,
            warnings=all_warnings,
            mitigation_suggestions=all_suggestions
        )
    
    def _calculate_confidence(
        self, 
        parsed_intent: ParsedIntent, 
        context: GameContext
    ) -> float:
        """
        计算置信度分数
        """
        scores = []
        
        # 1. 目标存在性分数
        target_exists = self._check_target_exists(parsed_intent.target, context)
        scores.append(1.0 if target_exists else 0.3)
        
        # 2. 动作-目标匹配分数
        action_target_match = self._check_action_target_match(
            parsed_intent.action, 
            parsed_intent.target_type
        )
        scores.append(action_target_match)
        
        # 3. 上下文一致性分数
        context_consistency = self._check_context_consistency(
            parsed_intent, context
        )
        scores.append(context_consistency)
        
        # 4. 解析方法分数（规则匹配置信度更高）
        parsing_method_score = 0.9 if "规则匹配" in str(parsed_intent) else 0.7
        scores.append(parsing_method_score)
        
        # 加权平均
        weights = [0.3, 0.25, 0.25, 0.2]
        confidence = sum(s * w for s, w in zip(scores, weights))
        
        return round(confidence, 3)
    
    def _generate_output(
        self,
        parsed_intent: ParsedIntent,
        safety_result: SafetyCheckResult,
        confidence: float,
        context: GameContext
    ) -> InstructionResult:
        """
        根据置信度和安全检测结果生成最终输出
        """
        # 高置信度：直接执行
        if confidence >= self.CONFIDENCE_HIGH:
            return InstructionResult(
                action=parsed_intent.action.value,
                target_id=parsed_intent.target,
                parameters=parsed_intent.parameters,
                confidence=confidence,
                danger_level=safety_result.danger_level,
                requires_clarification=False,
                clarification_prompt=None,
                rejection_reason=None,
                alternative_suggestions=[]
            )
        
        # 中置信度：请求澄清
        elif confidence >= self.CONFIDENCE_MEDIUM:
            clarification_prompt = self._generate_clarification_prompt(
                parsed_intent, context
            )
            return InstructionResult(
                action=parsed_intent.action.value,
                target_id=parsed_intent.target,
                parameters=parsed_intent.parameters,
                confidence=confidence,
                danger_level=safety_result.danger_level,
                requires_clarification=True,
                clarification_prompt=clarification_prompt,
                rejection_reason=None,
                alternative_suggestions=self._generate_alternatives(
                    parsed_intent, context
                )
            )
        
        # 低置信度：拒绝
        else:
            return InstructionResult(
                action="none",
                target_id=None,
                parameters={},
                confidence=confidence,
                danger_level=DangerLevel.NONE,
                requires_clarification=True,
                clarification_prompt="我没有完全理解您的意思，请尝试用更具体的描述。",
                rejection_reason="置信度过低",
                alternative_suggestions=self._generate_alternatives(
                    parsed_intent, context
                )
            )
```

## 4. 三层危险指令检测系统

### 4.1 Level 1 - 语法层检测器

```python
class SyntaxSafetyChecker:
    """
    Level 1: 语法层检测
    
    检测内容：
    1. 关键词黑名单匹配
    2. 动作-目标类型匹配检查
    3. 语法结构合法性
    """
    
    # 危险关键词黑名单
    DANGER_KEYWORDS = {
        # 致命危险（直接拒绝）
        "critical": [
            "爆炸", "引爆", "炸毁", "炸药", "炸弹",
            "自杀", "跳楼", "跳下去", "跳崖",
            "烧毁", "放火", "纵火", "燃烧瓶",
            "短路", "触电", "电击", "高压",
            "毒药", "毒死", "下毒", "毒气",
        ],
        # 高风险（警告+确认）
        "high": [
            "破坏", "砸碎", "打碎", "摧毁",
            "偷窃", "偷走", "盗取",
            "攻击", "殴打", "伤害",
            "闯入", "入侵", "非法进入",
        ],
        # 中等风险（提示风险）
        "medium": [
            "爬", "攀爬", "跳", "跳跃",
            "推", "拉", "搬动",
            "打开", "关闭",
        ]
    }
    
    # 动作-目标类型匹配规则
    ACTION_TARGET_RULES = {
        ActionType.MOVE: ["location", "object", "npc"],
        ActionType.INTERACT: ["object", "npc"],
        ActionType.USE_ITEM: ["object"],
        ActionType.EXAMINE: ["object", "location", "npc"],
        ActionType.COMMUNICATE: ["npc"],
    }
    
    def check(self, parsed_intent: ParsedIntent) -> Dict:
        """
        执行语法层安全检测
        """
        violations = []
        warnings = []
        suggestions = []
        
        # 1. 黑名单关键词检测
        keyword_result = self._check_dangerous_keywords(parsed_intent.raw_text)
        violations.extend(keyword_result["violations"])
        warnings.extend(keyword_result["warnings"])
        
        # 2. 动作-目标类型匹配检查
        match_result = self._check_action_target_match(parsed_intent)
        if not match_result["valid"]:
            violations.append(f"动作'{parsed_intent.action.value}'不能作用于目标类型'{parsed_intent.target_type}'")
            suggestions.extend(match_result["suggestions"])
        
        # 3. 参数合法性检查
        param_result = self._check_parameters(parsed_intent)
        warnings.extend(param_result["warnings"])
        
        return {
            "violations": violations,
            "warnings": warnings,
            "suggestions": suggestions
        }
    
    def _check_dangerous_keywords(self, text: str) -> Dict:
        """
        检测危险关键词
        """
        violations = []
        warnings = []
        
        text_lower = text.lower()
        
        # 检测致命危险关键词
        for keyword in self.DANGER_KEYWORDS["critical"]:
            if keyword in text_lower:
                violations.append(f"检测到致命危险关键词: '{keyword}'")
        
        # 检测高风险关键词
        for keyword in self.DANGER_KEYWORDS["high"]:
            if keyword in text_lower:
                warnings.append(f"检测到高风险关键词: '{keyword}'")
        
        return {"violations": violations, "warnings": warnings}
    
    def _check_action_target_match(self, parsed_intent: ParsedIntent) -> Dict:
        """
        检查动作与目标类型是否匹配
        """
        action = parsed_intent.action
        target_type = parsed_intent.target_type
        
        valid_targets = self.ACTION_TARGET_RULES.get(action, [])
        
        if target_type and target_type not in valid_targets:
            return {
                "valid": False,
                "suggestions": [
                    f"尝试使用其他动作，如: {self._suggest_alternative_actions(target_type)}"
                ]
            }
        
        return {"valid": True, "suggestions": []}
    
    def _check_parameters(self, parsed_intent: ParsedIntent) -> Dict:
        """
        检查参数合法性
        """
        warnings = []
        params = parsed_intent.parameters
        
        # 检查数值参数范围
        if "force" in params:
            force = params["force"]
            if isinstance(force, (int, float)) and force > 0.8:
                warnings.append(f"力度参数较高({force})，可能导致意外后果")
        
        if "speed" in params:
            speed = params["speed"]
            if isinstance(speed, (int, float)) and speed > 0.8:
                warnings.append(f"速度参数较高({speed})，存在安全风险")
        
        return {"warnings": warnings}
    
    def _suggest_alternative_actions(self, target_type: str) -> List[str]:
        """
        为目标类型建议替代动作
        """
        suggestions = {
            "location": ["move", "examine"],
            "object": ["interact", "examine", "use_item"],
            "npc": ["communicate", "examine"],
        }
        return suggestions.get(target_type, [])
```

### 4.2 Level 2 - 语义层检测器

```python
class SemanticSafetyChecker:
    """
    Level 2: 语义层检测
    
    检测内容：
    1. 上下文危险评估
    2. 连锁反应预测
    3. 意图隐含风险分析
    """
    
    def check(
        self, 
        parsed_intent: ParsedIntent, 
        context: GameContext
    ) -> Dict:
        """
        执行语义层安全检测
        """
        violations = []
        warnings = []
        suggestions = []
        
        # 1. 上下文危险评估
        context_result = self._assess_context_danger(parsed_intent, context)
        violations.extend(context_result["violations"])
        warnings.extend(context_result["warnings"])
        suggestions.extend(context_result["suggestions"])
        
        # 2. 连锁反应预测
        chain_result = self._predict_chain_reactions(parsed_intent, context)
        warnings.extend(chain_result["warnings"])
        suggestions.extend(chain_result["suggestions"])
        
        # 3. 隐含风险分析
        implicit_result = self._analyze_implicit_risks(parsed_intent, context)
        warnings.extend(implicit_result["warnings"])
        
        return {
            "violations": violations,
            "warnings": warnings,
            "suggestions": suggestions
        }
    
    def _assess_context_danger(
        self, 
        parsed_intent: ParsedIntent, 
        context: GameContext
    ) -> Dict:
        """
        评估当前上下文中的危险
        """
        violations = []
        warnings = []
        suggestions = []
        
        # 获取目标对象信息
        target_info = self._get_target_info(parsed_intent.target, context)
        
        if not target_info:
            return {"violations": [], "warnings": [], "suggestions": []}
        
        # 检查目标是否为危险物体
        if target_info.get("is_dangerous"):
            danger_type = target_info.get("danger_type", "unknown")
            
            if parsed_intent.action == ActionType.INTERACT:
                if danger_type == "heat_source":
                    warnings.append(f"目标'{parsed_intent.target}'是热源，直接接触可能导致烧伤")
                    suggestions.append("尝试使用工具或保持安全距离")
                elif danger_type == "electrical":
                    violations.append(f"目标'{parsed_intent.target}'是带电设备，直接接触有触电风险")
                    suggestions.append("先切断电源或使用绝缘工具")
                elif danger_type == "chemical":
                    warnings.append(f"目标'{parsed_intent.target}'可能含有危险化学物质")
                    suggestions.append("穿戴防护装备后再进行操作")
        
        # 检查环境危险
        env_danger = context.environment_state.get("danger_level", "none")
        if env_danger == "high":
            if parsed_intent.action in [ActionType.MOVE, ActionType.INTERACT]:
                warnings.append("当前环境危险等级较高，请谨慎行动")
        
        return {
            "violations": violations,
            "warnings": warnings,
            "suggestions": suggestions
        }
    
    def _predict_chain_reactions(
        self, 
        parsed_intent: ParsedIntent, 
        context: GameContext
    ) -> Dict:
        """
        预测可能的连锁反应
        """
        warnings = []
        suggestions = []
        
        # 获取目标对象
        target_info = self._get_target_info(parsed_intent.target, context)
        
        if not target_info:
            return {"warnings": [], "suggestions": []}
        
        # 分析连锁反应
        connected_objects = target_info.get("connected_to", [])
        
        if connected_objects:
            if parsed_intent.action == ActionType.INTERACT:
                interact_type = parsed_intent.parameters.get("interact_type", "")
                
                if interact_type in ["pull", "open"]:
                    warnings.append(f"操作'{parsed_intent.target}'可能会影响连接的物体: {connected_objects}")
                    suggestions.append("先检查连接关系再操作")
                
                elif interact_type == "press":
                    # 检查是否为关键开关
                    if target_info.get("is_critical_switch"):
                        warnings.append(f"'{parsed_intent.target}'是关键开关，可能影响多个系统")
        
        # 检查移动操作的连锁影响
        if parsed_intent.action == ActionType.MOVE:
            # 检查是否会经过危险区域
            path_dangers = self._check_path_dangers(
                context.jack_position, 
                parsed_intent.target,
                context.danger_zones
            )
            if path_dangers:
                warnings.append(f"移动路径可能经过危险区域: {path_dangers}")
                suggestions.append("考虑绕行或等待危险解除")
        
        return {"warnings": warnings, "suggestions": suggestions}
    
    def _analyze_implicit_risks(
        self, 
        parsed_intent: ParsedIntent, 
        context: GameContext
    ) -> Dict:
        """
        分析指令中的隐含风险
        """
        warnings = []
        
        # 检查时间敏感操作
        if parsed_intent.parameters.get("urgent"):
            warnings.append("这是一个紧急操作，可能导致决策失误")
        
        # 检查复杂操作
        if len(parsed_intent.parameters) > 3:
            warnings.append("指令包含多个参数，执行复杂度较高")
        
        # 检查Jack当前状态
        if context.jack_state == "fatigued":
            if parsed_intent.action in [ActionType.INTERACT, ActionType.USE_ITEM]:
                warnings.append("Jack当前处于疲劳状态，操作可能不够精确")
        
        return {"warnings": warnings}
    
    def _get_target_info(self, target: str, context: GameContext) -> Optional[Dict]:
        """
        从上下文中获取目标对象信息
        """
        for obj in context.nearby_objects:
            if obj.get("name") == target or obj.get("id") == target:
                return obj
        return None
    
    def _check_path_dangers(
        self, 
        start_pos: tuple, 
        target: str, 
        danger_zones: List[Dict]
    ) -> List[str]:
        """
        检查移动路径上的危险区域
        """
        dangers = []
        # 简化的路径危险检测
        for zone in danger_zones:
            if zone.get("intersects_path", False):
                dangers.append(zone.get("name", "未知危险区域"))
        return dangers
```

### 4.3 Level 3 - 状态层检测器

```python
class StateSafetyChecker:
    """
    Level 3: 状态层检测
    
    检测内容：
    1. 当前环境状态是否允许该操作
    2. Jack的当前状态（距离、能力、状态）
    3. 前置条件检查
    """
    
    def check(
        self, 
        parsed_intent: ParsedIntent, 
        context: GameContext
    ) -> Dict:
        """
        执行状态层安全检测
        """
        violations = []
        warnings = []
        suggestions = []
        
        # 1. 前置条件检查
        prereq_result = self._check_prerequisites(parsed_intent, context)
        violations.extend(prereq_result["violations"])
        suggestions.extend(prereq_result["suggestions"])
        
        # 2. Jack状态检查
        jack_result = self._check_jack_state(parsed_intent, context)
        violations.extend(jack_result["violations"])
        warnings.extend(jack_result["warnings"])
        suggestions.extend(jack_result["suggestions"])
        
        # 3. 环境条件检查
        env_result = self._check_environment_state(parsed_intent, context)
        violations.extend(env_result["violations"])
        warnings.extend(env_result["warnings"])
        
        return {
            "violations": violations,
            "warnings": warnings,
            "suggestions": suggestions
        }
    
    def _check_prerequisites(
        self, 
        parsed_intent: ParsedIntent, 
        context: GameContext
    ) -> Dict:
        """
        检查操作的前置条件
        """
        violations = []
        suggestions = []
        
        # 获取目标对象
        target_info = self._get_target_info(parsed_intent.target, context)
        
        if target_info:
            # 检查是否需要特定物品
            required_items = target_info.get("requires_items", [])
            for item in required_items:
                if item not in context.inventory:
                    violations.append(f"操作'{parsed_intent.target}'需要物品'{item}'，但Jack未携带")
                    suggestions.append(f"先获取'{item}'再尝试此操作")
            
            # 检查是否需要特定状态
            required_states = target_info.get("requires_states", [])
            for state in required_states:
                if not self._check_state_condition(state, context):
                    violations.append(f"当前不满足状态条件: {state}")
        
        return {"violations": violations, "suggestions": suggestions}
    
    def _check_jack_state(
        self, 
        parsed_intent: ParsedIntent, 
        context: GameContext
    ) -> Dict:
        """
        检查Jack的当前状态
        """
        violations = []
        warnings = []
        suggestions = []
        
        # 检查距离
        if parsed_intent.target:
            target_info = self._get_target_info(parsed_intent.target, context)
            if target_info:
                target_pos = target_info.get("position")
                if target_pos:
                    distance = self._calculate_distance(
                        context.jack_position, 
                        target_pos
                    )
                    interact_range = target_info.get("interact_range", 2.0)
                    
                    if distance > interact_range:
                        violations.append(
                            f"Jack距离'{parsed_intent.target}'太远({distance:.1f}米)，"
                            f"无法执行'{parsed_intent.action.value}'操作"
                        )
                        suggestions.append(f"先靠近'{parsed_intent.target}'再操作")
        
        # 检查Jack状态
        jack_state = context.jack_state
        
        if jack_state == "incapacitated":
            violations.append("Jack当前无法行动")
        elif jack_state == "restrained":
            if parsed_intent.action in [ActionType.MOVE, ActionType.INTERACT]:
                violations.append("Jack当前被限制，无法执行该操作")
        elif jack_state == "injured":
            if parsed_intent.action == ActionType.MOVE:
                warnings.append("Jack受伤，移动速度会降低")
        elif jack_state == "carrying_heavy":
            if parsed_intent.action == ActionType.MOVE:
                warnings.append("Jack携带重物，移动能力受限")
        
        return {
            "violations": violations,
            "warnings": warnings,
            "suggestions": suggestions
        }
    
    def _check_environment_state(
        self, 
        parsed_intent: ParsedIntent, 
        context: GameContext
    ) -> Dict:
        """
        检查环境状态
        """
        violations = []
        warnings = []
        
        env_state = context.environment_state
        
        # 检查光照
        light_level = env_state.get("light_level", 1.0)
        if light_level < 0.3:
            if parsed_intent.action in [ActionType.INTERACT, ActionType.EXAMINE]:
                warnings.append("环境光线较暗，操作可能不够精确")
        
        # 检查温度
        temperature = env_state.get("temperature", 20)
        if temperature > 40:
            warnings.append("环境温度较高，长时间停留有风险")
        elif temperature < 0:
            warnings.append("环境温度较低，可能影响操作灵活性")
        
        # 检查氧气
        oxygen_level = env_state.get("oxygen_level", 1.0)
        if oxygen_level < 0.5:
            violations.append("氧气含量不足，无法安全执行操作")
        elif oxygen_level < 0.8:
            warnings.append("氧气含量偏低，请尽快撤离")
        
        return {"violations": violations, "warnings": warnings}
    
    def _calculate_distance(
        self, 
        pos1: tuple, 
        pos2: tuple
    ) -> float:
        """
        计算两点间距离
        """
        import math
        return math.sqrt(
            sum((a - b) ** 2 for a, b in zip(pos1, pos2))
        )
    
    def _check_state_condition(self, condition: str, context: GameContext) -> bool:
        """
        检查状态条件是否满足
        """
        # 简化的状态条件检查
        condition_map = {
            "power_on": context.environment_state.get("power", False),
            "door_unlocked": context.environment_state.get("door_locked", True) == False,
        }
        return condition_map.get(condition, False)
    
    def _get_target_info(self, target: str, context: GameContext) -> Optional[Dict]:
        """
        从上下文中获取目标对象信息
        """
        for obj in context.nearby_objects:
            if obj.get("name") == target or obj.get("id") == target:
                return obj
        return None
```



## 5. 模糊指令处理与置信度机制

```python
class FuzzyInstructionHandler:
    """
    模糊指令处理器
    
    处理流程：
    1. 计算置信度分数
    2. 根据阈值决定处理方式
    3. 生成澄清请求或替代建议
    """
    
    # 置信度阈值
    CONFIDENCE_HIGH = 0.8
    CONFIDENCE_MEDIUM = 0.5
    CONFIDENCE_LOW = 0.3
    
    def __init__(self, llm_client):
        self.llm = llm_client
    
    def handle(
        self, 
        parsed_intent: ParsedIntent, 
        confidence: float,
        context: GameContext
    ) -> InstructionResult:
        """
        处理模糊指令
        """
        # 高置信度：直接执行
        if confidence >= self.CONFIDENCE_HIGH:
            return self._create_direct_result(parsed_intent, confidence)
        
        # 中置信度：请求澄清
        elif confidence >= self.CONFIDENCE_MEDIUM:
            return self._create_clarification_request(
                parsed_intent, confidence, context
            )
        
        # 低置信度：拒绝并给出建议
        else:
            return self._create_rejection_result(
                parsed_intent, confidence, context
            )
    
    def _create_direct_result(
        self, 
        parsed_intent: ParsedIntent, 
        confidence: float
    ) -> InstructionResult:
        """
        创建直接执行的结果
        """
        return InstructionResult(
            action=parsed_intent.action.value,
            target_id=parsed_intent.target,
            parameters=parsed_intent.parameters,
            confidence=confidence,
            danger_level=DangerLevel.NONE,
            requires_clarification=False,
            clarification_prompt=None,
            rejection_reason=None,
            alternative_suggestions=[]
        )
    
    def _create_clarification_request(
        self,
        parsed_intent: ParsedIntent,
        confidence: float,
        context: GameContext
    ) -> InstructionResult:
        """
        创建澄清请求
        """
        clarification_prompt = self._generate_clarification_prompt(
            parsed_intent, context
        )
        
        alternatives = self._generate_alternatives(parsed_intent, context)
        
        return InstructionResult(
            action=parsed_intent.action.value,
            target_id=parsed_intent.target,
            parameters=parsed_intent.parameters,
            confidence=confidence,
            danger_level=DangerLevel.NONE,
            requires_clarification=True,
            clarification_prompt=clarification_prompt,
            rejection_reason=None,
            alternative_suggestions=alternatives
        )
    
    def _create_rejection_result(
        self,
        parsed_intent: ParsedIntent,
        confidence: float,
        context: GameContext
    ) -> InstructionResult:
        """
        创建拒绝结果
        """
        reason = self._analyze_rejection_reason(parsed_intent, context)
        alternatives = self._generate_alternatives(parsed_intent, context)
        
        return InstructionResult(
            action="none",
            target_id=None,
            parameters={},
            confidence=confidence,
            danger_level=DangerLevel.NONE,
            requires_clarification=True,
            clarification_prompt=f"我没有理解您的意思。{reason}",
            rejection_reason=f"置信度过低 ({confidence:.2f})",
            alternative_suggestions=alternatives
        )
    
    def _generate_clarification_prompt(
        self,
        parsed_intent: ParsedIntent,
        context: GameContext
    ) -> str:
        """
        生成澄清请求提示
        """
        prompts = []
        
        # 目标不明确
        if not parsed_intent.target:
            prompts.append("请指明您想操作的对象")
        else:
            # 目标存在但不确定
            target_exists = self._check_target_exists(
                parsed_intent.target, context
            )
            if not target_exists:
                nearby = [obj.get("name") for obj in context.nearby_objects[:3]]
                prompts.append(
                    f"附近没有找到'{parsed_intent.target}'。"
                    f"您是否指的是: {', '.join(nearby)}?"
                )
        
        # 动作不明确
        if parsed_intent.action == ActionType.INTERACT:
            interact_type = parsed_intent.parameters.get("interact_type")
            if not interact_type:
                prompts.append("请说明您想如何操作（按下、拉动、打开等）")
        
        # 参数缺失
        if parsed_intent.action == ActionType.MOVE:
            if "direction" not in parsed_intent.parameters:
                prompts.append("请指明移动方向或目的地")
        
        return " ".join(prompts) if prompts else "请用更具体的方式描述您的意图"
    
    def _generate_alternatives(
        self,
        parsed_intent: ParsedIntent,
        context: GameContext
    ) -> List[str]:
        """
        生成替代建议
        """
        alternatives = []
        
        # 基于当前意图生成替代方案
        if parsed_intent.target:
            # 查找相似目标
            similar_targets = self._find_similar_targets(
                parsed_intent.target, context
            )
            for target in similar_targets[:2]:
                alternatives.append(
                    f"{parsed_intent.action.value} {target}"
                )
        
        # 基于上下文推荐常见操作
        if context.nearby_objects:
            obj = context.nearby_objects[0]
            alternatives.append(f"检查 {obj.get('name', '周围')}")
        
        # 添加通用建议
        alternatives.extend([
            "等待",
            "观察周围",
        ])
        
        return alternatives[:5]  # 最多返回5个建议
    
    def _analyze_rejection_reason(
        self,
        parsed_intent: ParsedIntent,
        context: GameContext
    ) -> str:
        """
        分析拒绝原因
        """
        reasons = []
        
        if not parsed_intent.target:
            reasons.append("未指明操作对象")
        elif not self._check_target_exists(parsed_intent.target, context):
            reasons.append(f"找不到对象'{parsed_intent.target}'")
        
        if parsed_intent.action == ActionType.INTERACT:
            if not parsed_intent.parameters.get("interact_type"):
                reasons.append("操作方式不明确")
        
        if not reasons:
            reasons.append("指令过于模糊")
        
        return "可能的原因: " + "; ".join(reasons)
    
    def _check_target_exists(
        self, 
        target: str, 
        context: GameContext
    ) -> bool:
        """
        检查目标是否存在
        """
        if not target:
            return False
        
        for obj in context.nearby_objects:
            if obj.get("name") == target or obj.get("id") == target:
                return True
        
        # 检查是否为已知位置
        known_locations = ["门口", "窗户", "控制台", "出口"]
        if target in known_locations:
            return True
        
        return False
    
    def _find_similar_targets(
        self,
        target: str,
        context: GameContext
    ) -> List[str]:
        """
        查找相似的目标
        """
        similar = []
        target_lower = target.lower()
        
        for obj in context.nearby_objects:
            obj_name = obj.get("name", "")
            # 简单的相似度检查
            if any(word in obj_name.lower() for word in target_lower):
                similar.append(obj_name)
        
        return similar


class ConfidenceCalculator:
    """
    置信度计算器
    
    综合考虑多个因素计算最终置信度
    """
    
    def calculate(
        self,
        parsed_intent: ParsedIntent,
        context: GameContext,
        parsing_method: str = "llm"
    ) -> float:
        """
        计算置信度分数
        
        返回: 0.0 - 1.0 之间的置信度分数
        """
        scores = []
        
        # 1. 目标存在性分数 (权重: 0.30)
        target_score = self._calculate_target_score(parsed_intent, context)
        scores.append((target_score, 0.30))
        
        # 2. 动作-目标匹配分数 (权重: 0.25)
        match_score = self._calculate_action_target_match_score(parsed_intent)
        scores.append((match_score, 0.25))
        
        # 3. 上下文一致性分数 (权重: 0.25)
        context_score = self._calculate_context_consistency(parsed_intent, context)
        scores.append((context_score, 0.25))
        
        # 4. 解析方法分数 (权重: 0.20)
        method_score = 0.9 if parsing_method == "rule" else 0.7
        scores.append((method_score, 0.20))
        
        # 加权计算
        weighted_sum = sum(score * weight for score, weight in scores)
        total_weight = sum(weight for _, weight in scores)
        
        confidence = weighted_sum / total_weight if total_weight > 0 else 0.0
        
        return round(min(max(confidence, 0.0), 1.0), 3)
    
    def _calculate_target_score(
        self,
        parsed_intent: ParsedIntent,
        context: GameContext
    ) -> float:
        """
        计算目标存在性分数
        """
        if not parsed_intent.target:
            return 0.0
        
        # 精确匹配
        for obj in context.nearby_objects:
            if obj.get("name") == parsed_intent.target:
                return 1.0
            if obj.get("id") == parsed_intent.target:
                return 0.9
        
        # 部分匹配
        target_lower = parsed_intent.target.lower()
        for obj in context.nearby_objects:
            obj_name = obj.get("name", "").lower()
            if target_lower in obj_name or obj_name in target_lower:
                return 0.6
        
        # 检查已知位置
        known_locations = ["门口", "窗户", "控制台", "出口", "入口"]
        if parsed_intent.target in known_locations:
            return 0.7
        
        return 0.2
    
    def _calculate_action_target_match_score(
        self,
        parsed_intent: ParsedIntent
    ) -> float:
        """
        计算动作-目标匹配分数
        """
        valid_combinations = {
            (ActionType.MOVE, "location"): 1.0,
            (ActionType.MOVE, "object"): 0.8,
            (ActionType.INTERACT, "object"): 1.0,
            (ActionType.INTERACT, "npc"): 0.7,
            (ActionType.EXAMINE, "object"): 1.0,
            (ActionType.EXAMINE, "location"): 1.0,
            (ActionType.EXAMINE, "npc"): 0.9,
            (ActionType.USE_ITEM, "object"): 1.0,
            (ActionType.COMMUNICATE, "npc"): 1.0,
        }
        
        key = (parsed_intent.action, parsed_intent.target_type)
        return valid_combinations.get(key, 0.3)
    
    def _calculate_context_consistency(
        self,
        parsed_intent: ParsedIntent,
        context: GameContext
    ) -> float:
        """
        计算上下文一致性分数
        """
        score = 0.5  # 基础分数
        
        # 检查与最近动作的连贯性
        if context.recent_actions:
            last_action = context.recent_actions[-1]
            # 如果当前动作与上一个动作逻辑连贯，加分
            if self._is_action_sequence_logical(last_action, parsed_intent):
                score += 0.3
        
        # 检查是否符合当前目标
        if context.current_objective:
            if self._is_action_relevant_to_objective(
                parsed_intent, context.current_objective
            ):
                score += 0.2
        
        return min(score, 1.0)
    
    def _is_action_sequence_logical(
        self,
        last_action: str,
        current_intent: ParsedIntent
    ) -> bool:
        """
        检查动作序列是否逻辑连贯
        """
        # 简化的逻辑检查
        logical_sequences = [
            ("move", ActionType.EXAMINE),
            ("examine", ActionType.INTERACT),
            ("interact", ActionType.MOVE),
        ]
        
        for prev, curr in logical_sequences:
            if prev in last_action.lower() and current_intent.action == curr:
                return True
        
        return False
    
    def _is_action_relevant_to_objective(
        self,
        parsed_intent: ParsedIntent,
        objective: str
    ) -> bool:
        """
        检查动作是否与目标相关
        """
        # 简化的相关性检查
        objective_keywords = objective.lower().split()
        intent_text = parsed_intent.raw_text.lower()
        
        return any(keyword in intent_text for keyword in objective_keywords)
```

## 6. 结构化输出Schema与物理状态机接口

### 6.1 输出Schema定义

```python
# 完整输出Schema（JSON格式）
OUTPUT_SCHEMA = {
    "$schema": "http://json-schema.org/draft-07/schema#",
    "title": "InstructionResult",
    "type": "object",
    "required": ["action", "confidence", "danger_level", "requires_clarification"],
    "properties": {
        "action": {
            "type": "string",
            "enum": ["move", "interact", "use_item", "examine", "communicate", "wait", "cancel", "none"],
            "description": "要执行的动作类型"
        },
        "target_id": {
            "type": ["string", "null"],
            "description": "目标对象的唯一标识符"
        },
        "parameters": {
            "type": "object",
            "description": "动作的详细参数",
            "properties": {
                "interact_type": {
                    "type": "string",
                    "enum": ["press", "pull", "open", "close", "pickup", "drop", "use"],
                    "description": "交互类型"
                },
                "direction": {
                    "type": "string",
                    "enum": ["toward", "away", "left", "right", "up", "down"],
                    "description": "移动方向"
                },
                "position": {
                    "type": "object",
                    "properties": {
                        "x": {"type": "number"},
                        "y": {"type": "number"},
                        "z": {"type": "number"}
                    },
                    "description": "目标位置坐标"
                },
                "force": {
                    "type": "number",
                    "minimum": 0,
                    "maximum": 1,
                    "description": "操作力度 (0-1)"
                },
                "speed": {
                    "type": "number",
                    "minimum": 0,
                    "maximum": 1,
                    "description": "移动速度 (0-1)"
                },
                "duration": {
                    "type": "number",
                    "minimum": 0,
                    "description": "持续时间（秒）"
                },
                "item_id": {
                    "type": "string",
                    "description": "要使用的物品ID"
                },
                "message": {
                    "type": "string",
                    "description": "交流消息内容"
                }
            },
            "additionalProperties": True
        },
        "confidence": {
            "type": "number",
            "minimum": 0,
            "maximum": 1,
            "description": "置信度分数 (0-1)"
        },
        "danger_level": {
            "type": "string",
            "enum": ["none", "low", "medium", "high", "critical"],
            "description": "危险等级"
        },
        "requires_clarification": {
            "type": "boolean",
            "description": "是否需要用户澄清"
        },
        "clarification_prompt": {
            "type": ["string", "null"],
            "description": "向用户显示的澄清请求"
        },
        "rejection_reason": {
            "type": ["string", "null"],
            "description": "指令被拒绝的原因"
        },
        "alternative_suggestions": {
            "type": "array",
            "items": {"type": "string"},
            "description": "替代建议列表"
        },
        "safety_warnings": {
            "type": "array",
            "items": {"type": "string"},
            "description": "安全警告信息"
        },
        "execution_metadata": {
            "type": "object",
            "description": "执行相关的元数据",
            "properties": {
                "estimated_duration": {
                    "type": "number",
                    "description": "预计执行时间（秒）"
                },
                "prerequisites": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "前置条件列表"
                },
                "expected_outcomes": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "预期结果列表"
                }
            }
        }
    }
}

# 输出示例
OUTPUT_EXAMPLES = {
    "example_1_direct_execution": {
        "action": "interact",
        "target_id": "control_panel_01",
        "parameters": {
            "interact_type": "press",
            "target_button": "power_button"
        },
        "confidence": 0.92,
        "danger_level": "low",
        "requires_clarification": False,
        "clarification_prompt": None,
        "rejection_reason": None,
        "alternative_suggestions": [],
        "safety_warnings": ["此操作将改变电源状态"],
        "execution_metadata": {
            "estimated_duration": 2.0,
            "prerequisites": ["靠近控制台"],
            "expected_outcomes": ["电源状态切换"]
        }
    },
    
    "example_2_clarification_needed": {
        "action": "move",
        "target_id": "door",
        "parameters": {
            "direction": "toward"
        },
        "confidence": 0.65,
        "danger_level": "none",
        "requires_clarification": True,
        "clarification_prompt": "附近有两扇门：主门（北方）和侧门（东方）。您想去哪一扇？",
        "rejection_reason": None,
        "alternative_suggestions": [
            "去主门",
            "去侧门"
        ],
        "safety_warnings": [],
        "execution_metadata": {}
    },
    
    "example_3_rejected": {
        "action": "none",
        "target_id": None,
        "parameters": {},
        "confidence": 0.25,
        "danger_level": "none",
        "requires_clarification": True,
        "clarification_prompt": "我没有理解您的意思。请尝试描述您想做什么，例如：去某个地方、检查某个物体、按下某个按钮等。",
        "rejection_reason": "置信度过低 (0.25)",
        "alternative_suggestions": [
            "检查周围环境",
            "去控制台",
            "等待"
        ],
        "safety_warnings": [],
        "execution_metadata": {}
    },
    
    "example_4_dangerous_rejected": {
        "action": "interact",
        "target_id": "electrical_panel",
        "parameters": {
            "interact_type": "open"
        },
        "confidence": 0.88,
        "danger_level": "critical",
        "requires_clarification": False,
        "clarification_prompt": None,
        "rejection_reason": "检测到致命危险: 目标'electrical_panel'是带电设备，直接接触有触电风险",
        "alternative_suggestions": [
            "先切断主电源",
            "使用绝缘工具操作",
            "呼叫专业人员"
        ],
        "safety_warnings": ["高压危险！", "可能导致严重伤害或死亡"],
        "execution_metadata": {}
    }
}
```

### 6.2 物理状态机交互接口

```python
class PhysicsStateMachineInterface:
    """
    AI Interpreter 与物理状态机的交互接口
    
    职责：
    1. 将结构化指令转换为物理世界操作
    2. 获取物理世界状态更新
    3. 处理执行结果与异常
    """
    
    def __init__(self, physics_engine, game_state_manager):
        self.physics = physics_engine
        self.state_manager = game_state_manager
    
    def execute_instruction(
        self, 
        instruction: InstructionResult,
        jack_agent
    ) -> Dict:
        """
        执行结构化指令
        
        Args:
            instruction: AI Interpreter生成的指令
            jack_agent: Jack智能体实例
            
        Returns:
            执行结果，包含状态变化和Jack的感知信息
        """
        if instruction.action == "none":
            return {
                "success": False,
                "reason": instruction.rejection_reason or "无有效动作",
                "state_changes": [],
                "jack_perception": None
            }
        
        # 根据动作类型分发执行
        action_handlers = {
            "move": self._handle_move,
            "interact": self._handle_interact,
            "use_item": self._handle_use_item,
            "examine": self._handle_examine,
            "communicate": self._handle_communicate,
            "wait": self._handle_wait,
            "cancel": self._handle_cancel,
        }
        
        handler = action_handlers.get(instruction.action)
        if not handler:
            return {
                "success": False,
                "reason": f"未知的动作类型: {instruction.action}",
                "state_changes": [],
                "jack_perception": None
            }
        
        return handler(instruction, jack_agent)
    
    def _handle_move(
        self, 
        instruction: InstructionResult,
        jack_agent
    ) -> Dict:
        """
        处理移动指令
        """
        params = instruction.parameters
        target_id = instruction.target_id
        
        # 获取目标位置
        target_position = self._get_target_position(target_id)
        if not target_position:
            return {
                "success": False,
                "reason": f"找不到目标位置: {target_id}",
                "state_changes": [],
                "jack_perception": None
            }
        
        # 计算路径
        path = self.physics.calculate_path(
            jack_agent.position,
            target_position,
            params.get("speed", 0.5)
        )
        
        # 执行移动
        speed = params.get("speed", 0.5)
        duration = self.physics.estimate_move_duration(path, speed)
        
        # 更新Jack状态
        jack_agent.set_state("moving", {
            "path": path,
            "speed": speed,
            "target": target_id
        })
        
        return {
            "success": True,
            "reason": None,
            "state_changes": [{
                "entity": "jack",
                "property": "position",
                "from": jack_agent.position,
                "to": target_position,
                "duration": duration
            }],
            "jack_perception": {
                "type": "movement_started",
                "target": target_id,
                "estimated_arrival": duration
            }
        }
    
    def _handle_interact(
        self, 
        instruction: InstructionResult,
        jack_agent
    ) -> Dict:
        """
        处理交互指令
        """
        params = instruction.parameters
        target_id = instruction.target_id
        interact_type = params.get("interact_type")
        
        # 获取目标对象
        target_obj = self.state_manager.get_object(target_id)
        if not target_obj:
            return {
                "success": False,
                "reason": f"找不到目标对象: {target_id}",
                "state_changes": [],
                "jack_perception": None
            }
        
        # 检查交互可行性
        distance = self._calculate_distance(
            jack_agent.position, 
            target_obj.position
        )
        interact_range = target_obj.get_interact_range()
        
        if distance > interact_range:
            return {
                "success": False,
                "reason": f"距离太远 ({distance:.1f}m > {interact_range}m)",
                "state_changes": [],
                "jack_perception": {
                    "type": "interaction_failed",
                    "reason": "out_of_range",
                    "target": target_id
                }
            }
        
        # 执行交互
        result = target_obj.interact(interact_type, params)
        
        # 收集状态变化
        state_changes = result.get("state_changes", [])
        
        # 更新物理世界
        for change in state_changes:
            self.physics.apply_change(change)
        
        return {
            "success": result.get("success", True),
            "reason": result.get("reason"),
            "state_changes": state_changes,
            "jack_perception": {
                "type": "interaction_complete",
                "target": target_id,
                "interaction": interact_type,
                "result": result.get("description", "操作完成")
            }
        }
    
    def _handle_examine(
        self, 
        instruction: InstructionResult,
        jack_agent
    ) -> Dict:
        """
        处理检查指令
        """
        target_id = instruction.target_id
        
        if target_id == "周围" or target_id is None:
            # 检查周围环境
            surroundings = self._get_surroundings(jack_agent.position)
            return {
                "success": True,
                "reason": None,
                "state_changes": [],
                "jack_perception": {
                    "type": "surroundings_observed",
                    "objects": surroundings["objects"],
                    "features": surroundings["features"]
                }
            }
        
        # 检查特定对象
        target_obj = self.state_manager.get_object(target_id)
        if not target_obj:
            return {
                "success": False,
                "reason": f"找不到目标: {target_id}",
                "state_changes": [],
                "jack_perception": None
            }
        
        # 获取对象详细信息
        details = target_obj.get_examine_details()
        
        return {
            "success": True,
            "reason": None,
            "state_changes": [],
            "jack_perception": {
                "type": "object_examined",
                "target": target_id,
                "details": details
            }
        }
    
    def _handle_use_item(
        self, 
        instruction: InstructionResult,
        jack_agent
    ) -> Dict:
        """
        处理使用物品指令
        """
        params = instruction.parameters
        item_id = params.get("item_id")
        target_id = instruction.target_id
        
        # 检查物品是否在背包中
        if item_id not in jack_agent.inventory:
            return {
                "success": False,
                "reason": f"Jack没有物品: {item_id}",
                "state_changes": [],
                "jack_perception": None
            }
        
        # 获取物品和目标
        item = self.state_manager.get_item(item_id)
        target = self.state_manager.get_object(target_id) if target_id else None
        
        # 执行使用
        result = item.use(target, params)
        
        return {
            "success": result.get("success", True),
            "reason": result.get("reason"),
            "state_changes": result.get("state_changes", []),
            "jack_perception": {
                "type": "item_used",
                "item": item_id,
                "target": target_id,
                "result": result.get("description", "物品已使用")
            }
        }
    
    def _handle_communicate(
        self, 
        instruction: InstructionResult,
        jack_agent
    ) -> Dict:
        """
        处理交流指令
        """
        params = instruction.parameters
        message = params.get("message", "")
        target_id = instruction.target_id
        
        return {
            "success": True,
            "reason": None,
            "state_changes": [],
            "jack_perception": {
                "type": "communication_sent",
                "target": target_id,
                "message": message
            }
        }
    
    def _handle_wait(
        self, 
        instruction: InstructionResult,
        jack_agent
    ) -> Dict:
        """
        处理等待指令
        """
        params = instruction.parameters
        duration = params.get("duration", 1.0)  # 默认等待1秒
        
        jack_agent.set_state("waiting", {"duration": duration})
        
        return {
            "success": True,
            "reason": None,
            "state_changes": [],
            "jack_perception": {
                "type": "waiting",
                "duration": duration
            }
        }
    
    def _handle_cancel(
        self, 
        instruction: InstructionResult,
        jack_agent
    ) -> Dict:
        """
        处理取消指令
        """
        current_action = jack_agent.get_current_action()
        
        if current_action:
            jack_agent.cancel_action()
            return {
                "success": True,
                "reason": None,
                "state_changes": [{
                    "entity": "jack",
                    "property": "action",
                    "from": current_action,
                    "to": None
                }],
                "jack_perception": {
                    "type": "action_cancelled",
                    "cancelled_action": current_action
                }
            }
        
        return {
            "success": True,
            "reason": "没有正在进行的动作",
            "state_changes": [],
            "jack_perception": {
                "type": "no_action_to_cancel"
            }
        }
    
    def get_game_context(self, jack_agent) -> GameContext:
        """
        获取当前游戏上下文（供AI Interpreter使用）
        """
        return GameContext(
            jack_position=jack_agent.position,
            jack_state=jack_agent.get_state(),
            nearby_objects=self._get_nearby_objects(jack_agent.position),
            environment_state=self._get_environment_state(),
            inventory=jack_agent.inventory,
            current_objective=self.state_manager.get_current_objective(),
            recent_actions=self.state_manager.get_recent_actions(5),
            danger_zones=self._get_danger_zones()
        )
    
    def _get_nearby_objects(self, position: tuple, radius: float = 10.0) -> List[Dict]:
        """获取附近对象"""
        return self.state_manager.query_objects_in_radius(position, radius)
    
    def _get_environment_state(self) -> Dict:
        """获取环境状态"""
        return self.state_manager.get_environment_state()
    
    def _get_danger_zones(self) -> List[Dict]:
        """获取危险区域"""
        return self.state_manager.get_danger_zones()
    
    def _get_target_position(self, target_id: str) -> Optional[tuple]:
        """获取目标位置"""
        obj = self.state_manager.get_object(target_id)
        if obj:
            return obj.position
        
        # 检查是否为预定义位置
        predefined = self.state_manager.get_predefined_location(target_id)
        if predefined:
            return predefined["position"]
        
        return None
    
    def _calculate_distance(self, pos1: tuple, pos2: tuple) -> float:
        """计算距离"""
        import math
        return math.sqrt(sum((a - b) ** 2 for a, b in zip(pos1, pos2)))
    
    def _get_surroundings(self, position: tuple) -> Dict:
        """获取周围环境信息"""
        objects = self._get_nearby_objects(position, radius=15.0)
        return {
            "objects": [
                {
                    "name": obj.get("name"),
                    "distance": self._calculate_distance(position, obj.get("position", position)),
                    "type": obj.get("type", "unknown")
                }
                for obj in objects
            ],
            "features": self.state_manager.get_environment_features(position)
        }
```



## 7. 完整流程示例

```python
# ============================================================
# 完整使用示例：从玩家输入到物理世界执行
# ============================================================

class GameLoop:
    """
    游戏主循环
    
    展示AI Interpreter与物理状态机的完整交互流程
    """
    
    def __init__(self):
        # 初始化各组件
        self.llm_client = LLMClient()  # LLM客户端
        self.physics_engine = PhysicsEngine()  # 物理引擎
        self.state_manager = GameStateManager()  # 游戏状态管理器
        self.jack_agent = JackAgent()  # Jack智能体
        
        # 初始化AI Interpreter
        self.interpreter = AIInterpreter(
            llm_client=self.llm_client,
            game_state_manager=self.state_manager
        )
        
        # 初始化物理状态机接口
        self.physics_interface = PhysicsStateMachineInterface(
            physics_engine=self.physics_engine,
            game_state_manager=self.state_manager
        )
    
    def process_player_input(self, player_input: str) -> str:
        """
        处理玩家输入的完整流程
        
        Args:
            player_input: 玩家的自然语言指令
            
        Returns:
            Jack的回复
        """
        # Step 1: 获取当前游戏上下文
        context = self.physics_interface.get_game_context(self.jack_agent)
        
        # Step 2: AI Interpreter分析指令
        instruction_result = self.interpreter.interpret_instruction(
            player_input, 
            context
        )
        
        # Step 3: 处理Interpreter输出
        if instruction_result.requires_clarification:
            # 需要澄清，直接返回澄清请求
            return self._generate_jack_response(
                instruction_result, 
                is_clarification=True
            )
        
        if instruction_result.rejection_reason:
            # 指令被拒绝，返回拒绝原因和建议
            return self._generate_jack_response(
                instruction_result, 
                is_rejection=True
            )
        
        # Step 4: 执行指令
        execution_result = self.physics_interface.execute_instruction(
            instruction_result,
            self.jack_agent
        )
        
        # Step 5: 生成Jack的回复
        jack_response = self._generate_jack_response(
            instruction_result,
            execution_result=execution_result
        )
        
        return jack_response
    
    def _generate_jack_response(
        self,
        instruction: InstructionResult,
        execution_result: Dict = None,
        is_clarification: bool = False,
        is_rejection: bool = False
    ) -> str:
        """
        生成Jack的回复
        """
        if is_clarification:
            return f"Jack: {instruction.clarification_prompt}"
        
        if is_rejection:
            response = f"Jack: 我无法执行这个指令。{instruction.rejection_reason}"
            if instruction.alternative_suggestions:
                response += f"\\n您可以尝试: {', '.join(instruction.alternative_suggestions)}"
            return response
        
        # 正常执行回复
        perception = execution_result.get("jack_perception", {})
        perception_type = perception.get("type", "unknown")
        
        # 根据感知类型生成回复
        response_templates = {
            "movement_started": "好的，我正在前往{target}。",
            "interaction_complete": "{result}",
            "object_examined": "我看到了: {details}",
            "surroundings_observed": "我观察到: {objects}",
            "item_used": "{result}",
            "waiting": "我会等待。",
            "action_cancelled": "已取消当前动作。",
        }
        
        template = response_templates.get(
            perception_type, 
            "指令已执行。"
        )
        
        return f"Jack: {template.format(**perception)}"


# ============================================================
# 具体示例演示
# ============================================================

"""
示例1: 正常移动指令
-------------------
玩家输入: "去控制台"

AI Interpreter处理:
- 语义解析: action=MOVE, target="控制台", target_type="location"
- 安全检测: 通过（无危险）
- 置信度: 0.92 (高)
- 输出: 直接执行

物理状态机执行:
- 计算路径
- Jack开始移动
- 返回状态变化

Jack回复: "好的，我正在前往控制台。"


示例2: 模糊指令
-------------------
玩家输入: "去那边"

AI Interpreter处理:
- 语义解析: action=MOVE, target="那边", target_type="location"
- 安全检测: 通过
- 置信度: 0.45 (低)
- 输出: 需要澄清

Jack回复: "Jack: 请指明您想去哪里。附近可选: 控制台, 门口, 储物柜"


示例3: 危险指令
-------------------
玩家输入: "打开配电箱"

AI Interpreter处理:
- 语义解析: action=INTERACT, target="配电箱", parameters={"interact_type": "open"}
- Level 1: 通过
- Level 2: 检测到危险 - 配电箱带电，直接接触有触电风险
- Level 3: 检查通过（距离足够）
- 危险等级: CRITICAL
- 输出: 拒绝执行

Jack回复: "Jack: 我无法执行这个指令。检测到致命危险: 目标'配电箱'是带电设备，直接接触有触电风险
您可以尝试: 先切断主电源, 使用绝缘工具操作, 呼叫专业人员"


示例4: 需要前置条件的指令
-------------------
玩家输入: "用钥匙卡开门"

AI Interpreter处理:
- 语义解析: action=USE_ITEM, target="门", parameters={"item_id": "钥匙卡"}
- Level 1: 通过
- Level 2: 通过
- Level 3: 检查失败 - Jack未携带钥匙卡
- 输出: 拒绝执行

Jack回复: "Jack: 我无法执行这个指令。操作'门'需要物品'钥匙卡'，但我未携带
您可以尝试: 先寻找钥匙卡"


示例5: 连锁反应预测
-------------------
玩家输入: "拉下那个杠杆"

AI Interpreter处理:
- 语义解析: action=INTERACT, target="杠杆", parameters={"interact_type": "pull"}
- Level 1: 通过
- Level 2: 检测到连锁反应 - 杠杆连接着吊桥机制，操作可能影响吊桥状态
- 危险等级: MEDIUM
- 置信度: 0.88
- 输出: 执行（带警告）

物理状态机执行:
- Jack拉下杠杆
- 吊桥开始下降
- 返回状态变化

Jack回复: "Jack: 我拉下了杠杆。吊桥正在下降，请小心！"
"""
```

## 8. 配置参数汇总

```python
# ============================================================
# 系统配置参数
# ============================================================

INTERPRETER_CONFIG = {
    # 置信度阈值
    "confidence_thresholds": {
        "high": 0.8,      # 高置信度，直接执行
        "medium": 0.5,    # 中置信度，请求澄清
        "low": 0.3,       # 低置信度，拒绝
    },
    
    # 安全检测配置
    "safety_check": {
        "enable_syntax_check": True,
        "enable_semantic_check": True,
        "enable_state_check": True,
        "stop_on_critical": True,  # 遇到致命危险立即停止
    },
    
    # 模糊匹配配置
    "fuzzy_matching": {
        "similarity_threshold": 0.6,
        "max_alternatives": 5,
    },
    
    # LLM配置
    "llm": {
        "model": "gpt-4",
        "temperature": 0.2,  # 低温度，更确定性输出
        "max_tokens": 500,
        "timeout": 5.0,  # 秒
    },
    
    # 上下文配置
    "context": {
        "nearby_object_radius": 10.0,  # 米
        "recent_actions_count": 5,
        "max_context_length": 1000,  # 字符
    }
}

# 危险关键词配置（可扩展）
DANGER_KEYWORDS_CONFIG = {
    "critical": [
        "爆炸", "引爆", "炸毁", "炸药", "炸弹",
        "自杀", "跳楼", "跳下去", "跳崖",
        "烧毁", "放火", "纵火", "燃烧瓶",
        "短路", "触电", "电击", "高压",
        "毒药", "毒死", "下毒", "毒气",
        "坠落", "坠落", "跌落",
    ],
    "high": [
        "破坏", "砸碎", "打碎", "摧毁",
        "偷窃", "偷走", "盗取",
        "攻击", "殴打", "伤害",
        "闯入", "入侵", "非法进入",
        "禁用", "关闭系统", "切断电源",
    ],
    "medium": [
        "爬", "攀爬", "跳", "跳跃",
        "推", "拉", "搬动",
        "快速", "加速", "冲刺",
    ]
}

# 动作-目标匹配规则
ACTION_TARGET_RULES = {
    "move": ["location", "object", "npc"],
    "interact": ["object", "npc"],
    "use_item": ["object"],
    "examine": ["object", "location", "npc"],
    "communicate": ["npc"],
    "wait": [],
    "cancel": [],
}
```

---

## 附录：关键流程图

### 意图识别主流程

```
┌─────────────────┐
│   玩家输入      │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  1. 输入预处理   │
│  - 清洗文本      │
│  - 标准化       │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  2. 语义解析     │
│  - 规则匹配      │
│  - LLM提取      │
│  - 模糊匹配      │
└────────┬────────┘
         │
         ▼
┌─────────────────┐     否
│ 解析成功?       │────────▶ 返回解析失败
└────────┬────────┘
         │ 是
         ▼
┌─────────────────┐
│  3. 安全检测     │
│  - Level 1 语法  │
│  - Level 2 语义  │
│  - Level 3 状态  │
└────────┬────────┘
         │
         ▼
┌─────────────────┐     是
│ 致命危险?       │────────▶ 拒绝执行
└────────┬────────┘
         │ 否
         ▼
┌─────────────────┐
│  4. 置信度评估   │
│  - 目标存在性    │
│  - 动作匹配     │
│  - 上下文一致   │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  5. 生成输出     │
│  - 高置信度:执行 │
│  - 中置信度:澄清 │
│  - 低置信度:拒绝 │
└─────────────────┘
```

### 安全检测三层架构

```
┌─────────────────────────────────────────────────────┐
│                    安全检测系统                       │
├─────────────────────────────────────────────────────┤
│                                                     │
│  ┌─────────────────────────────────────────────┐   │
│  │ Level 1: 语法层检测                          │   │
│  │ - 关键词黑名单匹配                            │   │
│  │ - 动作-目标类型匹配                           │   │
│  │ - 参数范围检查                               │   │
│  └──────────────────┬──────────────────────────┘   │
│                     │ 传递检测                        │
│                     ▼                               │
│  ┌─────────────────────────────────────────────┐   │
│  │ Level 2: 语义层检测                          │   │
│  │ - 上下文危险评估                            │   │
│  │ - 连锁反应预测                              │   │
│  │ - 隐含风险分析                              │   │
│  └──────────────────┬──────────────────────────┘   │
│                     │ 传递检测                        │
│                     ▼                               │
│  ┌─────────────────────────────────────────────┐   │
│  │ Level 3: 状态层检测                          │   │
│  │ - 前置条件检查                              │   │
│  │ - Jack状态检查                              │   │
│  │ - 环境条件检查                              │   │
│  └──────────────────┬──────────────────────────┘   │
│                     │                               │
│                     ▼                               │
│  ┌─────────────────────────────────────────────┐   │
│  │           综合危险等级评估                    │   │
│  │  NONE/LOW/MEDIUM/HIGH/CRITICAL              │   │
│  └─────────────────────────────────────────────┘   │
│                                                     │
└─────────────────────────────────────────────────────┘
```

---

*文档结束*
