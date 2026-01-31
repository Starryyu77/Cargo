import React, { useState, useRef, useEffect } from 'react';
import { CRTMonitor } from './CRTMonitor';
import { Message } from '../hooks/useGameController';
import { clsx } from 'clsx';

interface TerminalMonitorProps {
  messages: Message[];
  onSendMessage: (text: string) => void;
  isTyping: boolean;
}

export const TerminalMonitor: React.FC<TerminalMonitorProps> = ({ messages, onSendMessage, isTyping }) => {
  const [input, setInput] = useState("");
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, isTyping]);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (input.trim()) {
      onSendMessage(input);
      setInput("");
    }
  };

  return (
    <div className="h-full flex flex-col relative">
      {/* Screen Border/Glow Container */}
      <div className="crt-screen flex-1 flex flex-col p-6">
        {/* Terminal Header */}
        <div className="border-b border-crt-green pb-2 mb-4 opacity-70 text-xs uppercase flex justify-between">
          <span>conn poe messages.</span>
          <span className="animate-pulse">AWAITING COMMAND</span>
        </div>

        {/* Persistent Mission Log */}
        <div className="absolute top-16 right-6 w-64 border border-crt-green bg-black/90 p-4 text-xs z-20 shadow-[0_0_15px_rgba(51,255,51,0.2)]">
            <div className="flex justify-between items-center border-b border-crt-green mb-2 pb-1">
                <h3 className="font-bold">MISSION OBJECTIVES</h3>
                <span className="animate-pulse text-[10px] bg-red-500 text-black px-1">PRIORITY: HIGH</span>
            </div>
            
            <div className="space-y-3 opacity-90">
                <div>
                    <div className="font-bold text-crt-green mb-1 text-[10px] uppercase">Phase 1: Diagnosis</div>
                    <ul className="space-y-1 pl-2 border-l border-crt-green/50">
                        <li className="flex items-center gap-2">
                           <span className={messages.length > 2 ? "text-crt-green" : "text-crt-green/30"}>[✓]</span>
                           <span>Establish Comms</span>
                        </li>
                        <li className="flex items-center gap-2">
                           <span className="text-crt-green/30">[_]</span>
                           <span>Check Life Support Status</span>
                        </li>
                    </ul>
                </div>

                <div>
                    <div className="font-bold text-crt-green mb-1 text-[10px] uppercase">Phase 2: Repair (The MacGyver Protocol)</div>
                    <ul className="space-y-1 pl-2 border-l border-crt-green/50">
                        <li className="flex items-center gap-2">
                           <span className="text-crt-green/30">[_]</span>
                           <span>Locate <span className="text-white">Duct Tape</span> & <span className="text-white">Hose</span></span>
                        </li>
                        <li className="flex items-center gap-2">
                           <span className="text-crt-green/30">[_]</span>
                           <span>Locate <span className="text-white">Spare Filter</span></span>
                        </li>
                        <li className="flex items-center gap-2">
                           <span className="text-crt-green/30">[_]</span>
                           <span>Combine items to fix Scrubber</span>
                        </li>
                    </ul>
                </div>
            </div>
            
            <div className="mt-3 pt-2 border-t border-crt-green/30 text-[10px] italic opacity-70">
                &gt; ADVISORY: Jack is untrained. Do not use technical jargon.
            </div>
        </div>

        {/* Messages Area */}
        <div className="flex-1 overflow-y-auto space-y-3 pr-2 scrollbar-hide font-mono text-sm md:text-base leading-relaxed">
          {messages.map((msg) => (
            <div key={msg.id} className={clsx(
              "flex flex-col",
              msg.sender === 'System' && "opacity-50 italic",
              msg.sender === 'Mission Control' && "text-crt-green-dim"
            )}>
              <span className="font-bold mr-2 uppercase text-xs opacity-80 mb-1">
                {msg.sender === 'Mission Control' ? 'Mission Control' : msg.sender}:
              </span>
              <span className={clsx(
                  msg.sender === 'Jack' && "text-glow font-bold"
              )}>
                {msg.text}
              </span>
            </div>
          ))}
          {isTyping && (
             <div className="flex flex-col animate-pulse">
                <span className="font-bold mr-2 uppercase text-xs opacity-80 mb-1">Jack:</span>
                <span>...</span>
             </div>
          )}
          <div ref={messagesEndRef} />
        </div>

        {/* Input Area */}
        <div className="mt-4 pt-2 border-t border-crt-green border-opacity-30">
          <form onSubmit={handleSubmit} className="flex items-center gap-2">
            <span className="text-crt-green font-bold text-lg">&gt;</span>
            <input
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              className="bg-transparent border-none outline-none text-crt-green w-full font-mono placeholder-crt-green-dark focus:ring-0 text-lg"
              placeholder="Command line:_"
              autoFocus
            />
          </form>
        </div>
      </div>
    </div>
  );
};
