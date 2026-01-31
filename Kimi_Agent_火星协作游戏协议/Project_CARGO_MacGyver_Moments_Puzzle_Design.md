# Project: CARGO - MacGyver Moments 谜题设计文档

## 设计概述

本设计为硬核科幻解谜游戏"Project: CARGO"的三个核心MacGyver式工程改造谜题。每个谜题遵循以下原则：
- 真实物理/化学原理（可查证）
- 玩家与NPC之间存在"认知鸿沟"
- 高风险决策与容错机制
- 失败状态有意义（状态恶化需要补救）

---

# Puzzle 1: 环境改造 (The Habitat) - 空气洗涤器修复

## 背景设定

**地点**：CARGO基地 - 生命维持舱段
**时间**：基地发生系统故障后的第3小时
**危急程度**：HIGH - 氧气储备充足，但CO2浓度正在上升

**故事背景**：
基地的主CO2洗涤器（CDRA系统）因电力故障停止工作。备用系统使用LiOH（氢氧化锂）罐进行化学吸收，但风扇控制系统出现故障，气流无法正常通过吸收罐。Jack必须在CO2浓度达到危险水平（>20mmHg）前修复系统。

---

## 1. 玩家视角 - 技术手册内容

### 1.1 空气洗涤器系统原理图 (CO2 Scrubber System Schematic)

```
┌─────────────────────────────────────────────────────────────────────┐
│                    CO2 SCRUBBER SYSTEM - MODEL CDRA-BK              │
│                         [TECHNICAL MANUAL v2.4]                     │
└─────────────────────────────────────────────────────────────────────┘

                    ┌─────────────────────┐
                    │   ATMOSPHERE INTAKE │
                    │   (Cabin Air Flow)  │
                    └──────────┬──────────┘
                               │
                    ┌──────────▼──────────┐
                    │   PRE-FILTER UNIT   │
                    │   (Particulate)     │
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
                    │   (Clean Air)       │
                    └─────────────────────┘

CONTROL SYSTEM:
┌─────────────────────────────────────────────────────────────────────┐
│  POWER SUPPLY UNIT (PSU-24V)                                        │
│  ├── Input: 110V AC / 220V AC                                       │
│  ├── Output: 24V DC, 5A max                                         │
│  └── Status LED: [GREEN=Normal] [RED=Fault] [OFF=No Power]          │
│                                                                     │
│  CONTROL BOARD (CB-01)                                              │
│  ├── Microcontroller: ATmega328P                                    │
│  ├── Relay Module: 2x SPST (Fan Control)                            │
│  ├── Sensors: CO2 (0-5000ppm), Pressure, Temperature                │
│  └── Alarm Threshold: CO2 > 5000ppm (0.5%)                          │
│                                                                     │
│  WIRING HARNESS (Color Code)                                        │
│  ├── RED    : +24V (Main Power)                                     │
│  ├── BLACK  : GND (Common Ground)                                   │
│  ├── BLUE   : Fan Control Signal (Relay Coil)                       │
│  ├── YELLOW : CO2 Sensor Data                                       │
│  └── GREEN  : Status LED                                            │
└─────────────────────────────────────────────────────────────────────┘
```

### 1.2 化学反应公式

```
┌─────────────────────────────────────────────────────────────────────┐
│              CO2 ABSORPTION CHEMISTRY - LiOH REACTION               │
│                    [NASA Technical Reference]                       │
└─────────────────────────────────────────────────────────────────────┘

PRIMARY REACTION (Net Equation):

    2 LiOH(s) + CO₂(g) → Li₂CO₃(s) + H₂O(g)
    
    ΔH = -17.2 kcal/mol (Exothermic)
    
    Stoichiometric Ratio: 2 mol LiOH : 1 mol CO₂
    
    Mass Ratio: 47.9g LiOH absorbs 44g CO₂
    
    Absorption Efficiency: ~0.919g CO₂ per 1g LiOH

REACTION MECHANISM (Two-Step Process):

Step 1: Hydration (Exothermic)
    2 LiOH(s) + 2 H₂O(g) → 2 LiOH·H₂O(s)
    ΔH = -17.6 kcal/mol

Step 2: Carbonation (Endothermic)
    2 LiOH·H₂O(s) + CO₂(g) → Li₂CO₃(s) + 3 H₂O(g)
    ΔH = +18.1 kcal/mol

NOTE: Water vapor is REQUIRED for the reaction to proceed.
      The system operates optimally at 40-60% relative humidity.

THERMODYNAMIC DATA:
┌────────────────┬────────────────────────────────────────────────────┐
│ Parameter      │ Value                                              │
├────────────────┼────────────────────────────────────────────────────┤
│ Molar Mass LiOH│ 23.95 g/mol                                        │
│ Molar Mass CO₂ │ 44.01 g/mol                                        │
│ Reaction Heat  │ 21.4 kcal/mol CO₂ absorbed                         │
│ Canister Temp  │ 35-45°C during operation (normal)                  │
│ Max Capacity   │ 721g CO₂ per 785g LiOH canister                    │
└────────────────┴────────────────────────────────────────────────────┘
```

### 1.3 电路图与接线图

```
┌─────────────────────────────────────────────────────────────────────┐
│              ELECTRICAL SCHEMATIC - CDRA-BK CONTROL                 │
│                    [Wiring Diagram Rev.C]                           │
└─────────────────────────────────────────────────────────────────────┘

POWER DISTRIBUTION:

    110V/220V AC Input
           │
           ▼
    ┌──────────────┐
    │   FUSE F1    │  5A Slow-Blow
    │  [CRITICAL]  │  (Replace with EXACT rating)
    └──────┬───────┘
           │
           ▼
    ┌──────────────┐
    │   PSU-24V    │  Switching Power Supply
    │   [PSU]      │  Output: 24V DC, 5A
    │  ┌────────┐  │
    │  │+24V Out│──┼──┬──┬──┬──┬──┐
    │  │        │  │  │  │  │  │  │
    │  │GND Out │──┼──┴──┴──┴──┴──┘
    │  └────────┘  │
    └──────────────┘

CONTROL CIRCUIT (Low Voltage):

    +24V ───────────────────────────────────────────────┐
                                                        │
    ┌──────────────┐    ┌──────────────┐               │
    │   RELAY K1   │    │   FAN MOTOR  │               │
    │  [FAN CTRL]  │    │   [M1]       │               │
    │  ┌────────┐  │    │  ┌────────┐  │               │
    │  │ Coil   │  │    │  │   +    │──┼─── +24V       │
    │  │  Blue  │──┼────┘  │        │  │               │
    │  │ Wire   │  │       │   M    │  │               │
    │  └────────┘  │       │        │  │               │
    │       │      │       │   -    │──┼───┐           │
    │       NC     │       └────────┘  │   │           │
    │       │      │                   │   │           │
    │       COM────┼───────────────────┘   │           │
    │              │                       │           │
    │       NO     │                       │           │
    │       │      │                       │           │
    └───────┼──────┘                       │           │
            │                              │           │
    GND ────┴──────────────────────────────┴───────────┘

SENSOR INTERFACE:

    CO2 SENSOR (NDIR Type)
    ┌─────────────────────────┐
    │  +V  │ YELLOW │  +24V  │
    │  GND │ BLACK  │  GND   │
    │  OUT │ YELLOW │  MCU   │
    │  CAL │ GREEN  │  N/C   │
    └─────────────────────────┘
    
    Output: 4-20mA (0-5000ppm range)
    4mA  = 0 ppm
    20mA = 5000 ppm
    
    Current Reading Formula:
    CO2(ppm) = (I_mA - 4) × (5000 / 16)

STATUS LED INDICATORS:

    LED1 (GREEN) - Power OK
    └── Connected to +24V via 1kΩ resistor
    
    LED2 (RED) - System Fault
    └── Connected to MCU Pin 13 (Active LOW)
    
    LED3 (YELLOW) - Fan Running
    └── Connected in parallel with Fan Motor
```

### 1.4 故障诊断流程图

```
┌─────────────────────────────────────────────────────────────────────┐
│              TROUBLESHOOTING PROCEDURE - CDRA-BK                    │
│                    [Emergency Protocol 7.3]                         │
└─────────────────────────────────────────────────────────────────────┘

START: System Not Operating
            │
            ▼
    ┌───────────────┐
    │ Check PSU LED │
    │ Status        │
    └───────┬───────┘
            │
    ┌───────┴───────┐
    │               │
    ▼               ▼
┌───────┐      ┌───────┐
│ OFF   │      │ RED   │
│       │      │       │
└───┬───┘      └───┬───┘
    │              │
    ▼              ▼
┌──────────┐  ┌──────────┐
│ Check    │  │ Check    │
│ AC Input │  │ Fuse F1  │
│ Voltage  │  │ (5A)     │
└────┬─────┘  └────┬─────┘
     │             │
     ▼             ▼
┌──────────┐  ┌──────────┐
│ No AC?   │  │ Blown?   │
│→ Check  │  │→ Replace │
│ Breaker  │  │ with 5A  │
└────┬─────┘  └────┬─────┘
     │             │
     ▼             ▼
    NORMAL      NORMAL
     │             │
     └──────┬──────┘
            │
            ▼
    ┌───────────────┐
    │ Check Fan     │
    │ Operation     │
    └───────┬───────┘
            │
    ┌───────┴───────┐
    │               │
    ▼               ▼
┌───────┐      ┌───────┐
│ NO    │      │ YES   │
│       │      │       │
└───┬───┘      └───┬───┘
    │              │
    ▼              ▼
┌──────────┐  ┌──────────┐
│ Check    │  │ Check    │
│ Relay K1 │  │ CO2 Level│
│ (Click?) │  │ (Sensor) │
└────┬─────┘  └────┬─────┘
     │             │
     ▼             ▼
┌──────────┐  ┌──────────┐
│ Click    │  │ >5000ppm │
│ heard?   │  │ after    │
│          │  │ 10 min?  │
└────┬─────┘  └────┬─────┘
     │             │
  YES│          YES│
     ▼             ▼
┌──────────┐  ┌──────────┐
│ Check    │  │ Replace  │
│ Fan      │  │ LiOH     │
│ Wiring   │  │ Canister │
└────┬─────┘  └────┬─────┘
     │             │
  NO │          NO │
     ▼             ▼
┌──────────┐  ┌──────────┐
│ Replace  │  │ System   │
│ Relay K1 │  │ NORMAL   │
└──────────┘  └──────────┘

CRITICAL SAFETY NOTES:
□ LiOH is CAUSTIC - Use gloves and eye protection
□ Canister may be HOT (35-45°C) during operation
□ Do not operate without airflow - thermal runaway risk
□ Dispose of used canisters per hazardous material protocol
```

### 1.5 关键参数速查表

```
┌─────────────────────────────────────────────────────────────────────┐
│              QUICK REFERENCE - CDRA-BK PARAMETERS                   │
└─────────────────────────────────────────────────────────────────────┘

ELECTRICAL:
┌────────────────────┬────────────────────────────────────────────────┐
│ Parameter          │ Specification                                  │
├────────────────────┼────────────────────────────────────────────────┤
│ Input Voltage      │ 110-240V AC, 50/60Hz                          │
│ Output Voltage     │ 24V DC ±5%                                    │
│ Max Current        │ 5A (PSU) / 2.5A (Fan)                         │
│ Fuse Rating        │ 5A Slow-Blow (F1)                             │
│ Relay Coil         │ 24V DC, 100mA                                 │
│ Fan Motor          │ 24V DC Brushless, 60W                         │
└────────────────────┴────────────────────────────────────────────────┘

MECHANICAL:
┌────────────────────┬────────────────────────────────────────────────┐
│ Parameter          │ Specification                                  │
├────────────────────┼────────────────────────────────────────────────┤
│ Airflow Rate       │ 150-200 CFM                                    │
│ Canister Mass      │ 750g (fresh) / ~900g (spent)                  │
│ Operating Pressure │ 0.8-1.2 atm (differential)                    │
│ Filter Rating      │ HEPA H13 (99.97% @ 0.3μm)                     │
└────────────────────┴────────────────────────────────────────────────┘

OPERATIONAL LIMITS:
┌────────────────────┬────────────────────────────────────────────────┐
│ Parameter          │ Limit                                          │
├────────────────────┼────────────────────────────────────────────────┤
│ CO2 Alarm Level    │ 5000 ppm (0.5%)                               │
│ CO2 Critical       │ 20000 ppm (2%) - IMMEDIATE EVACUATION         │
│ Max Temperature    │ 60°C (canister surface)                       │
│ Humidity Range     │ 40-60% RH (optimal)                           │
│ Canister Life      │ ~30 days @ 1 person metabolic load            │
└────────────────────┴────────────────────────────────────────────────┘

WARNING INDICATORS:
□ Rapid temperature rise (>50°C in 5 min) - Check airflow
□ CO2 > 3000ppm with fan running - Replace canister
□ Unusual odor (ammonia-like) - LiOH leak, evacuate
□ Visible dust from canister - Filter breach, stop system
```

