# Project: CARGO - 后端物理仿真系统设计文档
## The Physics State

---

## 1. GameState 完整数据结构

```json
{
  "metadata": {
    "simulation_tick": 0,
    "game_time_seconds": 0,
    "last_update_timestamp": "ISO8601",
    "scenario_id": "cargo_bay_decompression"
  },
  
  "environment": {
    "oxygen_level": 21.0,           // 百分比 0-100，地球大气约21%
    "temperature": 22.0,            // 摄氏度
    "pressure": 101.325,            // kPa，标准大气压
    "co2_level": 0.04,              // 百分比，地球大气约0.04%
    "radiation": 0.0,               // mSv/h，毫西弗每小时
    "humidity": 50.0,               // 百分比
    "volume": 500.0,                // m³，舱室容积
    "hull_integrity": 100.0,        // 船体完整性百分比
    "breaches": [                   // 破损点列表
      {
        "id": "breach_001",
        "location": "cargo_bay_section_3",
        "size_mm": 5.0,             // 破损孔径mm
        "is_sealed": false
      }
    ]
  },
  
  "power_system": {
    "main_bus": {
      "online": true,
      "voltage": 28.0,              // V，航天标准电压
      "current_draw": 15.0,         // A
      "max_capacity": 5000.0        // W
    },
    "backup_battery": {
      "charge_percent": 100.0,
      "capacity_wh": 2000.0,        // Wh
      "health": 100.0,              // 电池健康度
      "discharge_rate": 0.0,        // W
      "temperature": 25.0
    },
    "solar_panels": {
      "online": true,
      "efficiency": 85.0,           // 受灰尘/老化影响
      "angle_degrees": 45.0,
      "output_watts": 3500.0,
      "dust_coverage": 15.0         // 灰尘覆盖百分比
    },
    "circuit_breakers": {
      "life_support": true,
      "communications": true,
      "lighting": true,
      "auxiliary": true
    },
    "total_load": 3200.0            // W
  },
  
  "life_support": {
    "co2_scrubber": {
      "status": "on",               // off|on|broken|maintenance
      "filter_life_percent": 87.0,
      "scrub_rate": 0.5,            // %CO2/分钟
      "power_draw": 200.0           // W
    },
    "o2_generator": {
      "status": "on",
      "output_rate": 0.3,           // %O2/分钟
      "reservoir_pressure": 2000.0, // kPa
      "power_draw": 150.0
    },
    "heater": {
      "status": false,
      "target_temp": 22.0,
      "output_watts": 2000.0,
      "power_draw": 0.0
    },
    "air_circulation": {
      "status": true,
      "fan_speed": 50.0,            // 百分比
      "power_draw": 100.0
    },
    "humidity_control": {
      "status": "auto",
      "target_humidity": 50.0,
      "power_draw": 50.0
    }
  },
  
  "jack": {
    "location": "command_module",
    "health": 100.0,
    "status": "conscious",          // conscious|dizzy|unconscious|dead
    
    "vitals": {
      "heart_rate": 75,             // bpm
      "oxygen_saturation": 98.0,    // %
      "body_temperature": 37.0,     // °C
      "blood_pressure": "120/80",   // mmHg
      "respiration_rate": 16        // 次/分钟
    },
    
    "stress_level": 15.0,           // 0-100
    "fatigue": 20.0,                // 0-100
    "hydration": 85.0,              // 0-100
    "calories_remaining": 2000.0,   // kcal
    
    "inventory": [
      {
        "item_id": "emergency_o2",
        "name": "紧急氧气瓶",
        "quantity": 1,
        "charges": 3
      }
    ],
    
    "active_effects": [],           // 当前状态效果
    
    "suit": {
      "wearing": false,
      "oxygen_supply": 0.0,
      "integrity": 100.0
    }
  },
  
  "communications": {
    "signal_strength": 85.0,        // 0-100
    "antenna_angle": {
      "azimuth": 180.0,
      "elevation": 45.0
    },
    "transmitter": {
      "status": "on",
      "frequency": 145.8,           // MHz
      "power_watts": 10.0
    },
    "receiver": {
      "status": "on",
      "squelch": 0.3
    },
    "noise_level": 0.2,             // 0-1
    "last_contact_timestamp": "ISO8601"
  },
  
  "cargo_bay": {
    "door_status": "sealed",        // sealed|unsealed|open
    "pressure_equalized": true,
    "cargo_items": [],
    "structural_damage": 0.0        // 0-100
  },
  
  "events": {
    "active": [],
    "history": [],
    "pending_triggers": []
  }
}
```

---

## 2. 仿真规则引擎（伪代码）

### 2.1 核心仿真类

```python
class PhysicsSimulator:
    """
    Project: CARGO 物理仿真引擎
    时间步长: 1秒游戏时间 = 1秒真实时间 (1:1)
    更新频率: 每秒1次主要更新，关键系统每秒10次子更新
    """
    
    def __init__(self, initial_state):
        self.state = initial_state
        self.tick_rate = 1              # 主循环每秒1次
        self.sub_tick_rate = 10         # 关键系统每秒10次
        self.event_queue = []
        self.sensory_translator = SensoryTranslator()
        
    def simulation_step(self, delta_time=1.0):
        """主仿真步进"""
        
        # 1. 环境系统更新
        self.update_environment(delta_time)
        
        # 2. 电力系统更新
        self.update_power_system(delta_time)
        
        # 3. 生命维持系统更新
        self.update_life_support(delta_time)
        
        # 4. Jack生理状态更新
        self.update_jack_physiology(delta_time)
        
        # 5. 通信系统更新
        self.update_communications(delta_time)
        
        # 6. 事件检测与触发
        self.detect_and_trigger_events()
        
        # 7. 生成感官反馈
        sensory_feedback = self.sensory_translator.translate(self.state)
        
        self.state.metadata.simulation_tick += 1
        self.state.metadata.game_time_seconds += delta_time
        
        return sensory_feedback
```

### 2.2 规则1：氧气消耗与平衡

