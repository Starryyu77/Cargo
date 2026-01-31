# AI驱动的火星生存游戏前端开发计划

## 1. 项目概述
基于AI驱动的火星生存游戏白皮书和游戏状态机，创建一个具有复古CRT显示器风格的交互式前端界面。游戏核心是解决电力系统谜题，玩家需要通过正确的操作序列来恢复电力。

## 2. 技术架构

### 2.1 前端技术栈
- **框架**: React 18 + TypeScript
- **构建工具**: Vite
- **样式**: Tailwind CSS 3.x
- **状态管理**: React Hooks (useState, useReducer)
- **动画**: CSS Animations + React Transition Group

### 2.2 项目结构
```
src/
├── components/
│   ├── CRTMonitor/          # CRT显示器外壳组件
│   │   ├── CRTMonitor.tsx
│   │   ├── CRTMonitor.css   # CRT特效样式
│   │   └── Scanlines.tsx    # 扫描线效果
│   ├── GameMonitors/        # 三个显示器组件
│   │   ├── LeftMonitor.tsx   # 左侧手册/图表显示器
│   │   ├── CenterMonitor.tsx # 中间终端显示器
│   │   └── RightMonitor.tsx  # 右侧顾问聊天显示器
│   ├── Terminal/
│   │   ├── Terminal.tsx     # 终端界面
│   │   ├── TerminalInput.tsx # 命令输入
│   │   └── TerminalOutput.tsx # 命令输出
│   ├── Advisors/
│   │   ├── AdvisorPanel.tsx # 顾问面板
│   │   └── AdvisorMessage.tsx # 顾问消息
│   └── GameUI/
│       ├── GameHeader.tsx   # 游戏标题
│       ├── StatusBar.tsx    # 状态栏
│       └── GameControls.tsx # 游戏控制
├── hooks/
│   ├── useGameState.ts      # 游戏状态管理
│   ├── useTerminal.ts       # 终端逻辑
│   └── useCRTEffect.ts      # CRT效果
├── utils/
│   ├── gameLogic.ts         # 游戏逻辑处理
│   ├── commandParser.ts     # 命令解析器
│   └── crtEffects.ts        # CRT效果工具
├── types/
│   └── game.types.ts        # TypeScript类型定义
└── App.tsx
```

## 3. 组件设计

### 3.1 CRT显示器外壳 (CRTMonitor)
```tsx
interface CRTMonitorProps {
  children: React.ReactNode;
  className?: string;
  glowIntensity?: number;
  scanlineOpacity?: number;
}
```

**功能**:
- 创建复古CRT显示器外观
- 添加发光效果和扫描线
- 支持自定义发光强度和扫描线透明度

### 3.2 左侧显示器 (LeftMonitor)
**显示内容**:
- 标题: "MANUAL: POWER SYSTEMS"
- 电力系统图表/接线图
- 底部说明文字

**Tailwind样式**:
```css
.crt-green {
  @apply text-green-400 bg-black font-mono;
  text-shadow: 0 0 2px #00ff00, 0 0 5px #00ff00;
}

.crt-glow {
  box-shadow: 
    inset 0 0 20px rgba(0, 255, 0, 0.1),
    0 0 10px rgba(0, 255, 0, 0.2);
}
```

### 3.3 中间显示器 (CenterMonitor - 终端)
**功能**:
- 显示游戏对话和系统消息
- 命令输入和解析
- 游戏状态反馈

**组件结构**:
```tsx
const CenterMonitor: React.FC = () => {
  const { messages, addMessage } = useTerminal();
  const { gameState, processCommand } = useGameState();

  return (
    <CRTMonitor>
      <div className="crt-green h-full p-4">
        <TerminalOutput messages={messages} />
        <TerminalInput onCommand={processCommand} />
      </div>
    </CRTMonitor>
  );
};
```

### 3.4 右侧显示器 (RightMonitor - 顾问系统)
**功能**:
- 显示两个AI顾问的建议
- 实时更新基于游戏状态的建议

**数据结构**:
```tsx
interface AdvisorMessage {
  id: string;
  advisor: 'A' | 'B';
  message: string;
  timestamp: number;
}
```

## 4. 游戏状态管理

