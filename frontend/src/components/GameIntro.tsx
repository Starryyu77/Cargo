import React, { useState, useEffect } from 'react';
import { clsx } from 'clsx';

interface GameIntroProps {
  onStart: () => void;
}

export const GameIntro: React.FC<GameIntroProps> = ({ onStart }) => {
  const [textIndex, setTextIndex] = useState(0);
  
  const lines = [
    "INITIALIZING UPLINK...",
    "ENCRYPTION: SECURE",
    "TARGET: MARS BASE CYDONIA",
    "CONNECTION ESTABLISHED."
  ];

  useEffect(() => {
    if (textIndex < lines.length) {
      const timer = setTimeout(() => setTextIndex(prev => prev + 1), 800);
      return () => clearTimeout(timer);
    }
  }, [textIndex]);

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/90 backdrop-blur-sm p-4">
      <div className="w-full max-w-2xl border-2 border-crt-green bg-black p-8 shadow-[0_0_50px_rgba(51,255,51,0.2)] relative overflow-hidden">
        
        {/* Scanlines */}
        <div className="absolute inset-0 bg-[linear-gradient(rgba(18,16,16,0)_50%,rgba(0,0,0,0.25)_50%),linear-gradient(90deg,rgba(255,0,0,0.06),rgba(0,255,0,0.02),rgba(0,0,255,0.06))] pointer-events-none bg-[length:100%_2px,3px_100%] z-10 opacity-20"></div>

        <div className="relative z-20 flex flex-col gap-6 text-crt-green font-mono">
          
          {/* Header */}
          <div className="border-b-2 border-crt-green pb-4 mb-2 flex justify-between items-end">
            <h1 className="text-3xl font-bold text-glow">PROJECT: CARGO</h1>
            <div className="text-xs flex flex-col items-end opacity-70">
              <span>DATE: 2088-10-14</span>
              <span>LOC: CYDONIA, MARS</span>
            </div>
          </div>

          {/* Loading Sequence */}
          <div className="text-xs opacity-70 h-16 font-mono">
            {lines.slice(0, textIndex + 1).map((line, i) => (
              <div key={i}>{line}</div>
            ))}
          </div>

          {/* Story Content */}
          <div className={clsx("transition-opacity duration-1000 flex flex-col gap-4", textIndex >= lines.length ? "opacity-100" : "opacity-0")}>
            <div className="bg-crt-green/10 p-4 border border-crt-green/30">
              <h2 className="text-lg font-bold mb-2 text-white bg-crt-green/20 inline-block px-2">CRITICAL ALERT</h2>
              <p className="leading-relaxed text-sm">
                The colony evacuation has failed. One survivor remains: <strong className="text-white">Jack Morrison</strong>.
              </p>
              <p className="leading-relaxed text-sm mt-2">
                He is a cargo hauler, not an engineer. He is untrained, panicked, and his life support is failing.
              </p>
            </div>

            <div className="flex flex-col gap-2">
              <h3 className="font-bold border-b border-crt-green/50 pb-1">YOUR MISSION</h3>
              <p className="text-sm">
                You are **Mission Control**. You are his only link to survival.
              </p>
              <ul className="text-sm list-disc list-inside space-y-1 opacity-90">
                <li>Use the <strong className="text-white">Manual (Left)</strong> to find technical specs.</li>
                <li>Guide Jack using <strong className="text-white">Simple English</strong> via the Terminal.</li>
                <li>Monitor the telemetry. Don't let him die.</li>
              </ul>
            </div>

            <button 
              onClick={onStart}
              className="mt-4 border border-crt-green bg-crt-green/10 py-3 px-6 text-center font-bold hover:bg-crt-green hover:text-black transition-all uppercase tracking-widest animate-pulse"
            >
              [ ESTABLISH UPLINK ]
            </button>
          </div>

        </div>
      </div>
    </div>
  );
};
