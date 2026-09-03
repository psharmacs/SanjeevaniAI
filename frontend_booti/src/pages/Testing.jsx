import { useState, useRef } from 'react';
import { Upload, Settings, Activity, ShieldCheck, PlayCircle, Loader2 } from 'lucide-react';
import clsx from 'clsx';

export default function Testing() {
  const [dragActive, setDragActive] = useState(false);
  const [selectedVideo, setSelectedVideo] = useState(null); // 'without_bed' or 'with_bed'
  const [processing, setProcessing] = useState(false);
  const [progress, setProgress] = useState(0);
  const [showResult, setShowResult] = useState(false);
  
  const handleDrag = (e) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === "dragenter" || e.type === "dragover") {
      setDragActive(true);
    } else if (e.type === "dragleave") {
      setDragActive(false);
    }
  };

  const processFile = (fileName) => {
    let videoType = null;
    if (fileName.includes('without_bed_raw')) {
      videoType = 'without_bed';
    } else if (fileName.includes('with_bed_raw')) {
      videoType = 'with_bed';
    }

    if (videoType) {
      setSelectedVideo(videoType);
      startProcessing();
    } else {
      alert("Please select 'without_bed_raw.mp4' or 'with_bed_raw.mp4'.");
    }
  };

  const handleDrop = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      processFile(e.dataTransfer.files[0].name);
    }
  };

  const handleChange = (e) => {
    e.preventDefault();
    if (e.target.files && e.target.files[0]) {
      processFile(e.target.files[0].name);
    }
  };

  const startProcessing = () => {
    setProcessing(true);
    setProgress(0);
    setShowResult(false);
    
    // Simulate AI processing progress (~20-24 seconds)
    let currentProgress = 0;
    const interval = setInterval(() => {
      // Average increment of 2% every 450ms = ~22 seconds
      currentProgress += Math.random() * 2 + 1;
      if (currentProgress >= 100) {
        currentProgress = 100;
        clearInterval(interval);
        setTimeout(() => {
          setProcessing(false);
          setShowResult(true);
        }, 800);
      }
      setProgress(Math.min(currentProgress, 100));
    }, 450);
  };

  const resetTest = () => {
    setSelectedVideo(null);
    setProcessing(false);
    setProgress(0);
    setShowResult(false);
  };

  const withoutBedLogs = [
    "SYSTEM: Initializing Sanjeevani AI Pipeline...",
    "YOLOv8: Person Detected (ID: 0) in Living Room",
    "POSE: angle=85.2° | ratio=2.1 | posture=STANDING",
    "TRACKING: Centroid baseline established.",
    "POSE: Rapid vertical displacement detected (ang_vel=45.3°/s)",
    "POSE: angle=4.1° | ratio=0.8 | posture=LYING",
    "SPATIAL: Person centroid is OUTSIDE of SAFE ZONE.",
    "STATUS: Fall Signature Detected. Waiting for movement...",
    "MOVEMENT: 0.0px | Evidence: 0/5 frames",
    "WARNING: Person lying still for 20s. DANGER state active.",
    "ESCALATION L1: Voice check-in initiated... 'Are you okay?'",
    "VOICE: Listening for response...",
    "VOICE: No response detected (Silence timeout).",
    "ESCALATION L2: Caregiver notification sent (simulated).",
    "STATUS: Danger sustained for 60s.",
    "ESCALATION L3: Emergency escalation triggered (simulated)."
  ];

  const withBedLogs = [
    "SYSTEM: Initializing Sanjeevani AI Pipeline...",
    "YOLOv8: Bed bounding box [SAFE ZONE] detected and mapped.",
    "YOLOv8: Person Detected (ID: 0)",
    "POSE: Posture confirmed as LYING",
    "SPATIAL: Person centroid is 100% contained within SAFE ZONE.",
    "SYSTEM: Fall detection bypassed. Authorized resting area rules applied.",
    "STATUS: Person remains resting safely in bed. No escalation required.",
    "SYSTEM: Monitoring continues. Overall status SAFE."
  ];

  const currentLogs = selectedVideo === 'without_bed' ? withoutBedLogs : selectedVideo === 'with_bed' ? withBedLogs : [];

  return (
    <div className="min-h-[calc(100vh-5rem)] p-6 md:p-12 max-w-5xl mx-auto flex flex-col bg-transparent">
      <header className="mb-12">
        <h1 className="text-3xl font-medium tracking-wide text-slate-800 flex items-center gap-3">
          <Settings className="w-8 h-8 text-teal-600" />
          Model Testing
        </h1>
        <p className="text-slate-500 mt-2 font-medium">Upload raw video footage to simulate Phase 3 processing.</p>
      </header>

      {!selectedVideo && !processing && !showResult && (
        <div 
          className={clsx(
            "flex-1 glass-panel rounded-[2rem] border-2 border-dashed transition-all duration-300 flex flex-col items-center justify-center p-12 text-center",
            dragActive ? "border-teal-400 bg-teal-50/50" : "border-slate-200"
          )}
          onDragEnter={handleDrag}
          onDragLeave={handleDrag}
          onDragOver={handleDrag}
          onDrop={handleDrop}
        >
          <div className="w-24 h-24 bg-teal-100 text-teal-600 rounded-full flex items-center justify-center mb-6 shadow-sm">
            <Upload className="w-10 h-10" />
          </div>
          <h2 className="text-2xl font-bold text-slate-800 mb-4">Upload Raw Footage</h2>
          <p className="text-slate-500 max-w-md mb-8">
            Drag and drop your raw test video here, or click to browse.
          </p>
          
          <label className="px-8 py-3.5 bg-teal-600 text-white rounded-xl font-medium shadow-md shadow-teal-500/20 hover:bg-teal-700 hover:shadow-teal-500/30 transition-all cursor-pointer transition-transform active:scale-95">
            Browse Files
            <input type="file" className="hidden" accept="video/mp4" onChange={handleChange} />
          </label>
        </div>
      )}

      {processing && (
        <div className="flex-1 glass-panel rounded-[2rem] flex flex-col items-center justify-center p-12 text-center border border-slate-200">
          <Activity className="w-20 h-20 text-amber-500 mb-8 animate-pulse" />
          <h2 className="text-2xl font-bold text-slate-800 mb-4 tracking-wide">Analyzing Frames...</h2>
          <p className="text-slate-500 font-medium mb-12">Applying YOLOv8 Detection & MediaPipe Pose Estimation</p>
          
          <div className="w-full max-w-md bg-slate-100 rounded-full h-3 mb-4 overflow-hidden border border-slate-200/50 shadow-inner">
            <div 
              className="bg-gradient-to-r from-amber-400 to-teal-500 h-full transition-all duration-300 rounded-full"
              style={{ width: `${progress}%` }}
            />
          </div>
          <div className="text-slate-600 font-bold font-mono tracking-wider">
            {Math.round(progress)}%
          </div>
        </div>
      )}

      {showResult && selectedVideo && (
        <div className="flex flex-col gap-6 fade-in">
          <div className="flex justify-between items-end mb-2">
            <div>
              <h2 className="text-2xl font-bold text-slate-800 flex items-center gap-2">
                <ShieldCheck className="w-7 h-7 text-teal-500" />
                Processing Complete
              </h2>
              <p className="text-slate-500 font-medium mt-1">Viewing analyzed simulation for: <span className="font-mono text-slate-700">{selectedVideo}_raw.mp4</span></p>
            </div>
            <button 
              onClick={resetTest}
              className="px-5 py-2.5 bg-slate-100 hover:bg-slate-200 text-slate-700 font-medium rounded-xl transition-all border border-slate-200 text-sm"
            >
              Test Another Video
            </button>
          </div>
          
          <div className="glass-panel rounded-[2rem] overflow-hidden p-2 border border-slate-200/60 shadow-lg">
            <div className="w-full aspect-video bg-slate-900 rounded-[1.5rem] overflow-hidden relative group">
              <style>{`
                video::-webkit-media-controls-current-time-display,
                video::-webkit-media-controls-time-remaining-display,
                video::-webkit-media-controls-timeline {
                    display: none;
                }
              `}</style>
              <video 
                className="w-full h-full object-contain"
                controls
                autoPlay
                disablePictureInPicture
                controlsList="nodownload noplaybackrate nofullscreen"
                src={`/videos/${selectedVideo}_pro.mp4`}
              >
                Your browser does not support the video tag.
              </video>
            </div>
          </div>

          <div className="bg-slate-900 rounded-[2rem] p-6 shadow-lg border border-slate-800 font-mono text-sm overflow-x-auto">
            <div className="text-slate-400 mb-4 pb-2 border-b border-slate-800/50 flex items-center justify-between">
              <span>SYSTEM LOG: {selectedVideo}_pro.mp4</span>
              <span className="flex items-center gap-2 text-teal-500 text-xs">
                <span className="w-2 h-2 rounded-full bg-teal-500 animate-pulse"></span>
                SIMULATED OUTPUT
              </span>
            </div>
            <ul className="space-y-2">
              {currentLogs.map((log, index) => (
                <li key={index} className={clsx(
                  "leading-relaxed",
                  log.includes("WARNING") || log.includes("ESCALATION") ? "text-amber-400" :
                  log.includes("SAFE ZONE") || log.includes("STATUS") ? "text-teal-400" :
                  "text-slate-300"
                )}>
                  {log}
                </li>
              ))}
            </ul>
          </div>
        </div>
      )}
    </div>
  );
}
