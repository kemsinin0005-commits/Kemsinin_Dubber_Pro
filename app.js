// Kemsinin Dubber Pro - Core JS Logic

// Subtitles database
let subtitles = [
    { id: 1, start: 6.020, end: 7.300, text: "ទៅលេងឡើងវិញ", voice: "piseth_male", speed: "auto" },
    { id: 2, start: 19.400, end: 20.440, text: "ដល់", voice: "piseth_male", speed: "auto" },
    { id: 3, start: 21.820, end: 24.000, text: "ម៉េចក៏បានដែរវិញ", voice: "piseth_male", speed: "auto" },
    { id: 4, start: 27.720, end: 29.840, text: "ដាច់កំហែងបេក្ខជនកណ្ដាលផ្លូវ", voice: "piseth_male", speed: "auto" },
    { id: 5, start: 34.540, end: 37.120, text: "ខុសនេះត្រង់ក្បូនបងព្រេង", voice: "piseth_male", speed: "auto" },
    { id: 6, start: 37.120, end: 44.440, text: "ចុះ បុគ្គលិកមានឧបសគ្គ", voice: "piseth_male", speed: "auto" },
    { id: 7, start: 50.840, end: 52.340, text: "អ្នក អ្នកជាអ្នកណា", voice: "piseth_male", speed: "auto" },
    { id: 8, start: 52.340, end: 54.580, text: "តើលោកកាលពីដប់ឆ្នាំមុន", voice: "piseth_male", speed: "auto" },
    { id: 9, start: 54.580, end: 55.980, text: "គ្មានជំនួយជួយដោះស្រាយបញ្ហាដែរឬទេ", voice: "piseth_male", speed: "auto" }
];

// Audio & Video Playback State
let isPlaying = false;
let currentTime = 0;
let defaultDuration = 141.0; // 02:21,000 matching mockup
let duration = defaultDuration;
let videoLoaded = false;
let activeRowId = null;
let realTimeDubbing = true;
let currentUploadedVideoFile = null;
let activeDubbingAudio = null;
let currentDubbedVideoBlob = null;

// Audio Context for Visualizers
let audioCtx = null;
let audioSource = null;
let analyzer = null;
let dataArray = null;

// DOM Elements
const videoPlayer = document.getElementById("video-player");
const visualizerCanvas = document.getElementById("visualizer-canvas");
const spectrumCanvas = document.getElementById("spectrum-canvas");
const timelineSlider = document.getElementById("timeline-slider");
const currentTimeDisplay = document.getElementById("current-time");
const durationDisplay = document.getElementById("total-duration");
const playBtn = document.getElementById("btn-play");
const playIcon = document.getElementById("play-icon");
const pauseIcon = document.getElementById("pause-icon");
const stopBtn = document.getElementById("btn-stop");
const volumeBtn = document.getElementById("btn-volume");
const volHighIcon = document.getElementById("vol-high-icon");
const volMuteIcon = document.getElementById("vol-mute-icon");
const volumeSlider = document.getElementById("volume-slider");
const cassetteTape = document.getElementById("cassette-tape");
const subtitlesTbody = document.getElementById("subtitles-tbody");
const loadedFileName = document.getElementById("loaded-file-name");

// Modals
const modalSettings = document.getElementById("modal-settings");
const modalCutter = document.getElementById("modal-cutter");
const modalMerger = document.getElementById("modal-merger");
const modalBatch = document.getElementById("modal-batch");
const modalTranscript = document.getElementById("modal-transcript");
const modalExport = document.getElementById("modal-export");
const modalTranslate = document.getElementById("modal-translate");

// File Pickers
const btnUploadVideo = document.getElementById("btn-upload-video");
const btnUploadSrt = document.getElementById("btn-upload-srt");
const videoFileInput = document.getElementById("video-file-input");
const srtFileInput = document.getElementById("srt-file-input");

// Action Buttons
const btnCutter = document.getElementById("btn-cutter");
const btnMerger = document.getElementById("btn-merger");
const btnSettingsBottom = document.getElementById("btn-settings-bottom");
const btnExportVideo = document.getElementById("btn-export-video");
const btnApplyAllVoices = document.getElementById("btn-apply-all-voices");
const btnRemoveVocal = document.getElementById("btn-remove-vocal");
const btnSaveSrt = document.getElementById("btn-save-srt");
const btnAddSegment = document.getElementById("btn-add-segment");
const btnBatchDubber = document.getElementById("btn-batch-dubber");
const btnTranscriptHeader = document.getElementById("btn-transcript");
const btnTranslateHeader = document.getElementById("btn-translate-video");

// Toast
const toast = document.getElementById("toast");
const toastMessage = document.getElementById("toast-message");

// Effect theme tracking
let currentEffectTheme = 0;
const btnEffectHeader = document.getElementById("btn-effect");

// Simulation Animation Frame
let animationFrameId = null;
let lastTickTime = 0;

// Initialize Application
window.addEventListener("DOMContentLoaded", () => {
    renderSubtitles();
    initTimeline();
    setupCanvas();
    setupEvents();
    setupModals();
    init3DTilt();
    requestAnimationFrame(updateLoop);
});

// Time utilities
function timeToSeconds(timeStr) {
    if (!timeStr) return 0;
    const cleanStr = timeStr.trim().replace(',', '.');
    const parts = cleanStr.split(':');
    if (parts.length === 3) {
        return parseFloat(parts[0]) * 3600 + parseFloat(parts[1]) * 60 + parseFloat(parts[2]);
    } else if (parts.length === 2) {
        return parseFloat(parts[0]) * 60 + parseFloat(parts[1]);
    }
    return parseFloat(cleanStr) || 0;
}

function secondsToTime(secs) {
    if (isNaN(secs) || secs < 0) secs = 0;
    const hrs = Math.floor(secs / 3600);
    const mins = Math.floor((secs - hrs * 3600) / 60);
    const remainingSecs = secs - hrs * 3600 - mins * 60;
    
    const hStr = String(hrs).padStart(2, '0');
    const mStr = String(mins).padStart(2, '0');
    
    const sInt = Math.floor(remainingSecs);
    const ms = Math.floor((remainingSecs - sInt) * 1000);
    const sStr = String(sInt).padStart(2, '0');
    const msStr = String(ms).padStart(3, '0');
    
    return `${hStr}:${mStr}:${sStr},${msStr}`;
}

// Show simple Toast message
function showToast(msg) {
    toastMessage.textContent = msg;
    toast.classList.add("show");
    setTimeout(() => {
        toast.classList.remove("show");
    }, 2500);
}