---

## 2. Jack视角 - 他的感知描述

### 2.1 场景描述

**[Jack的日志 - 第3小时]**

*我找到了那个...什么东西。它在一个金属柜子里，大概到我胸口那么高。柜门上有一些标签，但大部分都被刮花了，只能看清"CAUTION"和"VENTILATION"几个字。*

*里面有一个大圆筒，灰色的，大概像那种大号保温瓶那么大。圆筒两边连着软管——一边是黑色的，一边是蓝色的。圆筒上面有一些白色的颗粒状东西，闻起来有点像游泳池的味道，但更难闻。*

*旁边有一个小盒子，上面有个绿色的灯在亮着。盒子上有几个螺丝端子，电线从那里接出来——我能看到红色、黑色、蓝色和黄色的线。还有一个小风扇...不对，看起来更像电脑里的那种散热风扇，但是更大一些。*

*我按照你说的检查了那个绿色指示灯，它确实亮着。但是那个风扇不转。我用手碰了一下，它是松的，可以转动，但是自己不会动。*

### 2.2 情绪状态

```
[JACK STATUS]
┌─────────────────────────────────────────────────────────────────────┐
│  Stress Level: ████████░░  78% (Elevated)                          │
│  CO2 Exposure: ███░░░░░░░  28% (Mild headache reported)            │
│  Confidence:   ██░░░░░░░░  15% (Very Low)                          │
│  Trust:        ██████░░░░  60% (Building)                          │
└─────────────────────────────────────────────────────────────────────┘
```

**Jack的内心独白：**

> "我不知道这些东西是干什么的。那个白色颗粒...我碰了一下，手指有点刺痛。你确定这安全吗？"

> "风扇不转。我试着推了一下扇叶，它能动。是不是没电了？但是那个绿灯亮着啊..."

> "等等，我听到什么声音了。像是...滴答声？不，更像是气流的声音，但是很小。"

> "我开始有点头晕了。是不是因为这里空气不好？"

### 2.3 他对玩家指令的理解

**当玩家说"检查继电器K1"时：**

> "继...继电器？是那个有电线连着的小黑盒子吗？我看到有个东西，大概火柴盒大小，黑色的，上面有字...'OMRON'？还有数字...G5Q？"

**当玩家说"检查保险丝F1"时：**

> "保险丝...是那种小小的玻璃管吗？我在那个电源盒子里看到一个，是透明的，里面有一根金属丝。看起来没断啊？"

**当玩家说"测量风扇电阻"时：**

> "电阻？我...我没有万用表。我只有你之前让我找的那个工具包，里面有螺丝刀、胶带、还有一些电线。"

---

## 3. 核心交互循环

### 3.1 成功路径

```
┌─────────────────────────────────────────────────────────────────────┐
│                    SUCCESS PATH - CDRA-BK REPAIR                    │
└─────────────────────────────────────────────────────────────────────┘

STEP 1: 诊断
┌─────────────────────────────────────────────────────────────────────┐
│ Player: "首先确认电源。告诉我那个绿色LED的状态。"                    │
│                                                                      │
│ Jack: "绿灯亮着...但是有点闪烁？"                                    │
│                                                                      │
│ Player: "闪烁说明电压不稳。检查保险丝F1——那个透明的玻璃管。"         │
│                                                                      │
│ Jack: "我看到了...里面那根丝看起来是完整的。"                        │
│                                                                      │
│ Player: "好的，保险丝没问题。现在检查继电器。找一个黑色的小盒子，    │
│         上面可能有'OMRON'或者'G5Q'字样。"                            │
│                                                                      │
│ Jack: "找到了！但是...我听不到任何声音。它应该响吗？"                │
│                                                                      │
│ Player: "当你按下旁边的测试按钮时，应该会听到'咔嗒'声。试试看。"     │
│                                                                      │
│ Jack: "没有声音。完全没有。"                                         │
│                                                                      │
│ [诊断结果：继电器故障]                                                │
└─────────────────────────────────────────────────────────────────────┘

STEP 2: 获取替换部件
┌─────────────────────────────────────────────────────────────────────┐
│ Player: "我们需要一个替换的继电器。在工具柜里找一下——应该有备件。"  │
│                                                                      │
│ Jack: "工具柜...我找到了一个标着'ELECTRICAL'的抽屉。里面有几个黑    │
│         色的小盒子...有一个上面写着'G5Q-14 DC24'，是这个吗？"       │
│                                                                      │
│ Player: "就是这个。现在，在更换之前，必须先断电。找到电源开关，      │
│         把它关掉。"                                                  │
│                                                                      │
│ Jack: "开关...我看到了，红色的，在柜子侧面。关掉了。绿灯灭了。"    │
└─────────────────────────────────────────────────────────────────────┘

STEP 3: 更换继电器
┌─────────────────────────────────────────────────────────────────────┐
│ Player: "很好。现在小心地拔出旧的继电器。它应该是插在一个插座上的。" │
│                                                                      │
│ Jack: "拔出来了。有四个金属脚...有一个看起来有点黑？"                │
│                                                                      │
│ Player: "那是接触点烧蚀的痕迹。把新的插上去，确保方向正确——         │
│         通常有一个缺口或者标记指示方向。"                            │
│                                                                      │
│ Jack: "插好了。现在怎么办？"                                         │
│                                                                      │
│ Player: "重新打开电源开关。"                                         │
│                                                                      │
│ Jack: "开了！绿灯亮了...而且风扇开始转了！"                          │
│                                                                      │
│ [系统恢复正常运行]                                                    │
└─────────────────────────────────────────────────────────────────────┘

STEP 4: 验证
┌─────────────────────────────────────────────────────────────────────┐
│ Player: "很好！现在我们需要确认系统真的在工作。等大约5分钟，         │
│         然后告诉我你感觉如何——头晕有没有减轻？"                      │
│                                                                      │
│ Jack: "等等...让我感觉一下...确实，头没那么晕了。空气好像清新了一些。│
│         而且那个圆筒有点温温的，说明它在工作，对吗？"                │
│                                                                      │
│ Player: "完全正确。LiOH反应是放热的，温度升高说明CO2正在被吸收。     │
│         系统修复成功。"                                              │
│                                                                      │
│ [PUZZLE COMPLETE - 基础修复]                                          │
└─────────────────────────────────────────────────────────────────────┘
```

### 3.2 失败分支

```
┌─────────────────────────────────────────────────────────────────────┐
│                    FAILURE BRANCHES                                 │
└─────────────────────────────────────────────────────────────────────┘

FAILURE A: 带电操作导致短路
┌─────────────────────────────────────────────────────────────────────┐
│ Player: "直接拔下继电器，快点。"                                     │
│                                                                      │
│ Jack: "好的——"                                                       │
│                                                                      │
│ *火花* *噼啪声*                                                       │
│                                                                      │
│ Jack: "啊！有火花！那个绿灯灭了！还有一股烧焦的味道..."              │
│                                                                      │
│ [结果：控制板损坏，需要更换整个电路板]                                │
│ [后果：修复时间增加30分钟，CO2浓度继续上升]                           │
│ [补救：寻找备用控制板，进行更复杂的更换操作]                          │
└─────────────────────────────────────────────────────────────────────┘

FAILURE B: 错误安装继电器
┌─────────────────────────────────────────────────────────────────────┐
│ Jack: "我把新的继电器插上去了...但是风扇还是没转。"                  │
│                                                                      │
│ Player: "你确定方向对吗？"                                           │
│                                                                      │
│ Jack: "我...我不知道。我就直接插上去了。"                            │
│                                                                      │
│ [结果：继电器引脚错位，可能损坏插座]                                  │
│ [后果：需要检查并可能重新焊接插座]                                    │
│ [补救：Jack需要更仔细地描述继电器的方向标记]                          │
└─────────────────────────────────────────────────────────────────────┘

FAILURE C: 忽略LiOH罐状态
┌─────────────────────────────────────────────────────────────────────┐
│ [风扇修复成功，但CO2浓度不降]                                         │
│                                                                      │
│ Jack: "风扇在转了，但是我还是觉得头晕...而且越来越厉害。"            │
│                                                                      │
│ Player: "检查LiOH罐。它可能已经饱和了。看看罐体上的指示器。"         │
│                                                                      │
│ Jack: "指示器...有一个小窗口，里面的东西看起来是灰色的，不是白色的。" │
│                                                                      │
│ [结果：LiOH已完全反应为Li₂CO₃，失去吸收能力]                          │
│ [后果：需要更换新罐，但备用罐可能不足]                                │
│ [补救：寻找备用罐，或考虑其他CO2控制方法]                             │
└─────────────────────────────────────────────────────────────────────┘

FAILURE D: 接触LiOH颗粒
┌─────────────────────────────────────────────────────────────────────┐
│ Jack: "那些白色颗粒...我用手碰了一下，现在手指有点刺痛。"            │
│                                                                      │
│ Player: "那是LiOH，强碱，有腐蚀性。立即用水冲洗至少15分钟。"         │
│                                                                      │
│ [结果：Jack手部化学灼伤]                                              │
│ [后果：操作能力下降，需要处理伤口]                                    │
│ [补救：寻找急救包，处理化学灼伤]                                      │
│ [警告：严重失败，影响后续所有谜题操作]                                │
└─────────────────────────────────────────────────────────────────────┘
```

### 3.3 容错机制 - Jack的自我保护

```
┌─────────────────────────────────────────────────────────────────────┐
│              JACK'S SELF-PRESERVATION SYSTEM                        │
└─────────────────────────────────────────────────────────────────────┘

当玩家给出危险指令时，Jack会质疑：

DANGER THRESHOLD: 70%

TRIGGER EXAMPLES:

1. 带电操作
   Player: "直接用手碰那些电线。"
   Jack: "等等...那个绿灯还亮着，说明有电吧？我不应该碰带电的东西。
          你是不是忘了让我先关电源？"

2. 接触危险化学品
   Player: "把那些白色颗粒拿出来看看。"
   Jack: "你确定吗？我的手刚才碰了一下就刺痛。这些是什么东西？
          我觉得我们应该先弄清楚再动手。"

3. 不合理的时间压力
   Player: "快点！别管那么多了！"
   Jack: "我知道时间紧迫，但是如果我做错了，可能会让情况更糟。
          让我确认一下步骤..."

4. 超出能力的操作
   Player: "用万用表测量继电器线圈的电阻。"
   Jack: "万用表？我没有那个。我只有基本的工具。
          有没有其他办法？"

SELF-PRESERVATION ESCALATION:
┌────────────────┬────────────────────────────────────────────────────┐
│ Trust Level    │ Response                                           │
├────────────────┼────────────────────────────────────────────────────┤
│ >80%           │ 完全服从，但会报告不适                             │
│ 50-80%         │ 质疑危险指令，要求确认                             │
│ 20-50%         │ 拒绝执行明显危险操作                               │
│ <20%           │ 完全拒绝，可能自行采取行动                         │
└────────────────┴────────────────────────────────────────────────────┘
```

---

## 4. 科学原理说明

### 4.1 CO2吸收反应的化学方程式

```
┌─────────────────────────────────────────────────────────────────────┐
│              CHEMISTRY OF CO2 ABSORPTION                            │
└─────────────────────────────────────────────────────────────────────┘

PRIMARY REACTION:

    2 LiOH(s) + CO₂(g) → Li₂CO₃(s) + H₂O(g)
    
    Molar masses:
    • LiOH: 6.94 + 16.00 + 1.01 = 23.95 g/mol
    • CO₂: 12.01 + 2(16.00) = 44.01 g/mol
    • Li₂CO₃: 2(6.94) + 12.01 + 3(16.00) = 73.89 g/mol
    • H₂O: 2(1.01) + 16.00 = 18.02 g/mol
    
    Stoichiometry:
    2 × 23.95g LiOH + 44.01g CO₂ → 73.89g Li₂CO₃ + 18.02g H₂O
    
    47.9g LiOH absorbs 44g CO₂
    
    Absorption capacity: 0.919g CO₂ per 1g LiOH

THERMODYNAMICS:

    ΔH°rxn = ΣΔH°f(products) - ΣΔH°f(reactants)
    
    ΔH°f values (kJ/mol):
    • LiOH(s): -487.2
    • CO₂(g): -393.5
    • Li₂CO₃(s): -1216.0
    • H₂O(g): -241.8
    
    ΔH°rxn = [-1216.0 + (-241.8)] - [2(-487.2) + (-393.5)]
           = -1457.8 - (-1367.9)
           = -89.9 kJ/mol
    
    The reaction is EXOTHERMIC (heat releasing)

REACTION KINETICS:

    Rate = k[LiOH]²[CO₂][H₂O]
    
    The reaction requires water vapor as a catalyst.
    Without humidity, the reaction rate drops significantly.
    
    Optimal conditions:
    • Temperature: 20-40°C
    • Relative Humidity: 40-60%
    • CO₂ concentration: >1000 ppm for noticeable reaction
```

