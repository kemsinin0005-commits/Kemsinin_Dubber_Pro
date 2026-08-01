# Kemsinin Dubber Pro - AI-Powered Video Dubbing Studio

A premium, interactive web-based studio for editing subtitles and synchronizing AI-powered voiceovers. Built with a futuristic dark-theme neon glassmorphism layout, featuring real-time canvas audio visualizers, cassette tape animations, and synchronized translation readouts.

## 🚀 Key Features

* **High-Fidelity UI/UX**: Premium dark glassmorphism styling (`backdrop-filter`) with custom glowing highlights, responsive grids, and Google Fonts (*Outfit* and *Kantumruy Pro* for beautiful Khmer rendering).
* **3D Parallax Tilt**: Interactive card widgets that tilt and shift perspective dynamically following your mouse coordinates.
* **Smart Subtitle Grid**: Fully editable start/end timecodes, dialogue fields, voice profiles (Piseth, Sophea, Dara, Srey, Bora), and speed controls.
* **Timeline Synchronization**: Playing the timeline automatically scrolls to and highlights the currently active subtitle row. Clicking any row seeks the video playhead to the exact start time.
* **Real-Time AI Dubbing (Khmer TTS)**: Streaming high-quality, natural Google Translate TTS audio segments directly into the browser in sync with the timeline playback.
* **Canvas Visualizer & Spectrum**: Concentric pulsing hexagonal ring canvas and a bottom equalizer spectrum bar that react to playback (using the Web Audio API if a real video file is loaded).
* **Video & SRT Drag/Drop**: Load custom videos (MP4/WebM) and subtitles (`.srt` files) directly in-browser.
* **Built-in Utility Tools**:
  * **Cutter**: Splicing subtitle rows at current playhead timestamps.
  * **Merger**: Combining adjacent rows.
  * **Video Transcript**: Generating joined plain text with clipboard copying and TXT saving.
  * **Settings Panel**: Toggling real-time dubbing and setting voice parameters.
  * **Export Simulator**: Visualizing progress percentage loading grids and downloading output clips.

## 🛠 Tech Stack

* **Frontend**: HTML5, Vanilla CSS3, Modern JavaScript (ES6), inline SVG Icons.
* **Backend Utilities**: Python 3.x (local static file server with CORS headers).

## 🏃‍♂️ How to Run Locally

1. Clone this repository to your machine.
2. Double-click the **`run.bat`** file (on Windows). 
   * *This will start a local Python server and open your default browser pointing to `http://localhost:8000`.*
3. Drag-and-drop your video and start dubbing!
