import { useState, useEffect, useRef } from 'react';
import { motion } from 'framer-motion';
import { Shield, ShieldAlert, Activity, Eye, Mic } from 'lucide-react';
import clsx from 'clsx';

export default function Guardian() {
  const [overallStatus, setOverallStatus] = useState('OFFLINE');
  const [eventHistory, setEventHistory] = useState([]);
  const previousStatusRef = useRef('SAFE');

  const getStatusColor = (status) => {
    switch(status) {
      case 'SAFE': return 'text-emerald-400 bg-emerald-400/10 border-emerald-500/20';
      case 'ANALYSING': return 'text-amber-400 bg-amber-400/10 border-amber-500/20';
      case 'EMERGENCY': 
      case 'DANGER': return 'text-red-500 bg-red-500/10 border-red-500/20';
      case 'PRIVACY_MODE': return 'text-gray-400 bg-gray-800 border-gray-700';
      default: return 'text-gray-400 bg-gray-800 border-gray-700';
    }
  };

  const getStatusText = (status) => {
    switch(status) {
      case 'SAFE': return 'EVERYTHING LOOKS NORMAL';
      case 'ANALYSING': return 'UNUSUAL ACTIVITY DETECTED';
      case 'EMERGENCY': return 'FALL CONFIRMED';
      case 'DANGER': return 'DANGER DETECTED (LYING STILL)';
      case 'PRIVACY_MODE': return 'PRIVACY MODE ACTIVE';
      default: return 'SYSTEM OFFLINE';
    }
  };

  useEffect(() => {
    const ws = new WebSocket('ws://localhost:8000/ws');
    
    ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        const newStatus = data.overall_status || 'SAFE';
        setOverallStatus(newStatus);
        
        if (newStatus && newStatus !== previousStatusRef.current) {
          if (newStatus !== 'OFFLINE') {
            setEventHistory(prev => [
              { time: new Date().toLocaleTimeString([], {hour: '2-digit', minute:'2-digit', second:'2-digit'}), status: newStatus },
              ...prev
            ].slice(0, 10));
          }
          previousStatusRef.current = newStatus;
        }
      } catch (e) {
        console.error(e);
      }
    };

    ws.onclose = () => {
      setOverallStatus('OFFLINE');
      previousStatusRef.current = 'OFFLINE';
    };

    return () => ws.close();
  }, []);

  const togglePrivacy = async () => {
    try {
      await fetch('http://localhost:8000/api/privacy', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ enabled: overallStatus !== 'PRIVACY_MODE' })
      });
    } catch (e) {
      console.error(e);
    }
  };

  return (
    <div className="min-h-[calc(100vh-4rem)] p-6 md:p-12 max-w-7xl mx-auto flex flex-col">
      <header className="mb-12 flex justify-between items-end">
        <div>
          <h1 className="text-3xl font-light tracking-wide text-gray-300">Guardian View</h1>
          <p className="text-gray-500 mt-2">Human-friendly safety overview.</p>
        </div>
        <button 
          onClick={togglePrivacy}
          className={clsx(
            "px-6 py-3 rounded-full font-semibold flex items-center gap-2 transition-all border",
            overallStatus === 'PRIVACY_MODE' 
              ? "bg-gray-800 text-gray-300 border-gray-600 hover:bg-gray-700" 
              : "bg-emerald-500/10 text-emerald-400 border-emerald-500/20 hover:bg-emerald-500/20"
          )}
        >
          <Eye className="w-5 h-5" />
          {overallStatus === 'PRIVACY_MODE' ? 'Resume Monitoring' : 'Enable Privacy Mode'}
        </button>
      </header>

      <div className="flex-1 grid grid-cols-1 lg:grid-cols-3 gap-8">
        
        {/* Left Column: Big Status */}
        <div className={clsx(
          "lg:col-span-2 rounded-3xl border flex flex-col items-center justify-center p-12 transition-colors duration-1000",
          getStatusColor(overallStatus)
        )}>
          {overallStatus === 'SAFE' && <Shield className="w-24 h-24 mb-6 opacity-80" />}
          {overallStatus === 'ANALYSING' && <Activity className="w-24 h-24 mb-6 opacity-80 animate-pulse" />}
          {(overallStatus === 'EMERGENCY' || overallStatus === 'DANGER') && <ShieldAlert className="w-24 h-24 mb-6 opacity-100 animate-bounce" />}
          {overallStatus === 'PRIVACY_MODE' && <Eye className="w-24 h-24 mb-6 opacity-50" />}
          {overallStatus === 'OFFLINE' && <ShieldAlert className="w-24 h-24 mb-6 opacity-30" />}
          
          <h2 className="text-4xl font-bold tracking-widest mb-4">
            {overallStatus}
          </h2>
          <p className="text-xl text-gray-400 text-center max-w-md">
            {overallStatus === 'SAFE' && 'Sanjeevani is actively monitoring the environment.'}
            {overallStatus === 'ANALYSING' && 'System is analyzing sudden movement and posture changes.'}
            {(overallStatus === 'EMERGENCY' || overallStatus === 'DANGER') && 'Emergency protocol activated. Assistance may be required.'}
            {overallStatus === 'PRIVACY_MODE' && 'Camera and AI monitoring are currently paused.'}
            {overallStatus === 'OFFLINE' && 'Connecting to Sanjeevani backend...'}
          </p>
        </div>

        {/* Right Column: Live Feed & Timeline */}
        <div className="flex flex-col gap-6 h-full">
          <div className="bg-gray-900 border border-gray-800 rounded-3xl overflow-hidden relative aspect-video flex-shrink-0">
            <div className="absolute top-4 left-4 z-10 flex items-center gap-2 bg-black/50 backdrop-blur-md px-3 py-1.5 rounded-full border border-gray-700">
              <div className={clsx("w-2 h-2 rounded-full", overallStatus === 'OFFLINE' ? "bg-red-500" : "bg-emerald-500 animate-pulse")} />
              <span className="text-xs font-semibold text-gray-200 tracking-wider">LIVE</span>
            </div>
            {overallStatus === 'PRIVACY_MODE' ? (
              <div className="w-full h-full bg-gray-950 flex items-center justify-center text-gray-600 font-medium">
                CAMERA PAUSED
              </div>
            ) : (
              <img 
                src="http://localhost:8000/video_feed" 
                alt="Live AI Feed" 
                className="w-full h-full object-cover opacity-80 grayscale contrast-125"
                onError={(e) => { e.target.style.display = 'none'; }}
              />
            )}
          </div>

          <div className="bg-gray-900/50 border border-gray-800 rounded-3xl p-6 flex-1 flex flex-col min-h-[300px]">
            <h3 className="text-sm font-semibold tracking-widest text-gray-500 mb-6 flex items-center gap-2">
              <Activity className="w-4 h-4" />
              EVENT TIMELINE
            </h3>
            
            <div className="flex-1 overflow-y-auto pr-2 space-y-6">
              {eventHistory.length === 0 ? (
                <p className="text-gray-600 text-sm text-center mt-10">No recent events.</p>
              ) : (
                eventHistory.map((ev, i) => (
                  <div key={i} className="relative pl-6">
                    {i !== eventHistory.length - 1 && (
                      <div className="absolute left-[7px] top-5 bottom-[-24px] w-px bg-gray-800" />
                    )}
                    <div className={clsx(
                      "absolute left-0 top-1.5 w-4 h-4 rounded-full border-2 border-gray-900 shadow-[0_0_10px_rgba(0,0,0,0.5)]",
                      ev.status === 'SAFE' ? 'bg-emerald-500' :
                      ev.status === 'ANALYSING' ? 'bg-amber-500' :
                      ev.status === 'PRIVACY_MODE' ? 'bg-gray-500' : 'bg-red-500'
                    )} />
                    
                    <div className="flex justify-between items-start mb-1">
                      <span className={clsx(
                        "text-sm font-bold tracking-wider",
                        ev.status === 'SAFE' ? 'text-emerald-400' :
                        ev.status === 'ANALYSING' ? 'text-amber-400' :
                        ev.status === 'PRIVACY_MODE' ? 'text-gray-400' : 'text-red-400'
                      )}>
                        {ev.status}
                      </span>
                      <span className="text-xs text-gray-500 font-mono">{ev.time}</span>
                    </div>
                    <p className="text-xs text-gray-400">
                      {getStatusText(ev.status)}
                    </p>
                  </div>
                ))
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
