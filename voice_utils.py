import streamlit as st
import json
from typing import Optional, Dict, Any, Callable
import base64
from pathlib import Path
import tempfile
import os

def initialize_voice_state():
    """Initialize session state variables for voice input"""
    if "is_listening" not in st.session_state:
        st.session_state.is_listening = False
    if "transcript" not in st.session_state:
        st.session_state.transcript = ""
    if "audio_data" not in st.session_state:
        st.session_state.audio_data = None

def get_voice_input_js() -> str:
    """Return JavaScript code for voice input functionality"""
    return """
    <script>
    class VoiceInput {
        constructor() {
            this.recognition = null;
            this.isListening = false;
            this.transcript = '';
            this.onTranscriptUpdate = null;
            this.onListeningStateChange = null;
            this.initializeSpeechRecognition();
        }

        initializeSpeechRecognition() {
            if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
                const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
                this.recognition = new SpeechRecognition();
                this.recognition.continuous = true;
                this.recognition.interimResults = true;
                this.recognition.lang = 'en-US';

                this.recognition.onstart = () => {
                    this.isListening = true;
                    if (this.onListeningStateChange) {
                        this.onListeningStateChange(true);
                    }
                };

                this.recognition.onend = () => {
                    this.isListening = false;
                    if (this.onListeningStateChange) {
                        this.onListeningStateChange(false);
                    }
                };

                this.recognition.onresult = (event) => {
                    let interimTranscript = '';
                    let finalTranscript = '';

                    for (let i = event.resultIndex; i < event.results.length; i++) {
                        const transcript = event.results[i][0].transcript;
                        if (event.results[i].isFinal) {
                            finalTranscript += transcript;
                        } else {
                            interimTranscript += transcript;
                        }
                    }

                    this.transcript = finalTranscript + interimTranscript;
                    if (this.onTranscriptUpdate) {
                        this.onTranscriptUpdate(this.transcript);
                    }
                };

                this.recognition.onerror = (event) => {
                    console.error('Speech recognition error:', event.error);
                    this.stopListening();
                };
            } else {
                console.error('Speech recognition not supported');
            }
        }

        startListening() {
            if (this.recognition && !this.isListening) {
                try {
                    this.recognition.start();
                } catch (error) {
                    console.error('Error starting speech recognition:', error);
                }
            }
        }

        stopListening() {
            if (this.recognition && this.isListening) {
                try {
                    this.recognition.stop();
                } catch (error) {
                    console.error('Error stopping speech recognition:', error);
                }
            }
        }

        toggleListening() {
            if (this.isListening) {
                this.stopListening();
            } else {
                this.startListening();
            }
        }

        setTranscriptUpdateCallback(callback) {
            this.onTranscriptUpdate = callback;
        }

        setListeningStateCallback(callback) {
            this.onListeningStateChange = callback;
        }
    }

    // Initialize voice input
    const voiceInput = new VoiceInput();

    // Set up communication with Streamlit
    voiceInput.setTranscriptUpdateCallback((transcript) => {
        window.parent.postMessage({
            type: 'transcript_update',
            transcript: transcript
        }, '*');
    });

    voiceInput.setListeningStateCallback((isListening) => {
        window.parent.postMessage({
            type: 'listening_state_change',
            isListening: isListening
        }, '*');
    });

    // Listen for messages from Streamlit
    window.addEventListener('message', (event) => {
        if (event.data.type === 'toggle_listening') {
            voiceInput.toggleListening();
        }
    });
    </script>
    """

def inject_voice_input_js():
    """Inject JavaScript code for voice input into Streamlit"""
    js_code = get_voice_input_js()
    st.components.v1.html(js_code, height=0)

