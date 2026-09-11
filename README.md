# Sanjeevani AI 🛡️

*AI that cares. A safer tomorrow.*

Sanjeevani AI is an intelligent, edge-based safety system designed to observe, understand, and respond to protect the elderly and vulnerable. By leveraging real-time temporal reasoning and spatial tracking, Sanjeevani detects emergencies such as falls or abnormal vital signs and initiates a progressive escalation protocol to ensure zero-latency response.

## 🚀 Key Features

*   **Real-Time Fall Detection:** Utilizes joint vector tracking and posture analysis at the Edge to detect falls instantly without sending private video feeds to the cloud.
*   **Intelligent Bed Zone Mapping:** Maps spatial grids to monitor when a user enters or leaves a designated bed zone, seamlessly switching tracking modes.
*   **Wearable Vitals Integration:** Automatically pulls vital sign readings (e.g., heart rate) to detect unusual patterns like sudden drops or surges.
*   **Voice Command Integration:** Actively listens for distress wake words (e.g., *"Sanjeevani, I need help"*), bypassing physical fall requirements to dispatch immediate alerts.
*   **Progressive Escalation Protocol:** 
    *   *Level 1:* Voice check ("Are you okay?").
    *   *Level 2:* Secure alert dispatched to a designated caregiver.
    *   *Level 3:* Automatic escalation to emergency services/ambulance if unresolved.

## 🧠 Machine Learning Workflow & Pipeline

Sanjeevani AI processes data entirely at the Edge to ensure maximum privacy and minimal latency.

1.  **Video Feed Ingestion:** Edge node captures 1080p 30fps video.
2.  **Object & Spatial Tracking (YOLOv8):** Identifies the subject and tracks their position across the calibrated spatial grid.
3.  **Posture & Joint Vector Analysis (MediaPipe):** Extracts precise skeletal landmarks to calculate joint angles, velocity, and vertical displacement.
4.  **Temporal Reasoning Engine:** Analyzes the sequence of movements over time. Differentiates between a person safely lying down (e.g., entering the Bed Zone) vs. experiencing a sudden, uncontrolled fall.
5.  **False Alarm Mitigation:** If a fall is suspected, the system waits for recovery movement or a voice response before escalating.
6.  **Action Dispatcher:** Triggers the appropriate UI and backend alerts based on the confirmed threat level.

## 💻 Tech Stack

**Frontend / UI:**
*   **React (Vite):** High-performance rendering for the interactive dashboard and live feed simulation.
*   **Tailwind CSS:** Modern, responsive utility-first styling with custom glassmorphism UI elements.
*   **Framer Motion:** Smooth page transitions and telemetry animations.
*   **React Router:** Client-side routing for seamless navigation.

**Machine Learning & Backend:**
*   **YOLOv8:** Advanced object detection and spatial mapping.
*   **MediaPipe Pose:** High-fidelity human pose estimation.
*   **Python:** Core logic for the live feed server, video processing, and edge inference simulation.
*   **OpenCV:** Computer vision tasks and video stream manipulation.

## 🌐 Deployment
*   **Frontend Hosting:** Vercel (CI/CD integrated with GitHub)
