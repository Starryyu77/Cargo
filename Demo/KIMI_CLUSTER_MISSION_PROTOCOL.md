# KIMI_CLUSTER_MISSION_PROTOCOL

## 🎯 PRIME OBJECTIVE
**Role:** "Project: CARGO" 的首席游戏设计师 (Lead Designer) 及技术架构师。
**Mission:** 将概念白皮书 `/Users/starryyu/Documents/Cargo/AI 驱动的火星生存游戏白皮书.pdf` 转化为**全套工程实施规范**。
**Core Reference:** 深度参考电影《火星救援》(The Martian) 的叙事节奏与硬科幻风格，但核心机制需适配“非对称协作”。

## 🛠️ CAPABILITY LOCKS
- `[🎥 Cinematic Tone]`: 借鉴《火星救援》的孤寂感与黑色幽默。Jack 面对的是真实的物理危机（气压、温度、化学反应）。
- `[🧩 Hard Sci-Fi Logic]`: 情节设计必须符合基础科学常识（如：水的电解、电路负载），拒绝“魔法”设定。
- `[🏗️ Architecture]`: 定义前后端数据结构、State Machine、API。

## 📂 CONTEXT & CONSTRAINTS
**Context:**
- **Scenario:** 类似《火星救援》，一人滞留火星，唯一的联系是地球（玩家）。
- **Key Difference (关键差异):** 电影里的主角是全能科学家，但本游戏的 Jack 只是个**不懂技术的蓝领搬运工**。
- **Core Loop:** 玩家拥有《火星救援》级别的硬核知识库，但只能通过 Jack 这双“笨手”去操作，双方只能通过文字交互。

**Constraints:**
- **先设计，后编码:** 必须先完善剧本和游戏机制逻辑，再写代码。
- **资料库即玩法:** 左侧手册必须像 NASA 的原始文档一样枯燥、专业，图文并茂，而且需要有一些游戏交互中不需要的内容与 Jack 的生活化语言形成反差，后端的物理仿真需要参考前面的游戏设计

## 📝 OUTPUT SPECIFICATION

### PHASE 1: 游戏核心设计 (The Design Bible)

#### 1.1 角色与叙事 (Persona & Script)
**Jack Persona (角色设定):**
- **基本信息**: 32岁，重型机械操作员（前卡车司机）。身体强壮，但对化学、物理、编程一窍不通。
- **性格特征**:
    - **话痨 (Chatterbox)**: 极度害怕安静，通过不停说话来缓解焦虑。
    - **乐观 (Optimistic)**: 即使在绝境中也能开出糟糕的玩笑。
    - **反智/吐槽 (Anti-Intellectual/Sarcastic)**: 讨厌复杂的说明书，喜欢给昂贵的设备起愚蠢的绰号。
- **System Prompt 核心指令**:
    - 你不懂任何科学术语。如果听到“电解”或“热力学”，你会感到困惑或生气。
    - 你现在的状态是：又饿、又冷、极其恐慌，但试图用幽默掩饰。
    - 除非玩家给出极度直白的“傻瓜式”指令，否则你无法完成复杂操作。
    - 经常抱怨公司的设备是“垃圾”或“过度设计”。

**Opening Script (开场 3 分钟剧本):**
*(屏幕漆黑，只有呼吸声和类似风沙撞击金属的沉闷声响)*
*(屏幕闪烁，连接建立)*
**Jack:** "喂？喂？！这里是... 咳咳... 这里是货运专员 Jack。有没有人？随便谁都行，哪怕是税务局的混蛋我也认了！"
**System:** [SIGNAL ESTABLISHED: EARTH-MARS RELAY. DELAY: 0ms (SIMULATED)]
**Jack:** "哦谢天谢地，那个红灯终于不闪了。听着，老兄，情况有点... 稍微有点失控。那个叫‘赫尔墨斯’的大飞船？它刚才像个被踢了屁股的易拉罐一样飞走了。而我... 我好像被扔在这个红色的烂泥坑里了。"
**Jack:** "最要命的是，栖息舱的警报一直在叫唤什么‘气压临界’。我看着这堆仪表盘就像看天书一样。求你了，告诉我这只是个整人节目，摄像机藏在哪？"
**Jack:** "嘿！还在吗？别告诉我你也掉线了！我现在该按哪个按钮？这个红色的？还是旁边那个画着骷髅头的？"