```python
def update_environment(self, delta_time):
    """环境系统更新 - 氧气、CO2、气压"""
    
    env = self.state.environment
    jack = self.state.jack
    life_support = self.state.life_support
    
    # ===== 氧气消耗计算 =====
    # 基础消耗: 静息状态约0.25L/分钟 = 0.00417L/秒
    # 在标准状态下，0.00417L = 0.00000417m³
    # 舱室容积500m³，氧气占比21%
    # 每秒氧气消耗百分比 = (0.00417/500) * 100 / 21 * 21 = 0.000834%
    
    base_o2_consumption_rate = 0.000834  # %/秒 (静息状态)
    
    # 活动强度修正
    activity_multipliers = {
        "resting": 1.0,
        "light_work": 1.5,
        "moderate_work": 2.5,
        "heavy_work": 4.0,
        "panic": 3.0
    }
    
    # 压力修正: 低氧环境下呼吸加快
    pressure_factor = 1.0
    if env.pressure < 70:  # kPa
        pressure_factor = 1.5
    elif env.pressure < 50:
        pressure_factor = 2.0
    elif env.pressure < 30:
        pressure_factor = 3.0
    
    # Jack当前活动状态（可从指令历史推断）
    jack_activity = self.infer_jack_activity()
    activity_mult = activity_multipliers.get(jack_activity, 1.0)
    
    # 总氧气消耗率
    o2_consumption = base_o2_consumption_rate * activity_mult * pressure_factor
    
    # ===== CO2产生计算 =====
    # 呼吸商RQ ≈ 0.8，即消耗1L O2产生0.8L CO2
    co2_production = o2_consumption * 0.8
    
    # ===== 氧气补充（来自O2发生器）=====
    o2_replenishment = 0.0
    if life_support.o2_generator.status == "on" and self.has_power():
        o2_replenishment = life_support.o2_generator.output_rate / 60.0  # 转换为%/秒
    
    # ===== CO2清除（来自洗涤器）=====
    co2_scrubbing = 0.0
    if life_support.co2_scrubber.status == "on" and self.has_power():
        co2_scrubbing = life_support.co2_scrubber.scrub_rate / 60.0
    
    # ===== 气压变化（破损泄漏）=====
    pressure_loss = 0.0
    for breach in env.breaches:
        if not breach.is_sealed:
            # 使用简化版的气流公式: Q = C * A * sqrt(2 * ΔP / ρ)
            # C: 流量系数 (~0.6)
            # A: 孔面积 (m²)
            # ΔP: 内外压差 (Pa)
            # ρ: 空气密度 (~1.225 kg/m³ at STP)
            
            breach_area = math.pi * (breach.size_mm / 2000) ** 2  # mm转m，半径
            pressure_diff_pa = (env.pressure - 0) * 1000  # kPa转Pa，外部假设真空
            air_density = 1.225 * (env.pressure / 101.325) * (273.15 / (env.temperature + 273.15))
            
            flow_coefficient = 0.6
            if pressure_diff_pa > 0:
                mass_flow_rate = flow_coefficient * breach_area * math.sqrt(2 * pressure_diff_pa * air_density)
                # 转换为压力损失 (简化模型)
                pressure_loss_rate = (mass_flow_rate / (env.volume * air_density)) * env.pressure * 100
                pressure_loss += pressure_loss_rate * delta_time
    
    # ===== 应用所有变化 =====
    # 氧气变化
    env.oxygen_level += (o2_replenishment - o2_consumption) * delta_time
    env.oxygen_level = clamp(env.oxygen_level, 0.0, 100.0)
    
    # CO2变化
    env.co2_level += (co2_production - co2_scrubbing) * delta_time
    env.co2_level = clamp(env.co2_level, 0.0, 100.0)
    
    # 气压变化（泄漏导致）
    env.pressure -= pressure_loss
    env.pressure = max(env.pressure, 0.0)
    
    # 气压也受温度影响 (理想气体定律: P ∝ T)
    if env.temperature != self.previous_temperature:
        temp_ratio = (env.temperature + 273.15) / (self.previous_temperature + 273.15)
        env.pressure *= temp_ratio
    
    # 记录历史温度
    self.previous_temperature = env.temperature
```

### 2.3 规则2：温度变化

```python
def update_temperature(self, delta_time):
    """温度变化计算"""
    
    env = self.state.environment
    power = self.state.power_system
    life_support = self.state.life_support
    
    # ===== 热源 =====
    # 1. 人体散热 (Jack)
    # 基础代谢产热: ~100W
    # 活动产热: 轻工作+50W，重工作+200W
    jack_activity = self.infer_jack_activity()
    jack_heat_output = 100.0
    if jack_activity == "light_work":
        jack_heat_output += 50
    elif jack_activity == "moderate_work":
        jack_heat_output += 150
    elif jack_activity == "heavy_work":
        jack_heat_output += 300
    
    # 2. 设备产热
    equipment_heat = power.total_load * 0.1  # 假设10%电能转为热能
    
    # 3. 加热器
    heater_output = 0.0
    if life_support.heater.status and self.has_power():
        heater_output = life_support.heater.output_watts
    
    total_heat_input = jack_heat_output + equipment_heat + heater_output
    
    # ===== 热损失 =====
    # 1. 向太空辐射 ( Stefan-Boltzmann定律简化 )
    # P = εσA(T⁴ - T_space⁴)
    # 假设: ε=0.8, A=200m² (外表面积), T_space=3K
    
    stefan_boltzmann = 5.67e-8  # W/m²K⁴
    emissivity = 0.8
    surface_area = 200.0  # m²
    space_temp = 3.0      # K
    
    temp_kelvin = env.temperature + 273.15
    radiation_loss = emissivity * stefan_boltzmann * surface_area * (
        temp_kelvin**4 - space_temp**4
    )
    
    # 2. 船体热传导损失
    # Q = k * A * ΔT / d
    # 假设隔热层k=0.02 W/mK, d=0.1m
    conductivity = 0.02
    thickness = 0.1
    temp_diff = env.temperature - (-270)  # 假设外部接近绝对零度
    conduction_loss = conductivity * surface_area * temp_diff / thickness
    
    # 3. 空气循环带走的热量 (如果开启)
    circulation_loss = 0.0
    if life_support.air_circulation.status:
        circulation_loss = 100.0  # W
    
    total_heat_loss = radiation_loss + conduction_loss + circulation_loss
    
    # ===== 净热变化 =====
    # Q = mcΔT => ΔT = Q / (mc)
    # 空气: m = ρV = 1.225 * 500 = 612.5 kg
    # 空气比热容 c = 1005 J/kgK
    
    air_mass = 1.225 * env.volume  # kg
    air_specific_heat = 1005       # J/kgK
    
    net_heat = total_heat_input - total_heat_loss
    temperature_change = (net_heat * delta_time) / (air_mass * air_specific_heat)
    
    env.temperature += temperature_change
```

### 2.4 规则3：气压变化（密封破损详细模型）

```python
def calculate_pressure_drop_detailed(self, delta_time):
    """
    基于理想气体定律的气压变化详细模型
    PV = nRT
    
    当气体泄漏时:
    - 摩尔数n减少
    - 如果温度T恒定，P与n成正比
    - 泄漏速率取决于孔径大小和压差
    """
    
    env = self.state.environment
    
    # 初始条件
    P = env.pressure * 1000  # 转换为Pa
    V = env.volume           # m³
    T = env.temperature + 273.15  # K
    R = 8.314               # J/(mol·K)
    
    # 当前气体摩尔数
    n = (P * V) / (R * T)
    
    # 计算总泄漏速率
    total_molar_loss_rate = 0.0
    
    for breach in env.breaches:
        if not breach.is_sealed:
            # 孔面积 (m²)
            A = math.pi * (breach.size_mm / 1000 / 2) ** 2
            
            # 外部压力 (假设真空)
            P_out = 0.0
            
            # 临界压力比 (对于空气，γ ≈ 1.4)
            gamma = 1.4
            critical_ratio = (2 / (gamma + 1)) ** (gamma / (gamma - 1))
            
            # 判断是否阻塞流(choked flow)
            pressure_ratio = P_out / P if P > 0 else 1.0
            
            if pressure_ratio < critical_ratio:
                # 阻塞流 (音速)
                # 质量流率 = C_d * A * P * sqrt(γ / (R_specific * T)) * ((γ+1)/2)^(-(γ+1)/(2(γ-1)))
                R_specific = 287.05  # J/(kg·K) for air
                Cd = 0.6  # 流量系数
                
                mass_flow = Cd * A * P * math.sqrt(
                    gamma / (R_specific * T)
                ) * ((gamma + 1) / 2) ** (-(gamma + 1) / (2 * (gamma - 1)))
                
            else:
                # 亚音速流
                # 使用简化公式
                rho = P / (R_specific * T)  # 密度
                delta_P = P - P_out
                mass_flow = Cd * A * math.sqrt(2 * rho * delta_P)
            
            # 转换为摩尔流率
            molar_mass_air = 0.0289647  # kg/mol
            molar_flow = mass_flow / molar_mass_air
            
            total_molar_loss_rate += molar_flow
    
    # 更新摩尔数
    n_new = n - total_molar_loss_rate * delta_time
    n_new = max(n_new, 0.0)
    
    # 计算新压力
    P_new = (n_new * R * T) / V
    
    # 更新状态
    env.pressure = P_new / 1000  # 转换回kPa
    
    # 氧气比例保持不变（假设均匀混合泄漏）
    # 除非O2发生器或洗涤器在工作
```