### 4.2 气压与气体循环的物理关系

```
┌─────────────────────────────────────────────────────────────────────┐
│              PHYSICS OF AIR CIRCULATION                             │
└─────────────────────────────────────────────────────────────────────┘

FAN PERFORMANCE:

    Airflow rate Q (CFM) = (RPM × Displacement) / 1728
    
    For the CDRA-BK fan:
    • Rated RPM: 3000
    • Impeller diameter: 120mm
    • Rated airflow: 150-200 CFM
    
    Actual airflow depends on:
    1. System resistance (pressure drop)
    2. Power supply voltage
    3. Motor efficiency

PRESSURE DROP ACROSS CANISTER:

    ΔP = (f × L × ρ × v²) / (2 × D)
    
    Where:
    • f = friction factor
    • L = canister depth
    • ρ = air density
    • v = air velocity
    • D = hydraulic diameter
    
    Typical ΔP: 50-100 Pa (0.5-1 mbar)

CO2 CONCENTRATION DYNAMICS:

    d[CO₂]/dt = (Generation Rate - Removal Rate) / Volume
    
    Human CO₂ generation:
    • Resting: ~200 mL/min (STP)
    • Light activity: ~300 mL/min
    • Heavy activity: ~500+ mL/min
    
    At STP: 1 mol gas = 22.4 L
    CO₂ generation ≈ 0.009 mol/min per person
    
    For a 100m³ habitat with 1 person:
    • Without scrubbing: CO₂ increases ~0.2% per hour
    • Critical level (2%) reached in ~10 hours

GAS MIXING:

    In microgravity (or any environment), CO₂ can form "pockets"
    without proper ventilation.
    
    The fan ensures:
    1. Turbulent mixing (Re > 4000)
    2. Uniform CO₂ distribution
    3. Forced convection through canister
```

### 4.3 电路负载计算

```
┌─────────────────────────────────────────────────────────────────────┐
│              ELECTRICAL LOAD CALCULATIONS                           │
└─────────────────────────────────────────────────────────────────────┘

POWER SUPPLY RATING:

    Input: 110-240V AC, 50/60Hz
    Output: 24V DC, 5A max
    
    Max output power: P = V × I = 24V × 5A = 120W
    
    Efficiency (typical): 85%
    Input power at max load: 120W / 0.85 = 141W

FAN MOTOR LOAD:

    Rated: 24V DC, 2.5A
    Power consumption: P = 24V × 2.5A = 60W
    
    Starting current (inrush): 3-5 × rated = 7.5-12.5A
    Duration: 100-500ms
    
    This is why the fuse is "slow-blow" type
    
    Wire gauge requirement:
    • For 2.5A continuous: 22 AWG minimum
    • For 5A peak: 20 AWG recommended
    • Actual installation: 18 AWG (safety margin)

RELAY COIL LOAD:

    G5Q-14 DC24 specifications:
    • Coil voltage: 24V DC
    • Coil resistance: 288Ω ±10%
    • Coil current: I = V/R = 24/288 = 83.3mA
    • Coil power: P = V²/R = 576/288 = 2W
    
    Must be powered continuously during operation

TOTAL SYSTEM LOAD:

    Component          Current    Power
    ────────────────────────────────────
    Fan Motor          2.5A       60W
    Relay Coil         0.083A     2W
    CO2 Sensor         0.1A       2.4W (max)
    MCU + LEDs         0.05A      1.2W
    ────────────────────────────────────
    Total              2.733A     65.6W
    
    Safety margin: 5A / 2.733A = 1.83 (183%)
    This is adequate for reliable operation

FUSE SELECTION:

    Fuse rating = Max continuous load × 1.5
                = 2.733A × 1.5
                = 4.1A
    
    Selected: 5A slow-blow
    
    Time-current characteristics:
    • 100% rating: indefinite
    • 135% rating: 1 hour max
    • 200% rating: 5 seconds max
    • 1000% rating: 10ms max
```

---


# Puzzle 2: 电力系统重启 (Power Restoration)

## 背景设定

**地点**：CARGO基地 - 主配电室
**时间**：基地发生系统故障后的第5小时
**危急程度**：CRITICAL - 主电源中断，备用电池即将耗尽

**故事背景**：
基地的主发电机因冷却系统故障自动停机。备用电池系统只能维持生命维持设备运行约2小时。Jack需要手动重启主配电系统，将备用发电机接入电网。但配电箱的标签在事故中脱落或模糊，他必须通过玩家的指导完成正确的接线操作。

---

## 1. 玩家视角 - 技术手册内容

### 1.1 配电系统原理图

```
┌─────────────────────────────────────────────────────────────────────┐
│              MAIN POWER DISTRIBUTION SYSTEM                         │
│                    [TECHNICAL MANUAL v3.1]                          │
│              CARGO Base - Electrical Infrastructure                 │
└─────────────────────────────────────────────────────────────────────┘

POWER SOURCES:
┌─────────────────────────────────────────────────────────────────────┐
│                                                                     │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐             │
│  │ MAIN GEN    │    │ AUX GEN     │    │ BATTERY     │             │
│  │ (Offline)   │    │ (Standby)   │    │ (Active)    │             │
│  │ 480V 3-Phase│    │ 480V 3-Phase│    │ 48V DC      │             │
│  │ 100kW       │    │ 50kW        │    │ 200Ah       │             │
│  └──────┬──────┘    └──────┬──────┘    └──────┬──────┘             │
│         │                  │                  │                     │
│         │                  │                  │                     │
│         └──────────────────┼──────────────────┘                     │
│                            │                                         │
│                            ▼                                         │
│                   ┌─────────────────┐                                │
│                   │  TRANSFER       │                                │
│                   │  SWITCH PANEL   │                                │
│                   │  [CRITICAL]     │                                │
│                   └────────┬────────┘                                │
│                            │                                         │
└────────────────────────────┼─────────────────────────────────────────┘
                             │
                             ▼
                   ┌─────────────────┐
                   │  MAIN BREAKER   │
                   │  PANEL (MBP)    │
                   │  480V → 120/240V│
                   └────────┬────────┘
                            │
         ┌──────────────────┼──────────────────┐
         │                  │                  │
         ▼                  ▼                  ▼
   ┌──────────┐      ┌──────────┐      ┌──────────┐
   │ LIFE     │      │ HVAC     │      │ AUX      │
   │ SUPPORT  │      │ SYSTEM   │      │ SYSTEMS  │
   │ 120V AC  │      │ 240V AC  │      │ 120V AC  │
   │ 30A      │      │ 50A      │      │ 20A      │
   └──────────┘      └──────────┘      └──────────┘

CURRENT STATUS:
□ Main Generator: OFFLINE (Cooling fault)
□ Aux Generator: STANDBY (Ready to start)
□ Battery System: ACTIVE (2 hours remaining)
□ Life Support: OPERATIONAL (Battery)
□ HVAC: OFFLINE (Non-critical, load shed)
□ Aux Systems: OFFLINE
```

### 1.2 配电箱接线图

```
┌─────────────────────────────────────────────────────────────────────┐
│              TRANSFER SWITCH PANEL - INTERNAL WIRING                │
│                    [Wiring Diagram Rev.D]                           │
└─────────────────────────────────────────────────────────────────────┘

PANEL LAYOUT (Front View):

    ┌─────────────────────────────────────────────────────────────┐
    │  [1]      [2]      [3]      [4]      [5]      [6]          │
    │  MAIN    AUX     BAT+     BAT-    NEUTRAL   GROUND         │
    │  INPUT   INPUT   48V DC   48V DC   (White)   (Green)       │
    │  (Red)   (Blue)  (Red)   (Black)                            │
    │                                                             │
    │  ┌───┐   ┌───┐   ┌───┐   ┌───┐   ┌───┐   ┌───┐            │
    │  │ A │   │ B │   │ C │   │ D │   │ E │   │ F │  Terminal  │
    │  │   │   │   │   │   │   │   │   │   │   │   │  Blocks    │
    │  └───┘   └───┘   └───┘   └───┘   └───┘   └───┘            │
    │                                                             │
    │  [7]      [8]      [9]      [10]     [11]     [12]         │
    │  L1      L2       L3       NEUTRAL   GRND    INVERTER      │
    │  OUTPUT  OUTPUT   OUTPUT   OUT      OUT     CONTROL        │
    │  (Blk)   (Red)    (Blue)   (White)   (Grn)   (Yellow)      │
    │                                                             │
    │  ┌───┐   ┌───┐   ┌───┐   ┌───┐   ┌───┐   ┌───┐            │
    │  │ G │   │ H │   │ I │   │ J │   │ K │   │ L │            │
    │  │   │   │   │   │   │   │   │   │   │   │   │            │
    │  └───┘   └───┘   └───┘   └───┘   └───┘   └───┘            │
    │                                                             │
    │  ┌─────────────────────────────────────────────────────┐   │
    │  │              CIRCUIT BREAKERS                       │   │
    │  │  ┌─────┐  ┌─────┐  ┌─────┐  ┌─────┐               │   │
    │  │  │CB1  │  │CB2  │  │CB3  │  │CB4  │               │   │
    │  │  │100A │  │ 50A │  │ 30A │  │ 20A │               │   │
    │  │  │MAIN │  │ AUX │  │ BAT │  │INV  │               │   │
    │  │  └─────┘  └─────┘  └─────┘  └─────┘               │   │
    │  └─────────────────────────────────────────────────────┘   │
    │                                                             │
    │  [STATUS LEDS]                                              │
    │  ● MAIN PWR (Green)    ● AUX PWR (Yellow)                  │
    │  ● BAT PWR (Red)       ● FAULT (Red Blink)                 │
    └─────────────────────────────────────────────────────────────┘

REQUIRED CONNECTIONS FOR AUX GENERATOR START:

    Phase Connections:
    ┌─────────────────────────────────────────────────────────────┐
    │  Aux Gen L1 (Blue wire) → Terminal B → CB2 → Terminal G    │
    │  Aux Gen L2 (Black wire) → Terminal B → CB2 → Terminal H   │
    │  Aux Gen L3 (Red wire) → Terminal B → CB2 → Terminal I     │
    │  Aux Gen Neutral → Terminal E → Terminal J                 │
    │  Aux Gen Ground → Terminal F → Terminal K                  │
    └─────────────────────────────────────────────────────────────┘
    
    Control Connections:
    ┌─────────────────────────────────────────────────────────────┐
    │  Start Signal: Terminal L (Yellow) to AUX GEN START        │
    │  Interlock: CB2 must be ON before start signal active      │
    └─────────────────────────────────────────────────────────────┘

INVERTER CONNECTIONS (Battery to AC):

    DC Input:
    ┌─────────────────────────────────────────────────────────────┐
    │  Battery +48V → Terminal C → CB3 → Inverter +DC            │
    │  Battery -48V → Terminal D → CB3 → Inverter -DC            │
    └─────────────────────────────────────────────────────────────┘
    
    AC Output:
    ┌─────────────────────────────────────────────────────────────┐
    │  Inverter L1 → Terminal G → Life Support Panel             │
    │  Inverter L2 → Terminal H → Life Support Panel             │
    │  Inverter Neutral → Terminal J → Life Support Panel        │
    │  Inverter Ground → Terminal K → Life Support Panel         │
    └─────────────────────────────────────────────────────────────┘
```

### 1.3 线缆颜色编码标准

