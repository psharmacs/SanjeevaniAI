import { useState, useEffect, useRef } from 'react';
import { Terminal, Activity, Wifi, WifiOff, AlertTriangle } from 'lucide-react';
import clsx from 'clsx';

export default function Live() {
  const [state, setState] = useState(null);
  const [connected, setConnected] = useState(false);
  const logEndRef = useRef(null);

  useEffect(() => {
    let ws;
    const connect = () => {
      ws = new WebSocket('ws://localhost:8000/ws');
      ws.onopen = () => setConnected(true);
      ws.onclose = () => {
        setConnected(false);
        setTimeout(connect, 2000);
      };
      ws.onmessage = (event) => {
        try {
          setState(JSON.parse(event.data));
        } catch (e) {
          console.error(e);
        }
      };
    };
    connect();
    return () => ws?.close();
  }, []);

  // Auto-scroll logs
  useEffect(() => {
    logEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [state?.logs]);

  return (
    <div className="h-[calc(100vh-4rem)] bg-black p-4 flex flex-col md:flex-row gap-4 overflow-hidden">
      
      {/* Left Column: Video */}
      <div className="flex-1 flex flex-col rounded-xl border border-gray-800 bg-gray-950 overflow-hidden relative shadow-2xl">
        <div className="absolute top-0 left-0 right-0 p-4 flex justify-between items-start z-10 bg-gradient-to-b from-black/80 to-transparent pointer-events-none">
          <div className="flex items-center gap-3">
            {connected ? <Wifi className="w-5 h-5 text-emerald-500" /> : <WifiOff className="w-5 h-5 text-red-500" />}
            <span className="font-mono text-sm tracking-wider text-gray-300">
              {connected ? 'WS_CONNECTED' : 'WS_DISCONNECTED'}
            </span>
          </div>
          <div className="font-mono text-sm text-gray-400">
            FPS: {state?.fps || '0.0'}
          </div>
        </div>

        <div className="flex-1 relative bg-gray-950 flex items-center justify-center">
          {connected ? (
             <img 
               src="http://localhost:8000/video_feed" 
               className="max-h-full max-w-full object-contain" 
               alt="Video Feed" 
             />
          ) : (
            <div className="text-gray-600 font-mono flex flex-col items-center">
              <Activity className="w-12 h-12 mb-4 animate-pulse opacity-50" />
              WAITING FOR STREAM...
            </div>
          )}
        </div>
        
        {/* Bottom Bar overlay for critical status */}
        {state?.overall_status === 'EMERGENCY' && (
          <div className="absolute bottom-0 left-0 right-0 bg-red-600 text-white p-2 text-center font-bold tracking-widest uppercase animate-pulse">
            FALL EMERGENCY CONFIRMED
          </div>
        )}
        {state?.voice_emergency && (
          <div className="absolute bottom-0 left-0 right-0 bg-red-600 text-white p-2 text-center font-bold tracking-widest uppercase animate-pulse">
            VOICE EMERGENCY DETECTED
          </div>
        )}
      </div>

      {/* Right Column: Telemetry & Logs */}
      <div className="w-full md:w-96 flex flex-col gap-4">
        
        {/* Telemetry Card */}
        <div className="bg-gray-950 border border-gray-800 rounded-xl p-4 flex-shrink-0">
          <h3 className="font-mono text-xs text-gray-500 mb-4 flex items-center gap-2">
            <Activity className="w-4 h-4" /> LIVE TELEMETRY
          </h3>
          
          {state?.persons && state.persons.length > 0 ? (
            <div className="space-y-4 max-h-[300px] overflow-y-auto pr-2 custom-scrollbar">
              {state.persons.map(p => (
                <div key={p.id} className={clsx("p-3 border rounded border-gray-800 bg-gray-900/50", 
                  p.danger || p.fall_confirmed ? "border-red-500/50" : ""
                )}>
                  <div className="flex justify-between items-center mb-2">
                    <span className="font-mono font-bold text-gray-300">Target ID: {p.id}</span>
                    <span className={clsx("font-mono text-xs font-bold px-2 py-0.5 rounded",
                       p.state === 'Standing' || p.state === 'Sitting' ? 'bg-emerald-500/20 text-emerald-400' :
                       p.state === 'Recovery' ? 'bg-teal-500/20 text-teal-400' :
                       p.state === 'Pre-Fall' || p.state === 'Falling' ? 'bg-amber-500/20 text-amber-400' :
                       'bg-red-500/20 text-red-500'
                    )}>
                      {p.state}
                    </span>
                  </div>
                  
                  <div className="grid grid-cols-2 gap-2 text-xs font-mono text-gray-400">
                    <div>Posture: <span className="text-gray-200">{p.posture}</span></div>
                    <div>Risk: <span className="text-gray-200">{p.risk_score.toFixed(2)}</span></div>
                    <div>Ang Vel: <span className="text-gray-200">{p.angular_velocity?.toFixed(1) || 0}°/s</span></div>
                    <div>Motion: <span className="text-gray-200">{p.is_lying_moving ? 'Yes' : 'No'}</span></div>
                  </div>
                  
                  {/* Risk Bar */}
                  <div className="mt-3 h-1.5 w-full bg-gray-800 rounded-full overflow-hidden">
                     <div 
                       className={clsx("h-full transition-all duration-300", 
                         p.risk_score > 0.7 ? "bg-red-500" : p.risk_score > 0.4 ? "bg-amber-400" : "bg-emerald-400"
                       )} 
                       style={{width: `${p.risk_score * 100}%`}} 
                     />
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div className="text-center font-mono text-sm text-gray-600 py-4 border border-dashed border-gray-800 rounded">
              NO TARGETS DETECTED
            </div>
          )}
        </div>

        {/* Logs Console */}
        <div className="flex-1 bg-gray-950 border border-gray-800 rounded-xl p-4 flex flex-col overflow-hidden">
           <h3 className="font-mono text-xs text-gray-500 mb-2 flex items-center gap-2">
            <Terminal className="w-4 h-4" /> DECISION TRACE LOG
          </h3>
          <div className="flex-1 overflow-y-auto font-mono text-[11px] leading-tight text-gray-400 custom-scrollbar pr-2">
            {state?.logs && state.logs.length > 0 ? (
               state.logs.map((log, i) => (
                 <div key={i} className="mb-2 pb-2 border-b border-gray-800/50">
                    <div className="flex items-start gap-2">
                      <span className="text-gray-600">{new Date(log.time * 1000).toLocaleTimeString([], {hour12: false})}</span>
                      <span className={clsx(
                        log.type === 'FALL' || log.type === 'DANGER' || log.type === 'VOICE_EMERGENCY' ? 'text-red-400 font-bold' :
                        log.type === 'RECOVERY' ? 'text-teal-400' : 'text-amber-400'
                      )}>
                        [{log.type}]
                      </span>
                    </div>
                    <div className="ml-16 mt-0.5 text-gray-300">
                      Person ID: {log.id} 
                      {log.risk_score !== undefined && ` | Risk: ${log.risk_score}`}
                      {log.command && ` | Cmd: ${log.command}`}
                    </div>
                 </div>
               ))
            ) : (
               <div className="text-gray-600 mt-2">Waiting for events...</div>
            )}
            <div ref={logEndRef} />
          </div>
        </div>

      </div>
    </div>
  );
}
