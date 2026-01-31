import React from 'react';
import { clsx } from 'clsx';
import { twMerge } from 'tailwind-merge';

interface CRTMonitorProps extends React.HTMLAttributes<HTMLDivElement> {
  children: React.ReactNode;
  label?: string;
}

export const CRTMonitor: React.FC<CRTMonitorProps> = ({ children, className, label, ...props }) => {
  return (
    <div className={twMerge("flex flex-col gap-2", className)} {...props}>
      <div className="crt-screen w-full h-full p-4 flex flex-col relative bg-black">
        {label && (
           <div className="absolute top-4 left-4 border-b border-crt-green pb-1 mb-2 z-20">
             <h2 className="text-crt-green font-bold uppercase tracking-widest text-sm text-glow">
               {label}
             </h2>
           </div>
        )}
        <div className="relative z-20 w-full h-full overflow-hidden flex flex-col">
            {children}
        </div>
      </div>
    </div>
  );
};
