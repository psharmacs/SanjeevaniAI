import { useState } from 'react';
import { Camera, Activity, Accessibility, Clock, AlertTriangle, Zap, ShieldAlert, HeartPulse, ShieldCheck, Info, ChevronDown } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import clsx from 'clsx';

const PIPELINE_STAGES = [
  {
    id: 'camera',
    title: 'VISION INGESTION',
    icon: Camera,
    tech: 'OpenCV + ESP32',
    description: 'High-speed frame capture from the local camera network. Frames are pre-processed, downscaled to reduce bandwidth, and piped directly into the AI core at 30 FPS.'
  },
  {
    id: 'detection',
    title: 'HUMAN LOCALIZATION',
    icon: Accessibility,
    tech: 'YOLOv11',
    description: 'The system scans the frame to find human bounding boxes. It focuses computational power only on regions of interest, ignoring pets and moving shadows.'
  },
  {
    id: 'posture',
    title: 'POSTURE ESTIMATION',
    icon: Activity,
    tech: 'MediaPipe Pose',
    description: 'For each detected person, 33 3D landmarks are extracted. Geometric heuristics (bounding box aspect ratios, shoulder-to-hip angles) classify the current posture as Standing, Sitting, or Lying.'
  },
  {
    id: 'temporal',
    title: 'TEMPORAL ANALYSIS',
    icon: Clock,
    tech: 'Temporal Buffer',
    description: 'A 6-second rolling window stores feature history. It tracks the angular velocity of the torso and bounding box centroid drops to understand how fast a transition is happening.'
  },
  {
    id: 'risk',
    title: 'RISK ASSESSMENT',
    icon: AlertTriangle,
    tech: 'Rule Engine',
    description: 'Combines posture transitions (e.g., Standing -> Lying) with motion thresholds (velocity > 60°/s). Outputs a risk score from 0.0 to 1.0.'
  },
  {
    id: 'state',
    title: 'STATE TRANSITION',
    icon: Zap,
    tech: 'Finite State Machine',
    description: 'Moves through logical states: Normal -> Pre-Fall -> Falling -> Fall Confirmed. Also monitors for Recovery or static Danger (lying completely still for >= 5s).'
  },
  {
    id: 'response',
    title: 'EMERGENCY RESPONSE',
    icon: ShieldAlert,
    tech: 'Alert System',
    description: 'When danger is confirmed, it triggers notifications, saves a 15-second video recording of the event, and waits for a cooldown to prevent alert spam.'
  }
];