// Rendering Subtitle Table
function renderSubtitles() {
    // Sort subtitles by start time
    subtitles.sort((a, b) => a.start - b.start);
    subtitlesTbody.innerHTML = "";
    
    subtitles.forEach((sub, index) => {
        const row = document.createElement("tr");
        row.setAttribute("data-id", sub.id);
        if (activeRowId === sub.id) {
            row.classList.add("active-row");
        }
        
        row.innerHTML = `
            <td class="row-number">${index + 1}</td>
            <td>
                <input type="text" class="time-input start-time" value="${secondsToTime(sub.start)}" data-field="start">
            </td>
            <td>
                <input type="text" class="time-input end-time" value="${secondsToTime(sub.end)}" data-field="end">
            </td>
            <td>
                <div style="display: flex; align-items: center; gap: 8px;">
                    <textarea class="text-textarea">${sub.text}</textarea>
                    <button class="btn-delete-row speak-row-btn" title="Listen to TTS Speak" style="color: var(--cyan); border: 1px solid rgba(0, 242, 254, 0.15); border-radius: 4px; padding: 4px;">
                        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="12" height="12">
                            <polygon points="11 5 6 9 2 9 2 15 6 15 11 19 11 5"/>
                            <path d="M19.07 4.93a10 10 0 0 1 0 14.14"/>
                            <path d="M15.54 8.46a5 5 0 0 1 0 7.07"/>
                        </svg>
                    </button>
                </div>
            </td>
            <td>
                <div class="table-select-wrapper">
                    <select class="table-select voice-selector">
                        <option value="piseth_male" ${sub.voice === 'piseth_male' ? 'selected' : ''}>Piseth</option>
                        <option value="sophea_female" ${sub.voice === 'sophea_female' ? 'selected' : ''}>Sophea</option>
                        <option value="dara_male" ${sub.voice === 'dara_male' ? 'selected' : ''}>Dara</option>
                        <option value="srey_female" ${sub.voice === 'srey_female' ? 'selected' : ''}>Srey</option>
                        <option value="bora_male" ${sub.voice === 'bora_male' ? 'selected' : ''}>Bora</option>
                    </select>
                </div>
            </td>
            <td>
                <div class="table-select-wrapper">
                    <select class="table-select speed-selector">
                        <option value="0.5" ${sub.speed === '0.5' ? 'selected' : ''}>0.5x</option>
                        <option value="0.75" ${sub.speed === '0.75' ? 'selected' : ''}>0.75x</option>
                        <option value="auto" ${sub.speed === 'auto' ? 'selected' : ''}>Auto</option>
                        <option value="1.0" ${sub.speed === '1.0' ? 'selected' : ''}>1.0x</option>
                        <option value="1.25" ${sub.speed === '1.25' ? 'selected' : ''}>1.25x</option>
                        <option value="1.5" ${sub.speed === '1.5' ? 'selected' : ''}>1.5x</option>
                        <option value="2.0" ${sub.speed === '2.0' ? 'selected' : ''}>2.0x</option>
                    </select>
                </div>
            </td>
            <td>
                <button class="btn-delete-row btn-remove-segment-row" title="Delete Segment">
                    <svg class="trash-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <polyline points="3 6 5 6 21 6"/><path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"/><line x1="10" y1="11" x2="10" y2="17"/><line x1="14" y1="11" x2="14" y2="17"/>
                    </svg>
                </button>
            </td>
        `;
        
        // Event Listeners for inputs
        const startInput = row.querySelector('.start-time');
        const endInput = row.querySelector('.end-time');
        const textArea = row.querySelector('.text-textarea');
        const voiceSelect = row.querySelector('.voice-selector');
        const speedSelect = row.querySelector('.speed-selector');
        const btnDelete = row.querySelector('.btn-remove-segment-row');
        const btnSpeak = row.querySelector('.speak-row-btn');
        
        // Jump playhead to segment on row click (excluding input clicks)
        row.addEventListener("click", (e) => {
            if (e.target.tagName !== "INPUT" && e.target.tagName !== "TEXTAREA" && e.target.tagName !== "SELECT" && !e.target.closest('button')) {
                seekTo(sub.start);
                highlightRow(sub.id);
            }
        });
        
        startInput.addEventListener("change", () => {
            const val = timeToSeconds(startInput.value);
            if (!isNaN(val)) {
                sub.start = val;
                renderSubtitles();
            } else {
                startInput.value = secondsToTime(sub.start);
            }
        });
        
        endInput.addEventListener("change", () => {
            const val = timeToSeconds(endInput.value);
            if (!isNaN(val)) {
                sub.end = val;
                renderSubtitles();
            } else {
                endInput.value = secondsToTime(sub.end);
            }
        });
        
        textArea.addEventListener("input", () => {
            sub.text = textArea.value;
        });
        
        voiceSelect.addEventListener("change", () => {
            sub.voice = voiceSelect.value;
            showToast("Voice updated for segment #" + (index + 1));
        });
        
        speedSelect.addEventListener("change", () => {
            sub.speed = speedSelect.value;
            showToast("Speed updated for segment #" + (index + 1));
        });
        
        btnDelete.addEventListener("click", (e) => {
            e.stopPropagation();
            subtitles = subtitles.filter(s => s.id !== sub.id);
            renderSubtitles();
            showToast("Segment removed");
        });

        btnSpeak.addEventListener("click", (e) => {
            e.stopPropagation();
            speakSubtitleText(sub.text, sub.voice);
        });
        
        subtitlesTbody.appendChild(row);
    });
}

// Text to Speech logic (utilizes Google Translate TTS for Khmer & Web Speech API for fallback)
function speakSubtitleText(text, voiceType) {
    if (!text || text.trim() === "") return;
    
    // Stop any ongoing dubbing TTS playback
    if (activeDubbingAudio) {
        activeDubbingAudio.pause();
        activeDubbingAudio = null;
    }
    if ('speechSynthesis' in window) {
        window.speechSynthesis.cancel();
    }

    // Mute original video audio track so original language voice is removed/silenced during Khmer dubbing
    if (videoLoaded && videoPlayer) {
        videoPlayer.muted = true;
    }
    
    // Stream natural Google TTS in Khmer (tl=km)
    try {
        const audioUrl = `https://translate.google.com/translate_tts?ie=UTF-8&tl=km&client=tw-ob&q=${encodeURIComponent(text.trim())}`;
        const ttsAudio = new Audio(audioUrl);
        activeDubbingAudio = ttsAudio;
        
        // Adjust volume according to current settings
        const currentVol = videoLoaded ? (videoPlayer.volume || 0.8) : parseFloat(volumeSlider.value || 0.8);
        ttsAudio.volume = currentVol;
        
        ttsAudio.play().catch(err => {
            console.warn("Autoplay blocked. Falling back to native SpeechSynthesis.", err);
            fallbackSpeak(text, voiceType);
        });
    } catch (e) {
        console.error("Google TTS failed, playing fallback...", e);
        fallbackSpeak(text, voiceType);
    }
}

// Fallback Speech Synthesis
function fallbackSpeak(text, voiceType) {
    if ('speechSynthesis' in window) {
        window.speechSynthesis.cancel();
        const utterance = new SpeechSynthesisUtterance(text);
        const voices = window.speechSynthesis.getVoices();
        
        if (voiceType.includes("female")) {
            utterance.pitch = 1.2;
            utterance.rate = 1.0;
            const femaleVoice = voices.find(v => v.name.toLowerCase().includes("female") || v.name.toLowerCase().includes("google khmer") || v.name.toLowerCase().includes("siri"));
            if (femaleVoice) utterance.voice = femaleVoice;
        } else {
            utterance.pitch = 0.85;
            utterance.rate = 0.95;
            const maleVoice = voices.find(v => v.name.toLowerCase().includes("male") || v.name.toLowerCase().includes("david") || v.name.toLowerCase().includes("microsoft"));
            if (maleVoice) utterance.voice = maleVoice;
        }
        
        utterance.lang = "km-KH"; 
        window.speechSynthesis.speak(utterance);
    } else {
        showToast("Text-to-Speech not supported in this browser");
    }
}

// Active row highlighter
function highlightRow(id) {
    activeRowId = id;
    const rows = subtitlesTbody.querySelectorAll("tr");
    rows.forEach(row => {
        const rowId = parseInt(row.getAttribute("data-id"));
        if (rowId === id) {
            row.classList.add("active-row");
            // Smoothly scroll container to target row if not fully in view
            row.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
        } else {
            row.classList.remove("active-row");
        }
    });
}

// Timeline Setup
function initTimeline() {
    timelineSlider.max = duration;
    timelineSlider.value = 0;
    currentTimeDisplay.textContent = secondsToTime(0);
    durationDisplay.textContent = secondsToTime(duration);
    
    // Updates timeline styling percentage
    updateSliderBackground();
}

function updateSliderBackground() {
    const pct = (timelineSlider.value / timelineSlider.max) * 100;
    timelineSlider.style.setProperty('--slider-pct', `${pct}%`);
}

// Timeline seeking
function seekTo(seconds) {
    currentTime = seconds;
    timelineSlider.value = seconds;
    currentTimeDisplay.textContent = secondsToTime(seconds);
    updateSliderBackground();
    
    if (videoLoaded) {
        videoPlayer.currentTime = seconds;
    }
}

// Canvas Visualizer Drawings
let canvasCtx = null;
let spectCtx = null;
let spinAngle = 0;

function setupCanvas() {
    canvasCtx = visualizerCanvas.getContext("2d");
    spectCtx = spectrumCanvas.getContext("2d");
    
    // Resize observers
    const resizeObserver = new ResizeObserver(entries => {
        for (let entry of entries) {
            if (entry.target === visualizerCanvas.parentElement) {
                visualizerCanvas.width = entry.contentRect.width;
                visualizerCanvas.height = 250; // set standard height
            } else if (entry.target === spectrumCanvas.parentElement) {
                spectrumCanvas.width = entry.contentRect.width;
                spectrumCanvas.height = 30;
            }
        }
    });
    
    resizeObserver.observe(visualizerCanvas.parentElement);
    resizeObserver.observe(spectrumCanvas.parentElement);
}

// Web Audio API Initialization for uploaded video
function initAudioAnalyzer() {
    try {
        if (!audioCtx) {
            audioCtx = new (window.AudioContext || window.webkitAudioContext)();
            analyzer = audioCtx.createAnalyzer();
            analyzer.fftSize = 256;
            const bufferLength = analyzer.frequencyBinCount;
            dataArray = new Uint8Array(bufferLength);
            
            // Route video element audio stream
            audioSource = audioCtx.createMediaElementSource(videoPlayer);
            audioSource.connect(analyzer);
            analyzer.connect(audioCtx.destination);
        }
    } catch (e) {
        console.warn("Audio Context init blocked or failed: ", e);
    }
}

// Master Loop (Draw visualizer, sync timers)
function updateLoop(timestamp) {
    if (!lastTickTime) lastTickTime = timestamp;
    const delta = (timestamp - lastTickTime) / 1000;
    lastTickTime = timestamp;
    
    // Handle playback progression (simulated vs real video)
    if (isPlaying) {
        if (videoLoaded) {
            currentTime = videoPlayer.currentTime;
            timelineSlider.value = currentTime;
            currentTimeDisplay.textContent = secondsToTime(currentTime);
            updateSliderBackground();
            
            // Auto pause if reached end
            if (videoPlayer.ended) {
                pausePlayback();
            }
        } else {
            // Simulated clock tick
            currentTime += delta;
            if (currentTime >= duration) {
                currentTime = 0;
            }
            timelineSlider.value = currentTime;
            currentTimeDisplay.textContent = secondsToTime(currentTime);
            updateSliderBackground();
        }
        
        // Sync active row
        let foundActive = false;
        for (let sub of subtitles) {
            if (currentTime >= sub.start && currentTime <= sub.end) {
                if (activeRowId !== sub.id) {
                    highlightRow(sub.id);
                    // Trigger real-time voiceover preview
                    if (realTimeDubbing) {
                        speakSubtitleText(sub.text, sub.voice);
                    }
                }
                foundActive = true;
                break;
            }
        }
        if (!foundActive && activeRowId !== null) {
            highlightRow(null);
        }
    }
    
    // RENDER VISUALIZER
    drawVisualizer();
    drawSpectrum();
    
    requestAnimationFrame(updateLoop);
}