### 2.5 规则4：电路负载与电力管理

```python
def update_power_system(self, delta_time):
    """电力系统更新"""
    
    power = self.state.power_system
    life_support = self.state.life_support
    comms = self.state.communications
    
    # ===== 计算总负载 =====
    total_load = 0.0
    
    # 生命维持系统负载
    if life_support.co2_scrubber.status == "on":
        total_load += life_support.co2_scrubber.power_draw
    if life_support.o2_generator.status == "on":
        total_load += life_support.o2_generator.power_draw
    if life_support.heater.status:
        total_load += life_support.heater.power_draw
    if life_support.air_circulation.status:
        total_load += life_support.air_circulation.power_draw
    if life_support.humidity_control.status in ["on", "auto"]:
        total_load += life_support.humidity_control.power_draw
    
    # 通信系统负载
    if comms.transmitter.status == "on":
        total_load += comms.transmitter.power_watts * 10  # 发射时功耗
    if comms.receiver.status == "on":
        total_load += 20.0  # 接收机功耗
    
    # 照明负载
    if power.circuit_breakers.lighting:
        total_load += 200.0
    
    # 基础系统负载
    total_load += 100.0  # 传感器、计算机等
    
    power.total_load = total_load
    
    # ===== 电源管理 =====
    solar_output = 0.0
    if power.solar_panels.online:
        # 太阳能输出受角度和灰尘影响
        angle_factor = math.cos(math.radians(abs(power.solar_panels.angle_degrees - 45)))
        dust_factor = 1.0 - (power.solar_panels.dust_coverage / 100.0) * 0.5
        efficiency_factor = power.solar_panels.efficiency / 100.0
        
        solar_output = (power.solar_panels.output_watts * 
                       angle_factor * dust_factor * efficiency_factor)
    
    # 判断电源状态
    if solar_output >= total_load:
        # 太阳能充足
        power.main_bus.online = True
        excess_power = solar_output - total_load
        
        # 给电池充电
        if power.backup_battery.charge_percent < 100.0:
            charge_rate = min(excess_power, 500.0)  # 最大充电功率500W
            charge_amount = (charge_rate * delta_time) / (power.backup_battery.capacity_wh * 3600) * 100
            power.backup_battery.charge_percent = min(
                100.0, 
                power.backup_battery.charge_percent + charge_amount
            )
        
        power.backup_battery.discharge_rate = 0.0
        
    else:
        # 太阳能不足，需要电池补充
        deficit = total_load - solar_output
        
        if power.backup_battery.charge_percent > 0:
            # 电池供电
            power.backup_battery.discharge_rate = deficit
            discharge_amount = (deficit * delta_time) / (power.backup_battery.capacity_wh * 3600) * 100
            power.backup_battery.charge_percent = max(
                0.0,
                power.backup_battery.charge_percent - discharge_amount
            )
            power.main_bus.online = True
        else:
            # 电池耗尽，系统断电
            power.main_bus.online = False
            self.trigger_power_loss()
    
    # ===== 过载检测 =====
    if total_load > power.main_bus.max_capacity:
        self.trigger_circuit_overload()
```

### 2.6 规则5：Jack生理状态更新

```python
def update_jack_physiology(self, delta_time):
    """Jack生理状态更新"""
    
    jack = self.state.jack
    env = self.state.environment
    
    # ===== 血氧饱和度计算 =====
    # 基于环境氧分压
    # 氧分压 = 总压 × 氧浓度
    o2_partial_pressure = env.pressure * (env.oxygen_level / 100.0)
    
    # 血氧饱和度模型 (简化版氧解离曲线)
    # 正常: P_O2 = 21kPa, SpO2 = 98%
    # 危险: P_O2 < 8kPa, SpO2 < 85%
    # 致命: P_O2 < 5kPa, SpO2 < 70%
    
    if o2_partial_pressure >= 15:
        target_spo2 = 98.0
    elif o2_partial_pressure >= 10:
        target_spo2 = 90.0 + (o2_partial_pressure - 10) * 1.6
    elif o2_partial_pressure >= 5:
        target_spo2 = 75.0 + (o2_partial_pressure - 5) * 3.0
    else:
        target_spo2 = max(40.0, o2_partial_pressure * 15)
    
    # 平滑过渡
    jack.vitals.oxygen_saturation = lerp(
        jack.vitals.oxygen_saturation,
        target_spo2,
        0.1 * delta_time
    )
    
    # ===== 心率变化 =====
    # 低氧导致心率加快
    base_hr = 75
    if jack.vitals.oxygen_saturation < 90:
        base_hr += (90 - jack.vitals.oxygen_saturation) * 3
    
    # 压力导致心率加快
    base_hr += jack.stress_level * 0.5
    
    # 温度影响
    if env.temperature > 30:
        base_hr += (env.temperature - 30) * 2
    elif env.temperature < 10:
        base_hr += (10 - env.temperature) * 1.5
    
    jack.vitals.heart_rate = lerp(
        jack.vitals.heart_rate,
        base_hr,
        0.05 * delta_time
    )
    
    # ===== 体温调节 =====
    # 环境温度影响
    if env.temperature > 35:
        # 过热
        jack.vitals.body_temperature += 0.001 * (env.temperature - 35) * delta_time
    elif env.temperature < 15:
        # 过冷
        jack.vitals.body_temperature -= 0.001 * (15 - env.temperature) * delta_time
    else:
        # 正常范围内自我调节
        jack.vitals.body_temperature = lerp(
            jack.vitals.body_temperature,
            37.0,
            0.01 * delta_time
        )
    
    # ===== 压力水平更新 =====
    # 基于环境威胁
    threat_level = 0.0
    if jack.vitals.oxygen_saturation < 90:
        threat_level += 20.0
    if env.temperature > 40 or env.temperature < 0:
        threat_level += 15.0
    if jack.vitals.heart_rate > 120:
        threat_level += 10.0
    if env.pressure < 50:
        threat_level += 25.0
    
    jack.stress_level = min(100.0, jack.stress_level + threat_level * 0.01 * delta_time)
    
    # 压力自然衰减
    if threat_level == 0:
        jack.stress_level = max(0.0, jack.stress_level - 2.0 * delta_time)
    
    # ===== 状态判定 =====
    if jack.vitals.oxygen_saturation < 60 or jack.vitals.body_temperature < 30:
        jack.status = "dead"
    elif jack.vitals.oxygen_saturation < 75 or jack.stress_level > 90:
        jack.status = "unconscious"
    elif jack.vitals.oxygen_saturation < 85 or jack.stress_level > 70:
        jack.status = "dizzy"
    else:
        jack.status = "conscious"
```