```
┌─────────────────────────────────────────────────────────────────────┐
│              WIRE COLOR CODE - CARGO Base Standard                  │
│                    [IEC 60446 / NEC 310.12]                         │
└─────────────────────────────────────────────────────────────────────┘

AC POWER (480V 3-Phase):
┌────────────────┬────────────────────────────────────────────────────┐
│ Color          │ Function                                           │
├────────────────┼────────────────────────────────────────────────────┤
│ BROWN          │ L1 (Phase A)                                       │
│ BLACK          │ L2 (Phase B)                                       │
│ GRAY           │ L3 (Phase C)                                       │
│ BLUE           │ Neutral (when used)                                │
│ GREEN/YELLOW   │ Protective Earth (Ground)                          │
└────────────────┴────────────────────────────────────────────────────┘

AC POWER (120/240V Split Phase):
┌────────────────┬────────────────────────────────────────────────────┐
│ Color          │ Function                                           │
├────────────────┼────────────────────────────────────────────────────┤
│ BLACK          │ L1 (Hot) - 120V to Neutral                         │
│ RED            │ L2 (Hot) - 120V to Neutral, 240V to L1             │
│ WHITE          │ Neutral                                            │
│ GREEN/BARE     │ Ground                                             │
└────────────────┴────────────────────────────────────────────────────┘

DC POWER (48V Battery):
┌────────────────┬────────────────────────────────────────────────────┐
│ Color          │ Function                                           │
├────────────────┼────────────────────────────────────────────────────┤
│ RED            │ Positive (+48V)                                    │
│ BLACK          │ Negative (Return)                                  │
│ WHITE/RED      │ Positive (alternative)                             │
│ WHITE/BLACK    │ Negative (alternative)                             │
└────────────────┴────────────────────────────────────────────────────┘

CONTROL SIGNALS:
┌────────────────┬────────────────────────────────────────────────────┐
│ Color          │ Function                                           │
├────────────────┼────────────────────────────────────────────────────┤
│ YELLOW         │ Start/Run signal                                   │
│ ORANGE         │ Stop/Interlock signal                              │
│ PURPLE         │ Status/Monitor signal                              │
│ PINK           │ Alarm signal                                       │
└────────────────┴────────────────────────────────────────────────────┘

⚠️  CRITICAL WARNING:
    The accident caused damage to wire insulation markers.
    Some wires may have incorrect colors due to field repairs.
    ALWAYS verify with continuity tester before energizing.
```

### 1.4 启动程序检查清单

```
┌─────────────────────────────────────────────────────────────────────┐
│              AUXILIARY GENERATOR START PROCEDURE                    │
│                    [Emergency Protocol 4.2]                         │
└─────────────────────────────────────────────────────────────────────┘

PRE-START CHECKLIST:

□ STEP 1: Safety Verification
  □ Ensure Main Generator breaker CB1 is OPEN (OFF)
  □ Verify no personnel in generator compartment
  □ Check fuel level (minimum 25% required)
  □ Verify cooling system filled

□ STEP 2: Battery Connection Verification
  □ Terminal C: Battery + (Red wire) - TIGHT
  □ Terminal D: Battery - (Black wire) - TIGHT
  □ CB3 (Battery): CLOSED (ON)
  □ Inverter status LED: GREEN

□ STEP 3: Aux Generator Wiring (CRITICAL)
  □ Terminal B: Aux Gen Input (Blue wire) - CONNECTED
  □ Terminal E: Neutral (White wire) - CONNECTED
  □ Terminal F: Ground (Green wire) - CONNECTED
  □ CB2 (Aux): OPEN (OFF) - DO NOT CLOSE YET

□ STEP 4: Output Wiring Verification
  □ Terminal G: L1 Output (Black wire) - CONNECTED
  □ Terminal H: L2 Output (Red wire) - CONNECTED
  □ Terminal I: L3 Output (Blue wire) - CONNECTED
  □ Terminal J: Neutral Out (White wire) - CONNECTED
  □ Terminal K: Ground Out (Green wire) - CONNECTED

START SEQUENCE:

STEP 5: Pre-lube (if equipped)
  □ Press and hold PRE-LUBE button for 30 seconds
  □ Release button

STEP 6: Start Generator
  □ Close CB2 (Aux Generator breaker)
  □ Wait 3 seconds for control power
  □ Press START button (or connect Terminal L to +48V)
  □ Crank time: Max 10 seconds
  □ If no start, wait 30 seconds before retry

STEP 7: Monitor Start
  □ Oil pressure: >20 PSI within 5 seconds
  □ Frequency: 60 Hz ± 1 Hz
  □ Voltage: 480V ± 5%
  □ If any parameter out of range: IMMEDIATE SHUTDOWN

STEP 8: Load Transfer
  □ Allow generator to warm up for 2 minutes
  □ Verify stable operation
  □ Close output breakers to load panels
  □ Monitor load current (should be <80% rating)

POST-START MONITORING:
  □ Check every 15 minutes: Oil pressure, coolant temp, fuel level
  □ Log all readings
  □ If battery was used, begin recharge cycle

EMERGENCY SHUTDOWN CONDITIONS:
  ⚠️ Oil pressure <10 PSI
  ⚠️ Coolant temperature >100°C
  ⚠️ Overspeed (>66 Hz)
  ⚠️ Underspeed (<54 Hz)
  ⚠️ Excessive vibration
  ⚠️ Fuel leak detected
  ⚠️ Fire or smoke
```

---

## 2. Jack视角 - 他的感知描述

### 2.1 场景描述

**[Jack的日志 - 第5小时]**

*配电室...这里比我想象的要小。墙上有一个巨大的金属柜子，大概两米高，一米宽。柜门是打开的，里面全是电线、开关，还有一些我不认识的设备。*

*最显眼的是四个大开关——他们说是断路器。上面标着CB1、CB2、CB3、CB4。CB1和CB2现在是向下的，CB3是向上的。CB4...我看不清，好像也是向下的。*

*电线...到处都是电线。它们从上面、下面、旁边伸出来，连接到各种端子上。问题是，很多电线的颜色都不对劲。我记得红色应该是火线，但是有些红色电线上面贴着白色的标签，写着"NEUTRAL"。这不对吧？*

*地上有一个标签脱落了，上面写着"AUX GEN L1"。它应该是贴在某个地方的，但是我不知道是哪里。*

*旁边有一个小屏幕，显示着一些数字。我能看到"48.2V"和"BAT 67%"。电池还剩67%，你说我们还有不到2小时的时间。*

### 2.2 情绪状态

```
[JACK STATUS]
┌─────────────────────────────────────────────────────────────────────┐
│  Stress Level: ██████████  92% (Severe - Time pressure)            │
│  Fatigue:      ███████░░░  70% (Tired but alert)                   │
│  Confidence:   █░░░░░░░░░  8%  (Extremely Low)                     │
│  Fear:         █████████░  85% (Afraid of electrocution)           │
└─────────────────────────────────────────────────────────────────────┘
```

**Jack的内心独白：**

> "这些电线...我不敢碰。你说红色是火线，但是那个红色电线上面贴着'NEUTRAL'的标签。到底是看颜色还是看标签？"

> "那个CB2...你说要把它打开，但是它是控制什么的？如果搞错了会不会爆炸？"

> "我听到外面有声音。像是...发电机？不，可能是风声。这里隔音不好。"

> "我的手在抖。不是因为冷，是因为...我不知道自己在做什么。"

### 2.3 他对玩家指令的理解

**当玩家说"找到标着Terminal B的端子"时：**

> "Terminal B...让我看看...有很多端子排，每个上面有数字。我看到了A、B、C...B在上面一排，第二个位置。有一个蓝色的电线连着它，但是看起来有点松。"

**当玩家说"检查CB2的状态"时：**

> "CB2...就是那个标着'50A AUX'的开关？它现在是向下的。我记得向下是关，向上是开？还是反过来？"

**当玩家说"测量电压"时：**

> "我...我没有万用表。你之前让我带的工具包里没有那个。我只有一个手电筒、一双手套、还有一些胶带。"

---

## 3. 核心交互循环

### 3.1 成功路径

```
┌─────────────────────────────────────────────────────────────────────┐
│                    SUCCESS PATH - POWER RESTORATION                 │
└─────────────────────────────────────────────────────────────────────┘

STEP 1: 评估当前状态
┌─────────────────────────────────────────────────────────────────────┐
│ Player: "先不要碰任何东西。告诉我你看到什么。"                       │
│                                                                      │
│ Jack: "一个大金属柜，里面全是电线和开关。有四个大开关——CB1、CB2、   │
│        CB3、CB4。CB1和CB2是向下的，CB3是向上的，CB4也是向下的。      │
│        还有很多端子，标着字母和数字..."                              │
│                                                                      │
│ Player: "很好。先看那个小屏幕，告诉我显示什么。"                     │
│                                                                      │
│ Jack: "48.2V...BAT 67%...还有一个倒计时，显示1:47。"                 │
│                                                                      │
│ Player: "1小时47分钟。我们需要在那之前启动辅助发电机。现在，找到    │
│         标着'AUX GEN'的端子。它应该在上面一排。"                    │
│                                                                      │
│ Jack: "找到了！Terminal B，有一个蓝色的电线连着。"                   │
└─────────────────────────────────────────────────────────────────────┘

STEP 2: 验证接线（关键步骤）
┌─────────────────────────────────────────────────────────────────────┐
│ Player: "先不要碰CB2。我们需要确认所有接线都正确。                   │
│         看看Terminal B旁边的端子。"                                  │
│                                                                      │
│ Jack: "Terminal A有一个红色的粗电线...Terminal C有一个红色的细电线   │
│         和一个黑色的细电线..."                                       │
│                                                                      │
│ Player: "Terminal C是电池输入。红色应该是正极，黑色是负极。           │
│         现在看下面一排——Terminal G、H、I应该分别有输出线。"          │
│                                                                      │
│ Jack: "G是黑色，H是红色，I是蓝色...还有一个J是白色，K是绿色。"       │
│                                                                      │
│ Player: "看起来接线是正确的。现在检查辅助发电机的燃油。              │
│         在柜子旁边应该有一个燃油表。"                                │
│                                                                      │
│ Jack: "找到了！显示...45%。够吗？"                                   │
│                                                                      │
│ Player: "够了。现在开始启动程序。"                                   │
└─────────────────────────────────────────────────────────────────────┘

STEP 3: 启动辅助发电机
┌─────────────────────────────────────────────────────────────────────┐
│ Player: "第一步：确保CB1是断开的。它是向上的还是向下的？"            │
│                                                                      │
│ Jack: "向下的。"                                                     │
│                                                                      │
│ Player: "好。现在准备启动。先把CB2推上去——这是给辅助发电机供电控制。│
│         但是先不要启动，只是准备好。"                                │
│                                                                      │
│ Jack: "CB2...推上去了。我听到有声音了，像是...嗡嗡声？"              │
│                                                                      │
│ Player: "那是控制电源接通了。现在找到启动按钮——应该标着'START'，    │
│         或者可能是一个黄色的端子。"                                  │
│                                                                      │
│ Jack: "有一个黄色的按钮，标着'START'。我按了？"                      │
│                                                                      │
│ Player: "按下去，保持3秒钟。"                                        │
│                                                                      │
│ Jack: "*嗡嗡声变大*...*咳嗽声*...有烟！"                             │
│                                                                      │
│ Player: "别担心，那是正常的——冷启动时的废气。继续按住。"             │
│                                                                      │
│ Jack: "3秒了！我放了...声音还在！它在运转！"                         │
│                                                                      │
│ [辅助发电机启动成功]                                                  │
└─────────────────────────────────────────────────────────────────────┘

STEP 4: 负载转移
┌─────────────────────────────────────────────────────────────────────┐
│ Player: "很好！让它运转2分钟预热。同时监控那个小屏幕。"              │
│                                                                      │
│ Jack: "屏幕变了...480V，60.1Hz...还有一些数字在跳。"                 │
│                                                                      │
│ Player: "电压和频率都正常。2分钟后，我们可以开始转移负载。           │
│         找到Life Support面板的断路器，应该是CB4。"                   │
│                                                                      │
│ Jack: "CB4...找到了，标着'30A LIFE SUP'。"                           │
│                                                                      │
│ Player: "把它推上去。这会切断电池供电，切换到发电机供电。"           │
│                                                                      │
│ Jack: "推上去了！屏幕显示...负载电流25A。正常吗？"                   │
│                                                                      │
│ Player: "正常。现在Life Support由发电机供电了。接下来是HVAC..."      │
│                                                                      │
│ [系统逐步恢复，电池开始充电]                                          │
│ [PUZZLE COMPLETE - 基础恢复]                                          │
└─────────────────────────────────────────────────────────────────────┘
```

### 3.2 失败分支

