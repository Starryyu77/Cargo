import React, { useState } from 'react';
import { CRTMonitor } from './CRTMonitor';
import { manualDatabase } from '../data/manualData';
import { ManualEntry } from '../types/manual';
import { clsx } from 'clsx';

export const ManualMonitor: React.FC = () => {
  const [selectedId, setSelectedId] = useState<string>(manualDatabase[0].id);
  const selectedEntry = manualDatabase.find(e => e.id === selectedId) || manualDatabase[0];

  return (
    <CRTMonitor label="TECHNICAL DATABASE" className="h-full">
      <div className="flex flex-row h-full pt-8 gap-4">
        {/* Left Sidebar: Index */}
        <div className="w-1/3 border-r border-crt-green/30 pr-2 flex flex-col gap-2 overflow-y-auto custom-scrollbar">
          <div className="text-xs text-crt-green/50 mb-2 uppercase tracking-wider">Index_v.2.4</div>
          {manualDatabase.map((entry) => (
            <button
              key={entry.id}
              onClick={() => setSelectedId(entry.id)}
              className={clsx(
                "text-left p-2 text-xs font-mono transition-colors border border-transparent",
                selectedId === entry.id 
                  ? "bg-crt-green/20 border-crt-green text-crt-green" 
                  : "text-crt-green/70 hover:bg-crt-green/10"
              )}
            >
              <div className="font-bold">{entry.id}</div>
              <div className="truncate opacity-80 text-[10px]">{entry.title}</div>
            </button>
          ))}
        </div>

        {/* Right Content: Details */}
        <div className="w-2/3 flex flex-col overflow-y-auto custom-scrollbar pr-2">
          {/* Header */}
          <div className="border-b border-crt-green/50 pb-2 mb-4">
            <h1 className="text-lg font-bold text-crt-green text-glow">{selectedEntry.title}</h1>
            <div className="flex justify-between text-[10px] text-crt-green/60 mt-1 uppercase">
              <span>CAT: {selectedEntry.category}</span>
              <span>AUTH_LVL: {selectedEntry.access_level}</span>
            </div>
          </div>

          {/* Technical Content */}
          <div className="flex-1 flex flex-col gap-6">
            
            {/* Schematic View */}
            <div className="w-full aspect-video bg-crt-green/5 border border-crt-green/30 relative flex items-center justify-center overflow-hidden">
               {selectedEntry.technical_content.schematic_url === 'svg-internal' ? (
                 <PduSchematic />
               ) : (
                 <div className="flex flex-col items-center justify-center text-crt-green/40">
                   <div className="border border-crt-green/40 p-4 mb-2">[ IMAGE SIGNAL LOST ]</div>
                   <div className="text-xs">LOADING EXTERNAL ASSET: {selectedEntry.technical_content.schematic_url}</div>
                 </div>
               )}
               {/* Scanline overlay for image */}
               <div className="absolute inset-0 bg-[linear-gradient(rgba(18,16,16,0)_50%,rgba(0,0,0,0.25)_50%),linear-gradient(90deg,rgba(255,0,0,0.06),rgba(0,255,0,0.02),rgba(0,0,255,0.06))] z-10 pointer-events-none bg-[length:100%_2px,3px_100%]"></div>
            </div>

            {/* Specs & Data */}
            <div className="grid grid-cols-1 gap-4">
              <Section title="TECHNICAL SPECIFICATIONS">
                <div className="whitespace-pre-line font-mono text-xs text-crt-green/90 leading-relaxed">
                  {selectedEntry.technical_content.specs}
                </div>
              </Section>

              {selectedEntry.technical_content.warnings.length > 0 && (
                <Section title="WARNINGS" className="border-red-500/50">
                  <ul className="list-disc list-inside text-xs text-red-400">
                    {selectedEntry.technical_content.warnings.map((w, i) => (
                      <li key={i} className="mb-1">{w}</li>
                    ))}
                  </ul>
                </Section>
              )}

              {selectedEntry.technical_content.formulas.length > 0 && (
                <Section title="PHYSICS CONSTANTS">
                  <div className="flex flex-col gap-1">
                    {selectedEntry.technical_content.formulas.map((f, i) => (
                      <code key={i} className="block bg-crt-green/10 p-1 text-xs font-mono text-crt-green">{f}</code>
                    ))}
                  </div>
                </Section>
              )}
            </div>

            {/* Lore Snippet (Footer) */}
            {selectedEntry.lore_snippet && (
              <div className="mt-4 mb-8 relative group">
                <div className="absolute -left-2 top-0 bottom-0 w-1 bg-yellow-500/50"></div>
                <div className="pl-4 py-2 text-xs italic text-yellow-500/80 font-serif border-l border-transparent">
                  "{selectedEntry.lore_snippet}"
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </CRTMonitor>
  );
};

const Section: React.FC<{ title: string; children: React.ReactNode; className?: string }> = ({ title, children, className }) => (
  <div className={clsx("border border-crt-green/20 p-3 bg-black/40", className)}>
    <h3 className="text-[10px] font-bold text-crt-green/50 uppercase mb-2 border-b border-crt-green/10 pb-1">{title}</h3>
    {children}
  </div>
);

// The original SVG component preserved
const PduSchematic: React.FC = () => (
  <svg viewBox="0 0 300 400" className="w-full h-full opacity-90 stroke-crt-green fill-none p-4">
    {/* Main Power Box */}
    <rect x="50" y="50" width="200" height="300" strokeWidth="2" />
    <text x="70" y="40" fill="#33ff33" fontSize="12" className="font-mono">MAIN PDU SCHEMATIC</text>
    
    {/* Internal Components */}
    <rect x="80" y="80" width="60" height="60" strokeWidth="1" />
    <text x="85" y="115" fill="#33ff33" fontSize="10">RECTIFIER</text>

    <rect x="160" y="80" width="60" height="60" strokeWidth="1" />
    <text x="165" y="115" fill="#33ff33" fontSize="10">INVERTER</text>

    {/* Wires */}
    <path d="M 110 140 L 110 200 L 150 200" strokeWidth="1" strokeDasharray="4 2" />
    <path d="M 190 140 L 190 200 L 150 200" strokeWidth="1" strokeDasharray="4 2" />
    
    {/* Terminal Block */}
    <rect x="100" y="250" width="100" height="60" strokeWidth="2" />
    <circle cx="120" cy="280" r="5" fill="#33ff33" />
    <text x="115" y="300" fill="#33ff33" fontSize="10">A(+)</text>
    
    <circle cx="180" cy="280" r="5" fill="#33ff33" />
    <text x="175" y="300" fill="#33ff33" fontSize="10">B(-)</text>

    {/* Instructions Text */}
    <g transform="translate(60, 360)">
       <text x="0" y="0" fill="#33ff33" fontSize="8" className="opacity-80">1. OPEN COVER</text>
       <text x="0" y="10" fill="#33ff33" fontSize="8" className="opacity-80">2. RED WIRE -&gt; TERM A</text>
       <text x="0" y="20" fill="#33ff33" fontSize="8" className="opacity-80">3. BLUE WIRE -&gt; TERM B</text>
    </g>
  </svg>
);