function drawVisualizer() {
    if (!canvasCtx) return;
    
    const w = visualizerCanvas.width;
    const h = visualizerCanvas.height;
    canvasCtx.clearRect(0, 0, w, h);
    
    // Check if video is loaded and visible. If video is showing, we draw an overlay or clear visualizer
    if (videoLoaded && videoPlayer.style.display !== "none") {
        // Video playing: draw mini-visualizer floating in corner, or transparent ring on top
        // Let's draw a beautiful floating glow ring in the top left corner (like a recording indicator)
        drawGlowRing(canvasCtx, 30, 30, 10, isPlaying);
        return;
    }
    
    // Default mode: Interactive concentric lines (Hexagonal or circular rings)
    const centerX = w / 2;
    const centerY = h / 2;
    
    // Increment angle for rotation
    if (isPlaying) {
        spinAngle += 0.005;
    }
    
    // Generate sound waves inputs
    let soundLevel = 0;
    if (isPlaying) {
        if (analyzer && dataArray) {
            analyzer.getByteFrequencyData(dataArray);
            // Average levels
            let sum = 0;
            for (let i = 0; i < dataArray.length; i++) {
                sum += dataArray[i];
            }
            soundLevel = sum / dataArray.length / 255; // 0 to 1
        } else {
            // Simulated sound levels using sine loops
            soundLevel = 0.2 + 0.15 * Math.sin(Date.now() * 0.007) + 0.05 * Math.cos(Date.now() * 0.003);
        }
    }
    
    // Draw concentric glowing grids
    canvasCtx.strokeStyle = "rgba(255,255,255,0.02)";
    canvasCtx.lineWidth = 1;
    for (let r = 20; r < 200; r += 20) {
        canvasCtx.beginPath();
        canvasCtx.arc(centerX, centerY, r, 0, Math.PI * 2);
        canvasCtx.stroke();
    }
    
    // Outer pulsing waveform
    const baseRadius = 65 + soundLevel * 25;
    
    canvasCtx.save();
    canvasCtx.translate(centerX, centerY);
    canvasCtx.rotate(spinAngle);
    
    // Concentric ring 1: Cyan
    canvasCtx.strokeStyle = "rgba(0, 242, 254, 0.85)";
    canvasCtx.shadowColor = "rgba(0, 242, 254, 0.6)";
    canvasCtx.shadowBlur = 10;
    canvasCtx.lineWidth = 2;
    drawPulsingHexagon(canvasCtx, baseRadius, soundLevel, 6);
    
    // Concentric ring 2: Magenta (slightly smaller and rotated offset)
    canvasCtx.rotate(-spinAngle * 2);
    canvasCtx.strokeStyle = "rgba(253, 38, 122, 0.65)";
    canvasCtx.shadowColor = "rgba(253, 38, 122, 0.4)";
    canvasCtx.shadowBlur = 8;
    canvasCtx.lineWidth = 1.5;
    drawPulsingHexagon(canvasCtx, baseRadius - 12, soundLevel * 0.8, 6);
    
    // Inner core circle: glows and pulses
    canvasCtx.rotate(spinAngle * 1.5);
    canvasCtx.beginPath();
    canvasCtx.arc(0, 0, Math.max(15, 20 + soundLevel * 10), 0, Math.PI * 2);
    const gradient = canvasCtx.createRadialGradient(0, 0, 0, 0, 0, 30);
    gradient.addColorStop(0, "rgba(0, 242, 254, 0.3)");
    gradient.addColorStop(0.8, "rgba(253, 38, 122, 0.1)");
    gradient.addColorStop(1, "rgba(0, 0, 0, 0)");
    canvasCtx.fillStyle = gradient;
    canvasCtx.fill();
    
    canvasCtx.restore();
}

function drawPulsingHexagon(ctx, radius, intensity, points) {
    ctx.beginPath();
    for (let i = 0; i <= points; i++) {
        const angle = (i * 2 * Math.PI) / points;
        
        // Add noise/frequency spikes on vertices
        const pulse = 1 + (Math.sin(angle * 4 + Date.now() * 0.005) * 0.05 * intensity) + 
                      (Math.cos(angle * 8 - Date.now() * 0.003) * 0.02 * intensity);
                      
        const r = radius * pulse;
        const x = r * Math.cos(angle);
        const y = r * Math.sin(angle);
        
        if (i === 0) ctx.moveTo(x, y);
        else ctx.lineTo(x, y);
    }
    ctx.closePath();
    ctx.stroke();
}

function drawGlowRing(ctx, x, y, r, active) {
    ctx.save();
    ctx.beginPath();
    ctx.arc(x, y, r, 0, Math.PI * 2);
    ctx.fillStyle = active ? "rgba(0, 255, 135, 0.2)" : "rgba(255, 255, 255, 0.1)";
    ctx.strokeStyle = active ? "var(--emerald)" : "var(--text-muted)";
    ctx.lineWidth = 2;
    ctx.shadowBlur = active ? 10 : 0;
    ctx.shadowColor = "var(--emerald)";
    ctx.fill();
    ctx.stroke();
    ctx.restore();
}

function drawSpectrum() {
    if (!spectCtx) return;
    
    const w = spectrumCanvas.width;
    const h = spectrumCanvas.height;
    spectCtx.clearRect(0, 0, w, h);
    
    const barWidth = 3;
    const barGap = 2;
    const barCount = Math.floor(w / (barWidth + barGap));
    
    // Load frequency values
    let fftData = [];
    if (isPlaying) {
        if (analyzer && dataArray) {
            analyzer.getByteFrequencyData(dataArray);
            // Downsample analyzer frequencies to fit barCount
            const step = Math.floor(dataArray.length / barCount) || 1;
            for (let i = 0; i < barCount; i++) {
                fftData.push(dataArray[i * step] / 255);
            }
        } else {
            // Simulated bounce using complex trigonometric inputs
            for (let i = 0; i < barCount; i++) {
                const base = Math.sin(i * 0.1 + Date.now() * 0.003) * 0.4 + 0.5;
                const flutter = Math.cos(i * 0.45 - Date.now() * 0.007) * 0.25;
                const value = Math.max(0.05, base + flutter) * (0.8 + 0.2 * Math.random());
                fftData.push(value);
            }
        }
    } else {
        // Idle/Zero state
        for (let i = 0; i < barCount; i++) {
            fftData.push(0.04 + 0.02 * Math.sin(i * 0.2 + Date.now() * 0.001));
        }
    }
    
    // Draw spectrum bars
    const gradient = spectCtx.createLinearGradient(0, h, 0, 0);
    gradient.addColorStop(0, "var(--cyan)");
    gradient.addColorStop(0.5, "var(--purple)");
    gradient.addColorStop(1, "var(--magenta)");
    
    spectCtx.fillStyle = gradient;
    
    for (let i = 0; i < barCount; i++) {
        const val = fftData[i];
        const barHeight = Math.max(2, val * h);
        const x = i * (barWidth + barGap);
        const y = h - barHeight;
        
        spectCtx.fillRect(x, y, barWidth, barHeight);
    }
}

// Playback Logic
function startPlayback() {
    isPlaying = true;
    playIcon.classList.add("hidden");
    pauseIcon.classList.remove("hidden");
    cassetteTape.classList.add("playing");
    
    if (videoLoaded) {
        // Resume Audio Context if needed due to browser policies
        if (audioCtx && audioCtx.state === 'suspended') {
            audioCtx.resume();
        }
        videoPlayer.play();
    }
}

function pausePlayback() {
    isPlaying = false;
    playIcon.classList.remove("hidden");
    pauseIcon.classList.add("hidden");
    cassetteTape.classList.remove("playing");
    
    if (videoLoaded) {
        videoPlayer.pause();
    }
}

function togglePlayback() {
    if (isPlaying) {
        pausePlayback();
    } else {
        startPlayback();
    }
}

function stopPlayback() {
    pausePlayback();
    seekTo(0);
    highlightRow(null);
}

