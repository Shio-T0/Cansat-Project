# CanSat Telemetry Visualization UI

A user interface developed in **Python** and **JavaScript** by a member of the **InAxon CanSat Team** to visualize and interpret telemetry data that will be transmitted by a future CanSat mission.

---

## Features

### Real-Time Plotting
- **4 Plotly graphs** for continuous comparison between:
  - Experimental values  
  - Expected / theoretical values  
- Designed for immediate deviation detection and trend analysis.

### Image Monitoring System
- **Most Recent Image Viewer** — displays the latest received image instantly.
- **Image Monitor Gallery** — allows viewing of all received images in sequence.

### 3D Orientation Model
- Interactive **3D CanSat model** that dynamically reacts to inclination and orientation data.
- Provides intuitive spatial awareness of the satellite’s attitude.

### AI-Assisted Telemetry Interpretation
- Integrated AI module prompted with incoming telemetry data.
- Produces contextual interpretations and assists in anomaly recognition.

### Telemetry Data Panels
Displays key mission metrics in real time:
- **Altitude**
- **Percentual Error**
- **Coordinates**
- **Data Receiving Rate**

---

## Core Principle

**All components update in real time.**  
No manual refresh is required; the interface is designed for continuous live monitoring during mission operation.

---

## Technologies Used

- **Python** — backend logic, data handling, telemetry processing
- **JavaScript** — frontend interactivity and UI responsiveness
- **Plotly** — real-time graph visualization
- **AI Integration** — telemetry interpretation assistance using hugging face

---

## Purpose

This UI serves as a mission-control visualization and analysis tool, enabling the InAxon team to:
- Monitor flight conditions
- Detect anomalies quickly
- Compare predicted vs. actual performance
- Interpret telemetry with augmented intelligence
- Maintain situational awareness through visual and numerical feedback
