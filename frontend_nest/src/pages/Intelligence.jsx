import { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Camera, Focus, Activity, Clock, ShieldAlert, Zap, AlertTriangle } from 'lucide-react';
import clsx from 'clsx';

const PIPELINE_STAGES = [
  {
    id: 'camera',
    title: 'CAMERA INPUT',
    icon: Camera,
    tech: 'OpenCV / RTSP',
    description: 'Raw video frames are captured continuously. The system processes each frame in real-time, extracting only the necessary pixel data for analysis without permanently storing video unless an emergency occurs.'
  },
  {
    id: 'detection',
    title: 'PERSON DETECTION',
    icon: Focus,
    tech: 'YOLOv8',
    description: 'A lightweight neural network (YOLOv8n) identifies bounding boxes for any humans in the frame. A Centroid Tracker ensures consistent identification of individuals across consecutive frames.'
  },
  {
    id: 'posture',
    title: 'BODY UNDERSTANDING',
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
    <div className="min-h-[calc(100vh-4rem)] p-6 md:p-12 max-w-7xl mx-auto">
      <header className="mb-16 text-center">
        <h1 className="text-4xl font-light tracking-wide text-gray-200 mb-4">How Sanjeevani Thinks</h1>
        <p className="text-gray-400 max-w-2xl mx-auto">
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
                  <div className="absolute left-[1.35rem] top-12 bottom-[-10px] w-0.5 bg-gray-800" />
                )}
                <button
                  onMouseEnter={() => setActiveStage(stage.id)}
                  onClick={() => setActiveStage(stage.id)}
                  className={clsx(
                    "relative z-10 flex items-center gap-4 w-full p-4 rounded-xl text-left transition-all duration-300",
                    isActive ? "bg-gray-900 border border-gray-700 shadow-lg" : "hover:bg-gray-900/50 border border-transparent"
                  )}
                >
                  <div className={clsx(
                    "p-2 rounded-lg transition-colors",
                    isActive ? "bg-emerald-500/20 text-emerald-400" : "bg-gray-800 text-gray-500"
                  )}>
                    <Icon className="w-5 h-5" />
                  </div>
                  <div>
                    <div className={clsx("font-semibold text-sm tracking-widest", isActive ? "text-white" : "text-gray-500")}>
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
          <div className="bg-gray-900/40 border border-gray-800 rounded-3xl p-8 md:p-12 min-h-[400px] sticky top-24">
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
                    <div className="inline-block px-3 py-1 bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 rounded-full text-xs font-mono mb-6">
                      {stage.tech}
                    </div>
                    
                    <h2 className="text-3xl font-bold mb-6 text-gray-100">{stage.title}</h2>
                    
                    <p className="text-lg text-gray-400 leading-relaxed">
                      {stage.description}
                    </p>
                    
                    {/* Abstract Visualization Mockup */}
                    <div className="mt-12 h-32 w-full rounded-xl border border-gray-800 bg-gray-950/50 flex items-center justify-center overflow-hidden relative">
                      {/* Decorative abstract elements based on stage */}
                      {stage.id === 'camera' && (
                        <div className="grid grid-cols-8 gap-1 w-full h-full opacity-20 p-2">
                           {Array.from({length: 32}).map((_, i) => <div key={i} className="bg-emerald-500/50 rounded-sm" />)}
                        </div>
                      )}
                      {stage.id === 'detection' && (
                        <div className="absolute inset-0 flex items-center justify-center">
                          <div className="w-24 h-24 border-2 border-emerald-500/50 border-dashed rounded relative">
                            <div className="absolute -top-1 -left-1 w-2 h-2 bg-emerald-500" />
                            <div className="absolute -bottom-1 -right-1 w-2 h-2 bg-emerald-500" />
                          </div>
                        </div>
                      )}
                      {stage.id === 'posture' && (
                        <div className="flex gap-4">
                           <div className="w-2 h-2 bg-emerald-400 rounded-full" />
                           <div className="w-16 h-0.5 bg-emerald-400/50 self-center" />
                           <div className="w-2 h-2 bg-emerald-400 rounded-full" />
                        </div>
                      )}
                      {stage.id === 'temporal' && (
                         <div className="w-full flex items-end gap-1 p-4 h-full opacity-50">
                           {[20, 30, 25, 40, 60, 80, 95].map((h, i) => (
                             <div key={i} className="flex-1 bg-amber-400 rounded-t-sm transition-all" style={{height: `${h}%`}} />
                           ))}
                         </div>
                      )}
                      {stage.id === 'risk' && (
                        <div className="text-4xl font-mono text-red-400 font-bold">0.87</div>
                      )}
                      {stage.id === 'state' && (
                        <div className="flex items-center gap-2 text-sm font-mono text-gray-500">
                          <span>PRE_FALL</span> <ArrowRight className="w-4 h-4" /> <span className="text-red-400">FALL_CONFIRMED</span>
                        </div>
                      )}
                      {stage.id === 'response' && (
                         <div className="w-full h-full bg-red-500/10 flex items-center justify-center">
                           <ShieldAlert className="w-12 h-12 text-red-500 animate-pulse" />
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