### 2.7 规则6：通信系统

```python
def update_communications(self, delta_time):
    """通信系统更新"""
    
    comms = self.state.communications
    power = self.state.power_system
    
    # 检查电源
    if not power.main_bus.online:
        comms.transmitter.status = "off"
        comms.receiver.status = "off"
        return
    
    # 信号强度计算
    # 基于天线指向、距离、功率
    
    # 理想天线角度 (指向地球)
    ideal_azimuth = 180.0
    ideal_elevation = 45.0
    
    azimuth_error = abs(comms.antenna_angle.azimuth - ideal_azimuth)
    elevation_error = abs(comms.antenna_angle.elevation - ideal_elevation)
    
    # 指向精度影响
    pointing_factor = max(0.0, 1.0 - (azimuth_error + elevation_error) / 180.0)
    
    # 功率影响
    power_factor = min(1.0, comms.transmitter.power_watts / 10.0)
    
    # 基础信号强度 (假设距离固定)
    base_signal = 80.0
    
    comms.signal_strength = base_signal * pointing_factor * power_factor
    
    # 噪声水平 (来自太阳辐射等)
    comms.noise_level = 0.1 + (100 - comms.signal_strength) / 200.0
```

---

## 3. 时间步进与事件触发机制

### 3.1 仿真循环架构

```python
class SimulationLoop:
    """
    Project: CARGO 仿真循环
    
    时间比例: 1:1 (1秒游戏时间 = 1秒真实时间)
    更新层级:
    - 帧更新 (60 FPS): 仅UI渲染
    - 仿真更新 (1 Hz): 主要物理计算
    - 关键系统更新 (10 Hz): 气压、氧气等快速变化系统
    - 事件检测 (1 Hz): 阈值检查
    """
    
    def __init__(self, simulator):
        self.simulator = simulator
        self.running = False
        self.last_update_time = 0
        
        # 子系统更新频率
        self.update_frequencies = {
            "main": 1.0,        # 1 Hz
            "critical": 10.0,   # 10 Hz
            "events": 1.0,      # 1 Hz
            "sensory": 0.2      # 每5秒一次
        }
        
        self.accumulators = {k: 0.0 for k in self.update_frequencies}
        
    def run(self, delta_real_time):
        """运行仿真步进"""
        
        # 1:1 时间比例
        delta_game_time = delta_real_time
        
        # 累加器更新
        for key in self.accumulators:
            self.accumulators[key] += delta_game_time
        
        # 关键系统快速更新 (气压、氧气)
        if self.accumulators["critical"] >= 1.0 / self.update_frequencies["critical"]:
            sub_delta = 1.0 / self.update_frequencies["critical"]
            self.simulator.update_critical_systems(sub_delta)
            self.accumulators["critical"] -= sub_delta
        
        # 主系统更新
        if self.accumulators["main"] >= 1.0 / self.update_frequencies["main"]:
            main_delta = 1.0 / self.update_frequencies["main"]
            self.simulator.simulation_step(main_delta)
            self.accumulators["main"] -= main_delta
        
        # 事件检测
        if self.accumulators["events"] >= 1.0 / self.update_frequencies["events"]:
            self.simulator.detect_and_trigger_events()
            self.accumulators["events"] -= 1.0 / self.update_frequencies["events"]
        
        # 感官反馈
        if self.accumulators["sensory"] >= 1.0 / self.update_frequencies["sensory"]:
            feedback = self.simulator.sensory_translator.translate(self.simulator.state)
            self.send_to_llm(feedback)
            self.accumulators["sensory"] -= 1.0 / self.update_frequencies["sensory"]


class EventManager:
    """事件管理器 - 阈值检测与触发"""
    
    def __init__(self):
        self.triggers = []
        self.triggered_events = set()
        
    def register_trigger(self, trigger):
        """注册事件触发器"""
        self.triggers.append(trigger)
        
    def check_triggers(self, state):
        """检查所有触发器"""
        events = []
        
        for trigger in self.triggers:
            event_id = trigger.check(state)
            if event_id and event_id not in self.triggered_events:
                events.append(event_id)
                self.triggered_events.add(event_id)
                
                # 可重复触发的事件
                if trigger.repeatable:
                    self.triggered_events.discard(event_id)
        
        return events


class ThresholdTrigger:
    """阈值触发器"""
    
    def __init__(self, name, condition, event_id, repeatable=False):
        self.name = name
        self.condition = condition      # lambda state: bool
        self.event_id = event_id
        self.repeatable = repeatable
        self.last_state = False
        
    def check(self, state):
        current = self.condition(state)
        
        # 边缘触发: false -> true
        if current and not self.last_state:
            self.last_state = current
            return self.event_id
        
        self.last_state = current
        return None


# 预定义触发器示例
DEFAULT_TRIGGERS = [
    # 氧气相关
    ThresholdTrigger(
        "oxygen_critical",
        lambda s: s.environment.oxygen_level < 10,
        "event_oxygen_critical",
        repeatable=False
    ),
    ThresholdTrigger(
        "oxygen_low",
        lambda s: s.environment.oxygen_level < 15,
        "event_oxygen_low",
        repeatable=False
    ),
    
    # 气压相关
    ThresholdTrigger(
        "pressure_dropping_fast",
        lambda s: s.environment.pressure < 70 and len(s.environment.breaches) > 0,
        "event_pressure_drop",
        repeatable=False
    ),
    
    # 温度相关
    ThresholdTrigger(
        "temp_extreme_high",
        lambda s: s.environment.temperature > 50,
        "event_overheat",
        repeatable=False
    ),
    ThresholdTrigger(
        "temp_extreme_low",
        lambda s: s.environment.temperature < -10,
        "event_hypothermia",
        repeatable=False
    ),
    
    # 电力相关
    ThresholdTrigger(
        "power_loss",
        lambda s: not s.power_system.main_bus.online,
        "event_power_loss",
        repeatable=True
    ),
    
    # Jack状态
    ThresholdTrigger(
        "jack_unconscious",
        lambda s: s.jack.status == "unconscious",
        "event_jack_unconscious",
        repeatable=False
    ),
    
    # 通信相关
    ThresholdTrigger(
        "signal_lost",
        lambda s: s.communications.signal_strength < 10,
        "event_signal_lost",
        repeatable=True
    ),
]
```

### 3.2 状态变化批处理