```
┌─────────────────────────────────────────────────────────────────────┐
│                    FAILURE BRANCHES                                 │
└─────────────────────────────────────────────────────────────────────┘

FAILURE A: 错误的相序连接
┌─────────────────────────────────────────────────────────────────────┐
│ Player: "把蓝色电线接到Terminal G。"                                 │
│                                                                      │
│ Jack: "蓝色...G...好了。"                                            │
│                                                                      │
│ Player: "红色接到H，黑色接到I。"                                     │
│                                                                      │
│ Jack: "*接好后*...CB2推上去了...启动！"                              │
│                                                                      │
│ *发电机运转，但有异常噪音*                                            │
│                                                                      │
│ Jack: "声音不对...而且Life Support的灯在闪！"                        │
│                                                                      │
│ [结果：相序错误导致三相电机反转，设备损坏]                            │
│ [后果：Life Support设备受损，需要紧急维修]                            │
│ [补救：立即断开CB2，重新检查相序]                                     │
└─────────────────────────────────────────────────────────────────────┘

FAILURE B: 带电操作导致短路
┌─────────────────────────────────────────────────────────────────────┐
│ Player: "先把CB3断开，然后重新接线。"                                │
│                                                                      │
│ Jack: "CB3...是那个向上的开关？推下去？"                             │
│                                                                      │
│ Player: "对。"                                                       │
│                                                                      │
│ *Jack推下CB3，但手抖导致螺丝刀碰到相邻端子*                           │
│                                                                      │
│ *火花* *噼啪声* *CB3跳闸*                                             │
│                                                                      │
│ Jack: "啊！有火花！那个开关自己跳了！"                               │
│                                                                      │
│ [结果：短路导致电池保护熔断器熔断]                                    │
│ [后果：失去电池备份，时间压力剧增]                                    │
│ [补救：更换熔断器，或寻找备用电池]                                    │
└─────────────────────────────────────────────────────────────────────┘

FAILURE C: 忽略预热直接加载
┌─────────────────────────────────────────────────────────────────────┐
│ Player: "发电机启动了？好，马上把CB4推上去。"                        │
│                                                                      │
│ Jack: "马上？不等预热吗？"                                           │
│                                                                      │
│ Player: "没时间了，快！"                                             │
│                                                                      │
│ Jack: "好吧...CB4推上去了..."                                        │
│                                                                      │
│ *发电机声音突然变大，然后熄火*                                        │
│                                                                      │
│ Jack: "它停了！声音没了！"                                           │
│                                                                      │
│ [结果：冷机加载导致发动机熄火，可能损坏]                              │
│ [后果：需要重新启动，浪费时间]                                        │
│ [补救：等待更长时间预热，或检查发动机状态]                            │
└─────────────────────────────────────────────────────────────────────┘

FAILURE D: 错误的标签解读
┌─────────────────────────────────────────────────────────────────────┐
│ Jack: "我看到一根红色电线，上面贴着'NEUTRAL'的标签。                 │
│        还有一根白色电线，没有标签。我应该用哪个？"                   │
│                                                                      │
│ Player: "用红色的，标签是对的。"                                     │
│                                                                      │
│ *Jack连接后启动系统*                                                  │
│                                                                      │
│ Jack: "启动成功了！但是...我听到噼啪声，还有烧焦的味道！"            │
│                                                                      │
│ [结果：红色电线实际上是火线，不是中性线]                              │
│ [后果：设备损坏，可能引起火灾]                                        │
│ [补救：立即断电，检查损坏范围]                                        │
│ [严重警告：可能导致游戏结束]                                          │
└─────────────────────────────────────────────────────────────────────┘
```

### 3.3 认知鸿沟的体现

```
┌─────────────────────────────────────────────────────────────────────┐
│              THE KNOWLEDGE GAP - Player vs Jack                     │
└─────────────────────────────────────────────────────────────────────┘

PLAYER KNOWS:
┌─────────────────────────────────────────────────────────────────────┐
│ • 三相电源的相序重要性                                               │
│ • 断路器的正确操作顺序                                               │
│ • 电压、频率的正常范围                                               │
│ • 冷启动预热的必要性                                                 │
│ • 短路和电弧的危险性                                                 │
│ • 如何解读接线图和技术手册                                           │
└─────────────────────────────────────────────────────────────────────┘

JACK CAN DO:
┌─────────────────────────────────────────────────────────────────────┐
│ • 物理操作开关和断路器                                               │
│ • 连接和断开电线                                                     │
│ • 描述他看到的东西（颜色、位置、标签）                                 │
│ • 报告声音、气味、温度等感官信息                                       │
│ • 在指导下执行具体步骤                                               │
└─────────────────────────────────────────────────────────────────────┘

CRITICAL GAP AREAS:

1. 标签 vs 颜色的冲突
   Player: "按照标准，红色是火线。"
   Jack: "但是标签写着'NEUTRAL'..."
   
   → Player必须意识到事故后标签可能错误
   → Jack只能报告他看到的，不能判断对错

2. 电气安全知识
   Player: "先断开电源再操作。"
   Jack: "但是时间不够了..."
   
   → Jack会质疑，但可能服从
   → 玩家必须承担风险决策的责任

3. 故障诊断
   Player: "测量输出电压。"
   Jack: "我没有万用表。"
   
   → Player必须依赖Jack的感官描述
   → 信息不完整，需要推断

4. 时间压力下的决策
   Player: "跳过预热直接加载。"
   Jack: "这不安全..."
   
   → Jack的质疑是警告
   → 玩家可以选择冒险或保守
```

---

## 4. 科学原理说明

### 4.1 三相电力系统原理

```
┌─────────────────────────────────────────────────────────────────────┐
│              THREE-PHASE POWER SYSTEM                               │
└─────────────────────────────────────────────────────────────────────┘

PHASE RELATIONSHIP:

    V₁ = Vₘₐₓ × sin(ωt)
    V₂ = Vₘₐₓ × sin(ωt - 120°)
    V₃ = Vₘₐₓ × sin(ωt - 240°)
    
    Where ω = 2πf = 2π × 60 = 377 rad/s (for 60Hz)

LINE-TO-LINE VOLTAGE:

    Vₗₗ = √3 × Vₗₙ
    
    For 480V system:
    • Line-to-line: 480V
    • Line-to-neutral: 480/√3 = 277V
    
    For 208V system (derived from 480V):
    • Line-to-line: 208V
    • Line-to-neutral: 120V

POWER CALCULATION:

    Total Power P = √3 × Vₗₗ × Iₗ × PF
    
    Where:
    • Vₗₗ = Line-to-line voltage
    • Iₗ = Line current
    • PF = Power factor (typically 0.8-0.95)
    
    For Aux Generator (50kW, 480V, PF=0.85):
    I = 50000 / (√3 × 480 × 0.85) = 70.7A

PHASE SEQUENCE:

    Correct sequence (ABC): L1-L2-L3 = 0°-120°-240°
    
    If reversed (ACB): Motors run backward
    
    Detection: Use phase sequence indicator
    or observe motor rotation direction

SYNCHRONIZATION:

    Before connecting generator to grid:
    • Voltage match: ±5%
    • Frequency match: ±0.1 Hz
    • Phase angle: ±10°
    • Phase sequence: Must match
```

### 4.2 电路保护原理

```
┌─────────────────────────────────────────────────────────────────────┐
│              CIRCUIT PROTECTION DEVICES                             │
└─────────────────────────────────────────────────────────────────────┘

CIRCUIT BREAKER OPERATION:

    Thermal-Magnetic Breaker:
    
    Trip characteristic: I²t = constant
    
    • Thermal element: Responds to overload (I > 1.1×rated)
      Trip time: Minutes to hours
      
    • Magnetic element: Responds to short circuit (I > 5-10×rated)
      Trip time: Milliseconds

    Example - 50A breaker:
    • 55A (110%): May never trip
    • 75A (150%): Trip in ~10 minutes
    • 100A (200%): Trip in ~1 minute
    • 250A (500%): Trip in ~10 seconds
    • 500A (1000%): Trip instantly

FUSE CHARACTERISTICS:

    Time-Current Curve:
    
    Fuse rating: 5A slow-blow
    
    • 5A: Indefinite
    • 6.75A (135%): Max 1 hour
    • 10A (200%): Max 5 seconds
    • 50A (1000%): Max 10ms

SELECTIVE COORDINATION:

    Protection hierarchy:
    
    Branch circuit (20A) → Feeder (50A) → Main (100A)
    
    Fault at branch: Only branch breaker trips
    
    This prevents unnecessary widespread outage

GROUND FAULT PROTECTION:

    GFCI (Ground Fault Circuit Interrupter):
    
    Detects current imbalance: I_line - I_neutral > 5mA
    
    Trip time: <25ms
    
    Required for personnel protection in wet locations
```

### 4.3 电池与逆变器系统

```
┌─────────────────────────────────────────────────────────────────────┐
│              BATTERY & INVERTER SYSTEMS                             │
└─────────────────────────────────────────────────────────────────────┘

BATTERY CAPACITY:

    C-rate: Discharge current relative to capacity
    
    200Ah battery:
    • 1C = 200A discharge
    • 0.5C = 100A discharge
    • 0.1C = 20A discharge (recommended for longevity)
    
    Available energy:
    E = V × Ah = 48V × 200Ah = 9600Wh = 9.6kWh
    
    At 50% depth of discharge (DoD):
    Usable energy = 4.8kWh

RUNTIME CALCULATION:

    Load: Life Support = 2kW
    
    Runtime = Usable energy / Load
            = 4.8kWh / 2kW
            = 2.4 hours
    
    At 67% charge:
    Usable = 0.67 × 4.8 = 3.2kWh
    Runtime = 3.2 / 2 = 1.6 hours = 96 minutes

INVERTER EFFICIENCY:

    Typical efficiency: 85-95%
    
    For 90% efficiency:
    DC input power = AC output / 0.9
    
    Example:
    AC load: 2kW
    DC power required: 2 / 0.9 = 2.22kW
    DC current: 2220W / 48V = 46.25A

BATTERY CHARGING:

    Three-stage charging:
    
    1. Bulk charge: Constant current (0.1C-0.3C)
       Until voltage reaches absorption level (57.6V for 48V)
       
    2. Absorption: Constant voltage
       Current tapers down
       
    3. Float: Lower voltage (54V)
       Maintains full charge

BATTERY LIFETIME:

    Cycle life vs DoD:
    • 10% DoD: ~5000 cycles
    • 50% DoD: ~1000 cycles
    • 80% DoD: ~500 cycles
    
    Deep discharge reduces lifetime significantly
```

---


# Puzzle 3: 燃料合成 (The Chemistry Set)

## 背景设定

**地点**：CARGO基地 - 化学实验室/燃料储存区
**时间**：基地发生系统故障后的第12小时
**危急程度**：EXTREME - 通讯设备需要燃料启动，操作失误直接致命

**故事背景**：
基地的长距离通讯设备需要特定燃料（肼基燃料）才能启动。库存燃料已耗尽，但化学实验室有合成所需的基础化学品。Jack必须在玩家的指导下完成高风险的化学合成操作。任何配比错误、温度失控或污染都可能导致剧烈反应甚至爆炸。

---

## 1. 玩家视角 - 技术手册内容

### 1.1 燃料合成反应原理

```
┌─────────────────────────────────────────────────────────────────────┐
│              HYDRAZINE SYNTHESIS - RASCHIG PROCESS                  │
│                    [Chemical Engineering Manual]                    │
│                    CLASSIFIED - RESTRICTED ACCESS                   │
└─────────────────────────────────────────────────────────────────────┘

REACTION OVERVIEW:

    The Raschig process synthesizes hydrazine (N₂H₄) from ammonia (NH₃)
    and sodium hypochlorite (NaOCl) in aqueous solution.

PRIMARY REACTION:

    2 NH₃ + NaOCl → N₂H₄ + NaCl + H₂O
    
    ΔH = -30.5 kJ/mol (Exothermic)
    
    Molar masses:
    • NH₃: 17.03 g/mol
    • NaOCl: 74.44 g/mol
    • N₂H₄: 32.05 g/mol
    • NaCl: 58.44 g/mol
    • H₂O: 18.02 g/mol

STOICHIOMETRY:

    2 × 17.03g NH₃ + 74.44g NaOCl → 32.05g N₂H₄
    
    Mass ratio: 2.19:1 (NaOCl:NH₃)

SIDE REACTIONS (UNDESIRABLE):

    Excess hypochlorite:
    N₂H₄ + 2 NaOCl → N₂ + 2 NaCl + 2 H₂O
    
    This consumes product hydrazine!
    
    Chloramine formation:
    NH₃ + NaOCl → NH₂Cl + NaOH
    
    Chloramine is toxic and explosive!

CATALYST:

    Gelatin or glue is added as a catalyst/inhibitor:
    • Promotes primary reaction
    • Suppresses side reactions
    • Concentration: 0.1-0.5% by weight
```

### 1.2 实验装置图

