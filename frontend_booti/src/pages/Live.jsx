import React, { useEffect, useRef, useState } from 'react';
import { Cpu, Terminal, Activity, Wifi, ShieldAlert, HeartPulse } from 'lucide-react';
import clsx from 'clsx';
import { useBot } from '../context/BotContext';
import { useNavigate } from 'react-router-dom';

export default function Live() {
  const { 
    isActive, 
    activeRef, 
    playFallDetectionScript, 
    playBedZoneScript, 
    playGuidebookScript,
    stopTour
  } = useBot();
  const navigate = useNavigate();
  
  const [currentVideoIndex, setCurrentVideoIndex] = useState(0);
  const [logs, setLogs] = useState(["[SYS] System online. Awaiting demonstration protocol..."]);
  const [isVideoPlaying, setIsVideoPlaying] = useState(false);
  
  // Track completion of both elements for smooth transitions
  const [isVideoEnded, setIsVideoEnded] = useState(false);
  const [isScriptEnded, setIsScriptEnded] = useState(false);

  const logEndRef = useRef(null);
  const videoRef = useRef(null);

  const videos = [
    '/without_bed_final.mp4',
    '/with_bed_final.mp4'
  ];

  // Logs for Video 1 (Fall Detection)
  const fallLogs = [
    "[SYS] Initializing Sanjeevani AI Edge Node...",
    "[CAM] Video feed established (1080p, 30fps)",
    "[MODEL] YOLOv8 loaded successfully",
    "[MODEL] MediaPipe Pose active",
    "[DETECTION] Tracking movement across spatial grid",
    "[POSTURE] Subject standing - Normal Activity",
    "[POSTURE] Rapid acceleration detected",
    "[POSTURE] Torso angle: 12° - DANGER DETECTED",
    "[ALERT] Temporal verification running...",
    "[ALERT] Fall confirmed. Triggering Level 1 Protocol.",
    "[VOICE] Initiating: 'Are you okay?'",
    "[TIMER] Awaiting response (10s)...",
    "[ALERT] No response. Triggering Level 2 Caregiver Alert.",
    "[ALERT] Persisting danger. Triggering Level 3 Emergency Dispatch.",
    "[SYS] REPEATING: Level 1 Protocol...",
    "[POSTURE] Subject recovering. Movement detected.",
    "[ALERT] Recovery confirmed. Canceling trigger.",
    "[VOICE] Wake word detected: 'Sanjeevani, I need help'",
    "[ALERT] Manual distress signal confirmed.",
    "[ALERT] Dispatching Caretaker Alert..."
  ];

  // Logs for Video 2 (Bed Zone)
  const bedLogs = [
    "[SYS] Recalibrating spatial zones...",
    "[DETECTION] Tracking movement across spatial grid",
    "[POSTURE] Calculating joint vectors...",
    "[POSTURE] Torso angle: 85° - SAFE",
    "[ZONE] Subject entered BED ZONE",
    "[VITAL] Syncing with Wearable Device for BPM...",
    "[VITAL] Heart Rate: 72 BPM - NORMAL",
    "[VITAL] Heart Rate: 68 BPM - SLEEPING STATE",
    "[ZONE] Subject exited BED ZONE",
    "[DETECTION] Arming Fall Detection System...",
    "[POSTURE] Torso angle: 82° - SAFE",
    "[SYS] Continuous monitoring active..."
  ];

  useEffect(() => {
    // Reset state for new video
    setIsVideoPlaying(false);
    setIsVideoEnded(false);
    setIsScriptEnded(false);
    setLogs(["[SYS] System online. Awaiting demonstration protocol..."]);
    
    if (videoRef.current) {
      videoRef.current.pause();
      videoRef.current.currentTime = 0;
    }

    if (currentVideoIndex === 0) {
      playFallDetectionScript(() => {
        setIsVideoPlaying(true);
        if (videoRef.current) videoRef.current.play();
      }, () => setIsScriptEnded(true));
    } else if (currentVideoIndex === 1) {
      playBedZoneScript(() => {
        setIsVideoPlaying(true);
        if (videoRef.current) videoRef.current.play();
      }, () => setIsScriptEnded(true));
    }
  }, [currentVideoIndex]);

  useEffect(() => {
    // Only run logs if the video is actually playing
    if (!isVideoPlaying) return;

    const currentLogSource = currentVideoIndex === 0 ? fallLogs : bedLogs;
    let logIndex = 0;
    
    const interval = setInterval(() => {
      if (logIndex < currentLogSource.length) {
        setLogs(prev => [...prev, currentLogSource[logIndex]]);
        logIndex++;
      } else {
        clearInterval(interval);
      }
    }, 1500);

    return () => clearInterval(interval);
  }, [currentVideoIndex, isVideoPlaying]);

  useEffect(() => {
    logEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [logs]);

  const handleVideoEnded = () => {
    setIsVideoEnded(true);
  };

  const forceNextVideo = () => {
    window.speechSynthesis.cancel();
    if (currentVideoIndex < videos.length - 1) {
      setCurrentVideoIndex(prev => prev + 1);
    } else {
      navigate('/guidebook');
      playGuidebookScript();
    }
  };

  // Transition Engine: Only transition when BOTH the video ends AND the bot finishes talking!
  useEffect(() => {
    if (isVideoEnded && isScriptEnded) {
      forceNextVideo();
    }
  }, [isVideoEnded, isScriptEnded]);

  return (
    <div className="min-h-[calc(100vh-5rem)] p-6 max-w-7xl mx-auto flex flex-col">
      <header className="mb-8 flex flex-col md:flex-row justify-between items-start md:items-end gap-4">
        <div>
          <h1 className="text-4xl font-black tracking-widest text-slate-800">
            LIVE FEED
          </h1>
          <p className="text-slate-500 mt-2 font-medium tracking-wide">
            Real-time inference & temporal reasoning visualization
          </p>
        </div>
        
        <div className="flex flex-col sm:flex-row items-center gap-3">
          <button 
            onClick={forceNextVideo}
            className="px-4 py-2 bg-slate-800 text-white text-sm font-bold tracking-wider rounded-full hover:bg-slate-700 transition-colors shadow-lg"
          >
            SKIP SIMULATION ⏭
          </button>
          
          <div className="flex items-center gap-3 bg-teal-50 text-teal-700 px-4 py-2 rounded-full border border-teal-100 shadow-sm">
            <Wifi className="w-4 h-4 animate-pulse" />
            <span className="font-bold text-sm tracking-wider">EDGE NODE ACTIVE</span>
          </div>
        </div>
      </header>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 flex-1">
        
        {/* Main Video Area */}
        <div className="lg:col-span-2 glass-panel rounded-3xl overflow-hidden border border-slate-200 shadow-xl flex flex-col relative group">
          <div className="bg-slate-900 px-4 py-3 flex items-center justify-between z-10">
            <div className="flex items-center gap-3">
              <div className="flex gap-1.5">
                <div className="w-3 h-3 rounded-full bg-red-500 animate-pulse"></div>
                <div className="w-3 h-3 rounded-full bg-slate-700"></div>
                <div className="w-3 h-3 rounded-full bg-slate-700"></div>
              </div>
              <span className="text-slate-300 font-mono text-sm tracking-wider flex items-center gap-2">
                <Activity className="w-4 h-4 text-teal-400" />
                CAM_01_LIVING_ROOM
              </span>
            </div>
            <div className="text-slate-400 font-mono text-xs border border-slate-700 px-2 py-1 rounded bg-slate-800">
              YOLOv8 + MediaPipe
            </div>
          </div>
          
          <div className="bg-black flex-1 relative flex items-center justify-center overflow-hidden">
            <video 
              ref={videoRef}
              key={videos[currentVideoIndex]}
              className="w-full h-full object-contain"
              playsInline
              onEnded={handleVideoEnded}
            >
              <source src={videos[currentVideoIndex]} type="video/mp4" />
              Your browser does not support the video tag.
            </video>
            
            {/* Optional AI Scanning Overlay */}
            <div className="absolute inset-0 bg-[linear-gradient(rgba(20,184,166,0.1)_1px,transparent_1px),linear-gradient(90deg,rgba(20,184,166,0.1)_1px,transparent_1px)] bg-[size:40px_40px] pointer-events-none opacity-20"></div>
          </div>
        </div>

        {/* Telemetry Logs */}
        <div className="glass-panel rounded-3xl border border-slate-200 shadow-xl flex flex-col overflow-hidden bg-slate-900">
          <div className="bg-slate-950 px-5 py-4 border-b border-slate-800 flex items-center justify-between">
            <h3 className="text-slate-200 font-bold tracking-widest text-sm flex items-center gap-2">
              <Terminal className="w-4 h-4 text-teal-500" />
              SYSTEM LOGS
            </h3>
            {currentVideoIndex === 0 ? (
              <span className="text-xs font-bold text-orange-400 bg-orange-400/10 px-2 py-1 rounded border border-orange-400/20 flex items-center gap-1">
                 FALL DETECT
              </span>
            ) : (
              <span className="text-xs font-bold text-teal-400 bg-teal-400/10 px-2 py-1 rounded border border-teal-400/20 flex items-center gap-1">
                 BED ZONE
              </span>
            )}
          </div>
          
          <div className="flex-1 p-5 overflow-y-auto font-mono text-xs space-y-2 h-[500px]">
            {logs.map((log, i) => (
              <div 
                key={i} 
                className={clsx(
                  "animate-fade-in py-1 border-b border-slate-800/50 leading-relaxed",
                  log?.includes("[SYS]") && "text-slate-400",
                  log?.includes("[CAM]") && "text-slate-300",
                  log?.includes("[MODEL]") && "text-teal-400",
                  log?.includes("[DETECTION]") && "text-blue-300",
                  log?.includes("[POSTURE]") && "text-indigo-300",
                  log?.includes("DANGER") && "text-red-400 font-bold bg-red-950/30 px-2 rounded",
                  log?.includes("[ALERT]") && "text-orange-400",
                  log?.includes("[ZONE]") && "text-purple-400 font-bold",
                  log?.includes("[VITAL]") && "text-emerald-400",
                  log?.includes("[VOICE]") && "text-cyan-400 font-bold",
                  log?.includes("[TIMER]") && "text-yellow-400"
                )}
              >
                <span className="text-slate-600 mr-2">{new Date().toISOString().substring(11, 19)}</span>
                {log}
              </div>
            ))}
            <div ref={logEndRef} />
          </div>
        </div>
      </div>
    </div>
  );
}