```python
class StateChangeBatcher:
    """
    状态变化批处理 - 减少LLM调用频率
    累积相关变化，一次性生成描述
    """
    
    def __init__(self, batch_interval=5.0):
        self.batch_interval = batch_interval
        self.pending_changes = []
        self.last_batch_time = 0
        
    def record_change(self, change_type, old_value, new_value, severity="info"):
        """记录状态变化"""
        self.pending_changes.append({
            "type": change_type,
            "old": old_value,
            "new": new_value,
            "severity": severity,
            "timestamp": time.time()
        })
        
    def should_flush(self, current_time):
        """检查是否应该发送批次"""
        return (current_time - self.last_batch_time >= self.batch_interval and 
                len(self.pending_changes) > 0)
        
    def flush(self):
        """刷新批次，生成综合描述"""
        if not self.pending_changes:
            return None
        
        # 按严重程度和类型分组
        critical = [c for c in self.pending_changes if c["severity"] == "critical"]
        warning = [c for c in self.pending_changes if c["severity"] == "warning"]
        info = [c for c in self.pending_changes if c["severity"] == "info"]
        
        # 生成综合提示词
        prompt_parts = []
        
        if critical:
            prompt_parts.append("【紧急】" + self.summarize_changes(critical))
        if warning:
            prompt_parts.append("【警告】" + self.summarize_changes(warning))
        if info:
            prompt_parts.append(self.summarize_changes(info))
        
        self.pending_changes = []
        self.last_batch_time = time.time()
        
        return " ".join(prompt_parts)
        
    def summarize_changes(self, changes):
        """概括变化列表"""
        # 按类型分组
        by_type = {}
        for c in changes:
            by_type.setdefault(c["type"], []).append(c)
        
        summaries = []
        for change_type, type_changes in by_type.items():
            if len(type_changes) == 1:
                c = type_changes[0]
                summaries.append(f"{change_type}: {c['old']:.1f}→{c['new']:.1f}")
            else:
                # 多个同类型变化，取范围
                values = [c["new"] for c in type_changes]
                summaries.append(f"{change_type}: {min(values):.1f}~{max(values):.1f}")
        
        return "; ".join(summaries)
```

---

## 4. 感官转译层 (Sensory Translator)

### 4.1 感官转译器核心类

```python
class SensoryTranslator:
    """
    感官转译层 - 将数值状态转化为人类感知描述
    
    设计原则:
    1. 渐进式描述 - 从轻微到严重
    2. 多感官覆盖 - 视觉、听觉、触觉、本体感觉
    3. 情绪映射 - 将物理状态转化为心理感受
    4. 上下文感知 - 根据Jack的状态调整描述
    """
    
    def __init__(self):
        self.mappings = SENSORY_MAPPINGS
        self.previous_state = None
        self.description_history = []
        
    def translate(self, current_state):
        """
        将当前状态转化为感官描述
        返回: 用于LLM的提示词字符串
        """
        descriptions = []
        
        # 环境感官
        env_desc = self.translate_environment(current_state)
        if env_desc:
            descriptions.append(env_desc)
        
        # Jack生理感官
        jack_desc = self.translate_jack_physiology(current_state)
        if jack_desc:
            descriptions.append(jack_desc)
        
        # 系统状态感官
        system_desc = self.translate_system_status(current_state)
        if system_desc:
            descriptions.append(system_desc)
        
        # 合并并生成最终提示词
        return self.compile_prompt(descriptions, current_state)
        
    def translate_environment(self, state):
        """环境状态感官转译"""
        env = state.environment
        parts = []
        
        # 温度感知
        temp_desc = self.translate_temperature(env.temperature)
        if temp_desc:
            parts.append(temp_desc)
        
        # 氧气感知
        o2_desc = self.translate_oxygen(env.oxygen_level, env.pressure)
        if o2_desc:
            parts.append(o2_desc)
        
        # 气压感知
        pressure_desc = self.translate_pressure(env.pressure)
        if pressure_desc:
            parts.append(pressure_desc)
        
        # CO2感知
        co2_desc = self.translate_co2(env.co2_level)
        if co2_desc:
            parts.append(co2_desc)
        
        return " ".join(parts) if parts else None
        
    def translate_temperature(self, temp):
        """温度感官转译"""
        
        if temp > 50:
            return random.choice([
                "空气烫得让你无法呼吸，金属表面烫伤了你的皮肤。",
                "你感觉自己像被扔进了烤箱，汗水瞬间蒸发。",
                "热浪让你视线模糊，每一次呼吸都像在吸入火焰。"
            ])
        elif temp > 40:
            return random.choice([
                "汗水不断流进你的眼睛，呼吸的空气是热的。",
                "你感觉头晕目眩，皮肤被烤得发红。",
                "舱内的温度让你想起沙漠正午。"
            ])
        elif temp > 35:
            return random.choice([
                "你出了很多汗，衣服黏在身上。",
                "空气闷热，让你有些喘不过气。",
                "你感觉像是在一个没有空调的房间里。"
            ])
        elif temp < -20:
            return random.choice([
                "你的手指已经失去知觉，呼吸在空气中凝结成白雾。",
                "寒冷刺骨，你感觉血液都要凝固了。",
                "金属表面粘住了你的皮肤，像被烧伤一样疼。"
            ])
        elif temp < -10:
            return random.choice([
                "你不停地发抖，牙齿打颤。",
                "手指僵硬，操作变得困难。",
                "寒冷让你的思维变慢了。"
            ])
        elif temp < 5:
            return random.choice([
                "你感觉有点冷，抱紧了自己。",
                "呼出的气变成了白雾。",
                "你需要活动一下来保持体温。"
            ])
        
        return None
        
    def translate_oxygen(self, o2_level, pressure):
        """氧气感官转译"""
        
        o2_partial_pressure = pressure * (o2_level / 100.0)
        
        if o2_partial_pressure < 5:
            return random.choice([
                "你的视野迅速变窄，周围的一切都在远离你...",
                "你感到极度窒息，拼命想吸入更多空气...",
                "意识在迅速流失，你感到前所未有的恐惧..."
            ])
        elif o2_partial_pressure < 8:
            return random.choice([
                "你的视野边缘开始变黑，手脚发麻。",
                "你感到剧烈的头痛，思维变得混乱。",
                "心跳快得像要跳出胸膛，但你依然感到窒息。"
            ])
        elif o2_partial_pressure < 12:
            return random.choice([
                "你觉得有点困，刚才你说什么来着？",
                "你感到轻微的头晕，注意力难以集中。",
                "呼吸变得急促，但你总觉得吸不够气。"
            ])
        elif o2_partial_pressure < 16:
            return random.choice([
                "你感觉稍微有点气短。",
                "需要深呼吸才能感到满足。",
                "空气感觉"稀薄"了一些。"
            ])
        
        return None
        
    def translate_pressure(self, pressure):
        """气压感官转译"""
        
        if pressure < 30:
            return random.choice([
                "你的耳膜剧痛，感觉快要爆裂了。",
                "体内的气体在膨胀，你感到浑身不适。",
                "减压病的症状开始出现，关节隐隐作痛。"
            ])
        elif pressure < 50:
            return random.choice([
                "你的耳朵嗡嗡作响，需要不断吞咽来缓解。",
                "你感到胸闷，像是被什么东西压着。",
                "液体开始从鼻腔渗出，这是压力变化的迹象。"
            ])
        elif pressure < 70:
            return random.choice([
                "你感到耳朵有些不适，像是坐飞机时的感觉。",
                "舱内有一些奇怪的声音，可能是结构在应力下呻吟。"
            ])
        
        return None
        
    def translate_co2(self, co2_level):
        """CO2感官转译"""
        
        if co2_level > 5:
            return random.choice([
                "你感到强烈的恶心和头痛，空气闻起来酸臭。",
                "呼吸变得困难，你感到恐慌。",
                "你的判断力明显下降，动作变得不协调。"
            ])
        elif co2_level > 3:
            return random.choice([
                "你感到头痛和嗜睡，空气感觉"沉重"。",
                "你的心跳加快，试图补偿呼吸的不足。",
                "你感到有些烦躁和不安。"
            ])
        elif co2_level > 1:
            return random.choice([
                "空气感觉有些闷热，不够清新。",
                "你感到轻微的困倦。"
            ])
        
        return None
        
    def translate_jack_physiology(self, state):
        """Jack生理状态感官转译"""
        
        jack = state.jack
        parts = []
        
        # 压力水平
        if jack.stress_level > 80:
            parts.append("你的心跳快得像要爆炸，手在不受控制地颤抖。")
        elif jack.stress_level > 60:
            parts.append("你感到焦虑和紧张，手心全是汗。")
        elif jack.stress_level > 40:
            parts.append("你感到有些不安，心跳比平时快。")
        
        # 疲劳
        if jack.fatigue > 80:
            parts.append("你累极了，眼皮沉重得像铅块。")
        elif jack.fatigue > 60:
            parts.append("你感到很疲惫，需要休息。")
        
        return " ".join(parts) if parts else None
        
    def translate_system_status(self, state):
        """系统状态感官转译"""
        
        parts = []
        power = state.power_system
        
        # 电力状态
        if not power.main_bus.online:
            parts.append("舱内一片漆黑，只有应急灯发出微弱的绿光。")
        elif power.backup_battery.charge_percent < 20:
            parts.append("你听到电池发出低沉的警告蜂鸣声。")
        
        # 通风声音
        if state.life_support.air_circulation.status:
            parts.append("通风系统发出稳定的嗡嗡声。")
        else:
            parts.append("舱内异常安静，通风系统的声音消失了。")
        
        return " ".join(parts) if parts else None
        
    def compile_prompt(self, descriptions, state):
        """编译最终提示词"""
        
        # 基础模板
        template = """【环境感知】
{environment}

【身体状态】
{physiology}

【系统状态】
{systems}

【当前数据】
- 温度: {temp:.1f}°C
- 气压: {pressure:.1f} kPa
- 氧气: {o2:.1f}%
- CO2: {co2:.2f}%
- 心率: {hr} bpm
- 血氧: {spo2:.1f}%
"""
        
        return template.format(
            environment=descriptions[0] if len(descriptions) > 0 else "环境正常。",
            physiology=descriptions[1] if len(descriptions) > 1 else "身体状况良好。",
            systems=descriptions[2] if len(descriptions) > 2 else "系统运行正常。",
            temp=state.environment.temperature,
            pressure=state.environment.pressure,
            o2=state.environment.oxygen_level,
            co2=state.environment.co2_level,
            hr=state.jack.vitals.heart_rate,
            spo2=state.jack.vitals.oxygen_saturation
        )
```

