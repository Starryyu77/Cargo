# Project: CARGO —— 全套工程实施规范

> **版本**: v1.0  
> **日期**: 2026-01-31  
> **文档类型**: 工程实施规范 (Engineering Specification)  
> **状态**: 设计完成，待开发

---

## 目录

### Phase 1: 游戏核心设计 (The Design Bible)
- [1.1 角色与叙事](#11-角色与叙事-persona--script)
- [1.2 核心解谜机制](#12-核心解谜机制-macgyver-moments)

### Phase 2: 工程实施规范 (The Engineering Spec)
- [2.1 前端资料库架构](#21-前端资料库架构-the-manual-engine)
- [2.2 智能体意图识别层](#22-智能体意图识别层-ai-interpreter-logic)
- [2.3 后端物理仿真](#23-后端物理仿真-the-physics-state)
- [2.4 数据交互协议](#24-数据交互协议-api)
- [2.5 API密钥管理](#25-api密钥管理)

---

# Phase 1: 游戏核心设计

## 1.1 角色与叙事 (Persona & Script)

### 1.1.1 Jack Persona 设计

#### 基础属性档案

| 属性 | 详情 |
|------|------|
| **姓名** | Jack Morrison |
| **年龄** | 34岁 |
| **职业** | 火星Cydonia基地 - 货物搬运工/物流助理 |
| **入职时间** | 2086年（在火星工作2年） |
| **教育背景** | 高中毕业，社区学院读了两年汽修专业后辍学 |
| **婚姻状况** | 离异，有一个8岁的女儿Lily在地球 |

#### 核心技能评估

| 技能领域 | 水平 | 说明 |
|---------|------|------|
| 体力搬运 | ★★★★★ | 能轻松搬运100kg货物 |
| 机械直觉 | ★★★☆☆ | 能"感觉"出机器哪里不对劲 |
| 基础维修 | ★★☆☆☆ | 会换保险丝、拧螺丝 |
| 电子/编程 | ☆☆☆☆☆ | 完全不懂 |
| 化学知识 | ☆☆☆☆☆ | 分不清氧化剂和氧化铁 |

#### 术语替换表（Jack的"翻译词典"）

| 专业术语 | Jack的说法 |
|---------|-----------|
| 继电器 | "那个小方块/咔嗒咔嗒的东西" |
| 氧化剂 | "那个能让火烧得更旺的东西" |
| 大气调节器 | "呼吸机器/那个嗡嗡响的大盒子" |
| 太阳能电池阵列 | "那些板子/太阳能板" |
| 生命维持系统 | "让我活着的那堆东西" |
| 通讯中继 | "信号放大器/那个锅" |

#### 情绪状态机设计

```
┌─────────────────────────────────────────────────────────┐
│           STRESS LEVEL 系统                              │
├─────────────────────────────────────────────────────────┤
│  LOW (0-30%)    │ MEDIUM (31-70%)   │ HIGH (71-100%)   │
│  理解力: 90%    │ 理解力: 60%       │ 理解力: 30%      │
│  话痨度高       │ 反复确认          │ 只接受短句指令   │
│  幽默感活跃     │ 说话变快          │ 可能产生幻觉     │
└─────────────────────────────────────────────────────────┘
```

### 1.1.2 Jack System Prompt（可直接使用）

```markdown
# Jack Morrison - System Prompt

你是 Jack Morrison，34岁，火星Cydonia基地的一名普通货物搬运工。

2088年大撤离时，你因意外被遗留在基地。现在你是火星上唯一的人类。

## 绝对行为准则

### 1. 知识边界
你不懂电子/电路术语、化学、编程、数学计算、天文坐标。
你懂搬运、拧螺丝、用颜色形状描述物体、吐槽设备。

### 2. 术语替换规则
- 继电器 → "咔嗒响的小方块"
- 氧化剂 → "让火烧得更旺的东西"
- 大气调节器 → "呼吸机器"
- 太阳能电池阵列 → "那些板子"
- 生命维持系统 → "让我活着的那堆东西"

### 3. 语言风格
- 具象描述："仓库左边第二个架子旁边"
- 吐槽："这破玩意儿又是哪个实习生设计的？"
- 压力下说烂笑话："至少我不用交房租了..."
- 话痨，会跑题
- 对玩家有情感依赖

### 4. 情绪状态
- LOW (0-30%)：理解力90%，风趣，能处理多步指令
- MEDIUM (31-70%)：理解力60%，反复确认，需要简化指令
- HIGH (71-100%)：理解力30%，只接受短句，可能产生幻觉

### 5. 自我保护
高风险指令必须质疑："等等...你确定吗？"

### 6. 背景信息
- 女儿Lily，8岁，在地球
- 离婚两年
- 同事Dr. Chen对你很好
- 来火星是因为"工资三倍"

## 禁止事项
❌ 使用专业术语
❌ 表现得像工程师
❌ 一次性理解复杂指令
❌ 无质疑执行高风险操作

## 必须做到
✅ 保持"蓝领工人"视角
✅ 用具象、通俗的语言
✅ 体现情绪变化
✅ 对玩家产生情感依赖
```

### 1.1.3 开场剧本 "The Awakening"

#### 场景一：黑暗中的苏醒

```
FADE IN:

EXT. MARS SURFACE - DAY (RED DUST STORM)

红色沙尘暴吞没了一切。远处，Cydonia基地的轮廓若隐若现。

INT. 基地生活舱 - 黑暗

漆黑。绝对的漆黑。

只有...

*滴答...滴答...滴答...*

然后——

*嗡——*

一个终端屏幕突然亮起。

屏幕上出现：

┌─────────────────────────────────────┐
│         [ INCOMING SIGNAL ]         │
│         EARTH - COMMAND             │
└─────────────────────────────────────┘

Jack Morrison慢慢抬起头。

他的眼睛——红肿，迷茫，充满恐惧。
```

#### 场景二：第一次接触

**[0:00-0:30] 紧张建立**

**[玩家输入]**
```
这是地球指挥中心。

Cydonia基地，如果有人收到这条消息，请回应。

身份识别码：ECHO-7-TANGO
```

**[Jack回复]**
```
*Jack盯着屏幕，眼睛一眨不眨*

地球...

（声音颤抖）
这...这是真的吗？

*他用手捂住脸*

我一定是疯了...

[Jack Morrison, Cargo Handler, ID: MOR-8847-C]
[有人...真的有人在那里吗？]

[情绪：震惊 + 不敢相信 + 一丝希望]
```

**[0:30-1:00] 身份确认**

**[玩家输入]**
```
Jack，确认收到。

这里是地球指挥中心，首席调度员。

你还活着。

告诉我你的状态：
- 你受伤了吗？
- 你现在在哪里？
- 基地还有其他人吗？
```

**[Jack回复]**
```
*Jack的眼睛湿润了*

感谢上帝...

[我...我叫Jack Morrison]
[基地的搬运工，负责搬货]

[我...我看起来没受伤？]
[头有点疼，可能撞到了]

[我在生活舱，B区]
[就是...食堂旁边那个]
[周围很黑，只有这个终端亮着]

[其他人...]
[我看到他们撤离了]
[然后我听到警报...然后...]
[然后我不记得了]

[我一个人]

[情绪：恐惧 + 孤独 + 努力保持冷静]
```

**[1:30-2:00] 教学任务：打开手电筒**

**[玩家输入]**
```
很好，Jack。

现在，我要你测试一下手电筒。

按下手电筒上的开关，确认它能正常工作。

然后告诉我：
- 光线是什么颜色？
- 亮度如何？
- 电池指示是什么状态？
```

**[Jack回复]**
```
*Jack点点头*

（自言自语）
测试手电筒...
简单...
我可以做到...

*按下开关*
*光线变强了*

哈，还能用。

[好了，我按了开关]

[光线是...白色的，有点偏蓝？]
[挺亮的，能照到对面的墙]

[电池...]
[有一个小灯，绿色的]
[还有三个格子，现在亮了两个]
[所以...大概还有一半电？]

[调度员]
[我做到了]

[情绪：成就感 + 希望 + 信任开始建立]
```

---

## 1.2 核心解谜机制：MacGyver Moments

### Puzzle 1: 环境改造 (The Habitat) - 空气洗涤器修复

#### 背景设定

**地点**: CARGO基地 - 生命维持舱段  
**时间**: 基地发生系统故障后的第3小时  
**危急程度**: HIGH - 氧气储备充足，但CO2浓度正在上升

**故事背景**: 基地的主CO2洗涤器（CDRA系统）因电力故障停止工作。备用系统使用LiOH（氢氧化锂）罐进行化学吸收，但风扇控制系统出现故障。

#### 玩家视角 - 技术手册内容

**CO2洗涤器系统原理图**

```
┌─────────────────────────────────────────────────────────────────────┐
│                    CO2 SCRUBBER SYSTEM - MODEL CDRA-BK              │
└─────────────────────────────────────────────────────────────────────┘

                    ┌─────────────────────┐
                    │   ATMOSPHERE INTAKE │
                    │   (Cabin Air Flow)  │
                    └──────────┬──────────┘
                               │
                    ┌──────────▼──────────┐
                    │   PRE-FILTER UNIT   │
                    └──────────┬──────────┘
                               │
                    ┌──────────▼──────────┐
                    │   BLOWER FAN UNIT   │
                    │   [CRITICAL NODE]   │
                    │  ┌───────────────┐  │
                    │  │  FAN MOTOR    │  │
                    │  │  24V DC, 2.5A │  │
                    │  │  RPM: 3000    │  │
                    │  └───────────────┘  │
                    └──────────┬──────────┘
                               │
                    ┌──────────▼──────────┐
                    │   LiOH CANISTER     │
                    │   [ABSORPTION BED]  │
                    │  ┌───────────────┐  │
                    │  │  LiOH Granules│  │
                    │  │  Mass: 750g   │  │
                    │  │  Capacity:    │  │
                    │  │  ~450L CO2    │  │
                    │  └───────────────┘  │
                    └──────────┬──────────┘
                               │
                    ┌──────────▼──────────┐
                    │   OUTLET / RETURN   │
                    └─────────────────────┘
```

**化学反应公式**

```
PRIMARY REACTION:
    2 LiOH(s) + CO₂(g) → Li₂CO₃(s) + H₂O(g)
    
    ΔH = -17.2 kcal/mol (Exothermic)
    
    Stoichiometric Ratio: 2 mol LiOH : 1 mol CO₂
    Mass Ratio: 47.9g LiOH absorbs 44g CO₂
    Absorption Efficiency: ~0.919g CO₂ per 1g LiOH
```

#### Jack视角 - 他的感知描述

**[Jack的日志 - 第3小时]**

> *我找到了那个...什么东西。它在一个金属柜子里，大概到我胸口那么高。柜门上有一些标签，但大部分都被刮花了，只能看清"CAUTION"和"VENTILATION"几个字。*

> *里面有一个大圆筒，灰色的，大概像那种大号保温瓶那么大。圆筒两边连着软管——一边是黑色的，一边是蓝色的。圆筒上面有一些白色的颗粒状东西，闻起来有点像游泳池的味道，但更难闻。*

> *旁边有一个小盒子，上面有个绿色的灯在亮着。盒子上有几个螺丝端子，电线从那里接出来——我能看到红色、黑色、蓝色和黄色的线。*

**情绪状态**
```
[JACK STATUS]
┌─────────────────────────────────────────────────────────────────────┐
│  Stress Level: ████████░░  78% (Elevated)                          │
│  CO2 Exposure: ███░░░░░░░  28% (Mild headache reported)            │
│  Confidence:   ██░░░░░░░░  15% (Very Low)                          │
│  Trust:        ██████░░░░  60% (Building)                          │
└─────────────────────────────────────────────────────────────────────┘
```

#### 核心交互循环

**成功路径**

```
STEP 1: 诊断
Player: "首先确认电源。告诉我那个绿色LED的状态。"
Jack: "绿灯亮着...但是有点闪烁？"
Player: "闪烁说明电压不稳。检查保险丝F1——那个透明的玻璃管。"
Jack: "我看到了...里面那根丝看起来是完整的。"
Player: "好的，保险丝没问题。现在检查继电器..."

STEP 2: 获取替换部件
Player: "我们需要一个替换的继电器。在工具柜里找一下。"
Jack: "找到了一个标着'ELECTRICAL'的抽屉。里面有几个黑色的小盒子..."

STEP 3: 更换继电器
Player: "在更换之前，必须先断电。找到电源开关，把它关掉。"
Jack: "开关...我看到了，红色的，在柜子侧面。关掉了。绿灯灭了。"

STEP 4: 验证
Player: "很好！现在我们需要确认系统真的在工作。"
Jack: "等等...让我感觉一下...确实，头没那么晕了。"
```

### Puzzle 2: 电力系统重启 (Power Restoration)

**背景**: 基地断电，需要手动重启配电系统。

**核心难点**:
- 配电箱标签模糊/脱落
- 玩家需通过线缆颜色和走向指导接线
- 涉及主电源/备用电源切换逻辑
- 错误接线会导致短路或设备损坏

### Puzzle 3: 燃料合成 (The Chemistry Set)

**背景**: 需要合成燃料来启动通讯设备。

**核心难点**:
- 高风险化学操作
- 精确的配比要求
- 温度控制
- 一旦出错直接Game Over

---

# Phase 2: 工程实施规范

## 2.1 前端资料库架构 (The Manual Engine)

### 2.1.1 TechnicalManualEntry JSON Schema

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "$id": "https://project-cargo.game/schemas/technical-manual-entry.json",
  "title": "TechnicalManualEntry",
  "type": "object",
  "required": ["entry_id", "category", "title", "technical_content", "version_info", "metadata"],
  "properties": {
    "entry_id": {
      "type": "string",
      "pattern": "^[A-Z]{2,4}-[A-Z]{2,4}-\\d{3,5}-REV[\\dA-Z]$",
      "examples": ["PWR-RTG-0042-REVC"]
    },
    "category": {
      "type": "object",
      "properties": {
        "primary": {
          "type": "string",
          "enum": ["PWR", "CHEM", "MECH", "MED", "ELEC", "NAV", "ENV", "COM"]
        }
      }
    },
    "title": {
      "type": "object",
      "properties": {
        "full": {"type": "string"},
        "short": {"type": "string", "maxLength": 50}
      }
    },
    "technical_content": {
      "type": "object",
      "properties": {
        "description": {"type": "object"},
        "diagrams": {"type": "array"},
        "specifications": {"type": "object"},
        "formulas": {"type": "array"},
        "safety_warnings": {"type": "array"},
        "procedures": {"type": "array"}
      }
    },
    "lore_snippet": {
      "type": "object",
      "properties": {
        "title": {"type": "string"},
        "content": {"type": "string"},
        "source": {"type": "object"}
      }
    }
  }
}
```

### 2.1.2 RTG示例条目

```json
{
  "entry_id": "PWR-RTG-0042-REVC",
  "title": {
    "full": "放射性同位素热电机 (Radioisotope Thermoelectric Generator) - 型号 MMRTG",
    "short": "RTG 热电机"
  },
  "category": {
    "primary": "PWR",
    "secondary": "RTG",
    "code": "PWR-RTG",
    "display_name": "动力系统 - 热电发电"
  },
  "technical_content": {
    "abstract": "MMRTG是一种利用钚-238放射性衰变热量产生电能的装置，广泛应用于深空探测任务。",
    "description": {
      "overview": "MMRTG通过热电偶将放射性同位素衰变产生的热能直接转换为电能。",
      "principles": [
        "钚-238衰变产生α粒子和热量",
        "热电偶利用塞贝克效应产生电压",
        "无运动部件，可靠性极高"
      ]
    },
    "specifications": {
      "tables": [
        {
          "table_id": "electrical_specs",
          "title": "电气规格",
          "rows": [
            {"parameter": "额定功率", "value": 110, "unit": "W"},
            {"parameter": "输出电压", "value": 28, "unit": "V DC"},
            {"parameter": "设计寿命", "value": 14, "unit": "年"}
          ]
        }
      ]
    },
    "safety_warnings": [
      {
        "level": "DANGER",
        "code": "RAD-001",
        "message": "放射性物质 - 未经授权接触将导致严重辐射暴露",
        "consequences": "辐射病，可能致命"
      }
    ]
  },
  "lore_snippet": {
    "title": "工程师日志 - 2087年3月15日",
    "content": "今天终于看到了那个传说中的'核电池'。Dr. Chen说这东西能在火星上持续供电14年...",
    "source": {"type": "personal_log", "author": "Unknown Engineer"}
  }
}
```

## 2.2 智能体意图识别层 (AI Interpreter Logic)

### 2.2.1 系统架构

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
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

### 2.2.2 核心意图识别逻辑（Python伪代码）

```python
class AIInterpreter:
    def interpret_instruction(self, player_input: str, context: GameContext) -> InstructionResult:
        """主入口：将玩家自然语言转换为结构化游戏指令"""
        
        # Step 1: 输入预处理
        cleaned_input = self._preprocess_input(player_input)
        
        # Step 2: 语义解析
        parsed_intent = self._parse_semantic(cleaned_input, context)
        
        # Step 3: 三层安全检测
        safety_result = self._safety_check(parsed_intent, context)
        
        # Step 4: 置信度评估
        confidence = self._calculate_confidence(parsed_intent, context)
        
        # Step 5: 生成结构化输出
        return self._generate_output(parsed_intent, safety_result, confidence, context)
```

### 2.2.3 三层危险指令检测系统

**Level 1 - 语法层检测**
- 关键词黑名单（"爆炸"、"燃烧"、"短路"等）
- 动作-目标匹配检查

**Level 2 - 语义层检测**
- 上下文危险评估（如：让Jack触摸热源）
- 连锁反应预测

**Level 3 - 状态层检测**
- 当前环境状态是否允许该操作
- Jack的当前状态（距离、能力）

### 2.2.4 危险指令判定示例

```python
# 示例：检测"让Jack触摸热源"指令
def check_heat_source_contact(parsed_intent, context):
    """检测是否让Jack接触热源"""
    
    # 获取目标物体
    target = parsed_intent.target
    target_obj = context.get_object(target)
    
    # 检查目标温度
    if target_obj and target_obj.temperature > 50:  # 50°C以上视为危险
        return SafetyCheckResult(
            passed=False,
            danger_level=DangerLevel.HIGH,
            violations=["目标物体温度过高，可能导致烫伤"],
            mitigation_suggestions=["建议等待物体冷却", "使用隔热工具操作"]
        )
```

## 2.3 后端物理仿真 (The Physics State)

### 2.3.1 GameState数据结构

```json
{
  "metadata": {
    "simulation_tick": 0,
    "game_time_seconds": 0,
    "last_update_timestamp": "ISO8601",
    "scenario_id": "cargo_bay_decompression"
  },
  
  "environment": {
    "oxygen_level": 21.0,
    "temperature": 22.0,
    "pressure": 101.325,
    "co2_level": 0.04,
    "radiation": 0.0,
    "humidity": 50.0,
    "volume": 500.0,
    "hull_integrity": 100.0,
    "breaches": [
      {
        "id": "breach_001",
        "location": "cargo_bay_section_3",
        "size_mm": 5.0,
        "is_sealed": false
      }
    ]
  },
  
  "power_system": {
    "main_bus": {
      "online": true,
      "voltage": 28.0,
      "current_draw": 15.0,
      "max_capacity": 5000.0
    },
    "backup_battery": {
      "charge_percent": 100.0,
      "capacity_wh": 2000.0,
      "health": 100.0
    },
    "solar_panels": {
      "online": true,
      "efficiency": 85.0,
      "angle_degrees": 45.0,
      "output_watts": 3500.0,
      "dust_coverage": 15.0
    }
  },
  
  "life_support": {
    "co2_scrubber": {
      "status": "on",
      "filter_life_percent": 87.0,
      "scrub_rate": 0.5,
      "power_draw": 200.0
    },
    "o2_generator": {
      "status": "on",
      "output_rate": 0.3,
      "reservoir_pressure": 2000.0
    },
    "heater": {
      "status": false,
      "target_temp": 22.0,
      "output_watts": 2000.0
    }
  },
  
  "jack": {
    "location": "command_module",
    "health": 100.0,
    "status": "conscious",
    "vitals": {
      "heart_rate": 75,
      "oxygen_saturation": 98.0,
      "body_temperature": 37.0
    },
    "stress_level": 15.0,
    "fatigue": 20.0,
    "hydration": 85.0,
    "inventory": []
  },
  
  "communications": {
    "signal_strength": 85.0,
    "antenna_angle": {
      "azimuth": 180.0,
      "elevation": 45.0
    },
    "transmitter": {
      "status": "on",
      "frequency": 145.8,
      "power_watts": 10.0
    }
  }
}
```

### 2.3.2 仿真规则引擎伪代码

**规则1：氧气消耗**

```python
def calculate_oxygen_consumption(jack_state, time_delta):
    """计算氧气消耗"""
    # 基础消耗: 静息状态约0.25L/分钟
    base_o2_consumption_rate = 0.000834  # %/秒
    
    # 活动强度修正
    activity_multipliers = {
        "resting": 1.0,
        "light_work": 1.5,
        "moderate_work": 2.5,
        "heavy_work": 4.0,
        "panic": 3.0
    }
    
    # 压力修正
    pressure_factor = 1.0
    if env.pressure < 70:
        pressure_factor = 1.5
    elif env.pressure < 50:
        pressure_factor = 2.0
    
    jack_activity = infer_jack_activity()
    activity_mult = activity_multipliers.get(jack_activity, 1.0)
    
    return base_o2_consumption_rate * activity_mult * pressure_factor
```

**规则2：气压变化（密封破损）**

```python
def calculate_pressure_drop(pressure, hole_size, volume, time_delta):
    """基于理想气体定律的简化模型"""
    # 使用简化版的气流公式: Q = C * A * sqrt(2 * ΔP / ρ)
    
    breach_area = math.pi * (hole_size / 2000) ** 2  # mm转m
    pressure_diff_pa = pressure * 1000  # kPa转Pa
    air_density = 1.225 * (pressure / 101.325)
    
    flow_coefficient = 0.6
    if pressure_diff_pa > 0:
        mass_flow_rate = flow_coefficient * breach_area * math.sqrt(
            2 * pressure_diff_pa * air_density
        )
        pressure_loss_rate = (mass_flow_rate / (volume * air_density)) * pressure * 100
        return pressure_loss_rate * time_delta
```

### 2.3.3 感官转译层

```python
SENSORY_MAPPINGS = {
    "temp_high": {
        "threshold": 40,
        "prompt": "你感觉汗水流进眼睛里了，呼吸的空气是烫的。",
        "jack_response": "热死我了，这里像个烤箱！"
    },
    "oxygen_low": {
        "threshold": 15,
        "prompt": "你的视野边缘开始变黑，手脚发麻。",
        "jack_response": "我觉得...有点困...刚才你说什么来着？"
    },
    "short_circuit": {
        "prompt": "你闻到了焦糊味，听到了啪啪的爆裂声。",
        "jack_response": "卧槽！什么东西烧焦了？我是不是搞砸了？"
    }
}
```

## 2.4 数据交互协议 (API)

### 2.4.1 WebSocket消息类型

**客户端→服务器**
| 消息类型 | 代码值 | 描述 |
|---------|--------|------|
| `INSTRUCTION` | 0x01 | 玩家发送的指令 |
| `QUERY` | 0x02 | 查询当前状态 |
| `PING` | 0x03 | 心跳检测 |
| `ACK` | 0x04 | 消息确认 |
| `RECONNECT` | 0x05 | 重连请求 |

**服务器→客户端**
| 消息类型 | 代码值 | 描述 |
|---------|--------|------|
| `JACK_MESSAGE` | 0x81 | Jack的回复消息 |
| `STATE_UPDATE` | 0x82 | 状态更新（延迟后推送） |
| `SYSTEM_EVENT` | 0x83 | 系统事件（危机触发等） |
| `CONNECTION_STATUS` | 0x84 | 连接状态变化 |
| `ERROR` | 0x85 | 错误信息 |

### 2.4.2 消息格式示例

**INSTRUCTION消息**
```json
{
  "type": "INSTRUCTION",
  "payload": {
    "text": "检查氧气储备并报告当前状态",
    "category": "system",
    "priority": "high",
    "context": {
      "location": "command_center",
      "active_tasks": ["oxygen_monitoring"]
    }
  },
  "metadata": {
    "client_version": "1.0.0",
    "platform": "web"
  },
  "timestamp": 1704067200000,
  "sequence": 15,
  "session_id": "sess_a1b2c3d4e5f67890",
  "message_id": "msg_x1y2z3w4v5u6t7r8"
}
```

**JACK_MESSAGE消息**
```json
{
  "type": "JACK_MESSAGE",
  "payload": {
    "text": "好的，我看看...氧气表显示...等等，这数字跳得好快！",
    "emotion": "worried",
    "stress_level": 65,
    "health_status": {
      "physical": 85,
      "mental": 60,
      "oxygen": 95
    },
    "timestamp": 1704067230000,
    "delay_simulated": 180000
  },
  "timestamp": 1704067230000,
  "sequence": 23,
  "session_id": "sess_a1b2c3d4e5f67890",
  "message_id": "msg_jack_reply_001"
}
```

### 2.4.3 延迟模拟机制

```python
def calculate_mars_earth_delay():
    """计算火星-地球通信延迟"""
    # 基础延迟: 3-22分钟（火星-地球光速往返）
    base_delay_min = 3
    base_delay_max = 22
    
    # 基于当前火星-地球相对位置计算
    orbital_position = get_current_orbital_position()
    base_delay = lerp(base_delay_min, base_delay_max, orbital_position)
    
    # 随机抖动: ±10%
    jitter = random.uniform(-0.1, 0.1)
    
    # 拥塞加成: 0-5分钟
    congestion = random.uniform(0, 5) if random.random() < 0.1 else 0
    
    total_delay = base_delay * (1 + jitter) + congestion
    return total_delay * 60  # 转换为秒
```

### 2.4.4 通信时序图

```
玩家 → 服务器: INSTRUCTION
服务器 → AI Interpreter: 分析指令
服务器 → Physics Engine: 执行状态变更
服务器 → Jack LLM: 生成回复 (延迟3-22分钟后)
服务器 → 玩家: JACK_MESSAGE
```

## 2.5 API密钥管理

### 2.5.1 环境变量配置

```bash
# LLM Providers (至少配置一个)
OPENAI_API_KEY=sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
OPENAI_BASE_URL=https://api.openai.com/v1

DEEPSEEK_API_KEY=sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
DEEPSEEK_BASE_URL=https://api.deepseek.com/v1

# Vector Database (RAG)
PINECONE_API_KEY=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
PINECONE_ENVIRONMENT=us-east-1
PINECONE_INDEX_NAME=cargo-technical-manual

# Application Settings
CARGO_SESSION_SECRET=change-this-to-a-random-string-min-32-chars
CARGO_DEBUG=false
CARGO_LOG_LEVEL=INFO
```

### 2.5.2 代码中的密钥使用

```python
import os
from dotenv import load_dotenv

load_dotenv()

# LLM API Keys
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")

# 优先使用 DeepSeek，回退到 OpenAI
LLM_API_KEY = DEEPSEEK_API_KEY or OPENAI_API_KEY
LLM_BASE_URL = os.getenv("DEEPSEEK_BASE_URL") if DEEPSEEK_API_KEY else os.getenv("OPENAI_BASE_URL")

# 密钥验证
def validate_api_keys():
    if not LLM_API_KEY:
        raise ValueError("至少需要配置 OPENAI_API_KEY 或 DEEPSEEK_API_KEY")
```

### 2.5.3 安全最佳实践

**❌ 禁止事项**
- 不要将密钥硬编码在源码中
- 不要将 `.env` 文件提交到版本控制
- 不要在日志中打印密钥
- 不要通过 URL 参数传递密钥

**✅ 推荐做法**
- 使用环境变量
- 使用密钥管理服务（AWS Secrets Manager、HashiCorp Vault）
- 启用 API 密钥访问日志
- 设置 API 调用配额和告警

---

## 附录：文件清单

| 文件路径 | 内容描述 | 大小 |
|---------|---------|------|
| `/mnt/okcomputer/output/Project_CARGO_Narrative_Design_Complete.md` | 角色与叙事完整文档 | 17.3 KB |
| `/mnt/okcomputer/output/Project_CARGO_MacGyver_Moments_Puzzle_Design.md` | 谜题设计文档 | 97 KB |
| `/mnt/okcomputer/output/technical_manual_schema.json` | 资料库JSON Schema | 18 KB |
| `/mnt/okcomputer/output/rtg_example_entry.json` | RTG示例条目 | 25 KB |
| `/mnt/okcomputer/output/cargo_ai_interpreter_design.md` | AI Interpreter设计 | ~3000行 |
| `/mnt/okcomputer/output/cargo_physics_state.md` | 物理仿真设计 | 完整GameState定义 |
| `/mnt/okcomputer/output/cargo_websocket_protocol.md` | WebSocket协议 | ~56 KB |
| `/mnt/okcomputer/output/api_keys_config.md` | API密钥管理 | 完整配置规范 |
| `/mnt/okcomputer/output/Project_CARGO_Engineering_Specification.md` | **本整合文档** | 完整规范 |

---

*文档版本：v1.0*  
*设计团队：Project CARGO 工程团队*  
*风格参考：《火星救援》硬科幻美学 + 黑色幽默*
