import React from 'react';
import { useBot } from '../context/BotContext';
import clsx from 'clsx';
import { Sparkles, X } from 'lucide-react';

export default function SAIBot() {
  const { isActive, isSpeaking, caption, stopTour } = useBot();

  if (!isActive && !isSpeaking && !caption) return null;

  return (
    <div className="fixed bottom-8 right-8 z-50 flex items-end gap-4 max-w-lg pointer-events-none">
      
      {/* Caption Bubble */}
      {caption && (
        <div className="bg-slate-900/90 backdrop-blur-xl border border-white/20 text-white p-4 rounded-3xl shadow-2xl rounded-br-sm animate-fade-in mb-4 pointer-events-auto relative group">
          <button 
            onClick={stopTour}
            className="absolute -top-2 -left-2 bg-slate-800 text-slate-400 p-1 rounded-full border border-slate-700 opacity-0 group-hover:opacity-100 transition-opacity hover:text-white"
          >
            <X className="w-4 h-4" />
          </button>
          <div className="flex items-start gap-3">
            <Sparkles className="w-5 h-5 text-teal-400 shrink-0 mt-0.5" />
            <p className="text-sm font-medium leading-relaxed tracking-wide">
              {caption}
            </p>
          </div>
        </div>
      )}

      {/* Glowing Orb */}
      <div className="relative shrink-0 pointer-events-auto cursor-pointer" onClick={stopTour} title="Click to Stop Tour">
        <div className={clsx(
          "w-16 h-16 rounded-full bg-gradient-to-tr from-teal-500 via-emerald-400 to-cyan-300 shadow-[0_0_30px_rgba(45,212,191,0.5)] flex items-center justify-center transition-all duration-300",
          isSpeaking ? "scale-110 shadow-[0_0_50px_rgba(45,212,191,0.8)]" : "scale-100 animate-pulse"
        )}>
          {/* Inner Core */}
          <div className={clsx(
            "w-8 h-8 rounded-full bg-white/30 backdrop-blur-sm transition-all duration-150",
            isSpeaking ? "scale-125 animate-ping" : "scale-100"
          )} />
        </div>
        
        {/* Decorative Rings */}
        {isSpeaking && (
          <>
            <div className="absolute inset-0 rounded-full border-2 border-teal-400 animate-ping opacity-75" style={{ animationDuration: '1.5s' }} />
            <div className="absolute inset-0 rounded-full border-2 border-cyan-300 animate-ping opacity-50" style={{ animationDuration: '2s' }} />
          </>
        )}
      </div>
      
    </div>
  );
}