---

## 5. 状态-提示词映射表

### 5.1 温度变化系列

```python
TEMPERATURE_PROMPTS = {
    # 过热状态
    "temp_extreme_high": {
        "threshold": 50,
        "severity": "critical",
        "player_prompt": "舱内温度已达到{temp}°C，你感觉自己像被扔进了烤箱。汗水瞬间蒸发，皮肤被烤得发红。",
        "jack_response": "热死我了！这里像个烤箱！我快被烤熟了！",
        "physiological_effects": ["脱水", "热衰竭", "意识模糊"],
        "llm_context": "Jack处于极度危险的高温环境中，他的生命体征正在迅速恶化。"
    },
    
    "temp_high": {
        "threshold": 40,
        "severity": "warning",
        "player_prompt": "舱内温度{temp}°C，汗水不断流进你的眼睛，呼吸的空气是热的。",
        "jack_response": "太热了...我需要水...",
        "physiological_effects": ["大量出汗", "心跳加速"],
        "llm_context": "Jack感到很不舒服，高温让他难以集中注意力。"
    },
    
    "temp_warm": {
        "threshold": 35,
        "severity": "info",
        "player_prompt": "舱内有些闷热，你出了很多汗，衣服黏在身上。",
        "jack_response": "有点热，但还能忍受。",
        "physiological_effects": ["出汗增加"],
        "llm_context": "环境温度略高，Jack感到有些不适。"
    },
    
    # 过冷状态
    "temp_extreme_low": {
        "threshold": -20,
        "severity": "critical",
        "player_prompt": "舱内温度{temp}°C，你的手指已经失去知觉，呼吸在空气中凝结成白雾。寒冷刺骨，你感觉血液都要凝固了。",
        "jack_response": "我...我动不了了...好冷...",
        "physiological_effects": ["冻伤", "低体温症", "意识丧失"],
        "llm_context": "Jack处于极度危险的低温环境中，他的生命体征正在迅速恶化，可能失去意识。"
    },
    
    "temp_low": {
        "threshold": -10,
        "severity": "warning",
        "player_prompt": "舱内温度{temp}°C，你不停地发抖，牙齿打颤。手指僵硬，操作变得困难。",
        "jack_response": "太冷了...我在发抖...",
        "physiological_effects": ["寒战", "动作迟缓"],
        "llm_context": "Jack感到很冷，他的动作变得笨拙，思维也变慢了。"
    },
    
    "temp_cool": {
        "threshold": 5,
        "severity": "info",
        "player_prompt": "舱内有点冷，你呼出的气变成了白雾。",
        "jack_response": "有点凉，我需要活动一下。",
        "physiological_effects": ["轻微发抖"],
        "llm_context": "环境温度略低，Jack感到有些凉意。"
    }
}
```

### 5.2 氧气变化系列

```python
OXYGEN_PROMPTS = {
    "o2_fatal": {
        "threshold_pp": 5,  # kPa 氧分压
        "severity": "critical",
        "player_prompt": "你的视野迅速变窄，周围的一切都在远离你...意识在迅速流失...",
        "jack_response": "...救...救命...",
        "physiological_effects": ["意识丧失", "脑损伤", "死亡"],
        "llm_context": "Jack正在经历致命的缺氧，他即将失去意识，需要立即干预。",
        "time_to_unconscious": "30-60秒"
    },
    
    "o2_critical": {
        "threshold_pp": 8,
        "severity": "critical",
        "player_prompt": "你的视野边缘开始变黑，手脚发麻。你感到剧烈的头痛，思维变得混乱。心跳快得像要跳出胸膛。",
        "jack_response": "我...我觉得...有点困...头好痛...",
        "physiological_effects": ["判断力严重下降", "协调能力丧失", "即将昏迷"],
        "llm_context": "Jack处于严重缺氧状态，他的认知能力和运动能力都在快速下降。",
        "time_to_unconscious": "2-3分钟"
    },
    
    "o2_dangerous": {
        "threshold_pp": 12,
        "severity": "warning",
        "player_prompt": "你觉得有点困，刚才你说什么来着？你感到轻微的头晕，注意力难以集中。呼吸变得急促。",
        "jack_response": "嗯？你刚才说什么？我有点...头晕...",
        "physiological_effects": ["判断力下降", "反应变慢", "嗜睡"],
        "llm_context": "Jack感到缺氧的早期症状，他的反应变慢，需要提醒他专注。",
        "time_to_critical": "5-10分钟"
    },
    
    "o2_low": {
        "threshold_pp": 16,
        "severity": "info",
        "player_prompt": "你感觉稍微有点气短，需要深呼吸才能感到满足。空气感觉"稀薄"了一些。",
        "jack_response": "空气好像不太够...我需要多吸几口。",
        "physiological_effects": ["呼吸频率增加"],
        "llm_context": "Jack注意到氧气不足，但他还能正常思考和行动。",
        "time_to_dangerous": "15-30分钟"
    },
    
    "o2_normal": {
        "threshold_pp": 19,
        "severity": "none",
        "player_prompt": "呼吸正常。",
        "jack_response": "",
        "physiological_effects": [],
        "llm_context": "氧气水平正常，Jack呼吸顺畅。"
    }
}
```

