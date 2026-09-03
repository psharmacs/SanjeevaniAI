import { useState, useEffect, useRef } from 'react';
import { Shield, ShieldAlert, Activity, Eye, EyeOff } from 'lucide-react';
import clsx from 'clsx';

export default function Guardian() {
  const [state, setState] = useState(null);
  const [connected, setConnected] = useState(false);
  const [processedFrame, setProcessedFrame] = useState(null);
  
  const videoRef = useRef(null);
  const canvasRef = useRef(null);
  const wsRef = useRef(null);
  const streamIntervalRef = useRef(null);

  useEffect(() => {
    let ws;
    const connect = () => {
      ws = new WebSocket('ws://localhost:8000/ws');
      wsRef.current = ws;
      
      ws.onopen = async () => {
        setConnected(true);
        try {
          const stream = await navigator.mediaDevices.getUserMedia({ 
            video: { width: 320, height: 240, frameRate: { ideal: 24, max: 30 } } 
          });
          if (videoRef.current) {
            videoRef.current.srcObject = stream;
          }
          
          streamIntervalRef.current = setInterval(() => {
            if (videoRef.current && canvasRef.current && ws.readyState === WebSocket.OPEN) {
              const context = canvasRef.current.getContext('2d');
              context.drawImage(videoRef.current, 0, 0, 320, 240);
              const frameData = canvasRef.current.toDataURL('image/jpeg', 0.3);
              ws.send(frameData);
            }
          }, 50);
          
        } catch (err) {
          console.error("Camera access denied:", err);
        }
      };
      
      ws.onclose = () => {
        setConnected(false);
        if (streamIntervalRef.current) clearInterval(streamIntervalRef.current);
        setTimeout(connect, 2000);
      };
      
      ws.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          if (data.type === 'frame') {
            setProcessedFrame(`data:image/jpeg;base64,${data.image}`);
            setState(data.state);
          } else {
            setState(data);
          }
        } catch (e) {
          console.error(e);
        }
      };
    };
    connect();
    
    return () => {
      if (streamIntervalRef.current) clearInterval(streamIntervalRef.current);
      if (ws) ws.close();
      if (videoRef.current && videoRef.current.srcObject) {
        videoRef.current.srcObject.getTracks().forEach(track => track.stop());
      }
    };
  }, []);

  const togglePrivacy = async () => {
    const newMode = state?.overall_status !== 'PRIVACY_MODE';
    try {
      await fetch('http://localhost:8000/api/privacy', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ enabled: newMode })
      });
    } catch (e) {
      console.error(e);
    }
  };

  const isPrivacy = state?.overall_status === 'PRIVACY_MODE';
  const isEmergency = state?.overall_status === 'EMERGENCY' || state?.voice_emergency;
  const isDanger = state?.overall_status === 'DANGER';
  const overallStatus = state?.overall_status || 'OFFLINE';

  return (
    <div className="min-h-[calc(100vh-5rem)] p-6 max-w-7xl mx-auto flex flex-col bg-transparent">
      
      {/* Hidden elements for capturing webcam */}
      <video ref={videoRef} autoPlay playsInline muted className="hidden" />
      <canvas ref={canvasRef} width="640" height="480" className="hidden" />

      <header className="mb-8 flex justify-between items-end">
        <div>
          <h1 className="text-3xl font-medium tracking-wide text-slate-800 flex items-center gap-3">
            <Shield className="w-8 h-8 text-teal-600" />
            Guardian View
          </h1>
          <p className="text-slate-500 mt-2 font-medium">Continuous passive monitoring and fall detection powered by Sanjeevani AI. <br/>Keep an eye on your loved ones with privacy-first analysis.</p>
        </div>
        <button 
          onClick={togglePrivacy}
          className={clsx(
            "px-6 py-3 rounded-full font-bold tracking-wider text-sm transition-all shadow-md active:scale-95 flex items-center gap-2",
            isPrivacy 
              ? "bg-amber-100 text-amber-700 hover:bg-amber-200 border-2 border-amber-200"
              : "bg-teal-600 text-white hover:bg-teal-700 hover:shadow-teal-500/30"
          )}
        >
          {isPrivacy ? <Eye className="w-5 h-5" /> : <EyeOff className="w-5 h-5" />}
          {isPrivacy ? "DISABLE PRIVACY MODE" : "ENABLE PRIVACY MODE"}
        </button>
      </header>

      <div className="flex-1 grid grid-cols-1 lg:grid-cols-4 gap-6">
        
        {/* Main Feed */}
        <div className="lg:col-span-3 flex flex-col gap-6">
          <div className={clsx(
            "flex-1 rounded-[2.5rem] glass-panel overflow-hidden relative shadow-xl transition-all duration-500 border-2",
            isEmergency ? "border-red-500 shadow-[0_0_50px_rgba(239,68,68,0.3)]" :
            isDanger ? "border-amber-400 shadow-[0_0_30px_rgba(251,191,36,0.2)]" :
            "border-slate-200"
          )}>
            
            {/* Overlay Badges */}
            <div className="absolute top-6 left-6 z-10 flex gap-3">
              <div className="flex items-center gap-2 bg-slate-900/80 backdrop-blur-md text-white px-4 py-2 rounded-full border border-white/10 shadow-lg">
                {connected ? (
                  <>
                    <span className="w-2.5 h-2.5 bg-teal-400 rounded-full animate-pulse shadow-[0_0_10px_rgba(45,212,191,0.5)]"></span>
                    <span className="text-xs font-bold tracking-widest text-teal-50">AI ACTIVE</span>
                  </>
                ) : (
                  <>
                    <span className="w-2 h-2 bg-red-500 rounded-full"></span>
                    <span className="text-xs font-bold tracking-widest text-slate-300">DISCONNECTED</span>
                  </>
                )}
              </div>
            </div>

            {/* Video Feed */}
            <div className="w-full h-[600px] bg-slate-100 relative">
              {isPrivacy ? (
                <div className="absolute inset-0 flex flex-col items-center justify-center bg-slate-100/90 backdrop-blur-2xl z-20">
                  <EyeOff className="w-24 h-24 text-amber-500/50 mb-6" />
                  <h2 className="text-2xl font-bold text-slate-700 tracking-wider">CAMERA PAUSED</h2>
                  <p className="text-slate-500 mt-2 font-medium">Privacy mode active. AI is monitoring falls in the background.</p>
                </div>
              ) : connected && processedFrame ? (
                <img 
                  src={processedFrame} 
                  className="w-full h-full object-cover transition-opacity duration-500" 
                  alt="Guardian Live Feed"
                />
              ) : (
                <div className="absolute inset-0 flex items-center justify-center bg-slate-100">
                  <Activity className="w-12 h-12 text-slate-300 animate-pulse" />
                </div>
              )}
            </div>
          </div>
        </div>
        
        {/* Right Sidebar Status */}
        <div className="glass-panel rounded-[2.5rem] p-8 flex flex-col justify-center items-center text-center shadow-lg border border-slate-200">
            {overallStatus === 'SAFE' && <Shield className="w-20 h-20 mb-6 opacity-80 text-teal-500" />}
            {overallStatus === 'ANALYSING' && <Activity className="w-20 h-20 mb-6 opacity-80 animate-pulse text-amber-500" />}
            {(overallStatus === 'EMERGENCY' || overallStatus === 'DANGER') && <ShieldAlert className="w-20 h-20 mb-6 opacity-100 animate-bounce text-red-500" />}
            {overallStatus === 'PRIVACY_MODE' && <EyeOff className="w-20 h-20 mb-6 opacity-50 text-slate-500" />}
            {overallStatus === 'OFFLINE' && <ShieldAlert className="w-20 h-20 mb-6 opacity-30 text-slate-400" />}
            
            <h2 className="text-3xl font-bold tracking-widest mb-4">
              {overallStatus}
            </h2>
            <p className="text-slate-500 font-medium text-sm">
              {overallStatus === 'SAFE' && 'Sanjeevani is actively monitoring the environment.'}
              {overallStatus === 'ANALYSING' && 'System is analyzing sudden movement and posture changes.'}
              {(overallStatus === 'EMERGENCY' || overallStatus === 'DANGER') && 'Emergency protocol activated. Assistance may be required.'}
              {overallStatus === 'PRIVACY_MODE' && 'Camera and AI monitoring are currently paused.'}
              {overallStatus === 'OFFLINE' && 'Connecting to Sanjeevani backend...'}
            </p>
        </div>

      </div>
    </div>
  );
}
