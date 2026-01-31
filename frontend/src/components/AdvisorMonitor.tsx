import React from 'react';
import { CRTMonitor } from './CRTMonitor';
import { Telemetry } from '../types/game';

interface AdvisorMonitorProps {
    telemetry: Telemetry;
}

export const AdvisorMonitor: React.FC<AdvisorMonitorProps> = ({ telemetry }) => {
  return (
    <CRTMonitor className="h-full relative overflow-hidden flex flex-col">
        {/* Background Grid */}
        <div className="absolute inset-0 z-0 opacity-10 pointer-events-none" 
             style={{ backgroundImage: 'linear-gradient(0deg, transparent 24%, rgba(0, 255, 0, .3) 25%, rgba(0, 255, 0, .3) 26%, transparent 27%, transparent 74%, rgba(0, 255, 0, .3) 75%, rgba(0, 255, 0, .3) 76%, transparent 77%, transparent), linear-gradient(90deg, transparent 24%, rgba(0, 255, 0, .3) 25%, rgba(0, 255, 0, .3) 26%, transparent 27%, transparent 74%, rgba(0, 255, 0, .3) 75%, rgba(0, 255, 0, .3) 76%, transparent 77%, transparent)', backgroundSize: '50px 50px' }}>
        </div>

        <div className="relative z-10 p-4 flex flex-col h-full gap-4">
            {/* Header */}
            <div className="flex justify-between items-center border-b border-crt-green pb-2">
                <span className="text-xs font-bold bg-crt-green text-black px-2 py-0.5">BIO-TELEMETRY</span>
                <span className="text-[10px] animate-pulse">LIVE FEED // {telemetry.pressure.toFixed(1)} kPa</span>
            </div>

            {/* Vitals Grid */}
            <div className="grid grid-cols-2 gap-4">
                {/* Heart Rate */}
                <div className="flex flex-col items-center p-2 border border-crt-green/30">
                    <span className="text-[10px] opacity-70 uppercase">Heart Rate</span>
                    <span className="text-3xl font-bold">{telemetry.heart_rate}</span>
                    <span className="text-[10px]">BPM</span>
                </div>
                
                {/* Stress */}
                <div className="flex flex-col items-center p-2 border border-crt-green/30">
                    <span className="text-[10px] opacity-70 uppercase">Stress</span>
                    <span className={`text-3xl font-bold ${telemetry.stress > 50 ? "text-red-500 animate-pulse" : ""}`}>
                        {telemetry.stress.toFixed(0)}%
                    </span>
                    <span className="text-[10px]">CORTISOL</span>
                </div>
            </div>

            {/* Environment Bars */}
            <div className="space-y-3">
                {/* CO2 */}
                <div className="space-y-1">
                    <div className="flex justify-between text-xs">
                        <span>CO2 LEVEL</span>
                        <span className={telemetry.co2 > 1.0 ? "text-red-500 blink" : ""}>{telemetry.co2.toFixed(3)}%</span>
                    </div>
                    <div className="h-2 bg-crt-green/20 w-full">
                        <div className={`h-full transition-all duration-500 ${telemetry.co2 > 1.0 ? "bg-red-500" : "bg-crt-green"}`}
                             style={{ width: `${Math.min(telemetry.co2 * 30, 100)}%` }} />
                    </div>
                </div>

                {/* Temperature */}
                <div className="space-y-1">
                    <div className="flex justify-between text-xs">
                        <span>TEMP</span>
                        <span className={telemetry.temp < 10.0 ? "text-blue-400" : ""}>{telemetry.temp.toFixed(1)}°C</span>
                    </div>
                    <div className="h-2 bg-crt-green/20 w-full relative">
                        {/* -50 to 50 range */}
                        <div className={`absolute h-full w-2 transition-all duration-500 ${telemetry.temp < 10 ? "bg-blue-400" : "bg-crt-green"}`}
                             style={{ left: `${Math.max(0, Math.min(100, (telemetry.temp + 50)))}%` }} />
                    </div>
                </div>
                
                {/* Power */}
                <div className="space-y-1">
                     <div className="flex justify-between text-xs">
                        <span>BATTERY</span>
                        <span>{telemetry.battery.toFixed(1)}%</span>
                    </div>
                    <div className="h-2 bg-crt-green/20 w-full">
                         <div className="h-full bg-crt-green transition-all duration-500"
                             style={{ width: `${telemetry.battery}%` }} />
                    </div>
                </div>
            </div>

            {/* Inventory Section (New) */}
            <div className="flex-1 flex flex-col border-t border-crt-green/50 pt-2 mt-2">
                <span className="text-xs font-bold mb-2 block">INVENTORY</span>
                <div className="flex-1 overflow-y-auto space-y-1 pr-1 custom-scrollbar">
                    {telemetry.inventory && telemetry.inventory.length > 0 ? (
                        telemetry.inventory.map((item, idx) => (
                            <div key={idx} className="flex items-center gap-2 text-xs border border-crt-green/30 p-1">
                                <span className="w-2 h-2 bg-crt-green inline-block"></span>
                                <span>{item}</span>
                            </div>
                        ))
                    ) : (
                        <div className="text-xs opacity-50 italic text-center py-4">-- EMPTY --</div>
                    )}
                </div>
            </div>

        </div>
    </CRTMonitor>
  );
};