### 5.3 气压变化系列

```python
PRESSURE_PROMPTS = {
    "pressure_vacuum": {
        "threshold": 6.3,  # kPa，水的沸点压力
        "severity": "critical",
        "player_prompt": "舱内气压已接近真空！你的体液开始沸腾，耳膜剧痛，眼球凸出。这是致命的！",
        "jack_response": "啊——！！！",
        "physiological_effects": ["体液沸腾", "瞬间昏迷", "死亡"],
        "llm_context": "舱内已接近真空，Jack正在经历最痛苦的死亡方式之一。",
        "survival_time": "15-30秒"
    },
    
    "pressure_critical": {
        "threshold": 30,
        "severity": "critical",
        "player_prompt": "舱内气压{pressure}kPa，你的耳膜剧痛，感觉快要爆裂了。体内的气体在膨胀，你感到浑身不适。减压病的症状开始出现。",
        "jack_response": "我的耳朵！好痛！我...我感觉身体在膨胀...",
        "physiological_effects": ["耳膜损伤", "减压病", "氮气麻醉"],
        "llm_context": "气压极低，Jack面临严重的生理危险，需要立即增压或进入压力服。",
        "survival_time": "1-2分钟"
    },
    
    "pressure_dangerous": {
        "threshold": 50,
        "severity": "warning",
        "player_prompt": "舱内气压{pressure}kPa，你的耳朵嗡嗡作响，需要不断吞咽来缓解。你感到胸闷，像是被什么东西压着。",
        "jack_response": "我的耳朵...一直在响...感觉胸口很闷...",
        "physiological_effects": ["耳压不适", "胸闷"],
        "llm_context": "气压明显偏低，Jack感到明显的不适，但暂时没有生命危险。",
        "survival_time": "可生存，但不舒适"
    },
    
    "pressure_low": {
        "threshold": 70,
        "severity": "info",
        "player_prompt": "舱内气压{pressure}kPa，你感到耳朵有些不适，像是坐飞机时的感觉。舱内有一些奇怪的声音。",
        "jack_response": "气压在下降...我听到一些奇怪的声音...",
        "physiological_effects": ["轻微耳压不适"],
        "llm_context": "气压正在下降，Jack注意到了异常，但感觉还好。"
    }
}
```

### 5.4 电路异常系列

```python
POWER_PROMPTS = {
    "power_total_loss": {
        "trigger": "main_bus.offline",
        "severity": "critical",
        "player_prompt": "舱内突然一片漆黑！所有系统都停止了，只有应急灯发出微弱的绿光。你听到结构在寂静中发出轻微的咔嗒声。",
        "jack_response": "怎么回事？！灯灭了！所有东西都停了！",
        "consequences": ["生命维持停止", "通信中断", "温度失控", "氧气耗尽加速"],
        "llm_context": "完全断电，Jack陷入黑暗，所有系统离线，情况极其危急。"
    },
    
    "power_overload": {
        "trigger": "load > capacity",
        "severity": "critical",
        "player_prompt": "你听到电路发出刺耳的过载声，闻到一股焦糊味。某个地方的保险丝烧断了。",
        "jack_response": "什么味道？！电路在冒烟！",
        "consequences": ["断路器跳闸", "部分系统离线", "火灾风险"],
        "llm_context": "电路严重过载，Jack闻到了危险的味道，需要立即减少负载。"
    },
    
    "power_short_circuit": {
        "trigger": "short_detected",
        "severity": "critical",
        "player_prompt": "一道刺眼的电火花闪过，伴随着噼啪声。你闻到臭氧和烧焦塑料的味道。",
        "jack_response": "电火花！电路短路了！",
        "consequences": ["局部火灾", "设备损坏", "触电风险"],
        "llm_context": "发生短路，Jack看到了电火花，必须小心处理。"
    },
    
    "power_battery_low": {
        "threshold": 20,
        "severity": "warning",
        "player_prompt": "你听到电池发出低沉的警告蜂鸣声，电量指示灯变成了红色。",
        "jack_response": "电池快没电了...我们需要太阳能板或者减少用电。",
        "consequences": ["备用电力即将耗尽"],
        "llm_context": "电池电量低，Jack意识到需要节约用电或寻找替代电源。"
    },
    
    "power_fluctuation": {
        "trigger": "voltage_unstable",
        "severity": "info",
        "player_prompt": "灯光忽明忽暗，你听到设备发出不稳定的嗡嗡声。",
        "jack_response": "电力不太稳定...灯在闪。",
        "consequences": ["设备可能重启", "数据丢失风险"],
        "llm_context": "电力不稳定，Jack注意到了异常，但情况尚可控。"
    }
}
```

### 5.5 CO2浓度系列

```python
CO2_PROMPTS = {
    "co2_toxic": {
        "threshold": 5.0,  # %
        "severity": "critical",
        "player_prompt": "你感到强烈的恶心和头痛，空气闻起来酸臭。呼吸变得困难，你感到恐慌。你的判断力明显下降，动作变得不协调。",
        "jack_response": "我...我想吐...头好痛...空气...好臭...",
        "physiological_effects": ["呼吸性酸中毒", "意识模糊", "昏迷风险"],
        "llm_context": "CO2浓度已达到危险水平，Jack正在经历CO2中毒，需要立即通风或启动洗涤器。"
    },
    
    "co2_high": {
        "threshold": 3.0,
        "severity": "warning",
        "player_prompt": "你感到头痛和嗜睡，空气感觉"沉重"。你的心跳加快，试图补偿呼吸的不足。你感到有些烦躁和不安。",
        "jack_response": "我感觉...有点困...头有点痛...",
        "physiological_effects": ["嗜睡", "头痛", "心率增加"],
        "llm_context": "CO2浓度偏高，Jack感到不适，洗涤器可能需要维护或更换滤芯。"
    },
    
    "co2_elevated": {
        "threshold": 1.0,
        "severity": "info",
        "player_prompt": "空气感觉有些闷热，不够清新。你感到轻微的困倦。",
        "jack_response": "空气...有点闷...",
        "physiological_effects": ["轻微不适"],
        "llm_context": "CO2浓度略高，Jack注意到了空气质量的变化。"
    }
}
```

### 5.6 Jack状态系列