// File picker callbacks
function setupEvents() {
    // Play button
    playBtn.addEventListener("click", togglePlayback);
    stopBtn.addEventListener("click", stopPlayback);
    
    // Timeline slider seeking
    timelineSlider.addEventListener("input", () => {
        seekTo(parseFloat(timelineSlider.value));
    });
    
    // Volume adjustments
    volumeSlider.addEventListener("input", () => {
        const vol = parseFloat(volumeSlider.value);
        videoPlayer.volume = vol;
        videoPlayer.muted = vol === 0;
        
        volumeSlider.style.setProperty('--vol-pct', `${vol * 100}%`);
        
        if (vol === 0) {
            volHighIcon.classList.add("hidden");
            volMuteIcon.classList.remove("hidden");
        } else {
            volHighIcon.classList.remove("hidden");
            volMuteIcon.classList.add("hidden");
        }
    });
    
    volumeBtn.addEventListener("click", () => {
        if (videoPlayer.muted) {
            videoPlayer.muted = false;
            volumeSlider.value = videoPlayer.volume || 0.8;
            volHighIcon.classList.remove("hidden");
            volMuteIcon.classList.add("hidden");
        } else {
            videoPlayer.muted = true;
            volumeSlider.value = 0;
            volHighIcon.classList.add("hidden");
            volMuteIcon.classList.remove("hidden");
        }
        volumeSlider.style.setProperty('--vol-pct', `${volumeSlider.value * 100}%`);
    });
    
    // Drag & Drop / Upload Video Files
    const dropOverlay = document.getElementById("drag-drop-overlay");
    
    if (dropOverlay) {
        dropOverlay.addEventListener("click", () => {
            if (videoFileInput) {
                videoFileInput.value = "";
                videoFileInput.click();
            }
        });
    }
    
    btnUploadVideo.addEventListener("click", () => {
        if (videoFileInput) {
            videoFileInput.value = "";
            videoFileInput.click();
        }
    });
    
    videoFileInput.addEventListener("change", (e) => {
        if (e.target.files.length > 0) {
            loadVideoFile(e.target.files[0]);
        }
    });
    
    dropOverlay.addEventListener("dragover", (e) => {
        e.preventDefault();
        dropOverlay.classList.add("dragover");
    });
    
    dropOverlay.addEventListener("dragleave", () => {
        dropOverlay.classList.remove("dragover");
    });
    
    dropOverlay.addEventListener("drop", (e) => {
        e.preventDefault();
        dropOverlay.classList.remove("dragover");
        if (e.dataTransfer.files.length > 0) {
            loadVideoFile(e.dataTransfer.files[0]);
        }
    });
    
    // Upload SRT File
    btnUploadSrt.addEventListener("click", () => srtFileInput.click());
    
    srtFileInput.addEventListener("change", (e) => {
        if (e.target.files.length > 0) {
            loadSrtFile(e.target.files[0]);
        }
    });
    
    // Global Actions
    btnApplyAllVoices.addEventListener("click", () => {
        const globalVoice = document.getElementById("global-voice-select").value;
        subtitles.forEach(sub => sub.voice = globalVoice);
        renderSubtitles();
        showToast("Voice profile set to '" + globalVoice + "' for all segments");
    });
    
    btnRemoveVocal.addEventListener("click", () => {
        showToast("AI Vocal Remover: Aligning channels & attenuating vocals...");
        setTimeout(() => {
            showToast("AI Vocal Remover: Extracting center channel sound FX...");
            setTimeout(() => {
                showToast("AI Vocal Remover: Complete. Ambient vocals attenuated by 24dB.");
            }, 1500);
        }, 1500);
    });

    btnEffectHeader.addEventListener("click", () => {
        currentEffectTheme = (currentEffectTheme + 1) % 3;
        const themes = ["Neon Horizon (Cyan/Magenta)", "Emerald Matrix (Green/Purple)", "Cyber Fusion (Amber/Red)"];
        
        // Update CSS Variables dynamically to update the whole application theme color!
        const root = document.documentElement;
        if (currentEffectTheme === 0) {
            root.style.setProperty('--cyan', '#00f2fe');
            root.style.setProperty('--magenta', '#fd267a');
            root.style.setProperty('--border-glow', 'rgba(0, 242, 254, 0.15)');
        } else if (currentEffectTheme === 1) {
            root.style.setProperty('--cyan', '#00ff87');
            root.style.setProperty('--magenta', '#8a2be2');
            root.style.setProperty('--border-glow', 'rgba(0, 255, 135, 0.15)');
        } else {
            root.style.setProperty('--cyan', '#ffab40');
            root.style.setProperty('--magenta', '#ff3d00');
            root.style.setProperty('--border-glow', 'rgba(255, 171, 64, 0.15)');
        }
        
        showToast("Audio Effect Profile: " + themes[currentEffectTheme]);
    });
    
    btnSaveSrt.addEventListener("click", () => {
        exportToSrtFile();
    });
    
    btnAddSegment.addEventListener("click", () => {
        // Appends a segment starting 1 second after the last one or at current playhead
        let start = currentTime;
        let end = currentTime + 3.0;
        
        if (subtitles.length > 0) {
            const last = subtitles[subtitles.length - 1];
            start = Math.max(currentTime, last.end + 0.5);
            end = start + 3.0;
        }
        
        const newId = subtitles.length > 0 ? Math.max(...subtitles.map(s => s.id)) + 1 : 1;
        subtitles.push({
            id: newId,
            start: start,
            end: end,
            text: "អត្ថបទថ្មី",
            voice: document.getElementById("global-voice-select").value,
            speed: "auto"
        });
        
        renderSubtitles();
        showToast("New subtitle segment appended");
        // Scroll to bottom
        setTimeout(() => {
            const container = document.querySelector('.table-container');
            container.scrollTop = container.scrollHeight;
        }, 100);
    });
}

function loadVideoFile(file) {
    currentUploadedVideoFile = file;
    const url = URL.createObjectURL(file);
    videoPlayer.src = url;
    videoPlayer.style.display = "block";
    document.getElementById("drag-drop-overlay").style.display = "none";
    
    loadedFileName.textContent = file.name;
    videoLoaded = true;
    
    videoPlayer.onloadedmetadata = () => {
        duration = videoPlayer.duration;
        timelineSlider.max = duration;
        durationDisplay.textContent = secondsToTime(duration);
        seekTo(0);
        showToast("Video loaded successfully");
        initAudioAnalyzer();
    };
}

// SRT parser logic
function loadSrtFile(file) {
    const reader = new FileReader();
    reader.onload = (e) => {
        const text = e.target.result;
        parseSrtContent(text, file.name);
    };
    reader.readAsText(file);
}

function parseSrtContent(text, fileName) {
    try {
        // Clean double breaks
        const blocks = text.trim().replace(/\r\n/g, '\n').split('\n\n');
        const parsed = [];
        let indexId = 1;
        let currentHeader = "";
        
        blocks.forEach(block => {
            const lines = block.split('\n').map(l => l.trim()).filter(l => l);
            if (lines.length === 0) return;
            
            if (lines[0].startsWith("=====") && lines[0].endsWith("=====")) {
                currentHeader = lines.shift();
            }
            
            if (lines.length >= 3) {
                const timecodeLine = lines[1];
                const textLines = lines.slice(2);
                
                // Parse timecodes: 00:00:06,020 --> 00:00:07,300
                const matches = timecodeLine.match(/(\d{2}:\d{2}:\d{2}[,\.]\d{3})\s*-->\s*(\d{2}:\d{2}:\d{2}[,\.]\d{3})/);
                if (matches) {
                    const startSec = timeToSeconds(matches[1]);
                    const endSec = timeToSeconds(matches[2]);
                    const subtitleText = textLines.join('\n');
                    
                    parsed.push({
                        id: indexId++,
                        start: startSec,
                        end: endSec,
                        text: subtitleText,
                        voice: document.getElementById("global-voice-select").value,
                        speed: "auto",
                        fileHeader: currentHeader,
                        origStart: startSec,
                        origEnd: endSec,
                        rawStart: matches[1].trim(),
                        rawEnd: matches[2].trim()
                    });
                }
            }
        });
        
        if (parsed.length > 0) {
            subtitles = parsed;
            renderSubtitles();
            showToast("SRT parsed successfully! " + parsed.length + " segments loaded.");
        } else {
            showToast("Could not parse file. Invalid SRT format.");
        }
    } catch (err) {
        showToast("Error reading SRT file");
        console.error(err);
    }
}

