import { useState, useEffect, useRef } from 'react';
import { Shield, ShieldAlert, Activity, Eye, Mic, Clock, CameraOff, Video } from 'lucide-react';
import clsx from 'clsx';

export default function Guardian() {
  const [overallStatus, setOverallStatus] = useState('OFFLINE');
  const [eventHistory, setEventHistory] = useState([]);
  const previousStatusRef = useRef('SAFE');

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
            ].slice(0, 5));
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

  const isDanger = overallStatus === 'EMERGENCY' || overallStatus === 'DANGER';

  return (
    <div className="min-h-[calc(100vh-4rem)] p-4 md:p-8 bg-[#f8f9fa] flex justify-center">
      <div className="max-w-md w-full flex flex-col gap-6">
        
        {/* Top Bar */}
        <div className="flex items-center justify-between px-2 pt-4">
          <div>
            <h1 className="text-2xl font-medium tracking-tight text-gray-900">Living Room</h1>
            <p className="text-sm text-gray-500 mt-1">Sanjeevani Guardian</p>
          </div>
          <div className="w-12 h-12 rounded-full overflow-hidden border-2 border-white shadow-sm bg-gray-200 flex items-center justify-center">
            <Shield className="w-6 h-6 text-gray-400" />
          </div>
        </div>

        {/* Main Status Card */}
        <div className="bg-white rounded-[1.5rem] shadow-[0_4px_24px_rgba(0,0,0,0.04)] border border-gray-100 p-6 flex flex-col items-center justify-center text-center mt-2 relative overflow-hidden">
          {overallStatus === 'SAFE' && (
            <div className="absolute top-0 right-0 w-32 h-32 bg-green-100 rounded-full blur-3xl opacity-60 translate-x-10 -translate-y-10"></div>
          )}
          {isDanger && (
            <div className="absolute top-0 right-0 w-32 h-32 bg-red-100 rounded-full blur-3xl opacity-60 translate-x-10 -translate-y-10"></div>
          )}
          
          <div className={clsx(
            "w-20 h-20 rounded-full flex items-center justify-center mb-4 shadow-sm z-10 transition-colors",
            overallStatus === 'SAFE' ? "bg-green-50 text-green-600" :
            overallStatus === 'ANALYSING' ? "bg-amber-50 text-amber-600 animate-pulse" :
            overallStatus === 'PRIVACY_MODE' ? "bg-gray-100 text-gray-500" :
            overallStatus === 'OFFLINE' ? "bg-gray-100 text-gray-400" :
            "bg-red-50 text-red-600 animate-bounce"
          )}>
            {overallStatus === 'SAFE' ? <Shield className="w-10 h-10" /> :
             overallStatus === 'PRIVACY_MODE' ? <CameraOff className="w-10 h-10" /> :
             overallStatus === 'OFFLINE' ? <ShieldAlert className="w-10 h-10 opacity-50" /> :
             <ShieldAlert className="w-10 h-10" />}
          </div>
          
          <h2 className="text-3xl font-medium text-gray-900 z-10 capitalize">
            {overallStatus === 'SAFE' ? 'Safe & Quiet' :
             overallStatus === 'PRIVACY_MODE' ? 'Monitoring Paused' :
             overallStatus === 'OFFLINE' ? 'Connecting...' :
             overallStatus}
          </h2>
          <p className="text-gray-500 mt-2 z-10 text-sm max-w-[250px]">
            {overallStatus === 'SAFE' ? 'No unusual activity detected in the room.' :
             overallStatus === 'ANALYSING' ? 'Analyzing movement patterns.' :
             isDanger ? 'Emergency protocol activated. Assistance required.' :
             'Camera and AI are currently off.'}
          </p>
          
          <div className="inline-flex items-center gap-2 mt-6 px-4 py-2 bg-gray-50 rounded-full border border-gray-100 z-10">
            <div className={clsx(
              "w-2 h-2 rounded-full",
              overallStatus === 'SAFE' ? "bg-green-500 animate-pulse" :
              overallStatus === 'PRIVACY_MODE' || overallStatus === 'OFFLINE' ? "bg-gray-400" :
              "bg-red-500 animate-pulse"
            )}></div>
            <span className="text-xs font-medium text-gray-600 uppercase tracking-wider">
              {overallStatus === 'PRIVACY_MODE' || overallStatus === 'OFFLINE' ? 'System Inactive' : 'Live Monitoring On'}
            </span>
          </div>
        </div>

        {/* Quick Actions Grid */}
        <div className="grid grid-cols-2 gap-4">
          <a href="/live" className="bg-white rounded-[1.5rem] shadow-sm border border-gray-100 p-4 flex flex-col items-start hover:bg-gray-50 transition-colors text-left group">
            <div className="w-10 h-10 rounded-full bg-gray-50 flex items-center justify-center mb-3 group-hover:bg-blue-50 group-hover:text-blue-600 transition-colors">
              <Video className="w-5 h-5 text-gray-500 group-hover:text-blue-600" />
            </div>
            <span className="font-medium text-gray-900">View Camera</span>
            <span className="text-xs text-gray-500 mt-1">Tap for live feed</span>
          </a>

          <button onClick={togglePrivacy} className="bg-white rounded-[1.5rem] shadow-sm border border-gray-100 p-4 flex flex-col items-start hover:bg-gray-50 transition-colors text-left group">
            <div className="w-10 h-10 rounded-full bg-gray-50 flex items-center justify-center mb-3 group-hover:bg-purple-50 group-hover:text-purple-600 transition-colors">
              <CameraOff className="w-5 h-5 text-gray-500 group-hover:text-purple-600" />
            </div>
            <span className="font-medium text-gray-900">{overallStatus === 'PRIVACY_MODE' ? 'Resume' : 'Privacy Mode'}</span>
            <span className="text-xs text-gray-500 mt-1">Pause monitoring</span>
          </button>
        </div>

        {/* Event Timeline */}
        <div className="bg-white rounded-[1.5rem] shadow-sm border border-gray-100 p-6">
          <h3 className="font-medium text-gray-900 mb-6 flex items-center gap-2">
            <Clock className="w-5 h-5 text-gray-400" />
            Recent Activity
          </h3>
          
          <div className="space-y-4">
            {eventHistory.length === 0 ? (
              <p className="text-sm text-gray-500 text-center py-4">No recent events.</p>
            ) : (
              eventHistory.map((ev, i) => (
                <div key={i} className="flex gap-4">
                  <div className="flex flex-col items-center">
                    <div className={clsx(
                      "w-3 h-3 rounded-full mt-1.5",
                      ev.status === 'SAFE' ? 'bg-green-500' :
                      ev.status === 'ANALYSING' ? 'bg-amber-500' :
                      ev.status === 'PRIVACY_MODE' ? 'bg-gray-400' : 'bg-red-500'
                    )}></div>
                    {i !== eventHistory.length - 1 && (
                      <div className="w-px h-full bg-gray-100 my-1"></div>
                    )}
                  </div>
                  <div className="pb-4">
                    <p className="text-sm font-medium text-gray-900">{ev.status}</p>
                    <p className="text-xs text-gray-400 mt-0.5">{ev.time}</p>
                  </div>
                </div>
              ))
            )}
          </div>
        </div>

      </div>
    </div>
  );
}
