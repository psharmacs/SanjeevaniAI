import React, { createContext, useContext, useState, useRef, useEffect } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';

const BotContext = createContext();

export const useBot = () => useContext(BotContext);

export const BotProvider = ({ children }) => {
  const [isActive, setIsActive] = useState(false);
  const [caption, setCaption] = useState('');
  const [isSpeaking, setIsSpeaking] = useState(false);
  
  const synthRef = useRef(window.speechSynthesis);
  const activeRef = useRef(false);
  const navigate = useNavigate();

  // Ensure speech synthesis is ready and cancel any ongoing speech on load
  useEffect(() => {
    synthRef.current?.cancel();
  }, []);

  const speak = (text, onEndCallback) => {
    return new Promise((resolve) => {
      if (!activeRef.current) return resolve(); // Abort if cancelled

      synthRef.current.cancel(); // Stop anything currently playing
      
      const utterance = new SpeechSynthesisUtterance(text);
      
      // Try to find a good English voice
      const voices = synthRef.current.getVoices();
      const preferredVoice = voices.find(v => v.name.includes('Google UK English Female') || v.name.includes('Samantha') || v.lang === 'en-US' || v.lang === 'en-GB');
      if (preferredVoice) utterance.voice = preferredVoice;
      
      utterance.rate = 0.95; // Slightly slower for clarity
      utterance.pitch = 1.1; // Slightly friendly
      
      setCaption(text);
      setIsSpeaking(true);

      utterance.onend = () => {
        setIsSpeaking(false);
        if (onEndCallback) onEndCallback();
        resolve();
      };

      utterance.onerror = () => {
        setIsSpeaking(false);
        resolve();
      };

      synthRef.current.speak(utterance);
    });
  };

  // Script 1: Fall Detection (Video 1)
  const playFallDetectionScript = async (onIntroDone, onScriptComplete) => {
    const runId = Date.now();
    activeRef.current = runId;
    window.speechSynthesis.cancel(); 

    await speak("Welcome to the live demonstration. We will begin by testing the Fall Detection and Voice Integration systems.");
    if (activeRef.current !== runId) return;
    
    // Tell the video to start playing NOW
    if (onIntroDone) onIntroDone();
    const videoStartTime = Date.now();
    
    // Brief architectural explanation before the fall
    await new Promise(r => setTimeout(r, 1000));
    if (activeRef.current !== runId) return;
    await speak("Sanjeevani AI is actively processing the video feed in real-time at the Edge, continuously tracking joint vectors and posture without sending video to the cloud.");
    
    // HUGE GAP: This gives time for the user to scream and the video to say "Are you okay?" 
    await new Promise(r => setTimeout(r, 8000));
    if (activeRef.current !== runId) return;
    
    // Explanation of what just happened in the video
    await speak("As you just heard, the system detected the anomaly using temporal reasoning and instantly initiated the Level 1 Voice Protocol to check on the patient.");
    
    // Explaining Level 2 & 3 based on the voice response
    await new Promise(r => setTimeout(r, 2000));
    if (activeRef.current !== runId) return;
    await speak("Because an emergency was confirmed, Level 2 activates immediately. A secure alert is dispatched to the caregiver. If no one responds, it escalates to Level 3 to call an ambulance.");

    // Final benefit
    await new Promise(r => setTimeout(r, 2000));
    if (activeRef.current !== runId) return;
    await speak("This progressive escalation ensures emergencies are handled with zero latency, while completely preventing false alarms.");

    // PRECISION TIMING for the 0:57 mark in the video
    const elapsed1 = Date.now() - videoStartTime;
    const timeToWait1 = 56000 - elapsed1; // Wait until 56 seconds
    
    if (timeToWait1 > 0) {
      await new Promise(r => setTimeout(r, timeToWait1));
    }
    
    if (activeRef.current !== runId) return;
    await speak("Notice here, the system triggers Level 1 again. However, if the person doesn't say anything but starts recovering and moving after lying still, Sanjeevani detects this recovery and automatically cancels the trigger.");

    // PRECISION TIMING for the 01:23 (83s) mark in the video - Voice Command
    const elapsed2 = Date.now() - videoStartTime;
    const timeToWait2 = 82000 - elapsed2; // Wait until 82 seconds
    
    if (timeToWait2 > 0) {
      await new Promise(r => setTimeout(r, timeToWait2));
    }
    
    if (activeRef.current !== runId) return;
    await speak("Finally, observe our Voice Command Integration. The user explicitly calls out the wake word: 'Sanjeevani, I need help'. The system instantly recognizes this distress signal and dispatches a high-priority alert directly to the caretaker, bypassing the need for a physical fall.");

    if (activeRef.current === runId && onScriptComplete) {
      onScriptComplete();
    }
  };

  // Script 2: Bed Zone (Video 2)
  const playBedZoneScript = async (onIntroDone, onScriptComplete) => {
    const runId = Date.now();
    activeRef.current = runId;
    window.speechSynthesis.cancel(); 

    await speak("Now, we will move onto the second video, explaining the Bed Zone feature.");
    if (activeRef.current !== runId) return;

    // Tell the video to start playing NOW
    if (onIntroDone) onIntroDone();

    // The old original script sequence
    await new Promise(r => setTimeout(r, 2000));
    if (activeRef.current !== runId) return;
    await speak("Notice the intelligent Bed Zone mapping. The user has entered the designated Bed Zone to sleep.");

    await new Promise(r => setTimeout(r, 3000));
    if (activeRef.current !== runId) return;
    await speak("Sanjeevani is now automatically pulling vital sign readings from our provided wearable device to monitor their heart rate.");

    await new Promise(r => setTimeout(r, 4000));
    if (activeRef.current !== runId) return;
    await speak("If the vitals show an unusual pattern, like a sudden drop or surge, it will instantly send an emergency alert directly to the caregiver.");

    await new Promise(r => setTimeout(r, 6000));
    if (activeRef.current !== runId) return;
    await speak("The moment they leave the bed zone, the active fall detection system instantly kicks back on.");

    if (activeRef.current === runId && onScriptComplete) {
      onScriptComplete();
    }
  };

  const playGuidebookScript = async () => {
    const runId = Date.now();
    activeRef.current = runId;
    window.speechSynthesis.cancel();

    await new Promise(r => setTimeout(r, 1000));
    if (activeRef.current !== runId) return;

    await speak("For more information, you can refer to this page and the mentioned SIH presentation.");
    
    setTimeout(() => {
      if (activeRef.current !== runId) return;
      setCaption('');
      setIsActive(false);
      activeRef.current = null;
    }, 4000);
  };

  const startTour = async () => {
    setIsActive(true);
    activeRef.current = 'TOUR_START';
    navigate('/');
    window.speechSynthesis.cancel();
    
    await speak("Welcome to the Sanjeevani AI guided tour. I am your AI assistant, and I will be walking you through our intelligent safety system.");
    if (activeRef.current !== 'TOUR_START') return;
    
    navigate('/team');
    // Assuming playTeamScript existed previously
    await speak("We are a team of aspirational engineers dedicated to building Sanjeevani AI, an intelligent safety system that observes, understands, and responds to protect the elderly.");
    if (activeRef.current !== 'TOUR_START') return;
    
    navigate('/live');
    // Live.jsx will handle video sequencing and trigger scripts dynamically
  };

  const stopTour = () => {
    activeRef.current = false;
    synthRef.current?.cancel();
    setIsSpeaking(false);
    setIsActive(false);
    setCaption('');
  };

  return (
    <BotContext.Provider value={{ 
      isActive, 
      isSpeaking,
      caption, 
      startTour, 
      stopTour, 
      playFallDetectionScript,
      playBedZoneScript,
      playGuidebookScript,
      speak,
      activeRef
    }}>
      {children}
    </BotContext.Provider>
  );
};
