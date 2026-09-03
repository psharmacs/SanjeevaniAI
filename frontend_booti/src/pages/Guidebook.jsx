import React from 'react';
import { BookOpen, Presentation, Code2, Network, ShieldCheck, ArrowDown, BrainCircuit } from 'lucide-react';

export default function Guidebook() {
  const workflowSteps = [
    { title: "CAMERA", icon: "📷", desc: "Captures local video feed" },
    { title: "OpenCV", icon: "👁️", desc: "Frame extraction & processing" },
    { title: "YOLO", icon: "🎯", desc: "Person Detection" },
    { title: "MediaPipe", icon: "🧍", desc: "33 Body Landmarks" },
    { title: "Temporal Analysis", icon: "⏱️", desc: "Movement + Velocity" },
    { title: "Risk Engine", icon: "⚠️", desc: "Risk Score 0-1" },
    { title: "Safe Zone Check", icon: "🛏️", desc: "Bed / Normal Area" },
    { title: "FSM", icon: "🔄", desc: "SAFE / ANALYSING / DANGER / EMERGENCY" }
  ];

  return (
    <div className="min-h-[calc(100vh-5rem)] p-6 max-w-5xl mx-auto flex flex-col bg-transparent pb-24">
      
      <header className="mb-12 flex flex-col md:flex-row justify-between items-start md:items-end gap-6">
        <div>
          <div className="inline-flex items-center gap-2 bg-teal-50 text-teal-700 px-4 py-2 rounded-full font-bold text-sm tracking-widest mb-4 border border-teal-100 shadow-sm">
            <BookOpen className="w-4 h-4" />
            PROJECT DOCUMENTATION
          </div>
          <h1 className="text-4xl font-black tracking-widest text-slate-800">
            THE GUIDEBOOK
          </h1>
          <p className="text-slate-500 mt-3 font-medium text-lg max-w-xl">
            Technical architecture, vision, and presentation materials for Sanjeevani AI.
          </p>
        </div>
        
        {/* Animated Pop PPT Button */}
        <a 
          href="/SIH_Team_Prometheus.pptx" 
          target="_blank" 
          rel="noopener noreferrer"
          className="group px-8 py-4 bg-teal-600 text-white rounded-2xl font-bold tracking-wider transition-all duration-300 hover:scale-105 hover:bg-teal-700 hover:shadow-[0_0_30px_rgba(13,148,136,0.4)] flex items-center gap-3 shrink-0 animate-bounce shadow-xl"
        >
          <Presentation className="w-6 h-6" />
          VIEW PRESENTATION
        </a>
      </header>

      {/* AI Model Workflow Section */}
      <div className="glass-panel rounded-[2.5rem] border border-slate-200 p-10 shadow-lg mb-16">
        <h2 className="text-2xl font-black tracking-widest text-slate-800 mb-8 text-center flex items-center justify-center gap-3">
          <BrainCircuit className="w-8 h-8 text-teal-600" />
          Sanjeevani AI Model Workflow
        </h2>
        
        <div className="max-w-2xl mx-auto flex flex-col items-center">
          {workflowSteps.map((step, index) => (
            <React.Fragment key={index}>
              <div className="w-full bg-white border border-slate-200 rounded-2xl p-4 flex items-center justify-between shadow-sm hover:border-teal-300 transition-colors group">
                <div className="flex items-center gap-4">
                  <span className="text-2xl">{step.icon}</span>
                  <span className="font-bold text-slate-700 tracking-wider group-hover:text-teal-700 transition-colors">{step.title}</span>
                </div>
                <span className="text-sm font-medium text-slate-400">{step.desc}</span>
              </div>
              
              {index < workflowSteps.length - 1 && (
                <div className="py-2 text-teal-300 animate-pulse">
                  <ArrowDown className="w-5 h-5" />
                </div>
              )}
            </React.Fragment>
          ))}
        </div>
      </div>

      {/* Hardware Device Integration Section */}
      <div className="glass-panel rounded-[2.5rem] border border-slate-200 p-10 shadow-lg mb-16 overflow-hidden">
        <h2 className="text-2xl font-black tracking-widest text-slate-800 mb-4 text-center flex items-center justify-center gap-3">
          <span className="text-2xl">⌚</span> Sanjeevani Smart Wearable
        </h2>
        <p className="text-center text-slate-600 font-medium mb-8 max-w-2xl mx-auto">
          Our intelligent Bed Zone feature seamlessly syncs with this dedicated hardware device to pull continuous vitals (Heart Rate & SpO2) and monitor for dangerous drops or surges.
        </p>
        <div className="rounded-2xl overflow-hidden border border-slate-200 shadow-md">
          <img src="/hardware.png" alt="Sanjeevani Smart Wearable Device Features" className="w-full h-auto object-cover hover:scale-[1.02] transition-transform duration-500" />
        </div>
      </div>

      {/* Deep Dive Content from PDF */}
      <div className="space-y-12">
        <section className="glass-panel p-10 rounded-[2.5rem] border border-slate-200 shadow-md">
          <h2 className="text-2xl font-bold text-slate-800 mb-4 border-b pb-4 border-slate-200">The Problem & Our Vision</h2>
          <p className="text-slate-600 leading-relaxed mb-4">
            Imagine an elderly person living alone. They suddenly lose balance and fall. The fall itself may take only a few seconds, but the dangerous part can be what happens afterwards: nobody may know that the person needs help.
          </p>
          <p className="text-slate-600 leading-relaxed mb-4">
            Existing cameras can record an incident, but recording is not the same as understanding. A safety system should not merely capture what happened — it should recognize when something abnormal is happening and help trigger a response.
          </p>
          <p className="text-slate-600 leading-relaxed font-bold text-teal-700 bg-teal-50 p-4 rounded-xl">
            Sanjeevani AI turns a normal camera feed into an intelligent monitoring layer. Instead of asking only, "Is there a person?", our system asks: "What is the person doing, how has their posture changed, and does the sequence indicate a possible fall?"
          </p>
        </section>

        <section className="glass-panel p-10 rounded-[2.5rem] border border-slate-200 shadow-md">
          <h2 className="text-2xl font-bold text-slate-800 mb-4 border-b pb-4 border-slate-200">Core Fall Detection & Temporal Intelligence</h2>
          <h3 className="text-lg font-bold text-slate-700 mt-6 mb-2">How a Fall Looks to the System</h3>
          <p className="text-slate-600 leading-relaxed mb-4">
            A fall is usually a transition, not a static pose. A typical pattern can be represented as: <span className="font-bold text-slate-800">Upright posture → rapid movement → significant body-angle change → horizontal or low posture → possible post-fall state.</span>
          </p>
          <h3 className="text-lg font-bold text-slate-700 mt-6 mb-2">The False-Alarm Problem</h3>
          <p className="text-slate-600 leading-relaxed mb-4">
            Suppose a person intentionally lies on a bed. A frame-based system may see a horizontal body and immediately say "Fall detected." That creates a false alarm. Our principle is simple: <strong>never trust one frame when the problem itself is temporal.</strong>
          </p>
          <p className="text-slate-600 leading-relaxed">
            Sanjeevani AI looks at a sequence of observations. We maintain posture history and analyze changes over time. The reasoning becomes: What was the previous posture? Did movement suddenly increase? Did the body orientation change significantly? Is the new posture persistent?
          </p>
        </section>

        <section className="glass-panel p-10 rounded-[2.5rem] border border-slate-200 shadow-md">
          <h2 className="text-2xl font-bold text-slate-800 mb-4 border-b pb-4 border-slate-200">Decision Engine & Alert System</h2>
          <p className="text-slate-600 leading-relaxed mb-4">
            The system combines evidence from posture, angle change, movement and temporal history. Our rule engine checks whether the observed sequence is consistent with a fall.
          </p>
          <div className="bg-slate-50 border border-slate-200 p-6 rounded-2xl mb-4">
            <h4 className="font-bold text-slate-700 mb-2">Confirmation Before Escalation</h4>
            <p className="text-slate-600 text-sm">
              We do not want every unusual frame to become an emergency alert. At the same time, we do not want unnecessary delays. The system therefore aims for a balance between speed and reliability. After an alert is generated, a cooldown mechanism helps prevent repeated alerts for the same event to avoid alert fatigue.
            </p>
          </div>
        </section>

        <section className="glass-panel p-10 rounded-[2.5rem] border border-slate-200 shadow-md">
          <h2 className="text-2xl font-bold text-slate-800 mb-4 border-b pb-4 border-slate-200 flex items-center gap-2">
            <span className="text-orange-500">⚠️</span> Fall Detection & Intelligent Escalation
          </h2>
          
          <p className="text-slate-600 leading-relaxed mb-8">
            Sanjeevani AI follows a progressive 3-level escalation mechanism to respond to a potentially dangerous situation. Each level is triggered based on the duration of the confirmed <span className="font-bold text-red-500">DANGER</span> state and the person's response.
          </p>

          <div className="space-y-8">
            {/* Level 1 */}
            <div className="bg-white border border-slate-200 p-6 rounded-2xl shadow-sm relative overflow-hidden">
              <div className="absolute top-0 left-0 w-2 h-full bg-amber-400"></div>
              <h3 className="text-xl font-black text-amber-600 mb-4 ml-4">Level 1 – Voice Check-In</h3>
              
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6 ml-4">
                <div>
                  <h4 className="font-bold text-slate-700 mb-2">When is it triggered?</h4>
                  <ul className="list-disc list-outside ml-4 space-y-1 text-sm text-slate-600">
                    <li>The system first detects that the person is LYING continuously for 20 seconds.</li>
                    <li>After this 20-second confirmation, the system state changes to DANGER.</li>
                    <li>Level 1 is triggered immediately when DANGER begins.</li>
                  </ul>
                </div>
                <div>
                  <h4 className="font-bold text-slate-700 mb-2">How is it triggered?</h4>
                  <div className="flex flex-wrap items-center gap-2 text-xs font-bold text-slate-600 mb-3">
                    <span className="bg-slate-100 px-2 py-1 rounded">Continuous Lying (20s)</span>
                    <span>→</span>
                    <span className="bg-red-50 text-red-600 px-2 py-1 rounded border border-red-100">DANGER Confirmed</span>
                    <span>→</span>
                    <span className="bg-amber-50 text-amber-600 px-2 py-1 rounded border border-amber-100">Level 1 Starts</span>
                  </div>
                  <ul className="list-disc list-outside ml-4 space-y-1 text-sm text-slate-600">
                    <li>The system asks the person: <strong>"Are you okay?"</strong></li>
                    <li>The system listens for a response for up to 10 seconds.</li>
                  </ul>
                </div>
              </div>
              
              <div className="mt-6 ml-4 bg-slate-50 p-4 rounded-xl border border-slate-200">
                <h4 className="font-bold text-slate-700 mb-3">Possible Outcomes</h4>
                <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
                  <div className="bg-green-50 p-3 rounded-lg border border-green-100">
                    <span className="block font-bold text-green-700 text-sm mb-1">"YES" / "I'm okay"</span>
                    <span className="text-xs text-green-800/80">DANGER cleared. Escalation stops.</span>
                  </div>
                  <div className="bg-orange-50 p-3 rounded-lg border border-orange-100">
                    <span className="block font-bold text-orange-700 text-sm mb-1">"NO" / "Help"</span>
                    <span className="text-xs text-orange-800/80">Level 2 triggered immediately.</span>
                  </div>
                  <div className="bg-red-50 p-3 rounded-lg border border-red-100">
                    <span className="block font-bold text-red-700 text-sm mb-1">No / Unclear Response</span>
                    <span className="text-xs text-red-800/80">Level 2 triggered immediately.</span>
                  </div>
                </div>
              </div>
            </div>

            {/* Level 2 */}
            <div className="bg-white border border-slate-200 p-6 rounded-2xl shadow-sm relative overflow-hidden">
              <div className="absolute top-0 left-0 w-2 h-full bg-orange-500"></div>
              <h3 className="text-xl font-black text-orange-600 mb-4 ml-4">Level 2 – Caregiver Notification</h3>
              
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6 ml-4">
                <div>
                  <h4 className="font-bold text-slate-700 mb-2">When is it triggered?</h4>
                  <div className="space-y-4">
                    <div>
                      <span className="font-bold text-orange-700 text-sm">A. User-Response Trigger</span>
                      <p className="text-xs text-slate-600 mt-1">The person responds "No", "Help", OR gives no valid response. Level 2 is triggered immediately after Level 1 check-in.</p>
                    </div>
                    <div>
                      <span className="font-bold text-orange-700 text-sm">B. Time-Based Trigger</span>
                      <p className="text-xs text-slate-600 mt-1">If the danger condition continues, Level 2 is normally triggered 20 seconds after the start of the DANGER episode.</p>
                    </div>
                  </div>
                </div>
                <div>
                  <h4 className="font-bold text-slate-700 mb-2">How is it triggered?</h4>
                  <ul className="list-disc list-outside ml-4 space-y-1 text-sm text-slate-600 mb-4">
                    <li>DANGER state remains active.</li>
                    <li>Level 1 check-in fails or timer reaches threshold.</li>
                    <li>Level 2 is activated & caregiver notification initiated.</li>
                  </ul>
                  <div className="bg-orange-50 border border-orange-200 p-3 rounded-lg">
                    <span className="block text-xs font-bold text-orange-800 uppercase tracking-wider mb-1">Current Implementation</span>
                    <span className="text-sm text-orange-700">SMS & Voice Call sent to registered caretaker number.</span>
                  </div>
                </div>
              </div>
            </div>

            {/* Level 3 */}
            <div className="bg-white border border-slate-200 p-6 rounded-2xl shadow-sm relative overflow-hidden">
              <div className="absolute top-0 left-0 w-2 h-full bg-red-600"></div>
              <h3 className="text-xl font-black text-red-600 mb-4 ml-4">Level 3 – Emergency Escalation</h3>
              
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6 ml-4">
                <div>
                  <h4 className="font-bold text-slate-700 mb-2">When is it triggered?</h4>
                  <ul className="list-disc list-outside ml-4 space-y-1 text-sm text-slate-600">
                    <li>Triggered when the DANGER condition continuously persists for <strong>60 seconds</strong> from the beginning of the episode.</li>
                    <li>The system must remain in DANGER; any recovery or clearance prevents the escalation.</li>
                  </ul>
                </div>
                <div>
                  <h4 className="font-bold text-slate-700 mb-2">How is it triggered?</h4>
                  <ul className="list-disc list-outside ml-4 space-y-1 text-sm text-slate-600">
                    <li>Levels 1 and 2 have already been triggered.</li>
                    <li>Person remains in unresolved DANGER state.</li>
                    <li>After 60s of sustained DANGER, Level 3 is activated.</li>
                  </ul>
                  <div className="mt-4 bg-red-50 border border-red-200 p-3 rounded-lg inline-block">
                    <span className="text-sm text-red-700 font-bold flex items-center gap-2">
                      <span>🚑</span> Calls Helpline Number (Ambulance)
                    </span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </section>

        <section className="glass-panel p-10 rounded-[2.5rem] border border-slate-200 shadow-md">
          <h2 className="text-2xl font-bold text-slate-800 mb-4 border-b pb-4 border-slate-200 flex items-center gap-2">
            <span className="text-red-500">❤️</span> Heart Rate + <span className="text-teal-600">🛏️</span> Bed-Zone Monitoring
          </h2>
          
          <div className="mb-8">
            <h3 className="text-lg font-bold text-slate-800 mb-2">Why do we need it?</h3>
            <p className="text-slate-600 leading-relaxed">
              The purpose is to monitor an elderly person only when they are in the bed and detect unusual heart-rate behavior. This helps avoid unnecessary monitoring and alerts when the person is outside the monitored area.
            </p>
          </div>

          <div className="mb-8">
            <h3 className="text-lg font-bold text-slate-800 mb-4">How does it work?</h3>
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {/* Left Column - Steps */}
              <div className="space-y-4 flex flex-col justify-center">
                <div className="bg-slate-50 border border-slate-200 p-4 rounded-xl">
                  <h4 className="font-bold text-slate-700">Person Detection</h4>
                  <p className="text-sm text-slate-600">The camera uses YOLO to detect the person.</p>
                </div>
                <div className="bg-slate-50 border border-slate-200 p-4 rounded-xl">
                  <h4 className="font-bold text-slate-700">Bed-Zone Check</h4>
                  <p className="text-sm text-slate-600">The system checks whether the person is inside the predefined bed area.</p>
                </div>
                
                <div className="bg-teal-50 border border-teal-200 p-4 rounded-xl">
                  <h4 className="font-bold text-teal-800 mb-2">Key Point</h4>
                  <p className="text-sm text-teal-700 italic">"The bed-zone system decides when to monitor, and the heart-rate system decides when an alert is needed."</p>
                </div>
              </div>

              {/* Right Column - Flowchart */}
              <div className="bg-slate-900 rounded-2xl p-6 text-white font-mono text-sm flex flex-col items-center justify-center border border-slate-700 shadow-inner h-full">
                <div className="text-center font-bold mb-6 text-teal-400 tracking-wider">Monitoring Decision</div>
                
                <div className="bg-slate-800 px-5 py-2.5 rounded-lg border border-slate-600 shadow-md">Person Detected</div>
                <ArrowDown className="w-5 h-5 my-3 text-slate-500" />
                <div className="bg-slate-800 px-5 py-2.5 rounded-lg border border-slate-600 shadow-md">Bed-Zone Check</div>
                <ArrowDown className="w-5 h-5 my-3 text-slate-500" />
                
                <div className="flex gap-8 w-full justify-center">
                  <div className="flex flex-col items-center flex-1 max-w-[140px]">
                    <div className="h-10 flex items-center justify-center text-xs text-slate-400 mb-2 text-center">Inside Bed</div>
                    <ArrowDown className="w-5 h-5 mb-3 text-slate-500" />
                    <div className="bg-teal-500/20 text-teal-300 font-bold px-4 py-2 rounded-lg border border-teal-500/50 w-full text-center">HR ON</div>
                  </div>
                  <div className="flex flex-col items-center flex-1 max-w-[140px]">
                    <div className="h-10 flex items-center justify-center text-xs text-slate-400 mb-2 text-center leading-tight">Outside /<br/>Not Detected</div>
                    <ArrowDown className="w-5 h-5 mb-3 text-slate-500" />
                    <div className="bg-slate-800 text-slate-300 font-bold px-4 py-2 rounded-lg border border-slate-600 w-full text-center">HR OFF</div>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <div>
            <h3 className="text-lg font-bold text-slate-800 mb-4">Heart-Rate Analysis</h3>
            <p className="text-slate-600 mb-4 text-sm font-medium">When the person is inside the bed:</p>
            
            <div className="flex flex-wrap items-center gap-2 mb-8 text-sm font-bold text-slate-700">
              <span className="bg-slate-100 px-3 py-2 rounded-lg border border-slate-200">Heart Rate Reading</span>
              <span className="text-slate-400">→</span>
              <span className="bg-slate-100 px-3 py-2 rounded-lg border border-slate-200">Validation</span>
              <span className="text-slate-400">→</span>
              <span className="bg-slate-100 px-3 py-2 rounded-lg border border-slate-200">Processing / Smoothing</span>
              <span className="text-slate-400">→</span>
              <span className="bg-slate-100 px-3 py-2 rounded-lg border border-slate-200">Trend Analysis</span>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div className="bg-green-50 p-4 rounded-xl border border-green-200">
                <div className="text-green-700 font-bold mb-1 flex items-center gap-2">🟢 Normal</div>
                <p className="text-sm text-green-800/80">HR is stable. No alert needed.</p>
              </div>
              <div className="bg-yellow-50 p-4 rounded-xl border border-yellow-200">
                <div className="text-yellow-700 font-bold mb-1 flex items-center gap-2">🟡 Watch</div>
                <p className="text-sm text-yellow-800/80">HR continuously rises or drops. System is watching.</p>
              </div>
              <div className="bg-red-50 p-4 rounded-xl border border-red-200">
                <div className="text-red-700 font-bold mb-1 flex items-center gap-2">🔴 Danger Alert</div>
                <p className="text-sm text-red-800/80">Sustained abnormal HR. Immediate alert sent.</p>
              </div>
            </div>
          </div>

        </section>

        <section className="glass-panel p-10 rounded-[2.5rem] border border-slate-200 shadow-md">
          <h2 className="text-2xl font-bold text-slate-800 mb-4 border-b pb-4 border-slate-200 flex items-center gap-2">
            <span className="text-indigo-500">🎙️</span> Voice Integration — Sanjeevani AI
          </h2>
          
          <div className="mb-8 mt-6">
            <h3 className="text-lg font-bold text-slate-800 mb-2">Why do we need it?</h3>
            <p className="text-slate-600 leading-relaxed">
              If an elderly person is standing or sitting normally, with no fall detected and a normal heart rate, but gets injured in their hand or leg and needs assistance, they can simply use their voice to request immediate help from the caretaker.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-8 mb-8">
            <div className="space-y-6">
              <div>
                <h3 className="text-lg font-bold text-slate-800 mb-4">Voice Command</h3>
                <div className="bg-slate-50 p-4 rounded-xl border border-slate-200">
                  <p className="text-sm text-slate-600 mb-3">The person can say:</p>
                  <p className="font-bold text-indigo-700 text-lg mb-3">"Sanjeevani, I need help."</p>
                  <p className="text-sm text-slate-600">The system recognizes the Sanjeevani wake word and then checks for a help request.</p>
                </div>
              </div>

              <div>
                <h4 className="font-bold text-slate-700 mb-2">Two-Step Interaction:</h4>
                <div className="flex flex-col gap-2 font-mono text-sm">
                  <div className="bg-slate-100 p-3 rounded-lg border border-slate-200 flex items-center gap-3">
                    <span className="text-xl">👤</span> <span>"Sanjeevani"</span>
                  </div>
                  <div className="pl-6 border-l-2 border-indigo-200 ml-4 py-1 text-xs text-slate-500">
                    🎙️ System starts listening
                  </div>
                  <div className="bg-slate-100 p-3 rounded-lg border border-slate-200 flex items-center gap-3">
                    <span className="text-xl">👤</span> <span>"I need help"</span>
                  </div>
                  <div className="pl-6 border-l-2 border-indigo-200 ml-4 py-1 text-xs text-indigo-500 font-bold">
                    🚨 Help request confirmed
                  </div>
                </div>
              </div>
            </div>

            <div className="bg-slate-900 rounded-2xl p-6 text-white font-mono text-sm flex flex-col items-center justify-center border border-slate-700 shadow-inner">
              <div className="text-center font-bold mb-6 text-indigo-400 tracking-wider">How it works</div>
              
              <div className="bg-slate-800 px-5 py-2.5 rounded-lg border border-slate-600 shadow-md w-full text-center max-w-[280px]">
                👤 Elderly Person
              </div>
              <ArrowDown className="w-5 h-5 my-2 text-slate-500" />
              <div className="bg-slate-800 px-5 py-2.5 rounded-lg border border-slate-600 shadow-md w-full text-center max-w-[280px]">
                🗣️ Says: "Sanjeevani, I need help"
              </div>
              <ArrowDown className="w-5 h-5 my-2 text-slate-500" />
              <div className="bg-slate-800 px-5 py-2.5 rounded-lg border border-slate-600 shadow-md w-full text-center max-w-[280px]">
                🎙️ Voice Assistant detects request
              </div>
              <ArrowDown className="w-5 h-5 my-2 text-slate-500" />
              <div className="bg-slate-800 px-5 py-2.5 rounded-lg border border-slate-600 shadow-md w-full text-center max-w-[280px]">
                🚨 Help request is confirmed
              </div>
              <ArrowDown className="w-5 h-5 my-2 text-slate-500" />
              <div className="bg-red-500/20 text-red-300 font-bold px-5 py-3 rounded-lg border border-red-500/50 w-full text-center max-w-[280px]">
                📢 HELP REQUEST RECEIVED<br/>— ALERTING CARETAKER —
              </div>
              <ArrowDown className="w-5 h-5 my-2 text-slate-500" />
              <div className="bg-slate-800 px-5 py-2.5 rounded-lg border border-slate-600 shadow-md w-full text-center max-w-[280px]">
                👨‍⚕️ Caretaker Alert
              </div>
            </div>
          </div>

          <div className="bg-indigo-50 p-6 rounded-2xl border border-indigo-100">
            <h4 className="font-bold text-indigo-800 mb-2">Key Benefit</h4>
            <p className="text-sm text-indigo-700">
              Voice Integration provides an additional way to request help when the person is not experiencing a fall or abnormal heart rate but still needs assistance.
            </p>
          </div>
        </section>

        <section className="glass-panel p-10 rounded-[2.5rem] border border-slate-200 shadow-md">
          <h2 className="text-2xl font-bold text-slate-800 mb-4 border-b pb-4 border-slate-200 flex items-center gap-2">
            <span className="text-blue-500">🔒</span> Security Layer — Workflow
          </h2>
          
          <div className="mb-8 mt-6">
            <h3 className="text-lg font-bold text-slate-800 mb-2">Purpose</h3>
            <p className="text-slate-600 leading-relaxed">
              To make Sanjeevani safe by protecting patient data, controlling access, securing alerts, and preserving privacy.
            </p>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-5 gap-8 mb-8">
            <div className="lg:col-span-2 bg-slate-900 rounded-2xl p-6 text-white font-mono text-sm flex flex-col items-center justify-center border border-slate-700 shadow-inner">
              <div className="bg-slate-800 px-4 py-2 rounded-lg border border-slate-600 w-full text-center max-w-[220px]">User Access</div>
              <ArrowDown className="w-4 h-4 my-2 text-slate-500" />
              <div className="bg-slate-800 px-4 py-2 rounded-lg border border-slate-600 w-full text-center max-w-[220px]">🔐 Authentication</div>
              <ArrowDown className="w-4 h-4 my-2 text-slate-500" />
              <div className="bg-slate-800 px-4 py-2 rounded-lg border border-slate-600 w-full text-center max-w-[220px]">👥 Role Verification<br/><span className="text-xs text-slate-400">(Admin/Doctor/Caregiver)</span></div>
              <ArrowDown className="w-4 h-4 my-2 text-slate-500" />
              <div className="bg-slate-800 px-4 py-2 rounded-lg border border-slate-600 w-full text-center max-w-[220px]">🧠 AI Detection</div>
              <ArrowDown className="w-4 h-4 my-2 text-slate-500" />
              <div className="bg-slate-800 px-4 py-2 rounded-lg border border-slate-600 w-full text-center max-w-[220px] text-red-400">🚨 Danger Detected</div>
              <ArrowDown className="w-4 h-4 my-2 text-slate-500" />
              <div className="bg-slate-800 px-4 py-2 rounded-lg border border-slate-600 w-full text-center max-w-[220px]">🔒 Secure Alert</div>
              <ArrowDown className="w-4 h-4 my-2 text-slate-500" />
              <div className="bg-slate-800 px-4 py-2 rounded-lg border border-slate-600 w-full text-center max-w-[220px]">🎥 Privacy Protection<br/><span className="text-xs text-slate-400">(Face Blurring)</span></div>
              <ArrowDown className="w-4 h-4 my-2 text-slate-500" />
              <div className="bg-slate-800 px-4 py-2 rounded-lg border border-slate-600 w-full text-center max-w-[220px]">🔐 Data Encryption</div>
              <ArrowDown className="w-4 h-4 my-2 text-slate-500" />
              <div className="bg-slate-800 px-4 py-2 rounded-lg border border-slate-600 w-full text-center max-w-[220px]">📋 Audit Logging</div>
            </div>

            <div className="lg:col-span-3 flex flex-col justify-center space-y-6">
              <div>
                <h3 className="text-lg font-bold text-slate-800 mb-4">Why We Need It</h3>
                
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                  <div className="bg-slate-50 p-4 rounded-xl border border-slate-200">
                    <h4 className="font-bold text-slate-700 text-sm mb-1">Authentication & RBAC</h4>
                    <p className="text-xs text-slate-600">Prevent unauthorized access.</p>
                  </div>
                  <div className="bg-slate-50 p-4 rounded-xl border border-slate-200">
                    <h4 className="font-bold text-slate-700 text-sm mb-1">Encryption</h4>
                    <p className="text-xs text-slate-600">Protect sensitive patient data.</p>
                  </div>
                  <div className="bg-slate-50 p-4 rounded-xl border border-slate-200">
                    <h4 className="font-bold text-slate-700 text-sm mb-1">Secure Alerts</h4>
                    <p className="text-xs text-slate-600">Prevent fake or modified emergency alerts.</p>
                  </div>
                  <div className="bg-slate-50 p-4 rounded-xl border border-slate-200">
                    <h4 className="font-bold text-slate-700 text-sm mb-1">Face Blurring</h4>
                    <p className="text-xs text-slate-600">Protect personal privacy.</p>
                  </div>
                  <div className="bg-slate-50 p-4 rounded-xl border border-slate-200">
                    <h4 className="font-bold text-slate-700 text-sm mb-1">Audit Logs</h4>
                    <p className="text-xs text-slate-600">Track important events and detect tampering.</p>
                  </div>
                  <div className="bg-slate-50 p-4 rounded-xl border border-slate-200">
                    <h4 className="font-bold text-slate-700 text-sm mb-1">Secure Secrets</h4>
                    <p className="text-xs text-slate-600">Keep security keys protected.</p>
                  </div>
                </div>
              </div>
              
              <div className="bg-blue-50 border border-blue-200 p-5 rounded-xl">
                <p className="text-sm text-blue-800 font-medium italic leading-relaxed">
                  "The security layer makes Sanjeevani safer by protecting patient data, controlling access, securing emergency communication, and preserving privacy."
                </p>
              </div>
            </div>
          </div>
        </section>

        <section className="bg-white p-10 md:p-12 rounded-[2.5rem] shadow-xl border border-slate-200 mt-12">
          
          <div className="text-center mb-10">
            <h2 className="text-3xl md:text-4xl font-black tracking-tight text-slate-800 mb-4">
              Why is Sanjeevani AI Different and Better?
            </h2>
            <p className="text-lg text-slate-600 font-medium max-w-3xl mx-auto leading-relaxed">
              Sanjeevani AI is designed as a <span className="font-bold text-teal-600">complete elderly safety system</span>, rather than only a fall-detection system. Existing approaches commonly focus on a particular method such as wearable sensors, cameras, or smartphones, each with its own limitations.
            </p>
          </div>
          
          {/* Responsive Comparison Table */}
          <div className="overflow-x-auto mb-10 border border-slate-200 rounded-2xl shadow-sm">
            <table className="w-full text-left border-collapse min-w-[700px]">
              <thead>
                <tr className="bg-slate-50 border-b border-slate-200 text-slate-500 uppercase tracking-widest text-xs">
                  <th className="p-5 font-bold w-1/4">Feature</th>
                  <th className="p-5 font-bold w-1/3">Current Systems</th>
                  <th className="p-5 font-bold bg-teal-50/50 text-teal-700 w-5/12">Sanjeevani AI</th>
                </tr>
              </thead>
              <tbody className="text-sm font-medium">
                {[
                  { feat: "🧍 Fall Detection", cur: "Mainly detects whether a fall occurred", sai: "Detects fall + body posture + movement over time" },
                  { feat: "❤️ Health Monitoring", cur: "Often handled separately", sai: "Combines heart-rate information with safety monitoring" },
                  { feat: "🛏️ Bed Monitoring", cur: "Not always included", sai: "Monitors the bed zone and movement around the bed" },
                  { feat: "🚨 Danger Detection", cur: "Often gives an immediate alert", sai: "Uses continuous observation before escalating" },
                  { feat: "🔄 Recovery Detection", cur: "Limited in many systems", sai: "Recognizes when the person starts recovering or moves again" },
                  { feat: "🗣️ Voice Assistance", cur: "Usually a separate feature", sai: "Person can directly say 'Sanjeevani, I need help'" },
                  { feat: "👨‍⚕️ Caretaker Support", cur: "Alert may simply indicate a fall", sai: "Designed to provide clear, actionable alerts" },
                  { feat: "🎯 Multiple Situations", cur: "Mainly focused on falls", sai: "Handles falls, prolonged lying, bed movement, and active help requests" },
                  { feat: "⚡ Real-Time Response", cur: "Depends on the particular device/system", sai: "Designed for continuous real-time monitoring" },
                  { feat: "🔗 Integrated Approach", cur: "Different devices/features may work independently", sai: "Brings multiple safety signals together into one system" }
                ].map((row, i) => (
                  <tr key={i} className="border-b border-slate-100 last:border-0 hover:bg-slate-50/50 transition-colors">
                    <td className="p-5 text-slate-800 font-bold">{row.feat}</td>
                    <td className="p-5 text-slate-500">{row.cur}</td>
                    <td className="p-5 text-teal-800 bg-teal-50/30 font-semibold">{row.sai}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          <div className="bg-amber-50 border border-amber-200 rounded-2xl p-6 text-center">
            <h3 className="text-lg font-black text-amber-600 mb-2 tracking-wide flex items-center justify-center gap-2">
              <span className="text-2xl">⭐</span> THE MAIN DIFFERENCE
            </h3>
            <p className="text-slate-700 font-medium text-lg max-w-2xl mx-auto leading-relaxed">
              Sanjeevani AI does not simply ask, <i>"Did the person fall?"</i> — it tries to understand what is happening to the person and respond accordingly.
            </p>
          </div>
          
        </section>
      </div>

    </div>
  );
}
