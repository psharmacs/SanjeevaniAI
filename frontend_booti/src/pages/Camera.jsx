import { useState, useEffect, useRef } from 'react';
import { Terminal, Activity, Wifi, WifiOff, ShieldAlert, ServerOff, ArrowRight } from 'lucide-react';
import { Link } from 'react-router-dom';
import clsx from 'clsx';

export default function Camera() {
  const [state, setState] = useState(null);
  const [connected, setConnected] = useState(false);
  const [nodeOffline, setNodeOffline] = useState(false);
  const logEndRef = useRef(null);

  useEffect(() => {
    let ws;
    const connect = () => {
      ws = new WebSocket('ws://localhost:8000/ws');
      ws.onopen = () => setConnected(true);
      ws.onclose = () => {
        setConnected(false);
        // Only try to reconnect a few times or silently to avoid spamming the public user
        setTimeout(connect, 5000);
      };
      ws.onmessage = (event) => {
        try {
          setState(JSON.parse(event.data));
          setNodeOffline(false); // If we get data, it's definitely online
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

  // If websocket fails for more than a few seconds initially, we might consider the node offline.
  // We'll also rely on the image onError event as a surefire way to know if localhost:8000 is unreachable.

  return (
    <div className="min-h-[calc(100vh-5rem)] bg-transparent p-6 max-w-[1600px] mx-auto flex flex-col md:flex-row gap-6">
      
      {/* Left Column: Video */}
      <div className="flex-1 flex flex-col rounded-3xl glass-panel overflow-hidden relative border border-slate-200 shadow-xl">
        <div className="absolute top-0 left-0 right-0 p-6 flex justify-between items-start z-10 bg-gradient-to-b from-slate-50/90 to-transparent pointer-events-none">
          <div className="flex items-center gap-3 bg-white/80 backdrop-blur-md px-3 py-1.5 rounded-full border border-slate-200 shadow-sm">
            {connected ? <Wifi className="w-4 h-4 text-teal-600" /> : <WifiOff className="w-4 h-4 text-red-500" />}
            <span className="font-mono text-xs tracking-wider text-slate-700 font-bold">
              {connected ? 'NODE_CONNECTED' : 'NODE_DISCONNECTED'}
            </span>
          </div>
          {connected && (
            <div className="font-mono text-xs text-slate-700 font-bold bg-white/80 backdrop-blur-md px-3 py-1.5 rounded-full border border-slate-200 shadow-sm">
              FPS: {state?.fps || '0.0'}
            </div>
          )}
        </div>

        <div className="flex-1 relative bg-slate-100 flex items-center justify-center p-2 rounded-3xl overflow-hidden">
          {nodeOffline ? (
            <div className="flex flex-col items-center justify-center p-12 text-center max-w-lg mx-auto">
                <div className="w-24 h-24 bg-white rounded-full flex items-center justify-center shadow-lg border border-slate-100 mb-8 relative">
                   <div className="absolute inset-0 border-4 border-red-500 rounded-full animate-ping opacity-20"></div>
                   <ServerOff className="text-red-500 w-10 h-10 relative z-10" />
                </div>
                <h3 className="text-slate-800 text-3xl font-black tracking-tight mb-4">Edge Node Not Detected</h3>
                <p className="text-slate-600 text-lg leading-relaxed mb-8">
                  Access Restricted. This live monitoring module requires a Sanjeevani AI local hardware node to be active on your local network. 
                </p>
                <Link to="/live" className="inline-flex items-center gap-2 px-6 py-3 bg-teal-600 text-white font-bold rounded-full hover:bg-teal-700 transition-colors shadow-lg hover:shadow-xl shadow-teal-600/20">
                   View Simulation Instead <ArrowRight className="w-4 h-4" />
                </Link>
            </div>
          ) : connected ? (
             <img 
               src="http://localhost:8000/video_feed" 
               className="h-full w-full object-contain rounded-2xl border border-slate-200" 
               alt="Live Node Feed" 
               onError={() => setNodeOffline(true)}
             />
          ) : (
            <div className="text-slate-400 font-mono flex flex-col items-center">
              <Activity className="w-12 h-12 mb-4 animate-pulse opacity-50 text-slate-300" />
              CONNECTING TO EDGE NODE...
              {/* Fallback to offline if it takes too long */}
              <img 
               src="http://localhost:8000/video_feed" 
               style={{ display: 'none' }} 
               onError={() => setNodeOffline(true)}
               alt="ping"
              />
            </div>
          )}
        </div>
        
        {/* Bottom Bar overlay for critical status */}
        {state?.overall_status === 'EMERGENCY' && (
          <div className="absolute bottom-6 left-6 right-6 rounded-xl bg-red-500/95 backdrop-blur-md border border-red-400 text-white p-3 text-center font-bold tracking-widest uppercase animate-pulse shadow-[0_0_30px_rgba(239,68,68,0.3)]">
            FALL EMERGENCY CONFIRMED
          </div>
        )}
        {state?.voice_emergency && (
          <div className="absolute bottom-6 left-6 right-6 rounded-xl bg-red-500/95 backdrop-blur-md border border-red-400 text-white p-3 text-center font-bold tracking-widest uppercase animate-pulse shadow-[0_0_30px_rgba(239,68,68,0.3)]">
            VOICE EMERGENCY DETECTED
          </div>
        )}
      </div>

      {/* Right Column: Telemetry & Logs */}
      <div className="w-full md:w-[450px] flex flex-col gap-6 opacity-40 grayscale pointer-events-none transition-all duration-700" style={{ opacity: connected ? 1 : 0.4, filter: connected ? 'grayscale(0)' : 'grayscale(100%)' }}>
        
        {/* Telemetry Card */}
        <div className="glass-panel border border-slate-200 rounded-3xl p-6 flex-shrink-0 relative overflow-hidden shadow-xl">
          <div className="absolute top-0 right-0 p-4 opacity-[0.03]">
            <Activity className="w-32 h-32 text-slate-900" />
          </div>
          <h3 className="font-semibold tracking-widest text-slate-600 mb-6 flex items-center gap-2 text-sm">
            <Activity className="w-4 h-4 text-teal-600" /> LIVE TELEMETRY
          </h3>
          
          {state?.persons && state.persons.length > 0 ? (
            <div className="space-y-4 max-h-[300px] overflow-y-auto pr-2 custom-scrollbar relative z-10">
              {state.persons.map(p => (
                <div key={p.id} className={clsx("p-4 border rounded-2xl bg-white/50 backdrop-blur-sm transition-all shadow-sm", 
                  p.danger || p.fall_confirmed ? "border-red-400 shadow-[0_0_15px_rgba(239,68,68,0.15)] bg-red-50/50" : "border-slate-200"
                )}>
                  <div className="flex justify-between items-center mb-3">
                    <span className="font-mono font-bold text-slate-800">Target ID: {p.id}</span>
                    <span className={clsx("font-mono text-xs font-bold px-3 py-1 rounded-full border bg-white shadow-sm",
                       p.state === 'Standing' || p.state === 'Sitting' ? 'text-teal-600 border-teal-200' :
                       p.state === 'Recovery' ? 'text-blue-600 border-blue-200' :
                       p.state === 'Pre-Fall' || p.state === 'Falling' ? 'text-amber-600 border-amber-300' :
                       'text-red-600 border-red-300'
                    )}>
                      {p.state}
                    </span>
                  </div>
                  
                  <div className="grid grid-cols-2 gap-3 text-xs font-mono text-slate-500 bg-slate-50 p-3 rounded-xl border border-slate-200">
                    <div>Posture: <span className="text-slate-800 font-semibold">{p.posture}</span></div>
                    <div>Risk: <span className="text-slate-800 font-semibold">{p.risk_score.toFixed(2)}</span></div>
                    <div>Velocity: <span className="text-slate-800 font-semibold">{p.angular_velocity?.toFixed(1) || 0}°/s</span></div>
                    <div>Motion: <span className="text-slate-800 font-semibold">{p.is_lying_moving ? 'Yes' : 'No'}</span></div>
                  </div>
                  
                  {/* Risk Bar */}
                  <div className="mt-4 h-1.5 w-full bg-slate-200 rounded-full overflow-hidden border border-slate-100">
                     <div 
                       className={clsx("h-full transition-all duration-300", 
                         p.risk_score > 0.7 ? "bg-red-500" : p.risk_score > 0.4 ? "bg-amber-400" : "bg-teal-500"
                       )} 
                       style={{width: ${p.risk_score * 100}%}} 
                     />
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div className="text-center font-mono text-sm text-slate-400 py-6 border border-dashed border-slate-300 rounded-2xl bg-slate-50/50 relative z-10">
              NO TARGETS DETECTED
            </div>
          )}
        </div>

        {/* Logs Console */}
        <div className="flex-1 glass-panel border border-slate-200 rounded-3xl p-6 flex flex-col overflow-hidden shadow-xl">
           <h3 className="font-semibold tracking-widest text-slate-600 mb-4 flex items-center gap-2 text-sm">
            <Terminal className="w-4 h-4 text-slate-500" /> DECISION TRACE LOG
          </h3>
          <div className="flex-1 overflow-y-auto font-mono text-xs leading-relaxed text-slate-500 custom-scrollbar pr-3 bg-slate-50/50 rounded-2xl p-4 border border-slate-100">
            {state?.logs && state.logs.length > 0 ? (
               state.logs.map((log, i) => (
                 <div key={i} className="mb-3 pb-3 border-b border-slate-200/60 last:border-0 last:pb-0 last:mb-0">
                    <div className="flex items-start justify-between gap-2">
                      <span className={clsx("font-bold tracking-wider text-[11px]",
                        log.type === 'FALL' || log.type === 'DANGER' || log.type === 'VOICE_EMERGENCY' ? 'text-red-500' :
                        log.type === 'RECOVERY' ? 'text-blue-500' : 'text-amber-500'
                      )}>
                        [{log.type}]
                      </span>
                      <span className="text-slate-400 text-[10px]">{new Date(log.time * 1000).toLocaleTimeString([], {hour12: false, fractionalSecondDigits: 1})}</span>
                    </div>
                    <div className="mt-1 text-slate-600 font-medium">
                      Person ID: <span className="text-slate-900">{log.id}</span>
                      {log.risk_score !== undefined && <span className="opacity-60"> | Risk: </span>}
                      {log.risk_score !== undefined && <span className="text-slate-900">{log.risk_score.toFixed(3)}</span>}
                    </div>
                 </div>
               ))
            ) : (
               <div className="text-slate-400 mt-2 font-medium text-center italic">Waiting for events...</div>
            )}
            <div ref={logEndRef} />
          </div>
        </div>

      </div>
    </div>
  );
}