#### 1.2 核心解谜机制：MacGyver Moments (土法工程)
**Puzzle 1: 环境改造 - 拯救空气 (The Habitat CO2 Scrubber)**
*情境: 栖息舱的主空气循环系统故障，二氧化碳浓度正在飙升。Jack 需要用备用零件手动拼凑一个过滤装置。*

- **玩家视角 (手册内容):**
    - **图纸**: "MK-4 空气洗涤器原理图" - 显示气流方向、LiOH (氢氧化锂) 滤芯的安装位置、风扇接线图。
    - **警告**: "LiOH 粉末具有强腐蚀性，禁止直接接触皮肤。需配合活性炭滤网使用。"
    - **公式**: `2LiOH + CO2 -> Li2CO3 + H2O` (放热反应)

- **Jack 视角 (实际描述):**
    - "好吧，我找到了备品箱。里面有一堆看起来像汽车空调滤芯的方板子，但是它们不匹配这里的槽口！该死的设计师！"
    - "还有一桶白色的粉末，上面写着危险符号，闻起来像消毒水。旁边有些塑料管子，还有几卷银色的胶带。"
    - "原本那个机器还在冒烟，我不打算碰它。"

- **Interaction (交互逻辑):**
    1.  玩家必须意识到标准滤芯无法塞入现有槽口。
    2.  玩家查阅手册，发现可以用塑料管和胶带将滤芯“外挂”到风扇进气口。
    3.  玩家指示 Jack: "拿胶带，把方板子粘在管子的一头。" -> Jack: "好主意，用胶带解决一切！经典的工程学。"
    4.  玩家指示 Jack: "把粉末倒在板子上" -> Jack (错误反馈): "老兄，这上面画着骷髅头呢！而且这粉末飞得到处都是，我眼睛好疼！" (Game Over 风险: Jack 受伤)
    5.  正确指示: "找个袜子或者破布，把粉末包起来，然后塞进管子里。"

### PHASE 2: 工程实施规范 (The Engineering Spec)

#### 2.1 前端资料库架构 (The Manual Engine)
左侧资料库用于展示硬核技术文档。数据结构需支持富文本、图表和隐藏的“背景碎片”。

**JSON Schema:**
```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "ManualEntry",
  "type": "object",
  "properties": {
    "id": { "type": "string", "description": "唯一标识符，如 'RTG-001'" },
    "title": { "type": "string", "description": "显示标题" },
    "category": { "type": "string", "enum": ["LifeSupport", "Power", "Rover", "Comms"] },
    "access_level": { "type": "integer", "description": "解锁需要的权限等级" },
    "technical_content": {
      "type": "object",
      "properties": {
        "schematic_url": { "type": "string", "format": "uri", "description": "蓝图图片路径" },
        "specs": { "type": "string", "description": "枯燥的技术参数，Markdown格式" },
        "warnings": { "type": "array", "items": { "type": "string" }, "description": "红字警告内容" },
        "formulas": { "type": "array", "items": { "type": "string" }, "description": "相关的物理/化学公式" }
      }
    },
    "lore_snippet": {
      "type": "string",
      "description": "隐藏的背景故事，如'工程师在边角写的吐槽'，用于增加世界观深度"
    }
  }
}
```

**Example Entry (RTG - 放射性同位素热电机):**
```json
{
  "id": "RTG-MK1",
  "title": "多任务放射性同位素热电发生器 (MMRTG)",
  "category": "Power",
  "access_level": 1,
  "technical_content": {
    "schematic_url": "/assets/schematics/rtg_core.png",
    "specs": "**热功率**: 2000 Wt\n**电功率**: 110 We (初始)\n**燃料**: 钚-238 (PuO2)\n**半衰期**: 87.7 年\n**外壳温度**: >200°C",
    "warnings": [
      "极度高温！禁止触摸散热鳍片。",
      "辐射危害：一旦外壳破损，立即撤离并封锁区域。"
    ],
    "formulas": ["P(t) = P0 * (1/2)^(t/87.7)"]
  },
  "lore_snippet": "批注：到底是哪个天才决定把它埋在离居住舱这么远的地方？如果冬天暖气坏了，我发誓我会把它挖出来抱在怀里睡觉。 —— 任务指挥官 Lewis"
}
```

