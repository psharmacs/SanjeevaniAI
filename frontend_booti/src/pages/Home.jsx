import { Link } from 'react-router-dom';
import { motion } from 'framer-motion';
import { Users, HeartPulse, Shield, Leaf, Play, CheckCircle2 } from 'lucide-react';

export default function Home() {
  return (
    <div className="relative min-h-screen flex items-center overflow-hidden bg-[#e6f0e9]">
      
      {/* Background Image */}
      <div className="absolute inset-0 z-0">
        <img 
          src="/new_hanumant.jpg" 
          alt="Hanuman holding Sanjeevani mountain" 
          className="w-full h-full object-cover object-center"
        />
        {/* Very subtle gradient overlay to ensure text readability without ruining the bright sunset */}
        <div className="absolute inset-0 bg-gradient-to-r from-white/60 via-white/20 to-transparent" />
      </div>

      <section className="relative z-10 w-full max-w-7xl mx-auto px-6 pt-24 pb-12 flex flex-col md:flex-row items-center justify-between">
        
        {/* Left Side: Hero Content */}
        <motion.div 
          initial={{ opacity: 0, x: -50 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ duration: 1.2, ease: "easeOut" }}
          className="flex flex-col items-start max-w-2xl"
        >
          <span className="text-sm font-semibold tracking-widest text-slate-700 uppercase mb-4">
            Inspired by a timeless story
          </span>
          
          <h1 className="text-7xl md:text-[5.5rem] font-bold text-slate-900 leading-none mb-2" style={{ fontFamily: 'Georgia, serif' }}>
            Sanjeevani <span className="text-[#0a4d3c]">AI</span>
          </h1>
          
          <h2 className="text-3xl md:text-4xl font-semibold text-slate-800 mb-6" style={{ fontFamily: 'Georgia, serif' }}>
            AI that cares. <span className="text-[#0a4d3c]">A safer tomorrow.</span>
          </h2>
          
          <p className="text-lg md:text-xl text-slate-700 mb-10 leading-relaxed font-medium max-w-xl">
            Just as Sanjeevani brought life and hope in the Ramayana, we use the power of AI to detect health risks early, protect vulnerable people, and save lives.
          </p>
          
          {/* Buttons */}
          <div className="flex items-center gap-4 mb-16">
            <Link 
              to="/live" 
              className="px-8 py-3.5 bg-[#0a4d3c] text-white hover:bg-[#07362a] font-medium rounded-full flex items-center gap-2 transition-all shadow-lg"
            >
              Explore Our Solution &rarr;
            </Link>
          </div>

          {/* Four Features */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-8">
            <div className="flex flex-col items-center text-center">
              <div className="w-14 h-14 rounded-full bg-teal-100/80 flex items-center justify-center mb-3">
                <Users className="w-7 h-7 text-teal-700" />
              </div>
              <h3 className="font-bold text-sm text-slate-900 leading-tight mb-1">Safer<br/>People</h3>
              <p className="text-[0.65rem] text-slate-600 leading-snug">Care that reaches<br/>every individual</p>
            </div>
            
            <div className="flex flex-col items-center text-center">
              <div className="w-14 h-14 rounded-full bg-rose-100/80 flex items-center justify-center mb-3">
                <HeartPulse className="w-7 h-7 text-rose-700" />
              </div>
              <h3 className="font-bold text-sm text-slate-900 leading-tight mb-1">Healthier<br/>Communities</h3>
              <p className="text-[0.65rem] text-slate-600 leading-snug">Stronger together,<br/>for a better society</p>
            </div>
            
            <div className="flex flex-col items-center text-center">
              <div className="w-14 h-14 rounded-full bg-blue-100/80 flex items-center justify-center mb-3">
                <Shield className="w-7 h-7 text-blue-700" />
              </div>
              <h3 className="font-bold text-sm text-slate-900 leading-tight mb-1">Earlier<br/>Intervention</h3>
              <p className="text-[0.65rem] text-slate-600 leading-snug">Detect today,<br/>prevent tomorrow</p>
            </div>
            
            <div className="flex flex-col items-center text-center">
              <div className="w-14 h-14 rounded-full bg-amber-100/80 flex items-center justify-center mb-3">
                <Leaf className="w-7 h-7 text-amber-700" />
              </div>
              <h3 className="font-bold text-sm text-slate-900 leading-tight mb-1">A Brighter<br/>Tomorrow</h3>
              <p className="text-[0.65rem] text-slate-600 leading-snug">More lives.<br/>More possibilities.</p>
            </div>
          </div>
        </motion.div>

        {/* Right Side: Glass Card & Quotes */}
        <motion.div 
          initial={{ opacity: 0, x: 50 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ duration: 1.2, delay: 0.3, ease: "easeOut" }}
          className="hidden md:flex flex-col items-end justify-center self-stretch relative pt-20"
        >
          {/* Top Right Quote */}
          <div className="mb-32 text-right mr-8">
            <h3 className="text-2xl italic font-serif text-slate-800 mb-2 max-w-xs">
              "Compassion has the power to bring life back."
            </h3>
            <p className="text-xs font-bold tracking-widest text-slate-600 uppercase">
              Inspired by<br/>The Ramayana
            </p>
          </div>

          {/* Glassmorphism Card */}
          <div className="bg-white/10 backdrop-blur-md border border-white/30 rounded-3xl p-8 shadow-2xl w-80 relative overflow-hidden">
            <div className="absolute inset-0 bg-gradient-to-br from-white/20 to-transparent" />
            <div className="relative z-10">
              <div className="flex items-center gap-3 mb-6">
                <Leaf className="w-8 h-8 text-white drop-shadow-md" />
                <h3 className="text-xl font-bold text-white drop-shadow-md">Technology for<br/>Humanity</h3>
              </div>
              
              <ul className="space-y-4">
                <li className="flex items-center gap-3">
                  <CheckCircle2 className="w-5 h-5 text-teal-300" />
                  <span className="text-white text-sm font-medium drop-shadow-sm">Detect Risks Early</span>
                </li>
                <li className="flex items-center gap-3">
                  <CheckCircle2 className="w-5 h-5 text-teal-300" />
                  <span className="text-white text-sm font-medium drop-shadow-sm">Real-time Monitoring</span>
                </li>
                <li className="flex items-center gap-3">
                  <CheckCircle2 className="w-5 h-5 text-teal-300" />
                  <span className="text-white text-sm font-medium drop-shadow-sm">Timely Alerts</span>
                </li>
              </ul>
            </div>
          </div>

          {/* Bottom Gold Text */}
          <div className="mt-16 text-center w-80">
            <p className="text-xl font-serif text-amber-500 tracking-widest uppercase" style={{ textShadow: '0 2px 4px rgba(0,0,0,0.5)' }}>
              Because<br/>Every Life<br/>Matters
            </p>
          </div>
        </motion.div>
        
      </section>

      {/* Footer Text */}
      <div className="absolute bottom-6 left-0 right-0 z-10 flex justify-center">
        <p className="text-[0.65rem] font-bold tracking-[0.2em] uppercase text-slate-800 bg-white/40 backdrop-blur-sm px-6 py-2 rounded-full">
          People &times; Technology &times; Compassion = A Healthier Tomorrow
        </p>
      </div>

    </div>
  );
}