### 4.1 状态定义 (基于game_state.py)
```tsx
enum GameState {
  START = 'START',           // 初始状态，盒子关闭
  BOX_OPEN = 'BOX_OPEN',     // 盒子打开，可见电线
  RED_CONNECTED = 'RED_CONNECTED',    // 红线连接到A端子
  BLUE_CONNECTED = 'BLUE_CONNECTED',   // 蓝线连接到B端子
  POWER_ON = 'POWER_ON',     // 成功状态
  SHORT_CIRCUIT = 'SHORT_CIRCUIT'    // 失败状态
}

interface GameContext {
  currentState: GameState;
  history: GameState[];
  attempts: number;
  startTime: number;
}
```

### 4.2 命令处理
```tsx
const commandActions = {
  'open box': () => transitionTo(GameState.BOX_OPEN),
  'connect red to a': () => handleWireConnection('red', 'A'),
  'connect blue to b': () => handleWireConnection('blue', 'B'),
  'connect red to b': () => handleShortCircuit(),
  'connect blue to a': () => handleShortCircuit(),
  'flip switch': () => handleSwitchFlip()
};
```

## 5. CRT视觉效果

### 5.1 扫描线效果
```css
@keyframes scanline {
  0% { transform: translateY(-100%); }
  100% { transform: translateY(100vh); }
}

.scanline {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 2px;
  background: linear-gradient(
    to bottom,
    rgba(0, 255, 0, 0) 0%,
    rgba(0, 255, 0, 0.3) 50%,
    rgba(0, 255, 0, 0) 100%
  );
  animation: scanline 3s linear infinite;
  pointer-events: none;
}
```

### 5.2 发光文字效果
```css
.crt-text {
  color: #00ff00;
  font-family: 'Courier New', monospace;
  text-shadow: 
    0 0 2px #00ff00,
    0 0 4px #00ff00,
    0 0 6px #00ff00;
  filter: blur(0.5px);
}
```

### 5.3 显示器边框
```css
.crt-frame {
  border: 4px solid #222;
  border-radius: 10px;
  background: #111;
  box-shadow: 
    inset 0 0 20px rgba(0, 0, 0, 0.8),
    0 0 20px rgba(0, 255, 0, 0.1);
}
```

## 6. 交互设计

### 6.1 命令输入
- 支持自然语言输入
- 命令自动补全提示
- 历史命令导航（上下键）
- 错误提示和帮助系统

### 6.2 响应式反馈
- 每个操作都有即时的视觉反馈
- 状态变化时的动画效果
- 成功/失败的不同视觉表现

### 6.3 顾问系统
- 基于当前游戏状态提供建议
- 两个顾问可能有不同观点
- 建议内容动态更新

## 7. 响应式设计

### 7.1 桌面端 (优先)
- 三显示器并排布局
- 每个显示器最小宽度400px
- 支持全屏模式

### 7.2 平板适配
- 显示器垂直堆叠
- 保持CRT比例和效果

### 7.3 移动端
- 单显示器视图，可切换
- 触摸优化的命令输入
- 简化的UI元素

## 8. 性能优化

### 8.1 渲染优化
- React.memo防止不必要的重渲染
- 使用CSS transform实现动画
- 虚拟化长消息列表

### 8.2 CRT效果优化
- 使用will-change属性
- 合理的动画帧率
- GPU加速的CSS属性

## 9. 开发里程碑

### 第一阶段：基础框架 (1-2天)
- [ ] 项目初始化和配置
- [ ] CRT显示器外壳组件
- [ ] 基础样式和主题

### 第二阶段：游戏逻辑 (2-3天)
- [ ] 状态管理系统
- [ ] 命令解析器
- [ ] 游戏状态转换逻辑

### 第三阶段：UI组件 (3-4天)
- [ ] 三个显示器组件
- [ ] 终端界面
- [ ] 顾问聊天系统

### 第四阶段：视觉效果 (2-3天)
- [ ] CRT扫描线效果
- [ ] 发光文字效果
- [ ] 动画和过渡效果

### 第五阶段：测试和优化 (2-3天)
- [ ] 响应式测试
- [ ] 性能优化
- [ ] 用户体验测试

## 10. 部署和构建

### 10.1 构建配置
```bash
# 开发环境
npm run dev

# 生产构建
npm run build

# 预览构建结果
npm run preview
```

### 10.2 部署建议
- 静态文件托管 (Vercel, Netlify)
- CDN加速
- PWA支持 (可选)

这个前端计划将创建一个沉浸式的火星生存游戏体验，结合复古CRT视觉效果和现代Web技术，为玩家提供独特的解谜体验。