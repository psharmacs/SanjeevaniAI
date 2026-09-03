import { Shield, ArrowRight, Activity, Cpu, Sparkles } from 'lucide-react';
import { useBot } from '../context/BotContext';

export default function Home() {
  const { startTour, isActive } = useBot();

  return (
    <div 
      className="min-h-[calc(100vh-5rem)] flex flex-col items-center justify-center p-6 relative overflow-hidden"
      style={{
        backgroundImage: 'url("/bg-mountains.jpg")',
        backgroundSize: 'cover',
        backgroundPosition: 'center',
      }}
    >
      
      {/* White Tint Overlay */}
      <div className="absolute inset-0 bg-white/85 backdrop-blur-[2px] z-0" />
      
      {/* Decorative Background Elements */}
      <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[800px] h-[800px] bg-teal-400/10 rounded-full blur-3xl pointer-events-none z-0" />
      
      <div className="max-w-4xl w-full flex flex-col items-center text-center relative z-10">
        <div className="inline-flex items-center gap-2 bg-teal-50 text-teal-700 px-4 py-2 rounded-full font-bold text-sm tracking-widest mb-8 border border-teal-100 shadow-sm animate-fade-in-up">
          <Sparkles className="w-4 h-4" />
          SMART INDIA HACKATHON 2026
        </div>
        
        <h1 className="text-6xl md:text-8xl font-black text-slate-800 tracking-tight leading-none mb-6 animate-fade-in-up" style={{ animationDelay: '100ms' }}>
          SANJEEVANI<span className="text-teal-600">.AI</span>
        </h1>
        
        <p className="text-xl md:text-2xl text-slate-500 font-medium max-w-2xl mb-12 animate-fade-in-up" style={{ animationDelay: '200ms' }}>
          The next generation of context-aware elderly safety monitoring. Powered by edge computing and AI.
        </p>

        {!isActive ? (
          <button 
            onClick={startTour}
            className="px-10 py-4 bg-teal-600 text-white rounded-full font-bold tracking-widest transition-all duration-300 hover:scale-105 hover:bg-teal-700 hover:shadow-[0_0_30px_rgba(13,148,136,0.5)] flex items-center gap-3 animate-bounce shadow-xl"
          >
            INITIALIZE EXPERIENCE
            <ArrowRight className="w-5 h-5" />
          </button>
        ) : (
          <div className="px-10 py-4 bg-teal-50/50 border border-teal-100 text-teal-700 rounded-full font-bold tracking-widest animate-pulse flex items-center gap-3">
            <Activity className="w-5 h-5" />
            AI ACTIVE...
          </div>
        )}

      </div>
    </div>
  );
}