```python
JACK_STATUS_PROMPTS = {
    "jack_dead": {
        "trigger": "status == dead",
        "severity": "game_over",
        "player_prompt": "Jack没有了反应。他的眼睛睁着，但已经失去了生命的光彩。",
        "jack_response": "[无响应]",
        "llm_context": "Jack已经死亡，游戏结束。",
        "game_state": "GAME_OVER"
    },
    
    "jack_unconscious": {
        "trigger": "status == unconscious",
        "severity": "critical",
        "player_prompt": "Jack倒下了，没有了意识。他的呼吸微弱而不规律。",
        "jack_response": "[昏迷中，偶尔发出微弱的呻吟]",
        "llm_context": "Jack已经失去意识，如果不立即干预，他将死亡。玩家需要通过指令直接操作系统。",
        "time_to_death": "3-5分钟"
    },
    
    "jack_dizzy": {
        "trigger": "status == dizzy",
        "severity": "warning",
        "player_prompt": "Jack摇摇晃晃，眼神迷离。他说话含糊不清，动作不协调。",
        "jack_response": "我...我有点头晕...你刚才说什么？",
        "llm_context": "Jack处于半清醒状态，他的反应变慢，判断力下降，需要立即帮助。"
    },
    
    "jack_panic": {
        "trigger": "stress_level > 90",
        "severity": "warning",
        "player_prompt": "Jack陷入恐慌！他呼吸急促，眼睛瞪大，声音颤抖。",
        "jack_response": "我们要死了！我们要死了！我该怎么办？！告诉我该怎么办！",
        "llm_context": "Jack处于恐慌状态，他无法理性思考，需要玩家用冷静的语气安抚他。"
    },
    
    "jack_stressed": {
        "trigger": "stress_level > 60",
        "severity": "info",
        "player_prompt": "Jack明显很紧张，他的手在微微颤抖，说话比平时快。",
        "jack_response": "情况...不太妙...我们该怎么办？",
        "llm_context": "Jack感到压力，但他还能听从指令，需要玩家的鼓励和明确的指示。"
    },
    
    "jack_normal": {
        "trigger": "status == conscious AND stress < 40",
        "severity": "none",
        "player_prompt": "Jack看起来状态不错，注意力集中。",
        "jack_response": "我准备好了，告诉我该做什么。",
        "llm_context": "Jack状态良好，可以执行复杂的指令。"
    }
}
```

---

## 6. LLM接口设计

### 6.1 提示词生成器

```python
class LLMPromptGenerator:
    """
    LLM提示词生成器
    将仿真状态转化为自然语言描述，供LLM生成Jack的对话
    """
    
    def __init__(self, sensory_translator):
        self.translator = sensory_translator
        
    def generate_prompt(self, state, player_input=None, event_triggered=None):
        """
        生成完整的LLM提示词
        
        Args:
            state: 当前游戏状态
            player_input: 玩家输入（如果有）
            event_triggered: 触发的事件（如果有）
        
        Returns:
            完整的LLM提示词字符串
        """
        
        parts = []
        
        # 1. 系统提示词（角色定义）
        parts.append(self.get_system_prompt())
        
        # 2. 当前状态描述
        parts.append(self.translator.translate(state))
        
        # 3. 事件描述（如果有）
        if event_triggered:
            parts.append(self.get_event_description(event_triggered))
        
        # 4. 玩家指令（如果有）
        if player_input:
            parts.append(f"\n【玩家指令】\n{player_input}")
        
        # 5. 输出格式要求
        parts.append(self.get_output_format())
        
        return "\n".join(parts)
        
    def get_system_prompt(self):
        """系统提示词 - 角色定义"""
        return """【系统设定】
你是Jack，一名被困在受损货运飞船"CARGO-7"上的宇航员。
飞船正在经历减压、电力故障和生命维持系统失效。

你的性格特点：
- 专业但会恐慌：你是受过训练的宇航员，但面对死亡威胁时会害怕
- 依赖玩家：玩家是任务控制中心，你是执行者
- 会抱怨但服从：你会表达不满和恐惧，但最终会执行命令
- 有幽默感：在压力之下会用黑色幽默缓解紧张
- 会提供反馈：你会描述执行动作时的感受和观察

重要规则：
1. 永远不要直接读出状态数据（如"氧气15%"），而是描述感受
2. 根据你的压力水平和身体状况调整语气和用词
3. 如果状态危险，表达恐惧和 urgency
4. 如果执行动作，描述动作过程和结果
5. 保持第一人称视角
"""
    
    def get_event_description(self, event_id):
        """获取事件描述"""
        event_descriptions = {
            "event_oxygen_critical": "【紧急事件】氧气水平已降至危险水平！",
            "event_pressure_drop": "【紧急事件】气压正在快速下降！",
            "event_power_loss": "【紧急事件】主电源已断开！",
            "event_overheat": "【紧急事件】舱内温度正在危险上升！",
            "event_signal_lost": "【警告】通信信号丢失！",
        }
        return event_descriptions.get(event_id, f"【事件】{event_id}")
    
    def get_output_format(self):
        """输出格式要求"""
        return """
【输出要求】
以Jack的身份回应，包含：
1. 你对当前情况的感受（基于环境感知）
2. 对身体状况的描述（基于生理数据）
3. 对玩家指令的回应（如果有）
4. 你的建议或疑问（可选）

语气应该符合你的压力水平和身体状况。
"""


# 使用示例
def example_usage():
    """使用示例"""
    
    # 初始化
    simulator = PhysicsSimulator(initial_state)
    translator = SensoryTranslator()
    prompt_generator = LLMPromptGenerator(translator)
    
    # 仿真步进
    while game_running:
        # 执行物理计算
        feedback = simulator.simulation_step(delta_time)
        
        # 生成LLM提示词
        prompt = prompt_generator.generate_prompt(
            state=simulator.state,
            player_input=latest_player_command,
            event_triggered=latest_event
        )
        
        # 发送给LLM
        jack_response = llm.generate(prompt)
        
        # 显示给玩家
        display_to_player(jack_response)
```

---

## 7. 物理公式参考

### 7.1 氧气消耗
```
基础消耗: 0.25 L/min (静息)
活动修正: 1x-4x
压力修正: 1x-3x

氧分压 = 总压 × 氧浓度
正常范围: 19-21 kPa
危险阈值: < 12 kPa
致命阈值: < 5 kPa
```

### 7.2 温度变化
```
热输入: 人体(100-400W) + 设备(10%负载) + 加热器
热损失: 辐射 + 传导 + 对流

辐射: P = εσA(T⁴ - T_space⁴)
传导: Q = kAΔT/d

温度变化: ΔT = Q/(mc)
空气: m = ρV, c = 1005 J/kgK
```

### 7.3 气压泄漏
```
理想气体定律: PV = nRT

阻塞流质量流率:
m = Cd × A × P × sqrt(γ/(R×T)) × ((γ+1)/2)^(-(γ+1)/(2(γ-1)))

亚音速流:
m = Cd × A × sqrt(2ρΔP)
```

### 7.4 电路负载
```
功率: P = VI
电池放电: %/s = (P × t) / (容量 × 3600) × 100
过载检测: 负载 > 额定容量
```

---

## 8. 总结

本文档定义了Project: CARGO的完整物理仿真系统：

1. **GameState数据结构**: 包含环境、电力、生命维持、Jack状态、通信等完整状态
2. **仿真规则引擎**: 氧气、温度、气压、电路等核心物理规则的伪代码实现
3. **时间步进机制**: 1:1时间比例，分层更新频率，事件触发系统
4. **感官转译层**: 将数值状态转化为人类感知描述
5. **状态-提示词映射**: 完整的阈值-描述映射表
6. **LLM接口**: 提示词生成器设计

所有物理公式基于真实科学原理，但进行了游戏性简化，确保"逻辑自洽的游戏性"。