def create_mic_button():
    """Create a microphone button with animation"""
    st.markdown("""
        <style>
        .mic-button-container {
            display: flex;
            align-items: center;
            gap: 10px;
            margin: 10px 0;
        }
        .mic-button {
            background: none;
            border: none;
            cursor: pointer;
            padding: 12px;
            border-radius: 50%;
            transition: all 0.3s ease;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 1.5rem;
            color: #1f1f1f;
            position: relative;
            z-index: 1;
        }
        .mic-button:hover {
            background-color: rgba(0, 0, 0, 0.1);
        }
        .mic-button:focus {
            outline: 2px solid #007bff;
            outline-offset: 2px;
        }
        .mic-button.listening {
            animation: pulse 1.5s infinite;
            background-color: rgba(255, 0, 0, 0.1);
        }
        @keyframes pulse {
            0% { transform: scale(1); }
            50% { transform: scale(1.1); }
            100% { transform: scale(1); }
        }
        .listening-indicator {
            display: none;
            align-items: center;
            gap: 8px;
            color: #dc3545;
            font-size: 0.9rem;
            margin-top: 5px;
        }
        .listening-indicator.active {
            display: flex;
        }
        .listening-indicator::before {
            content: '';
            width: 8px;
            height: 8px;
            background-color: #dc3545;
            border-radius: 50%;
            animation: blink 1s infinite;
        }
        @keyframes blink {
            0% { opacity: 1; }
            50% { opacity: 0.3; }
            100% { opacity: 1; }
        }
        </style>
    """, unsafe_allow_html=True)

    # Create a container for the microphone button
    mic_container = st.container()
    with mic_container:
        # Add a label for accessibility
        st.markdown('<label for="mic_button" class="sr-only">Voice Input</label>', unsafe_allow_html=True)
        
        # Create the microphone button with proper ARIA attributes
        button_id = "mic_button"
        if st.button("🎤", key=button_id, use_container_width=True):
            st.session_state.is_listening = not st.session_state.is_listening
            st.markdown(f"""
                <script>
                window.parent.postMessage({{
                    type: 'toggle_listening'
                }}, '*');
                </script>
            """, unsafe_allow_html=True)
        
        # Add listening indicator with ARIA attributes
        st.markdown(f"""
            <div class="listening-indicator" id="listening-indicator" role="status" aria-live="polite">
                <span class="sr-only">Voice input is </span>
                <span aria-hidden="true">Listening...</span>
            </div>
            <script>
                window.addEventListener('message', (event) => {{
                    if (event.data.type === 'listening_state_change') {{
                        const indicator = document.getElementById('listening-indicator');
                        if (event.data.isListening) {{
                            indicator.classList.add('active');
                            indicator.setAttribute('aria-label', 'Voice input is active');
                        }} else {{
                            indicator.classList.remove('active');
                            indicator.setAttribute('aria-label', 'Voice input is inactive');
                        }}
                    }}
                }});
            </script>
        """, unsafe_allow_html=True)

def display_transcript():
    """Display the current transcript"""
    if st.session_state.transcript:
        st.markdown(f"""
            <div class="transcript-container" role="status" aria-live="polite">
                <div class="transcript-text">
                    <strong>Transcript:</strong> <span id="transcript-content">{st.session_state.transcript}</span>
                </div>
            </div>
        """, unsafe_allow_html=True)

def handle_voice_input(callback: Callable[[str], None]):
    """Handle voice input and call the callback with transcribed text"""
    initialize_voice_state()
    inject_voice_input_js()
    create_mic_button()
    display_transcript()

    # Listen for messages from JavaScript
    st.markdown("""
        <script>
        window.addEventListener('message', (event) => {
            if (event.data.type === 'transcript_update') {
                const transcriptContent = document.getElementById('transcript-content');
                if (transcriptContent) {
                    transcriptContent.textContent = event.data.transcript;
                }
                window.parent.postMessage({
                    type: 'streamlit:setComponentValue',
                    value: event.data.transcript
                }, '*');
            }
        });
        </script>
    """, unsafe_allow_html=True)

    # Handle transcript updates
    if st.session_state.transcript:
        callback(st.session_state.transcript)
        st.session_state.transcript = "" 