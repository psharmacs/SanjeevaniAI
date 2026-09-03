import { useState } from 'react';
import { Camera, Activity, Accessibility, Clock, AlertTriangle, Zap, ShieldAlert } from 'lucide-react';
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

export default function Intelligence() {
  const [activeStage, setActiveStage] = useState(PIPELINE_STAGES[0].id);

  return (
    <div className="min-h-[calc(100vh-5rem)] p-6 md:p-12 max-w-7xl mx-auto bg-transparent">
      <header className="mb-16 text-center">
        <h1 className="text-4xl font-normal tracking-wide text-slate-900 mb-4" style={{ fontFamily: 'Georgia, serif' }}>How Sanjeevani Thinks</h1>
        <p className="text-slate-600 max-w-2xl mx-auto font-medium">
          The intelligence pipeline transforms raw pixels into semantic understanding. Explore the architecture below.
        </p>
      </header>

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-12">
        {/* Interactive Flowchart */}
        <div className="lg:col-span-5 flex flex-col gap-2">
          {PIPELINE_STAGES.map((stage, index) => {
            const isActive = activeStage === stage.id;
            const Icon = stage.icon;
            return (
              <div key={stage.id} className="relative flex items-center">
                {index !== PIPELINE_STAGES.length - 1 && (
                  <div className="absolute left-[1.35rem] top-12 bottom-[-10px] w-0.5 bg-slate-200" />
                )}
                <button
                  onMouseEnter={() => setActiveStage(stage.id)}
                  onClick={() => setActiveStage(stage.id)}
                  className={clsx(
                    "relative z-10 flex items-center gap-4 w-full p-4 rounded-xl text-left transition-all duration-300",
                    isActive ? "bg-white border border-slate-200 shadow-lg" : "hover:bg-white/50 border border-transparent"
                  )}
                >
                  <div className={clsx(
                    "p-2 rounded-lg transition-colors shadow-sm",
                    isActive ? "bg-teal-500 text-white" : "bg-white text-slate-400 border border-slate-100"
                  )}>
                    <Icon className="w-5 h-5" />
                  </div>
                  <div>
                    <div className={clsx("font-bold text-sm tracking-widest", isActive ? "text-slate-800" : "text-slate-500")}>
                      {stage.title}
                    </div>
                  </div>
                </button>
              </div>
            );
          })}
        </div>

        {/* Details Panel */}
        <div className="lg:col-span-7">
          <div className="glass-panel rounded-3xl p-8 md:p-12 min-h-[400px] sticky top-28">
            <AnimatePresence mode="wait">
              {PIPELINE_STAGES.map((stage) => (
                stage.id === activeStage && (
                  <motion.div
                    key={stage.id}
                    initial={{ opacity: 0, x: 20 }}
                    animate={{ opacity: 1, x: 0 }}
                    exit={{ opacity: 0, x: -20 }}
                    transition={{ duration: 0.3 }}
                  >
                    <div className="inline-block px-3 py-1 bg-teal-50 text-teal-600 border border-teal-200 rounded-full text-xs font-mono mb-6 font-bold shadow-sm">
                      {stage.tech}
                    </div>
                    
                    <h2 className="text-3xl font-bold mb-6 text-slate-800" style={{ fontFamily: 'Georgia, serif' }}>{stage.title}</h2>
                    
                    <p className="text-lg text-slate-600 leading-relaxed font-medium">
                      {stage.description}
                    </p>
                    
                    {/* Abstract Visualization Mockup */}
                    <div className="mt-12 h-32 w-full rounded-xl border border-slate-200 bg-white/50 flex items-center justify-center overflow-hidden relative shadow-inner">
                      {/* Decorative abstract elements based on stage */}
                      {stage.id === 'camera' && (
                        <div className="grid grid-cols-8 gap-1 w-full h-full opacity-30 p-2">
                           {Array.from({length: 32}).map((_, i) => <div key={i} className="bg-teal-500/50 rounded-sm" />)}
                        </div>
                      )}
                      {stage.id === 'detection' && (
                        <div className="absolute inset-0 flex items-center justify-center">
                          <div className="w-24 h-24 border-2 border-teal-500/50 border-dashed rounded relative bg-teal-50/50">
                            <div className="absolute -top-1 -left-1 w-2 h-2 bg-teal-500 rounded-full" />
                            <div className="absolute -bottom-1 -right-1 w-2 h-2 bg-teal-500 rounded-full" />
                          </div>
                        </div>
                      )}
                      {stage.id === 'posture' && (
                        <div className="flex gap-4">
                           <div className="w-2 h-2 bg-teal-500 rounded-full shadow-[0_0_8px_rgba(20,184,166,0.5)]" />
                           <div className="w-16 h-0.5 bg-teal-500/50 self-center" />
                           <div className="w-2 h-2 bg-teal-500 rounded-full shadow-[0_0_8px_rgba(20,184,166,0.5)]" />
                        </div>
                      )}
                      {stage.id === 'temporal' && (
                         <div className="w-full flex items-end gap-1 p-4 h-full opacity-60">
                           {[20, 30, 25, 40, 60, 80, 95].map((h, i) => (
                             <div key={i} className="flex-1 bg-amber-400 rounded-t-md transition-all" style={{height: `${h}%`}} />
                           ))}
                         </div>
                      )}
                      {stage.id === 'risk' && (
                        <div className="text-4xl font-mono text-red-500 font-bold drop-shadow-sm">0.87</div>
                      )}
                      {stage.id === 'state' && (
                        <div className="flex items-center gap-2 text-sm font-mono text-slate-500 font-bold">
                          <span>PRE_FALL</span> <ArrowRight className="w-4 h-4 text-slate-400" /> <span className="text-red-500">FALL_CONFIRMED</span>
                        </div>
                      )}
                      {stage.id === 'response' && (
                         <div className="w-full h-full bg-red-50 flex items-center justify-center">
                           <ShieldAlert className="w-12 h-12 text-red-500 animate-pulse drop-shadow-md" />
                         </div>
                      )}
                    </div>
                  </motion.div>
                )
              ))}
            </AnimatePresence>
          </div>
        </div>
      </div>
    </div>
  );
}

function ArrowRight(props) {
  return (
    <svg {...props} xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M5 12h14"/><path d="m12 5 7 7-7 7"/></svg>
  );
}