#### 2.2 智能体意图识别层 (AI Interpreter Logic)
位于前端与LLM之间的中间件，用于拦截和分析玩家指令的安全性与有效性。

**Middleware Design (Python Logic):**
```python
class CommandInterpreter:
    def __init__(self, llm_client):
        self.llm = llm_client
        self.safety_rules = [
            "禁止让Jack直接接触高温物体",
            "禁止在未穿戴EVA服时打开气闸",
            "禁止混合不明化学品"
        ]

    def analyze_intent(self, user_input: str, current_context: dict) -> dict:
        """
        分析用户输入的意图和安全性。
        返回: { "action": str, "is_safe": bool, "danger_reason": str, "confidence": float }
        """
        prompt = f"""
        Current Context: {current_context}
        User Input: "{user_input}"
        Safety Rules: {self.safety_rules}
        
        Analyze the input. Is it asking Jack to do something physically dangerous based on the rules and context?
        If yes, set is_safe to False and explain why.
        Extract the core action verb and object.
        """
        
        response = self.llm.generate(prompt) # 实际上调用 Gemini 3 Pro
        return self._parse_response(response)

    def execute_logic(self, user_input, game_state):
        analysis = self.analyze_intent(user_input, game_state)
        
        if not analysis['is_safe']:
            return {
                "type": "DANGER_INTERCEPT",
                "message": f"Jack 犹豫了：'等等，老兄，你是想害死我吗？{analysis['danger_reason']}'"
            }
        
        # Proceed to normal game loop
        return {"type": "PROCEED", "action": analysis['action']}
```

#### 2.3 后端物理仿真 (The Physics State)
后端维护一个真实的物理状态机，独立于 LLM 的叙述。

**State Machine Definition:**
```python
from dataclasses import dataclass

@dataclass
class EnvironmentState:
    o2_level: float = 21.0      # Percentage
    co2_level: float = 0.04     # Percentage
    temperature: float = 20.0   # Celsius
    pressure: float = 101.3     # kPa
    radiation: float = 0.0      # mSv/h

@dataclass
class JackState:
    calories: int = 2000
    hydration: float = 100.0    # Percentage
    stress: float = 0.0         # 0-100
    injury_level: int = 0       # 0=None, 1=Minor, 2=Major

class PhysicsEngine:
    def update(self, state: EnvironmentState, delta_time_minutes: int, events: list):
        # 模拟 CO2 积累 (假设洗涤器坏了)
        if "SCRUBBER_OFFLINE" in events:
            # 每个人每分钟产生约 0.02g CO2，此处简化为浓度上升
            # 假设舱体体积 100m3
            rise_rate = 0.001 * delta_time_minutes # % per minute
            state.co2_level += rise_rate
            
        # 模拟气压下降 (如果密封条破损)
        if "SEAL_BREACH" in events:
            # 伯努利方程简化版
            leak_rate = 0.5 * (state.pressure - 0.6) # 0.6 is Mars outside pressure
            state.pressure -= leak_rate * delta_time_minutes * 0.01

        # 临界值检查
        if state.co2_level > 2.0:
            return "GAME_OVER_SUFFOCATION"
            
        return "OK"
```

#### 2.4 数据交互协议 (API)
前端与后端通过 WebSocket 进行实时通信。

**WebSocket Message Format:**

**Client -> Server (User Command):**
```json
{
  "type": "COMMAND",
  "payload": {
    "text": "用胶带把管子封死",
    "timestamp": 1678888888
  }
}
```

**Server -> Client (Game Update):**
```json
{
  "type": "UPDATE",
  "payload": {
    "jack_response": "这就动手。希望这胶带够粘... 好了，贴上了。看起来丑爆了，但似乎不漏气了。",
    "system_alert": null,
    "physics_update": {
      "co2_level": 0.05,
      "pressure": 101.2
    },
    "sound_effect": "tape_rip.mp3"
  }
}
```

**Server -> Client (Danger Alert):**
```json
{
  "type": "INTERCEPT",
  "payload": {
    "jack_response": "你是认真的吗？那玩意儿现在有一百多度！我手会废掉的！",
    "reason": "HIGH_TEMP_WARNING"
  }
}
```