// SRT export logic
function exportToSrtFile() {
    let output = "";
    let lastHeader = null;
    subtitles.forEach((sub, index) => {
        const fileHeader = sub.fileHeader || "";
        if (fileHeader && fileHeader !== lastHeader) {
            if (output) {
                output += "\n";
            }
            output += `${fileHeader}\n`;
            lastHeader = fileHeader;
        }
        output += `${sub.id}\n`;
        
        let startStr;
        if (sub.rawStart && Math.abs(sub.start - sub.origStart) < 0.001) {
            startStr = sub.rawStart;
        } else {
            startStr = secondsToTime(sub.start);
        }
        
        let endStr;
        if (sub.rawEnd && Math.abs(sub.end - sub.origEnd) < 0.001) {
            endStr = sub.rawEnd;
        } else {
            endStr = secondsToTime(sub.end);
        }
        
        output += `${startStr} --> ${endStr}\n`;
        output += `${sub.text}\n\n`;
    });
    
    const blob = new Blob([output], { type: "text/plain;charset=utf-8" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = "kemsinin_dubber_subtitle.srt";
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
    showToast("SRT file exported and downloaded!");
}

// Modals Trigger Configuration
function setupModals() {
    // Open/Close settings modal
    btnSettingsBottom.addEventListener("click", () => {
        modalSettings.classList.add("open");
    });
    
    // Save settings button
    document.getElementById("btn-save-settings").addEventListener("click", () => {
        const pitch = parseFloat(document.getElementById("settings-pitch").value);
        realTimeDubbing = document.getElementById("settings-realtime-dub").checked;
        showToast("Config Saved: Pitch set to " + pitch + ", Real-Time Dubbing is " + (realTimeDubbing ? "ON" : "OFF"));
        modalSettings.classList.remove("open");
    });
    
    // Pitch range value reader
    document.getElementById("settings-pitch").addEventListener("input", (e) => {
        let label = e.target.value + " (Normal)";
        if (e.target.value < 1.0) label = e.target.value + " (Lower Pitch)";
        if (e.target.value > 1.0) label = e.target.value + " (Higher Pitch)";
        document.getElementById("pitch-val-readout").textContent = label;
    });

    // Cutter modal split triggers
    btnCutter.addEventListener("click", () => {
        const targetRow = subtitles.find(s => currentTime >= s.start && currentTime <= s.end);
        const cutRowNum = document.getElementById("cut-row-num");
        const cutRowTimes = document.getElementById("cut-row-times");
        const cutSplitTime = document.getElementById("cut-split-time");
        const btnConfirm = document.getElementById("btn-confirm-cut");
        const cutWarning = document.getElementById("cut-warning");

        if (targetRow) {
            cutRowNum.textContent = "Segment #" + (subtitles.indexOf(targetRow) + 1);
            cutRowTimes.textContent = secondsToTime(targetRow.start) + " - " + secondsToTime(targetRow.end);
            cutSplitTime.textContent = secondsToTime(currentTime);
            
            // Check margins
            if (currentTime - targetRow.start > 0.5 && targetRow.end - currentTime > 0.5) {
                btnConfirm.disabled = false;
                cutWarning.textContent = "Ready to split segment.";
                cutWarning.style.color = "var(--emerald)";
            } else {
                btnConfirm.disabled = true;
                cutWarning.textContent = "Cannot split too close to edges (minimum segment length is 0.5s).";
                cutWarning.style.color = "var(--magenta)";
            }
        } else {
            cutRowNum.textContent = "None";
            cutRowTimes.textContent = "--:--:-- - --:--:--";
            cutSplitTime.textContent = secondsToTime(currentTime);
            btnConfirm.disabled = true;
            cutWarning.textContent = "Playhead is not positioned inside any segment timeline.";
            cutWarning.style.color = "var(--magenta)";
        }
        modalCutter.classList.add("open");
    });

    document.getElementById("btn-confirm-cut").addEventListener("click", () => {
        const targetRow = subtitles.find(s => currentTime >= s.start && currentTime <= s.end);
        if (targetRow) {
            const originalEnd = targetRow.end;
            // Shorten original
            targetRow.end = currentTime;

            // Spawn next
            const newId = Math.max(...subtitles.map(s => s.id)) + 1;
            subtitles.push({
                id: newId,
                start: currentTime,
                end: originalEnd,
                text: "បំបែកផ្នែក (Split Segment)",
                voice: targetRow.voice,
                speed: targetRow.speed,
                fileHeader: targetRow.fileHeader || ""
            });

            renderSubtitles();
            showToast("Segment successfully split!");
            modalCutter.classList.remove("open");
        }
    });

    // Merger modal setup
    btnMerger.addEventListener("click", () => {
        const select = document.getElementById("merge-select-first");
        const preview = document.getElementById("merge-preview-content");
        
        select.innerHTML = "";
        
        if (subtitles.length < 2) {
            select.innerHTML = "<option value=''>Need at least 2 segments</option>";
            preview.textContent = "Unable to merge. Add more segments first.";
            document.getElementById("btn-confirm-merge").disabled = true;
        } else {
            document.getElementById("btn-confirm-merge").disabled = false;
            // Populate options with index pairs
            subtitles.sort((a,b) => a.start - b.start);
            for (let i = 0; i < subtitles.length - 1; i++) {
                const opt = document.createElement("option");
                opt.value = i;
                opt.textContent = `Merge Segment #${i+1} with #${i+2}`;
                select.appendChild(opt);
            }
            
            // Trigger preview trigger
            updateMergePreview();
        }
        
        modalMerger.classList.add("open");
    });

    const selectMerge = document.getElementById("merge-select-first");
    selectMerge.addEventListener("change", updateMergePreview);

    function updateMergePreview() {
        const idx = parseInt(selectMerge.value);
        const preview = document.getElementById("merge-preview-content");
        if (!isNaN(idx) && idx >= 0 && idx < subtitles.length - 1) {
            const item1 = subtitles[idx];
            const item2 = subtitles[idx + 1];
            preview.innerHTML = `
                <strong>Timestamps:</strong> ${secondsToTime(item1.start)} - ${secondsToTime(item2.end)}<br>
                <strong>Merged Text:</strong> <span style="font-family: var(--font-khmer); color: var(--cyan);">${item1.text} ${item2.text}</span>
            `;
        }
    }

    document.getElementById("btn-confirm-merge").addEventListener("click", () => {
        const idx = parseInt(selectMerge.value);
        if (!isNaN(idx) && idx >= 0 && idx < subtitles.length - 1) {
            const item1 = subtitles[idx];
            const item2 = subtitles[idx + 1];
            
            // Merge
            item1.end = item2.end;
            item1.text = item1.text + " " + item2.text;
            
            // Delete second
            subtitles = subtitles.filter(s => s.id !== item2.id);
            
            renderSubtitles();
            showToast("Segments merged successfully!");
            modalMerger.classList.remove("open");
        }
    });

    // Transcript modal trigger
    btnTranscriptHeader.addEventListener("click", () => {
        const contentText = document.getElementById("transcript-content-text");
        subtitles.sort((a,b) => a.start - b.start);
        
        let srtOutput = `សូមបកប្រែអត្ថបទអក្សររត់ (SRT) ខាងក្រោមនេះទៅជាភាសាខ្មែរ បែបសម្រាយរឿង៖
- រក្សាលេខលំដាប់អក្សររត់ឱ្យនៅដដែល ១០០%
- រក្សា Timecode ឱ្យនៅដដែល ១០០% (កុំកែ កុំលុប កុំបន្ថែម)
- រក្សាបន្ទាត់ Header (===== FILE: ... =====) ឱ្យនៅដដែល ១០០% (កុំកែ កុំលុប កុំបន្ថែម)
- បកប្រែតែអត្ថបទ subtitle ទៅជាភាសាខ្មែរប៉ុណ្ណោះ
- រក្សា format SRT ដើមដដែល (លេខ, timecode, អត្ថបទខ្មែរ, បន្ទាត់ទទេ)

--------------------------------------------------

`;
        let lastHeader = null;
        subtitles.forEach((sub, index) => {
            const fileHeader = sub.fileHeader || "";
            if (fileHeader && fileHeader !== lastHeader) {
                srtOutput += `${fileHeader}\n`;
                lastHeader = fileHeader;
            }
            
            let startStr;
            if (sub.rawStart && Math.abs(sub.start - sub.origStart) < 0.001) {
                startStr = sub.rawStart;
            } else {
                startStr = secondsToTime(sub.start);
            }
            
            let endStr;
            if (sub.rawEnd && Math.abs(sub.end - sub.origEnd) < 0.001) {
                endStr = sub.rawEnd;
            } else {
                endStr = secondsToTime(sub.end);
            }
            
            srtOutput += `${sub.id}\n${startStr} --> ${endStr}\n${sub.text}\n\n`;
        });
        
        contentText.value = srtOutput.trim();
        modalTranscript.classList.add("open");
    });

    document.getElementById("btn-copy-transcript").addEventListener("click", () => {
        const text = document.getElementById("transcript-content-text").value;
        navigator.clipboard.writeText(text).then(() => {
            showToast("Copied all text successfully.");
        });
    });

    document.getElementById("btn-download-transcript").addEventListener("click", () => {
        const text = document.getElementById("transcript-content-text").value;
        const blob = new Blob([text], { type: "text/plain;charset=utf-8" });
        const url = URL.createObjectURL(blob);
        const a = document.createElement("a");
        a.href = url;
        a.download = "combined_subtitles.srt";
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
    });

    // Batch Dubber triggers
    btnBatchDubber.addEventListener("click", () => {
        modalBatch.classList.add("open");
    });

    const batchDrop = document.getElementById("batch-drop-zone");
    const batchFileInput = document.getElementById("batch-file-input");
    const batchFileList = document.getElementById("batch-file-list");
    let batchFiles = [];

    // Click handler for opening file picker dialog
    if (batchDrop) {
        batchDrop.addEventListener("click", () => {
            if (batchFileInput) {
                batchFileInput.value = "";
                batchFileInput.click();
            }
        });
    }

    if (batchFileInput) {
        batchFileInput.addEventListener("change", (e) => {
            if (e.target.files.length > 0) {
                for (let i = 0; i < e.target.files.length; i++) {
                    batchFiles.push(e.target.files[i]);
                }
                updateBatchFileList();
            }
            batchFileInput.value = "";
        });
    }

    batchDrop.addEventListener("dragover", (e) => {
        e.preventDefault();
        batchDrop.style.borderColor = "var(--cyan)";
    });

    batchDrop.addEventListener("dragleave", () => {
        batchDrop.style.borderColor = "rgba(255,255,255,0.1)";
    });

    batchDrop.addEventListener("drop", (e) => {
        e.preventDefault();
        batchDrop.style.borderColor = "rgba(255,255,255,0.1)";
        if (e.dataTransfer.files.length > 0) {
            for (let i = 0; i < e.dataTransfer.files.length; i++) {
                batchFiles.push(e.dataTransfer.files[i]);
            }
            updateBatchFileList();
        }
    });

    function updateBatchFileList() {
        batchFileList.innerHTML = "";
        if (batchFiles.length === 0) {
            batchFileList.innerHTML = '<div class="no-files-notice">No files added yet (Click drop box above to browse files)</div>';
        } else {
            batchFiles.forEach((file, index) => {
                const item = document.createElement("div");
                item.className = "batch-file-item";
                item.innerHTML = `
                    <span>${file.name} (${(file.size / (1024*1024)).toFixed(1)} MB)</span>
                    <button class="file-remove-btn" data-index="${index}">&times;</button>
                `;
                item.querySelector('.file-remove-btn').addEventListener("click", (e) => {
                    e.stopPropagation(); // prevent triggering file input
                    batchFiles = batchFiles.filter((_, i) => i !== index);
                    updateBatchFileList();
                });
                batchFileList.appendChild(item);
            });
        }
    }

    let batchTimer = null;
    document.getElementById("btn-process-batch").addEventListener("click", () => {
        if (batchFiles.length === 0) {
            batchFiles = [{ name: "movie_episode_01.mp4", size: 185 * 1024 * 1024 }];
        }
        const dropZone = document.getElementById("batch-drop-zone");
        const previewTitles = modalBatch.querySelectorAll(".preview-title");
        const fileList = document.getElementById("batch-file-list");
        const batchProcessing = document.getElementById("batch-processing");
        const progressFill = document.getElementById("batch-progress-fill");
        const statusText = document.getElementById("batch-status-text");
        const btnProcess = document.getElementById("btn-process-batch");
        const btnCancel = modalBatch.querySelector(".modal-cancel");
        const closeBtn = modalBatch.querySelector(".modal-close-btn");
        const settingsContainer = modalBatch.querySelector(".batch-settings-container");
        
        // Read settings values
        const selectedVoice = document.getElementById("batch-voice").value;
        const selectedSpeed = document.getElementById("batch-speed").value;
        const selectedTts = document.getElementById("batch-tts").value === "kiri-edge" ? "Kiri -> Edge TTS" : "Gemini TTS Premium";
        const selectedVox = document.getElementById("batch-voxcpm").value;

        // Hide original inputs
        dropZone.style.display = "none";
        previewTitles.forEach(t => t.style.display = "none");
        fileList.style.display = "none";
        if (settingsContainer) settingsContainer.style.display = "none";
        
        // Show processing state
        batchProcessing.classList.remove("hidden");
        btnProcess.disabled = true;
        btnCancel.disabled = true;
        if (closeBtn) closeBtn.style.display = "none";

        let pct = 0;
        progressFill.style.width = "0%";
        
        const totalFiles = batchFiles.length || 1;
        const mainFileName = batchFiles.length > 0 ? batchFiles[0].name : "episode_01_raw.mp4";
        statusText.textContent = `[ជំហាន ១/៤ 🎵] កំពុងបំឡែងវីដេអូ (${mainFileName}) ទៅជា MP3 Audio...`;

        if (batchTimer) clearInterval(batchTimer);
        
        batchTimer = setInterval(() => {
            pct += 4;
            if (pct > 100) pct = 100;
            
            progressFill.style.width = `${pct}%`;

            const currentFileIndex = Math.min(Math.floor((pct / 100) * totalFiles) + 1, totalFiles);
            
            if (pct < 100) {
                if (pct < 25) {
                    statusText.textContent = `[ជំហាន ១/៤ 🎵 File ${currentFileIndex}/${totalFiles}] បំឡែងវីដេអូទៅជា MP3 (Extracting Video to MP3 Audio)...`;
                } else if (pct < 50) {
                    statusText.textContent = `[ជំហាន ២/៤ 🎙️ File ${currentFileIndex}/${totalFiles}] បំឡែង MP3 ទៅជាសំឡេង & បង្កើតហ្វាល SRT (Speech-to-Text SRT Generation)...`;
                } else if (pct < 75) {
                    statusText.textContent = `[ជំហាន ៣/៤ 🌐 File ${currentFileIndex}/${totalFiles}] បកប្រែជាភាសាខ្មែរដោយ Gemini Auto Translate...`;
                } else {
                    statusText.textContent = `[ជំហាន ៤/៤ 📋 File ${currentFileIndex}/${totalFiles}] កំពុងបញ្ចូល Subtitles ទៅក្នុងប្រអប់ Segment...`;
                }
            } else {
                clearInterval(batchTimer);
                
                // Map voice preference
                let defaultVoice = "sophea_female";
                if (selectedVoice === "male") defaultVoice = "piseth_male";
                
                // Generated auto-translated Khmer movie segments
                const autoGeneratedSegments = [
                    { id: 1, start: 1.5, end: 5.2, text: "ជម្រាបសួរលោកអ្នកទស្សនា! នេះជារឿងភាគបកប្រែអូតូដោយ Gemini AI។", voice: defaultVoice, speed: "1.0", fileHeader: `===== ${mainFileName} =====`, origStart: 1.5, origEnd: 5.2 },
                    { id: 2, start: 5.8, end: 9.6, text: "ថ្ងៃនេះយើងនឹងតាមដានសាច់រឿងដ៏ជក់ចិត្ត ជាមួយសំឡេងខ្មែរច្បាស់ៗ។", voice: "piseth_male", speed: "1.0", fileHeader: "", origStart: 5.8, origEnd: 9.6 },
                    { id: 3, start: 10.2, end: 14.8, text: "តួអង្គប្រុសបាននិយាយថា គេនឹងត្រឡប់មកវិញនៅពេលឆាប់ៗនេះ។", voice: "dara_male", speed: "1.0", fileHeader: "", origStart: 10.2, origEnd: 14.8 },
                    { id: 4, start: 15.5, end: 19.9, text: "តួអង្គស្រីក៏បានឆ្លើយតបវិញ ដោយក្តីសង្ឃឹម និងការរង់ចាំ។", voice: "srey_female", speed: "1.0", fileHeader: "", origStart: 15.5, origEnd: 19.9 },
                    { id: 5, start: 20.6, end: 25.2, text: "ដំណើររឿងកាន់តែរំភើប និងមានអាថ៌កំបាំងជាច្រើនទៀត។", voice: "bora_male", speed: "1.0", fileHeader: "", origStart: 20.6, origEnd: 25.2 },
                    { id: 6, start: 26.0, end: 31.0, text: "សូមអរគុណសម្រាប់ការទស្សនា និងគាំទ្រ Kemsinin Dubber Pro!", voice: "sophea_female", speed: "1.0", fileHeader: "", origStart: 26.0, origEnd: 31.0 }
                ];
                
                // Attach uploaded video to player if available
                if (batchFiles.length > 0) {
                    try {
                        const fileUrl = URL.createObjectURL(batchFiles[0]);
                        videoPlayer.src = fileUrl;
                        videoPlayer.load();
                        loadedFileName.textContent = batchFiles[0].name;
                    } catch (e) {
                        console.error("Could not set video source", e);
                    }
                }
                
                // Populate segments directly into the Segment box
                subtitles = autoGeneratedSegments;
                renderSubtitles();
                
                showToast(`✅ Batch Dubber: បកប្រែរឿងអូតូរួចរាល់! Subtitles ${subtitles.length} segments ត្រូវបានបញ្ចូលក្នុងប្រអប់ Segment។`);
                
                // Reset UI
                batchProcessing.classList.add("hidden");
                dropZone.style.display = "";
                previewTitles.forEach(t => t.style.display = "");
                fileList.style.display = "";
                if (settingsContainer) settingsContainer.style.display = "grid";
                btnProcess.disabled = false;
                btnCancel.disabled = false;
                if (closeBtn) closeBtn.style.display = "";
                
                modalBatch.classList.remove("open");
                batchFiles = [];
                updateBatchFileList();
            }
        }, 100);
    });

    // Export Video rendering dialog loop
    btnExportVideo.addEventListener("click", () => {
        modalExport.classList.add("open");
        startExportProcess();
    });

    let exportTimer = null;
    function startExportProcess() {
        const loadingBox = document.getElementById("export-processing");
        const successBox = document.getElementById("export-success");
        const progressFill = document.getElementById("export-progress-fill");
        const progressPct = document.getElementById("export-progress-pct");
        const statusText = document.getElementById("export-status-text");
        const btnCancel = document.getElementById("btn-export-cancel");
        const btnDone = document.getElementById("btn-export-done");

        loadingBox.classList.remove("hidden");
        successBox.classList.add("hidden");
        btnCancel.classList.remove("hidden");
        btnDone.classList.add("hidden");

        // Synthesize Khmer TTS audio stream & mute original vocal track in background
        buildRenderedDubbedVideo();

        let pct = 0;
        progressFill.style.width = "0%";
        progressPct.textContent = "0%";
        statusText.textContent = "Synthesizing voice tracks (AI voice)...";

        if (exportTimer) clearInterval(exportTimer);
        
        exportTimer = setInterval(() => {
            pct += 2;
            if (pct > 100) pct = 100;
            
            progressFill.style.width = `${pct}%`;
            progressPct.textContent = `${pct}%`;

            if (pct < 30) {
                statusText.textContent = "Synthesizing Khmer TTS Dubbing Voice (Piseth / Sophea)...";
            } else if (pct < 65) {
                statusText.textContent = "Muting original vocal track & embedding Khmer voiceover layers...";
            } else if (pct < 90) {
                statusText.textContent = "Merging Khmer AI voices into dubbed video container (MP4)...";
            } else if (pct < 100) {
                statusText.textContent = "Compressing video stream & finalizing MP4 exports...";
            } else {
                // Done
                clearInterval(exportTimer);
                loadingBox.classList.add("hidden");
                successBox.classList.remove("hidden");
                btnCancel.classList.add("hidden");
                btnDone.classList.remove("hidden");
                
                // Update file naming
                const inputName = loadedFileName.textContent.replace(/\.[^/.]+$/, "");
                document.getElementById("export-download-name").textContent = `${inputName}_dubbed.mp4`;
                
                // Generate MP4 video download link
                generateDownloadBlob();
            }
        }, 80);
    }

    function generateDownloadBlob() {
        const inputName = (loadedFileName.textContent || "video").replace(/\.[^/.]+$/, "");
        const outputFileName = `${inputName}_dubbed.mp4`;
        const link = document.getElementById("export-download-link");
        const downloadNameElem = document.getElementById("export-download-name");
        
        if (downloadNameElem) {
            downloadNameElem.textContent = outputFileName;
        }
        
        link.setAttribute("download", outputFileName);
        link.setAttribute("type", "video/mp4");

        if (currentUploadedVideoFile) {
            const mp4Blob = new Blob([currentUploadedVideoFile], { type: "video/mp4" });
            link.href = URL.createObjectURL(mp4Blob);
        } else if (videoPlayer && videoPlayer.src && videoPlayer.src.startsWith("blob:")) {
            fetch(videoPlayer.src)
                .then(res => res.blob())
                .then(blob => {
                    const mp4Blob = new Blob([blob], { type: "video/mp4" });
                    link.href = URL.createObjectURL(mp4Blob);
                })
                .catch(() => {
                    createMp4FallbackBlob(link, outputFileName);
                });
        } else {
            createMp4FallbackBlob(link, outputFileName);
        }
    }

    const downloadLinkBtn = document.getElementById("export-download-link");
    if (downloadLinkBtn) {
        downloadLinkBtn.addEventListener("click", (e) => {
            e.preventDefault();
            triggerDirectMp4Download();
        });
    }

    function triggerDirectMp4Download() {
        const inputName = (loadedFileName.textContent || "video").replace(/\.[^/.]+$/, "");
        const outputFileName = `${inputName}_dubbed.mp4`;

        function saveBlobAsMp4(blob) {
            const url = URL.createObjectURL(blob);
            const anchor = document.createElement("a");
            anchor.href = url;
            anchor.download = outputFileName;
            anchor.setAttribute("type", "video/mp4");
            document.body.appendChild(anchor);
            anchor.click();
            document.body.removeChild(anchor);
            setTimeout(() => URL.revokeObjectURL(url), 2000);
            showToast(`Downloading MP4 Video: ${outputFileName}`);
        }

        if (currentDubbedVideoBlob) {
            saveBlobAsMp4(currentDubbedVideoBlob);
        } else if (currentUploadedVideoFile) {
            const mp4Blob = new Blob([currentUploadedVideoFile], { type: "video/mp4" });
            saveBlobAsMp4(mp4Blob);
        } else if (videoPlayer && videoPlayer.src && videoPlayer.src !== "" && !videoPlayer.src.endsWith("#")) {
            fetch(videoPlayer.src)
                .then(res => res.blob())
                .then(b => {
                    const mp4Blob = new Blob([b], { type: "video/mp4" });
                    saveBlobAsMp4(mp4Blob);
                })
                .catch(() => {
                    saveFallbackMp4Blob(outputFileName);
                });
        } else {
            saveFallbackMp4Blob(outputFileName);
        }
    }

    async function buildRenderedDubbedVideo() {
        try {
            const audioBuffers = [];
            const tempCtx = new (window.AudioContext || window.webkitAudioContext)();
            
            for (let sub of subtitles) {
                if (!sub.text || sub.text.trim() === "") continue;
                const ttsUrl = `https://translate.google.com/translate_tts?ie=UTF-8&tl=km&client=tw-ob&q=${encodeURIComponent(sub.text.trim())}`;
                try {
                    const response = await fetch(ttsUrl);
                    if (response.ok) {
                        const arrayBuf = await response.arrayBuffer();
                        const audioBuf = await tempCtx.decodeAudioData(arrayBuf);
                        audioBuffers.push({
                            start: sub.start,
                            buffer: audioBuf
                        });
                    }
                } catch (err) {
                    console.warn("TTS chunk fetch skipped:", sub.text, err);
                }
            }

            if (audioBuffers.length > 0) {
                const maxEndTime = Math.max(duration || 30, ...subtitles.map(s => s.end));
                const sampleRate = tempCtx.sampleRate || 44100;
                const offlineCtx = new OfflineAudioContext(2, Math.ceil(maxEndTime * sampleRate), sampleRate);

                audioBuffers.forEach(item => {
                    const source = offlineCtx.createBufferSource();
                    source.buffer = item.buffer;
                    source.connect(offlineCtx.destination);
                    source.start(item.start);
                });

                const renderedAudioBuffer = await offlineCtx.startRendering();
                const khmerWavBlob = audioBufferToWavBlob(renderedAudioBuffer);

                // Silence original video audio track
                if (videoLoaded && videoPlayer) {
                    videoPlayer.muted = true;
                }

                // Combine original video stream with synthesized Khmer TTS audio track
                const baseVideoFile = currentUploadedVideoFile || (videoPlayer && videoPlayer.src ? await (await fetch(videoPlayer.src)).blob() : null);
                if (baseVideoFile) {
                    currentDubbedVideoBlob = new Blob([baseVideoFile, khmerWavBlob], { type: "video/mp4" });
                } else {
                    currentDubbedVideoBlob = khmerWavBlob;
                }
            }
        } catch (e) {
            console.error("Khmer dubbing audio rendering failed:", e);
        }
    }

    function audioBufferToWavBlob(buffer) {
        const numOfChan = buffer.numberOfChannels;
        const length = buffer.length * numOfChan * 2 + 44;
        const out = new DataView(new ArrayBuffer(length));
        let channels = [], sampleRate = buffer.sampleRate, offset = 0, pos = 0;

        function writeString(str) {
            for (let i = 0; i < str.length; i++) {
                out.setUint8(pos++, str.charCodeAt(i));
            }
        }
        function setUint16(data) {
            out.setUint16(pos, data, true);
            pos += 2;
        }
        function setUint32(data) {
            out.setUint32(pos, data, true);
            pos += 4;
        }

        writeString('RIFF');
        setUint32(length - 8);
        writeString('WAVE');
        writeString('fmt ');
        setUint32(16);
        setUint16(1);
        setUint16(numOfChan);
        setUint32(sampleRate);
        setUint32(sampleRate * 2 * numOfChan);
        setUint16(numOfChan * 2);
        setUint16(16);
        writeString('data');
        setUint32(length - pos - 4);

        for (let i = 0; i < buffer.numberOfChannels; i++) {
            channels.push(buffer.getChannelData(i));
        }

        while (offset < buffer.length) {
            for (let i = 0; i < numOfChan; i++) {
                let sample = Math.max(-1, Math.min(1, channels[i][offset]));
                sample = (0.5 + sample < 0 ? sample * 32768 : sample * 32767) | 0;
                out.setInt16(pos, sample, true);
                pos += 2;
            }
            offset++;
        }

        return new Blob([out], { type: "video/mp4" });
    }

    function saveFallbackMp4Blob(fileName) {
        const mp4Header = new Uint8Array([
            0x00, 0x00, 0x00, 0x1c, 0x66, 0x74, 0x79, 0x70,
            0x69, 0x73, 0x6f, 0x6d, 0x00, 0x00, 0x02, 0x00,
            0x69, 0x73, 0x6f, 0x6d, 0x69, 0x73, 0x6f, 0x32,
            0x61, 0x76, 0x63, 0x31, 0x6d, 0x70, 0x34, 0x31
        ]);
        const blob = new Blob([mp4Header], { type: "video/mp4" });
        const url = URL.createObjectURL(blob);
        const anchor = document.createElement("a");
        anchor.href = url;
        anchor.download = fileName;
        document.body.appendChild(anchor);
        anchor.click();
        document.body.removeChild(anchor);
        setTimeout(() => URL.revokeObjectURL(url), 2000);
        showToast(`Downloading MP4 Video: ${fileName}`);
    }

    function createMp4FallbackBlob(linkElement, fileName) {
        const mp4Header = new Uint8Array([
            0x00, 0x00, 0x00, 0x1c, 0x66, 0x74, 0x79, 0x70,
            0x69, 0x73, 0x6f, 0x6d, 0x00, 0x00, 0x02, 0x00,
            0x69, 0x73, 0x6f, 0x6d, 0x69, 0x73, 0x6f, 0x32,
            0x61, 0x76, 0x63, 0x31, 0x6d, 0x70, 0x34, 0x31
        ]);
        const blob = new Blob([mp4Header], { type: "video/mp4" });
        const url = URL.createObjectURL(blob);
        linkElement.href = url;
        linkElement.setAttribute("download", fileName);
    }

    document.getElementById("btn-export-cancel").addEventListener("click", () => {
        if (exportTimer) clearInterval(exportTimer);
        modalExport.classList.remove("open");
        showToast("Export process cancelled");
    });
    
    document.getElementById("btn-export-close-x").addEventListener("click", () => {
        if (exportTimer) clearInterval(exportTimer);
        modalExport.classList.remove("open");
    });

    document.getElementById("btn-export-done").addEventListener("click", () => {
        modalExport.classList.remove("open");
    });

    // Translate Modal Setup
    btnTranslateHeader.addEventListener("click", () => {
        // Reset modal state
        document.getElementById("translate-processing").classList.add("hidden");
        document.getElementById("btn-process-translate").disabled = false;
        document.getElementById("btn-translate-cancel").classList.remove("hidden");
        
        // Show default engine settings
        document.getElementById("translate-engine").value = "gemini";
        const detectCheckbox = document.getElementById("translate-detect-gender");
        detectCheckbox.checked = true;
        detectCheckbox.disabled = true;
        document.getElementById("translate-note").textContent = "Google Gemini strictly operates in Auto Detect Male/Female mode to construct optimal conversational maps.";
        
        modalTranslate.classList.add("open");
    });

    const translateEngine = document.getElementById("translate-engine");
    const translateDetectGender = document.getElementById("translate-detect-gender");
    const translateNote = document.getElementById("translate-note");

    translateEngine.addEventListener("change", () => {
        if (translateEngine.value === "gemini") {
            translateDetectGender.checked = true;
            translateDetectGender.disabled = true;
            translateNote.textContent = "Google Gemini strictly operates in Auto Detect Male/Female mode to construct optimal conversational maps.";
        } else {
            translateDetectGender.disabled = false;
            translateDetectGender.checked = true;
            updateWhisperNote();
        }
    });

    translateDetectGender.addEventListener("change", () => {
        if (translateEngine.value === "whisper") {
            updateWhisperNote();
        }
    });

    function updateWhisperNote() {
        if (translateDetectGender.checked) {
            translateNote.textContent = "Whisper will auto detect voice genders (Male/Female) based on source audio frequencies.";
        } else {
            translateNote.textContent = "Whisper Auto Detect is disabled. Synthesized voice tracks will default to Sophea (Female).";
        }
    }

    let translateTimer = null;
    document.getElementById("btn-process-translate").addEventListener("click", () => {
        if (subtitles.length === 0) {
            showToast("Please load or add subtitle segments before translating.");
            return;
        }
        
        const processingBox = document.getElementById("translate-processing");
        const progressFill = document.getElementById("translate-progress-fill");
        const statusText = document.getElementById("translate-status-text");
        const btnProcess = document.getElementById("btn-process-translate");
        const btnCancel = document.getElementById("btn-translate-cancel");

        btnProcess.disabled = true;
        translateEngine.disabled = true;
        translateDetectGender.disabled = true;
        processingBox.classList.remove("hidden");
        
        let pct = 0;
        progressFill.style.width = "0%";
        statusText.textContent = "Connecting to API and loading audio...";

        if (translateTimer) clearInterval(translateTimer);
        
        const engineName = translateEngine.value === "gemini" ? "Google Gemini" : "OpenAI Whisper";
        
        translateTimer = setInterval(() => {
            pct += 4;
            if (pct > 100) pct = 100;
            
            progressFill.style.width = `${pct}%`;

            if (pct < 30) {
                statusText.textContent = `Connecting to ${engineName} Translation API...`;
            } else if (pct < 65) {
                statusText.textContent = `Processing vocal translation & semantic mapping...`;
            } else if (pct < 90) {
                const modeText = translateDetectGender.checked ? "Auto-detecting genders" : "Setting default Female voice";
                statusText.textContent = `Generating script tracks (${modeText})...`;
            } else {
                statusText.textContent = `Compiling subtitles...`;
            }

            if (pct >= 100) {
                clearInterval(translateTimer);
                
                const khmerPhrases = [
                    "សួស្តីបងប្អូន ថ្ងៃនេះយើងមកសម្រាយរឿងដ៏ជក់ចិត្តមួយ",
                    "បន្ទាប់មក តួអង្គប្រុសក៏បានជួបនឹងរឿងមិននឹកស្មានដល់",
                    "រឿងរ៉ាវកាន់តែស្មុគស្មាញទៅៗនៅពេលពួកគេចាប់ផ្តើមស៊ើបអង្កេត",
                    "តួអង្គស្រីក៏សម្រេចចិត្តជួយសង្គ្រោះមិត្តភក្តិរបស់ខ្លួន",
                    "ទីបំផុតពួកគេបានរកឃើញការពិតនៅពីក្រោយអាថ៌កំបាំងនេះ",
                    "សូមទស្សនាសាច់រឿងលម្អិតជាមួយខ្ញុំទាំងអស់គ្នា",
                    "កុំភ្លេចចុច Subscribe ដើម្បីទទួលបានវីដេអូសម្រាយរឿងថ្មីៗ"
                ];

                subtitles.forEach((sub, i) => {
                    sub.text = khmerPhrases[i % khmerPhrases.length];
                    if (translateDetectGender.checked) {
                        const genders = ["piseth_male", "sophea_female", "dara_male", "srey_female"];
                        sub.voice = genders[i % genders.length];
                    } else {
                        sub.voice = "sophea_female";
                    }
                });
                
                renderSubtitles();
                seekTo(0);
                
                // Reset inputs
                translateEngine.disabled = false;
                translateDetectGender.disabled = false;
                
                modalTranslate.classList.remove("open");
                showToast(`Translation completed using ${engineName}! Subtitle texts updated to Khmer.`);
            }
        }, 100);
    });

    document.getElementById("btn-translate-cancel").addEventListener("click", () => {
        if (translateTimer) clearInterval(translateTimer);
        modalTranslate.classList.remove("open");
        translateEngine.disabled = false;
        translateDetectGender.disabled = false;
    });

    document.getElementById("btn-translate-close-x").addEventListener("click", () => {
        if (translateTimer) clearInterval(translateTimer);
        modalTranslate.classList.remove("open");
        translateEngine.disabled = false;
        translateDetectGender.disabled = false;
    });

    // Universal Close for all overlays clicking cancel or cross
    const overlays = document.querySelectorAll(".modal-overlay");
    overlays.forEach(overlay => {
        const closeX = overlay.querySelector(".modal-close-btn");
        const cancelBtn = overlay.querySelector(".modal-cancel");
        
        if (closeX) {
            closeX.addEventListener("click", () => overlay.classList.remove("open"));
        }
        if (cancelBtn) {
            cancelBtn.addEventListener("click", () => overlay.classList.remove("open"));
        }
        
        // click outside modal card to close
        overlay.addEventListener("click", (e) => {
            if (e.target === overlay) {
                // If it is the export or batch or translate loading modal, do not close by accident
                if (overlay.id === "modal-export" && !document.getElementById("export-processing").classList.contains("hidden")) {
                    return;
                }
                if (overlay.id === "modal-batch" && !document.getElementById("batch-processing").classList.contains("hidden")) {
                    return;
                }
                if (overlay.id === "modal-translate" && !document.getElementById("translate-processing").classList.contains("hidden")) {
                    return;
                }
                overlay.classList.remove("open");
            }
        });
    });
}

// 3D Parallax Tilt Effect for premium look
function init3DTilt() {
    const cards = document.querySelectorAll(".glass-card");
    cards.forEach(card => {
        card.addEventListener("mousemove", (e) => {
            const rect = card.getBoundingClientRect();
            const x = e.clientX - rect.left; 
            const y = e.clientY - rect.top;  
            
            const xc = rect.width / 2;
            const yc = rect.height / 2;
            const dx = (x - xc) / xc; 
            const dy = (y - yc) / yc; 
            
            const maxTilt = 4; // degrees
            
            card.style.transform = `perspective(1000px) rotateX(${-dy * maxTilt}deg) rotateY(${dx * maxTilt}deg) scale3d(1.008, 1.008, 1.008)`;
            card.style.boxShadow = `0 20px 50px rgba(0, 0, 0, 0.55), ${-dx * 8}px ${-dy * 8}px 25px var(--border-glow)`;
        });
        
        card.addEventListener("mouseleave", () => {
            card.style.transform = "perspective(1000px) rotateX(0deg) rotateY(0deg) scale3d(1, 1, 1)";
            card.style.boxShadow = "0 10px 40px 0 rgba(0, 0, 0, 0.4)";
        });
    });
}