export default function Guidebook() {
  const [activeStage, setActiveStage] = useState(PIPELINE_STAGES[0].id);

  return (
    <div className="bg-transparent text-slate-800">
      
      {/* SECTION 1: THE VISION (Hero) */}
      <section className="relative min-h-[calc(100vh-5rem)] flex items-center justify-center p-6 md:p-12 overflow-hidden">
        {/* Background Gradients */}
        <div className="absolute inset-0 pointer-events-none">
          <div className="absolute top-0 right-0 w-[50vw] h-[50vw] bg-teal-100/40 rounded-full blur-[120px] mix-blend-multiply translate-x-1/4 -translate-y-1/4"></div>
          <div className="absolute bottom-0 left-0 w-[40vw] h-[40vw] bg-teal-200/30 rounded-full blur-[100px] mix-blend-multiply -translate-x-1/4 translate-y-1/4"></div>
        </div>

        <div className="max-w-5xl mx-auto relative z-10 flex flex-col items-center text-center">
          <motion.div 
            initial={{ opacity: 0, y: 30 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.8 }}
          >
            <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-white border border-teal-100 text-teal-700 font-bold tracking-[0.2em] uppercase text-xs mb-8 shadow-sm">
              <ShieldCheck className="w-4 h-4" /> The Sanjeevani Concept
            </div>
            <h1 className="text-5xl md:text-7xl font-black tracking-tight text-slate-900 mb-8 leading-tight">
              Beyond Recording. <br />
              <span className="text-transparent bg-clip-text bg-gradient-to-r from-teal-600 to-teal-400">Into Understanding.</span>
            </h1>
          </motion.div>

          <motion.div 
            initial={{ opacity: 0, y: 30 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.8, delay: 0.2 }}
            className="glass-panel p-8 md:p-12 rounded-[2.5rem] border border-white shadow-[0_20px_40px_rgb(0,0,0,0.05)] text-left max-w-4xl"
          >
            <h2 className="text-2xl font-bold text-slate-800 mb-6">The Problem & Our Vision</h2>
            <div className="space-y-6 text-slate-600 text-lg leading-relaxed font-light">
              <p>
                Imagine an elderly person living alone. They suddenly lose balance and fall. The fall itself may take only a few seconds, but the dangerous part can be what happens afterwards: nobody may know that the person needs help.
              </p>
              <p>
                Existing cameras can record an incident, but recording is not the same as understanding. A safety system should not merely capture what happened — it should recognize when something abnormal is happening and help trigger a response.
              </p>
              <div className="p-6 md:p-8 rounded-2xl bg-teal-50 border border-teal-100 text-teal-900 font-medium text-center shadow-inner relative overflow-hidden mt-8">
                <div className="absolute -right-10 -top-10 w-40 h-40 bg-teal-200/50 rounded-full blur-3xl"></div>
                <p className="relative z-10 text-xl leading-relaxed">
                  "Sanjeevani AI turns a normal camera feed into an intelligent monitoring layer. We don't just ask if there's a person—we ask what they are doing, and if they are safe."
                </p>
              </div>
            </div>
          </motion.div>

          <motion.div 
            initial={{ opacity: 0 }}
            whileInView={{ opacity: 1 }}
            viewport={{ once: true }}
            transition={{ delay: 1, duration: 1 }}
            className="absolute bottom-10 left-1/2 -translate-x-1/2 animate-bounce text-teal-600"
          >
            <ChevronDown className="w-8 h-8 opacity-50" />
          </motion.div>
        </div>
      </section>

      {/* SECTION 2: THE PIPELINE (Interactive Architecture) */}
      <section className="relative py-24 px-6 md:px-12 bg-slate-900 overflow-hidden">
        <div className="absolute inset-0 bg-[url('https://www.transparenttextures.com/patterns/cubes.png')] opacity-5"></div>
        <div className="absolute top-1/4 left-1/4 w-[500px] h-[500px] bg-teal-900/30 rounded-full blur-[120px] pointer-events-none"></div>

        <div className="max-w-7xl mx-auto relative z-10">
          <div className="text-center mb-20">
            <h2 className="text-4xl md:text-5xl font-black text-white mb-6 tracking-tight">The Intelligence Pipeline</h2>
            <p className="text-slate-400 text-lg max-w-2xl mx-auto font-light">
              Explore the step-by-step neural architecture that processes raw video into semantic, life-saving alerts at 30 frames per second.
            </p>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 lg:gap-16">
            
            {/* Interactive Flowchart Sidebar */}
            <div className="lg:col-span-5 flex flex-col gap-3 relative">
              <div className="absolute left-[1.35rem] top-8 bottom-8 w-px bg-slate-700/50" />
              
              {PIPELINE_STAGES.map((stage) => {
                const isActive = activeStage === stage.id;
                const Icon = stage.icon;
                return (
                  <button
                    key={stage.id}
                    onMouseEnter={() => setActiveStage(stage.id)}
                    onClick={() => setActiveStage(stage.id)}
                    className={clsx(
                      "relative z-10 flex items-center gap-5 w-full p-4 rounded-2xl text-left transition-all duration-300 group overflow-hidden",
                      isActive ? "bg-white/10 border border-white/20 shadow-[0_0_30px_rgb(13,148,136,0.15)]" : "hover:bg-white/5 border border-transparent"
                    )}
                  >
                    {isActive && (
                      <motion.div layoutId="activeBackground" className="absolute inset-0 bg-gradient-to-r from-teal-500/10 to-transparent" initial={false} transition={{ type: "spring", stiffness: 300, damping: 30 }} />
                    )}
                    <div className={clsx(
                      "p-3 rounded-xl transition-all duration-300 relative z-10",
                      isActive ? "bg-teal-500 text-white shadow-lg shadow-teal-500/30 scale-110" : "bg-slate-800 text-slate-400 group-hover:text-slate-200"
                    )}>
                      <Icon className="w-5 h-5" />
                    </div>
                    <div className="relative z-10">
                      <div className={clsx("font-bold text-sm tracking-[0.15em] transition-colors duration-300", isActive ? "text-white" : "text-slate-400 group-hover:text-slate-200")}>
                        {stage.title}
                      </div>
                    </div>
                  </button>
                );
              })}
            </div>

            {/* Details Panel */}
            <div className="lg:col-span-7">
              <div className="bg-slate-800/50 backdrop-blur-xl rounded-[2.5rem] p-8 md:p-12 min-h-[450px] sticky top-28 border border-slate-700 shadow-2xl overflow-hidden relative">
                {/* Abstract glowing orb in panel */}
                <div className="absolute -top-32 -right-32 w-64 h-64 bg-teal-500/20 rounded-full blur-[80px]"></div>

                <AnimatePresence mode="wait">
                  {PIPELINE_STAGES.map((stage) => (
                    stage.id === activeStage && (
                      <motion.div
                        key={stage.id}
                        initial={{ opacity: 0, x: 20, filter: 'blur(4px)' }}
                        animate={{ opacity: 1, x: 0, filter: 'blur(0px)' }}
                        exit={{ opacity: 0, x: -20, filter: 'blur(4px)' }}
                        transition={{ duration: 0.4 }}
                        className="relative z-10"
                      >
                        <div className="inline-flex items-center gap-2 px-4 py-1.5 bg-slate-900 text-teal-400 border border-slate-700 rounded-full text-xs font-mono mb-8 font-bold tracking-widest shadow-inner">
                          <Activity className="w-3 h-3" /> {stage.tech}
                        </div>
                        
                        <h2 className="text-3xl md:text-4xl font-black mb-6 text-white tracking-tight">{stage.title}</h2>
                        
                        <p className="text-lg text-slate-300 leading-relaxed font-light">
                          {stage.description}
                        </p>
                        
                        {/* Abstract Tech Visualization Mockup */}
                        <div className="mt-12 h-32 w-full rounded-2xl border border-slate-700/50 bg-slate-900/50 flex flex-col items-center justify-center overflow-hidden relative group">
                          {/* Animated grid lines for tech feel */}
                          <div className="absolute inset-0 opacity-20" style={{ backgroundImage: 'linear-gradient(rgba(255,255,255,0.1) 1px, transparent 1px), linear-gradient(90deg, rgba(255,255,255,0.1) 1px, transparent 1px)', backgroundSize: '20px 20px' }}></div>
                          
                          <motion.div 
                            animate={{ opacity: [0.5, 1, 0.5], scale: [0.95, 1.05, 0.95] }} 
                            transition={{ duration: 3, repeat: Infinity, ease: "easeInOut" }}
                            className="relative z-10 flex items-center justify-center text-teal-500/50"
                          >
                             {(() => { const ActiveIcon = stage.icon; return <ActiveIcon className="w-16 h-16 stroke-[1.5]" />; })()}
                          </motion.div>
                        </div>
                      </motion.div>
                    )
                  ))}
                </AnimatePresence>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* SECTION 3: CORE PHILOSOPHY / CONCLUSION */}
      <section className="py-24 px-6 md:px-12 bg-white relative overflow-hidden">
        <div className="max-w-4xl mx-auto text-center relative z-10">
           <HeartPulse className="w-12 h-12 text-teal-600 mx-auto mb-8" />
           <h2 className="text-4xl font-black tracking-tight text-slate-900 mb-8">Edge Computing for Privacy & Dignity</h2>
           <p className="text-lg text-slate-600 leading-relaxed font-light mb-12">
              Sanjeevani AI operates on the Edge. No video feeds are sent to the cloud. By analyzing movement patterns locally, we preserve the complete privacy and dignity of the individuals we protect, bridging the gap between comprehensive safety and absolute security.
           </p>
        </div>
      </section>
      
    </div>
  );
}