```
┌─────────────────────────────────────────────────────────────────────┐
│              HYDRAZINE SYNTHESIS APPARATUS                          │
│                    [Laboratory Setup Diagram]                       │
└─────────────────────────────────────────────────────────────────────┘

                    ┌─────────────────────┐
                    │   CONDENSER         │
                    │   (Water cooled)    │
                    │   ┌─────────────┐   │
                    │   │  Cold Water │   │
                    │   │    IN       │   │
                    │   └──────┬──────┘   │
                    │          │          │
                    │   ┌──────┴──────┐   │
                    │   │   Glass     │   │
                    │   │   Coil      │   │
                    │   └──────┬──────┘   │
                    │          │          │
                    │   ┌──────┴──────┐   │
                    │   │  Cold Water │   │
                    │   │    OUT      │   │
                    │   └─────────────┘   │
                    └──────────┬──────────┘
                               │
                    ┌──────────▼──────────┐
                    │   REACTION VESSEL   │
                    │   (Round-bottom     │
                    │    flask, 2L)       │
                    │  ┌───────────────┐  │
                    │  │   Stir bar    │  │
                    │  │  (magnetic)   │  │
                    │  └───────────────┘  │
                    │  ┌───────────────┐  │
                    │  │  Thermometer  │  │
                    │  │  Port (T1)    │  │
                    │  └───────────────┘  │
                    │  ┌───────────────┐  │
                    │  │ Addition      │  │
                    │  │ Funnel (AF)   │  │
                    │  └───────────────┘  │
                    └──────────┬──────────┘
                               │
                    ┌──────────▼──────────┐
                    │   HEATING MANTLE    │
                    │   (Variable power)  │
                    │  ┌───────────────┐  │
                    │  │  Power: 0-500W│  │
                    │  │  Control:     │  │
                    │  │  Dial 1-10    │  │
                    │  └───────────────┘  │
                    └─────────────────────┘
                    
SUPPORT EQUIPMENT:

┌─────────────────────────────────────────────────────────────────────┐
│                                                                     │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐             │
│  │  BALANCE    │    │  pH METER   │    │  VENTILATION│             │
│  │  (0.01g)    │    │  (0-14 pH)  │    │  HOOD       │             │
│  │             │    │             │    │  (Required) │             │
│  └─────────────┘    └─────────────┘    └─────────────┘             │
│                                                                     │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐             │
│  │  SAFETY     │    │  EMERGENCY  │    │  CHEMICAL   │             │
│  │  GOGGLES    │    │  SHOWER     │    │  STORAGE    │             │
│  │  (Required) │    │  (Nearby)   │    │  CABINET    │             │
│  └─────────────┘    └─────────────┘    └─────────────┘             │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘

REAGENT STORAGE:

    ┌─────────────────────────────────────────────────────────────┐
    │  SHELF A: Ammonia Solution (NH₄OH)                          │
    │           Concentration: 28-30% (w/w)                       │
    │           Volume: 500mL                                     │
    │           Storage: Cool, ventilated area                    │
    │                                                             │
    │  SHELF B: Sodium Hypochlorite (NaOCl)                       │
    │           Concentration: 10-15% (commercial bleach)         │
    │           Volume: 1L                                        │
    │           Storage: Dark bottle, cool place                  │
    │           ⚠️  Degrades over time - check concentration      │
    │                                                             │
    │  SHELF C: Gelatin (catalyst)                                │
    │           Form: Powder                                      │
    │           Mass: 50g                                         │
    │                                                             │
    │  SHELF D: Distilled Water                                   │
    │           Volume: 5L                                        │
    └─────────────────────────────────────────────────────────────┘
```

### 1.3 操作流程与安全规程

```
┌─────────────────────────────────────────────────────────────────────┐
│              HYDRAZINE SYNTHESIS PROCEDURE                          │
│                    [CRITICAL - FOLLOW EXACTLY]                      │
│                    ⚠️  DEVIATION MAY BE FATAL ⚠️                    │
└─────────────────────────────────────────────────────────────────────┘

PRE-OPERATION SAFETY CHECK:

□ Personal Protective Equipment (MANDATORY)
  □ Chemical-resistant gloves (neoprene or butyl rubber)
  □ Safety goggles (indirect vent)
  □ Lab coat or chemical apron
  □ Closed-toe shoes
  
□ Ventilation
  □ Fume hood operational
  □ Airflow indicator: GREEN
  □ Backup ventilation: Available
  
□ Emergency Equipment
  □ Safety shower within 10 seconds reach
  □ Eyewash station functional
  □ Fire extinguisher (Class B, C) accessible
  □ Spill kit available
  
□ Reagent Verification
  □ NH₄OH concentration verified (<30%)
  □ NaOCl concentration verified (10-15%)
  □ No visible contamination
  □ Reagents at room temperature

SYNTHESIS PROCEDURE:

STEP 1: Catalyst Preparation
┌─────────────────────────────────────────────────────────────────────┐
│  1.1 Weigh 2.0g gelatin powder                                     │
│  1.2 Add to 100mL distilled water in beaker                        │
│  1.3 Heat gently (50°C) until dissolved                            │
│  1.4 Allow to cool to room temperature                             │
│  1.5 Set aside                                                     │
└─────────────────────────────────────────────────────────────────────┘

STEP 2: Ammonia Solution Preparation
┌─────────────────────────────────────────────────────────────────────┐
│  2.1 In reaction vessel, add 200mL distilled water                 │
│  2.2 Slowly add 100mL concentrated NH₄OH (28-30%)                  │
│      ⚠️  ADD ACID TO WATER, NEVER WATER TO ACID                    │
│  2.3 Add prepared gelatin solution                                 │
│  2.4 Place stir bar in vessel                                      │
│  2.5 Position vessel in heating mantle                             │
│  2.6 Connect condenser (water flow: bottom in, top out)            │
│  2.7 Start magnetic stirrer (medium speed)                         │
└─────────────────────────────────────────────────────────────────────┘

STEP 3: Temperature Control Setup
┌─────────────────────────────────────────────────────────────────────┐
│  3.1 Insert thermometer through port T1                            │
│  3.2 Set heating mantle to minimum power (setting 1)               │
│  3.3 Target temperature: 60-70°C                                   │
│  3.4 NEVER EXCEED 80°C - Decomposition risk!                       │
└─────────────────────────────────────────────────────────────────────┘

STEP 4: Hypochlorite Addition (CRITICAL STEP)
┌─────────────────────────────────────────────────────────────────────┐
│  4.1 Measure 150mL NaOCl solution (10-15%)                         │
│  4.2 Pour into addition funnel AF                                  │
│  4.3 Ensure addition funnel stopcock is CLOSED                     │
│  4.4 Position funnel above reaction vessel                         │
│                                                                     │
│  ⚠️  ADDITION RATE IS CRITICAL ⚠️                                  │
│                                                                     │
│  4.5 Open stopcock to SLOW DRIP (approximately 1 drop/second)      │
│  4.6 Addition time: 15-20 minutes                                  │
│  4.7 Monitor temperature continuously                              │
│  4.8 If temperature exceeds 75°C: STOP ADDITION immediately        │
│  4.9 Resume only when temperature drops to 65°C                    │
└─────────────────────────────────────────────────────────────────────┘

STEP 5: Reaction Completion
┌─────────────────────────────────────────────────────────────────────┐
│  5.1 After complete addition, maintain temperature at 65°C         │
│  5.2 Continue stirring for 30 minutes                              │
│  5.3 Turn off heating                                              │
│  5.4 Allow to cool to room temperature                             │
│  5.5 Product: Aqueous hydrazine solution (~3-5% w/w)               │
└─────────────────────────────────────────────────────────────────────┘

STEP 6: Product Transfer
┌─────────────────────────────────────────────────────────────────────┐
│  6.1 Product contains NaCl byproduct                               │
│  6.2 For fuel use, concentration must be increased                 │
│  6.3 Use fractional distillation or evaporation                    │
│  6.4 Target concentration: 50-70% hydrazine                        │
│  6.5 Store in approved container with vented cap                   │
│  6.6 Label clearly: "HYDRAZINE - TOXIC AND FLAMMABLE"              │
└─────────────────────────────────────────────────────────────────────┘

EMERGENCY PROCEDURES:

HYDRAZINE CONTACT:
□ Skin: Flush with water for 15 minutes
□ Eyes: Flush with water for 15 minutes, seek medical attention
□ Inhalation: Move to fresh air, administer oxygen if available
□ Ingestion: Do NOT induce vomiting, seek immediate medical help

FIRE:
□ Hydrazine fires are Class B (flammable liquid)
□ Use CO₂ or dry chemical extinguisher
□ Do NOT use water (spreads contamination)
□ Evacuate area if fire cannot be controlled

SPILL:
□ Small spill (<100mL): Absorb with vermiculite or sand
□ Large spill: Evacuate, call emergency response
□ Neutralize with dilute acid (acetic acid)
```

### 1.4 危险参数速查表

```
┌─────────────────────────────────────────────────────────────────────┐
│              HAZARD DATA - HYDRAZINE SYNTHESIS                      │
│                    ⚠️  CRITICAL SAFETY INFORMATION ⚠️               │
└─────────────────────────────────────────────────────────────────────┘

REAGENT HAZARDS:
┌────────────────┬────────────────────────────────────────────────────┐
│ Reagent        │ Hazards                                            │
├────────────────┼────────────────────────────────────────────────────┤
│ NH₄OH (28%)    │ • Corrosive (pH ~11.5)                            │
│                │ • Vapor irritates respiratory tract               │
│                │ • Contact causes skin/eye burns                   │
│                │ • NEVER mix with acids (releases toxic NH₃)       │
├────────────────┼────────────────────────────────────────────────────┤
│ NaOCl (bleach) │ • Corrosive (pH ~11)                              │
│                │ • Oxidizer - contact with organics may ignite     │
│                │ • Decomposes in light/heat (releases Cl₂)         │
│                │ • NEVER mix with acids (releases toxic Cl₂)       │
│                │ • NEVER mix with ammonia (forms explosive NCl₃)   │
├────────────────┼────────────────────────────────────────────────────┤
│ N₂H₄ (product) │ • Toxic (TLV: 0.01 ppm)                           │
│                │ • Flammable (flash point: 52°C)                   │
│                │ • Carcinogen (suspected)                          │
│                │ • Decomposes explosively at >200°C                │
│                │ • Reacts violently with oxidizers                 │
└────────────────┴────────────────────────────────────────────────────┘

CRITICAL TEMPERATURES:
┌────────────────┬────────────────────────────────────────────────────┐
│ Parameter      │ Value / Limit                                      │
├────────────────┼────────────────────────────────────────────────────┤
│ Reaction temp  │ 60-70°C (optimal)                                 │
│ Maximum temp   │ 80°C (DO NOT EXCEED)                              │
│ Flash point    │ 52°C (hydrazine)                                  │
│ Autoignition   │ 270°C (hydrazine in air)                          │
│ Decomposition  │ >200°C (explosive)                                │
│ Boiling point  │ 113°C (hydrazine)                                 │
└────────────────┴────────────────────────────────────────────────────┘

CONCENTRATION LIMITS:
┌────────────────┬────────────────────────────────────────────────────┐
│ Parameter      │ Limit                                              │
├────────────────┼────────────────────────────────────────────────────┤
│ NH₄OH max      │ 30% (higher = excessive vapor)                    │
│ NaOCl max      │ 15% (higher = excessive side reactions)           │
│ N₂H₄ target    │ 50-70% (for fuel use)                             │
│ N₂H₄ max safe  │ 100% (anhydrous - extreme hazard)                 │
└────────────────┴────────────────────────────────────────────────────┘

EXPOSURE LIMITS:
┌────────────────┬────────────────────────────────────────────────────┐
│ Substance      │ Exposure Limit                                     │
├────────────────┼────────────────────────────────────────────────────┤
│ NH₃ vapor      │ 25 ppm (8-hour TWA)                               │
│ NH₃ vapor      │ 35 ppm (STEL - 15 min)                            │
│ N₂H₄ vapor     │ 0.01 ppm (8-hour TWA)                             │
│ N₂H₄ skin      │ Avoid all contact                                 │
│ Cl₂ (if formed)│ 0.5 ppm (ceiling)                                 │
└────────────────┴────────────────────────────────────────────────────┘

INCOMPATIBLE MATERIALS:
□ Acids (all types) - releases toxic gases
□ Oxidizers (strong) - fire/explosion risk
□ Metals (copper, brass, bronze) - catalytic decomposition
□ Organic materials (with NaOCl) - fire risk
```

---

## 2. Jack视角 - 他的感知描述

### 2.1 场景描述

**[Jack的日志 - 第12小时]**

*化学实验室...这里让我毛骨悚然。到处都是玻璃瓶、奇怪的设备，还有一股...清洁用品和某种甜腻味道混合的气味。*

*中央有一个大桌子，上面放着一个圆底的玻璃瓶子，大概能装两升水。瓶子下面有一个加热的东西，像电热毯但是更厚。瓶子上面连着一个玻璃管，盘成螺旋状，然后通到另一个瓶子里。*

