import { useState } from 'react';
import { ManualMonitor } from './components/ManualMonitor';
import { TerminalMonitor } from './components/TerminalMonitor';
import { AdvisorMonitor } from './components/AdvisorMonitor';
import { useGameController } from './hooks/useGameController';
import { ErrorBoundary } from './components/ErrorBoundary';
import { GameIntro } from './components/GameIntro';

function App() {
  const { messages, sendMessage, isTyping, telemetry } = useGameController();
  const [gameStarted, setGameStarted] = useState(false);

  return (
    <ErrorBoundary>
      {!gameStarted && <GameIntro onStart={() => setGameStarted(true)} />}
      
      <div className="min-h-screen bg-zinc-950 p-4 md:p-8 flex items-center justify-center font-mono text-crt-green">
        <div className="w-full max-w-7xl grid grid-cols-1 lg:grid-cols-12 gap-6 h-[90vh] lg:h-[800px]">
          
          {/* Left Monitor: Manual (Expanded to 4 cols) */}
          <div className="lg:col-span-4 h-full min-h-[300px]">
            <ManualMonitor />
          </div>

          {/* Center Monitor: Terminal (Expanded to 8 cols) */}
          <div className="lg:col-span-8 h-full min-h-[400px]">
            <TerminalMonitor 
              messages={messages} 
              onSendMessage={sendMessage} 
              isTyping={isTyping} 
            />
          </div>

          {/* Right Monitor: Removed (Status integrated into chat) */}
          {/* <div className="lg:col-span-3 h-full min-h-[300px]">
            <AdvisorMonitor telemetry={telemetry} />
          </div> */}
        </div>
        
        {/* Background Ambience */}
        <div className="fixed inset-0 pointer-events-none bg-[radial-gradient(circle_at_center,_rgba(13,64,13,0.15),_rgba(0,0,0,0.8))] -z-10" />
      </div>
    </ErrorBoundary>
  );
}

export default App;