*旁边有一个小柜子，里面有几瓶东西。一个标着"AMMONIA"，透明的液体。另一个标着"SODIUM HYPOCHLORITE"，也是透明的但是有点黄。还有一个棕色的瓶子，上面标着...我看不清，标签褪色了。*

*墙上有一个大通风口，现在开着，发出嗡嗡声。旁边有一个红色的紧急淋浴头，还有一个小水池，标着"EYEWASH"。* 

*我找到了手套和护目镜。手套是蓝色的，很厚。护目镜让我看东西有点变形。*

### 2.2 情绪状态

```
[JACK STATUS]
┌─────────────────────────────────────────────────────────────────────┐
│  Stress Level: ██████████  95% (Extreme - Life threatening task)   │
│  Fear Level:   ██████████  90% (Terrified of chemicals)            │
│  Confidence:   ░░░░░░░░░░  2%  (Virtually none)                    │
│  Trust:        ████████░░  75% (High - only hope)                  │
└─────────────────────────────────────────────────────────────────────┘
```

**Jack的内心独白：**

> "这些东西...你说它们是安全的，但是标签上写着'CORROSIVE'和'TOXIC'。我...我不想碰它们。"

> "那个圆底瓶子...如果它破了怎么办？这些玻璃看起来好薄。"

> "味道越来越重了。那个通风口真的有用吗？"

> "等一下...我听到什么声音。像是...嘶嘶声？从那个加热的东西传来的？"

> "我的手在抖。我控制不了。如果我洒了怎么办？"

### 2.3 他对玩家指令的理解

**当玩家说"量取100mL氨水"时：**

> "100mL...我找到了一个量杯，但是刻度是盎司和毫升都有。100mL是...大概这么多？"

**当玩家说"缓慢加入"时：**

> "缓慢...多慢算缓慢？一滴一滴？还是像细流一样？"

**当玩家说"监控温度"时：**

> "温度...有一个温度计插在瓶子里。现在显示...我看不清，水珠在玻璃上...大概60多？数字在跳。"

**当玩家说"如果温度超过75度立即停止"时：**

> "75度...现在是...68...69...70...上升得很快！我要停了吗？"

---

## 3. 核心交互循环

### 3.1 成功路径

```
┌─────────────────────────────────────────────────────────────────────┐
│                    SUCCESS PATH - HYDRAZINE SYNTHESIS               │
│                    ⚠️  NO MISTAKES ALLOWED ⚠️                       │
└─────────────────────────────────────────────────────────────────────┘

STEP 1: 安全准备
┌─────────────────────────────────────────────────────────────────────┐
│ Player: "先不要碰任何东西。确认安全设备。"                           │
│                                                                      │
│ Jack: "我找到了手套和护目镜...通风口在运转，有嗡嗡声。"              │
│                                                                      │
│ Player: "很好。找到紧急淋浴和洗眼器，确认它们的位置。"               │
│                                                                      │
│ Jack: "红色的淋浴头在左边，洗眼器在小水池那里。"                     │
│                                                                      │
│ Player: "现在开始准备。找到标着'GELATIN'的瓶子。"                    │
│                                                                      │
│ Jack: "找到了，棕色的瓶子，里面有一些粉末。"                         │
└─────────────────────────────────────────────────────────────────────┘

STEP 2: 催化剂准备
┌─────────────────────────────────────────────────────────────────────┐
│ Player: "我们需要2克明胶。找到天平。"                                │
│                                                                      │
│ Jack: "天平...找到了，电子的，上面显示0.00。"                        │
│                                                                      │
│ Player: "放一个称量纸上去，然后归零。"                               │
│                                                                      │
│ Jack: "好了，显示0.00。现在加明胶？"                                 │
│                                                                      │
│ Player: "一点一点加，直到显示2.00。"                                 │
│                                                                      │
│ Jack: "1.50...1.80...2.00！好了。"                                   │
│                                                                      │
│ Player: "现在把它倒进一个烧杯，加100mL蒸馏水。"                      │
│                                                                      │
│ Jack: "水...标着'DISTILLED WATER'的瓶子。100mL...好了。"             │
│                                                                      │
│ Player: "轻轻加热到50度，直到明胶溶解。不要太热。"                   │
│                                                                      │
│ Jack: "有一个小电热板...我调到低档...明胶在溶解了，变成透明的。"     │
└─────────────────────────────────────────────────────────────────────┘

STEP 3: 反应准备
┌─────────────────────────────────────────────────────────────────────┐
│ Player: "让明胶溶液冷却。同时准备反应瓶。                           │
│         在圆底瓶里加200mL蒸馏水。"                                   │
│                                                                      │
│ Jack: "200mL...倒进去了。"                                           │
│                                                                      │
│ Player: "现在找到氨水，标着'AMMONIA'或'NH4OH'。"                     │
│                                                                      │
│ Jack: "找到了，透明的瓶子，标着'AMMONIUM HYDROXIDE 28%'。"           │
│                                                                      │
│ Player: "小心地量取100mL，然后缓慢加入反应瓶。                       │
│         记住：永远把酸（或碱）加入水，而不是反过来。"                 │
│                                                                      │
│ Jack: "缓慢...我在倒...有白烟！"                                     │
│                                                                      │
│ Player: "正常的，是氨气。通风系统会处理。继续。"                     │
│                                                                      │
│ Jack: "倒完了。现在加明胶溶液？"                                     │
│                                                                      │
│ Player: "对，倒进去。然后放一个搅拌子在瓶子里，打开搅拌器。"         │
│                                                                      │
│ Jack: "搅拌子...那个小磁铁？放进去了。搅拌器...开了，在转。"         │
└─────────────────────────────────────────────────────────────────────┘

STEP 4: 关键步骤 - 次氯酸钠添加
┌─────────────────────────────────────────────────────────────────────┐
│ Player: "这是最关键的一步。找到次氯酸钠，标着'SODIUM HYPOCHLORITE'。 │
│         或者可能是'BLEACH'。"                                        │
│                                                                      │
│ Jack: "找到了，标着'SODIUM HYPOCHLORITE 12%'，瓶子有点黄。"          │
│                                                                      │
│ Player: "量取150mL。然后倒入那个有活塞的漏斗——应该是架在反应瓶上面的。│
│         "                                                           │
│                                                                      │
│ Jack: "150mL...倒进去了。漏斗...找到了，架好了。"                    │
│                                                                      │
│ Player: "现在确认活塞是关闭的。然后插入温度计。"                     │
│                                                                      │
│ Jack: "活塞关着。温度计...插进去了。现在显示...25度。"               │
│                                                                      │
│ Player: "打开加热，调到最低档。我们要把温度升到60-65度。"            │
│                                                                      │
│ Jack: "加热开了...温度在上升...40...50...55...60度了。"              │
│                                                                      │
│ Player: "好，现在可以开始添加了。慢慢打开活塞，让它一滴一滴地流。   │
│         大概每秒一滴。"                                              │
│                                                                      │
│ Jack: "一滴...一滴...温度在上升吗？62...63...64..."                  │
│                                                                      │
│ Player: "控制在65度以下。如果升得太快，关小活塞。"                   │
│                                                                      │
│ Jack: "65度了！我关小一点...64...63...好的，稳定了。"                │
│                                                                      │
│ [持续15-20分钟，玩家需要持续监控温度]                                 │
└─────────────────────────────────────────────────────────────────────┘

STEP 5: 完成与收获
┌─────────────────────────────────────────────────────────────────────┐
│ Player: "添加完成了？温度怎么样？"                                   │
│                                                                      │
│ Jack: "漏斗空了。温度在63度。"                                       │
│                                                                      │
│ Player: "保持加热和搅拌30分钟。然后关掉加热，让它冷却。"             │
│                                                                      │
│ [30分钟后]                                                           │
│                                                                      │
│ Jack: "冷却了。液体是...有点黄色的透明液体。"                        │
│                                                                      │
│ Player: "那就是肼溶液。现在需要浓缩。找到蒸馏装置或者...             │
│         看看有没有旋转蒸发器。"                                      │
│                                                                      │
│ Jack: "有一个玻璃装置，标着'ROTARY EVAPORATOR'。"                    │
│                                                                      │
│ Player: "把溶液倒进去，设置温度80度，慢慢蒸发掉大部分水。            │
│         我们需要大约50-60%的浓度。"                                  │
│                                                                      │
│ [蒸发完成后]                                                         │
│                                                                      │
│ Jack: "体积少了大概一半...液体变稠了一点。"                          │
│                                                                      │
│ [燃料合成完成]                                                        │
│ [PUZZLE COMPLETE - 高度危险操作成功]                                  │
└─────────────────────────────────────────────────────────────────────┘
```

### 3.2 失败分支（Game Over级别）

```
┌─────────────────────────────────────────────────────────────────────┐
│                    CRITICAL FAILURE BRANCHES                        │
│                    ⚠️  THESE RESULT IN GAME OVER ⚠️                 │
└─────────────────────────────────────────────────────────────────────┘

FAILURE A: 氨水与次氯酸钠直接混合（形成三氯化氮）
┌─────────────────────────────────────────────────────────────────────┐
│ Player: "直接把次氯酸钠倒进反应瓶，快点。"                           │
│                                                                      │
│ Jack: "直接倒？不是说要慢慢加吗？"                                   │
│                                                                      │
│ Player: "没时间了，直接倒！"                                         │
│                                                                      │
│ *Jack将150mL次氯酸钠一次性倒入含有氨水的反应瓶*                       │
│                                                                      │
│ *剧烈反应* *黄色气体产生* *液体变成浑浊黄色*                          │
│                                                                      │
│ Jack: "有黄色气体！液体在冒泡！温度飙升！"                           │
│                                                                      │
│ [结果：形成三氯化氮(NCl₃)，极其不稳定的爆炸性化合物]                  │
│ [后果：混合物在数秒内爆炸]                                            │
│ [GAME OVER - 化学爆炸]                                                │
│                                                                      │
│ 科学解释：                                                           │
│ NH₃ + 3 NaOCl → NCl₃ + 3 NaOH                                        │
│ NCl₃在常温下会自发爆炸分解                                           │
└─────────────────────────────────────────────────────────────────────┘

FAILURE B: 温度失控导致肼分解
┌─────────────────────────────────────────────────────────────────────┐
│ Jack: "温度...70度了...还在升...75...80..."                          │
│                                                                      │
│ Player: "继续观察，应该没事。"                                       │
│                                                                      │
│ Jack: "85度了！液体在剧烈沸腾！"                                     │
│                                                                      │
│ *温度继续上升*                                                        │
│                                                                      │
│ Jack: "90度！玻璃在震动！"                                           │
│                                                                      │
│ [结果：肼在高温下分解产生氮气和氢气]                                  │
│ [后果：气体压力导致容器爆炸]                                          │
│ [GAME OVER - 热爆炸]                                                  │
│                                                                      │
│ 科学解释：                                                           │
│ N₂H₄ → N₂ + 2 H₂ (at T > 200°C)                                      │
│ 分解是放热的，一旦开始会自我加速                                      │
└─────────────────────────────────────────────────────────────────────┘

FAILURE C: 肼蒸气吸入过量
┌─────────────────────────────────────────────────────────────────────┐
│ [通风系统故障或操作不当]                                              │
│                                                                      │
│ Jack: "味道...好重...头晕..."                                        │
│                                                                      │
│ Player: "继续操作，快完成了。"                                       │
│                                                                      │
│ Jack: "我...我看不清了..."                                           │
│                                                                      │
│ *Jack失去意识*                                                        │
│                                                                      │
│ [结果：肼蒸气中毒]                                                    │
│ [后果：如果没有立即救援，死亡]                                        │
│ [GAME OVER - 化学中毒]                                                │
│                                                                      │
│ 科学解释：                                                           │
│ 肼TLV (Threshold Limit Value): 0.01 ppm                              │
│ 100 ppm: 立即危险                                                     │
│ 症状：头晕、恶心、抽搐、肝/肾损伤                                     │
└─────────────────────────────────────────────────────────────────────┘

FAILURE D: 肼与金属催化剂接触爆炸
┌─────────────────────────────────────────────────────────────────────┐
│ Player: "用那个铜勺子搅拌一下。"                                     │
│                                                                      │
│ Jack: "铜勺子...找到了..."                                           │
│                                                                      │
│ *Jack将铜勺插入肼溶液*                                                │
│                                                                      │
│ *立即剧烈反应* *火花* *溶液开始冒烟*                                   │
│                                                                      │
│ Jack: "有火花！溶液在变热！"                                         │
│                                                                      │
│ [结果：铜催化肼分解]                                                  │
│ [后果：热失控导致爆炸]                                                │
│ [GAME OVER - 催化爆炸]                                                │
│                                                                      │
│ 科学解释：                                                           │
│ 铜、铜合金、重金属离子都会催化肼的分解                                │
│ 必须使用不锈钢或玻璃器具                                            │
└─────────────────────────────────────────────────────────────────────┘
```

### 3.3 容错机制（极其有限）

```
┌─────────────────────────────────────────────────────────────────────┐
│              LIMITED ERROR RECOVERY                                 │
│                    ⚠️  MOST ERRORS ARE FATAL ⚠️                     │
└─────────────────────────────────────────────────────────────────────┘

RECOVERABLE ERRORS:

1. 温度轻微超标 (70-75°C)
   Jack: "温度73度了！"
   Player: "立即停止加热，开大搅拌速度。"
   
   → 如果及时响应，可以恢复
   → 反应可能会有些副产物，但产品可用

2. 添加速度稍快
   Jack: "我在加了...比一滴一滴快一点..."
   Player: "慢下来，温度怎么样？"
   
   → 如果温度可控，可以继续
   → 可能会有更多副反应

3. 浓度计算错误（小误差）
   Player: "用了120mL次氯酸钠而不是150mL"
   
   → 产率降低，但仍能得到产品
   → 需要更多原料重新合成

IRRECOVERABLE ERRORS:

□ 任何两种反应物的直接接触（未稀释）
□ 温度超过80°C超过10秒
□ 通风系统失效后继续操作
□ 使用错误的容器材料（铜、橡胶等）
□ 没有防护装备的操作

JACK的自我保护极限:

即使信任度100%，Jack也会拒绝：
□ 在没有通风的情况下操作
□ 直接闻化学试剂
□ 用手直接接触任何试剂
□ 在没有护目镜的情况下操作

如果玩家坚持危险操作：
→ Jack会质疑
→ 如果玩家继续施压，Jack可能自行判断并停止
→ 信任度会急剧下降
```

---

## 4. 科学原理说明

### 4.1 肼合成的化学方程式

```
┌─────────────────────────────────────────────────────────────────────┐
│              CHEMISTRY OF HYDRAZINE SYNTHESIS                       │
└─────────────────────────────────────────────────────────────────────┘

RASCHIG PROCESS - DETAILED MECHANISM:

Step 1: Chloramine formation (fast)
    NH₃ + NaOCl → NH₂Cl + NaOH
    
    This is an equilibrium reaction.
    Chloramine (NH₂Cl) is unstable and reactive.

Step 2: Chloramine reacts with excess ammonia (rate-determining)
    NH₂Cl + NH₃ + NaOH → N₂H₄ + NaCl + H₂O
    
    Requires excess ammonia to proceed.
    Base (NaOH) catalyzes this step.

Overall Reaction:
    2 NH₃ + NaOCl → N₂H₄ + NaCl + H₂O

THERMODYNAMICS:

    ΔH°f values (kJ/mol):
    • NH₃ (aq): -80.3
    • NaOCl (aq): -347
    • N₂H₄ (aq): +50.6
    • NaCl (aq): -407
    • H₂O (l): -285.8
    
    ΔH°rxn = [50.6 + (-407) + (-285.8)] - [2(-80.3) + (-347)]
           = -642.2 - (-507.6)
           = -134.6 kJ/mol
    
    The reaction is EXOTHERMIC
    Heat must be removed to control temperature

SIDE REACTION - OXIDATION:

    If excess NaOCl is present:
    N₂H₄ + 2 NaOCl → N₂ + 2 NaCl + 2 H₂O
    
    This DESTROYS the product!
    
    Prevention: Use excess NH₃, add NaOCl slowly

DANGEROUS SIDE REACTION - NCl₃ FORMATION:

    If NH₃:NaOCl ratio < 1:1:
    NH₃ + 3 NaOCl → NCl₃ + 3 NaOH
    
    Nitrogen trichloride (NCl₃) is:
    • Highly explosive
    • Unstable at room temperature
    • Detonates on contact with organics
    
    Prevention: Always maintain excess ammonia

CATALYST ROLE OF GELATIN:

    Gelatin contains proteins that:
    1. Form a protective colloid around reaction intermediates
    2. Slow down the oxidation side reaction
    3. Promote the desired condensation reaction
    
    Mechanism: Protein molecules adsorb onto reaction intermediates,
    sterically hindering the approach of oxidizing species.
```

### 4.2 温度控制的热力学

```
┌─────────────────────────────────────────────────────────────────────┐
│              THERMAL CONTROL IN CHEMICAL REACTIONS                  │
└─────────────────────────────────────────────────────────────────────┘

HEAT BALANCE:

    Accumulation = Generation - Removal
    
    m × Cp × dT/dt = Q_rxn - Q_cooling
    
    Where:
    • m = mass of reaction mixture
    • Cp = heat capacity (~4.2 J/g°C for aqueous)
    • Q_rxn = heat generated by reaction
    • Q_cooling = heat removed by cooling

REACTION RATE TEMPERATURE DEPENDENCE:

    Arrhenius equation:
    k = A × exp(-Ea/RT)
    
    Where:
    • k = rate constant
    • A = pre-exponential factor
    • Ea = activation energy
    • R = gas constant (8.314 J/mol·K)
    • T = temperature (K)
    
    For every 10°C increase, rate approximately doubles

RUNAWAY REACTION CONDITIONS:

    Runaway occurs when:
    Q_rxn > Q_cooling_max
    
    Critical temperature (Tc):
    The temperature at which heat generation exceeds
    maximum heat removal capacity
    
    For hydrazine synthesis:
    • Tc ≈ 80-90°C (depending on scale)
    • Above Tc: exponential temperature rise
    • Result: thermal explosion

COOLING METHODS:

    1. Condenser cooling:
       Q = ṁ × Cp × ΔT
       
       Where ṁ = water flow rate
       
    2. Reaction vessel heat transfer:
       Q = U × A × ΔT
       
       Where:
       • U = overall heat transfer coefficient
       • A = heat transfer area
       • ΔT = temperature difference

TEMPERATURE CONTROL STRATEGY:

    • Maintain reaction temperature 10-20°C below Tc
    • Add reactant slowly (limits Q_rxn)
    • Ensure adequate cooling capacity
    • Monitor temperature continuously
    • Have emergency cooling ready
```

### 4.3 化学安全参数

```
┌─────────────────────────────────────────────────────────────────────┐
│              CHEMICAL SAFETY PARAMETERS                             │
└─────────────────────────────────────────────────────────────────────┘

FLASH POINT AND FLAMMABILITY:

    Flash point (T_flash): Lowest temperature at which vapor
    ignites in presence of ignition source
    
    Hydrazine: T_flash = 52°C (122°F)
    
    Flammability limits in air:
    • LEL (Lower Explosive Limit): 1.8% v/v
    • UEL (Upper Explosive Limit): 100% v/v
    
    Autoignition temperature: 270°C (518°F)

TOXICITY PARAMETERS:

    TLV-TWA (Threshold Limit Value - Time Weighted Average):
    Maximum concentration for 8-hour exposure
    
    Hydrazine: TLV-TWA = 0.01 ppm (0.013 mg/m³)
    
    IDLH (Immediately Dangerous to Life or Health):
    Hydrazine: 50 ppm
    
    LC50 (Lethal Concentration 50):
    Concentration that kills 50% of test animals
    
    Hydrazine (rat, 4-hour): 570 ppm

REACTIVITY HAZARDS:

    Incompatible materials:
    • Oxidizers: Violent reaction, fire risk
    • Acids: Forms explosive salts
    • Metals (Cu, Fe, Ni): Catalytic decomposition
    • Halogens: Forms explosive compounds
    
    Decomposition:
    • Onset: ~200°C
    • Products: N₂, H₂, NH₃
    • Heat of decomposition: -50 kJ/mol

PERSONAL PROTECTIVE EQUIPMENT:

    Respiratory:
    • Supplied air respirator (for >10 ppm)
    • Full-face respirator with organic vapor cartridge
    
    Skin:
    • Butyl rubber gloves (neoprene acceptable)
    • Chemical-resistant apron
    • Closed-toe shoes
    
    Eye:
    • Chemical splash goggles (indirect vent)
    • Face shield (for large quantities)

EMERGENCY RESPONSE:

    Exposure:
    • Inhalation: Remove to fresh air, oxygen if available
    • Skin: Flush with water 15+ minutes
    • Eyes: Flush with water 15+ minutes, seek medical help
    • Ingestion: Do NOT induce vomiting, seek immediate help
    
    Fire:
    • Use CO₂, dry chemical, or foam
    • Do NOT use water (spreads contamination)
    • Evacuate if fire uncontrollable
    
    Spill:
    • Small: Absorb with vermiculite/sand
    • Large: Evacuate, call hazmat team
    • Neutralize with dilute acetic acid
```

---

# 附录：设计总结

## 三个谜题的核心差异

```
┌─────────────────────────────────────────────────────────────────────┐
│              PUZZLE COMPARISON MATRIX                               │
└─────────────────────────────────────────────────────────────────────┘

                    Puzzle 1    Puzzle 2    Puzzle 3
                    (Air)       (Power)     (Fuel)
┌─────────────────────────────────────────────────────────────────────┐
│ Risk Level        Medium      High        Extreme                   │
│ Time Pressure     Moderate    High        Moderate                  │
│ Complexity        Medium      High        Very High                 │
│ Error Tolerance   High        Medium      None                      │
│ Scientific Field  Chemistry   Electrical  Chemistry                 │
│ Failure Recovery  Easy        Moderate    Impossible                │
│ Player Knowledge  Technical   Technical   Advanced                  │
│ Jack Fear Level   Low         Medium      Very High                 │
└─────────────────────────────────────────────────────────────────────┘

COGNITIVE GAP IN EACH PUZZLE:

Puzzle 1:
  Player knows: How the system works, what each component does
  Jack sees: "A gray canister with white stuff inside"
  Gap: Component identification, understanding function

Puzzle 2:
  Player knows: Electrical theory, safety procedures
  Jack sees: "A bunch of wires and switches"
  Gap: Color coding interpretation, sequence understanding

Puzzle 3:
  Player knows: Chemical reactions, safety protocols
  Jack sees: "Scary bottles and glassware"
  Gap: Everything - Jack is completely dependent on player guidance

SUCCESS METRICS:

Puzzle 1: System operational, CO2 levels dropping
Puzzle 2: Generator running, loads transferred
Puzzle 3: Fuel synthesized, no injuries or contamination
```

---

## 设计原则验证

```
┌─────────────────────────────────────────────────────────────────────┐
│              DESIGN PRINCIPLES CHECKLIST                            │
└─────────────────────────────────────────────────────────────────────┘

☑ 真实物理/化学原理
   • LiOH CO2吸收：NASA验证的反应
   • 三相电力系统：标准电气工程
   • 肼合成：Raschig工艺，工业应用

☑ 认知鸿沟设计
   • 玩家有知识，Jack有操作能力
   • 信息必须通过对话传递
   • Jack的描述可能不准确/不完整

☑ 高风险决策
   • 每个谜题都有时间压力
   • 错误选择有实际后果
   • 没有"完美"解决方案，只有"足够好"

☑ 容错机制
   • Jack会质疑危险指令
   • 小错误可以恢复
   • 大错误导致状态恶化而非立即结束
   • Puzzle 3除外（高风险化学品操作）

☑ 失败状态有意义
   • 失败不会简单Game Over
   • 状态恶化需要补救
   • 每次失败都提供学习机会

☑ 硬科幻风格
   • 所有技术基于现实
   • 公式和数据可查
   • 没有"魔法"解决方案
```

---

## 科学原理来源

### Puzzle 1 - 空气洗涤器
- NASA Technical Reports: CO2 Removal Systems for Spacecraft
- LiOH Reaction: 2 LiOH(s) + CO₂(g) → Li₂CO₃(s) + H₂O(g)
- Source: NASA CR 114604, "Chemical Pump Study"
- Application: ISS, Space Shuttle, Apollo missions

### Puzzle 2 - 电力系统
- Three-phase power: Standard electrical engineering
- Circuit protection: NEC (National Electrical Code)
- Battery systems: IEEE 485 standard
- Inverter efficiency: Industry standard 85-95%

### Puzzle 3 - 燃料合成
- Raschig Process: Industrial hydrazine synthesis
- Reaction: 2 NH₃ + NaOCl → N₂H₄ + NaCl + H₂O
- Source: Industrial & Engineering Chemistry
- Hazards: OSHA/NIOSH guidelines

---

**文档版本**: 1.0
**设计日期**: 2024
**分类**: 游戏设计文档 - 核心机制
**状态**: 完成

---

*"在极端环境下，知识就是生存的工具，而信任是唯一的货币。"*

