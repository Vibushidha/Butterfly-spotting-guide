import streamlit as st
import random
import pydeck as pdk
import pandas as pd
import re
import speech_recognition as sr
import os
from streamlit_webrtc import webrtc_streamer, WebRtcMode, AudioProcessorBase
import av
import numpy as np
import io
# -----------------------------
# 🎙️ Real-Time Voice Processor
# -----------------------------
# This class runs on the server to collect audio chunks from the browser.

class SpeechToTextProcessor(AudioProcessorBase):
    def __init__(self):
        # Using a list to hold raw audio frames
        self.audio_container = []
        self.is_recording = False
        self.recognizer = sr.Recognizer() # Initialize the recognizer once

    # The method called repeatedly with audio frames from the browser
    def recv(self, frame: av.AudioFrame) -> av.AudioFrame:
        if self.is_recording:
            # Append the raw data from the audio frame
            self.audio_container.append(frame.to_ndarray().tobytes())
        return frame # Return the frame to avoid dropping it (WebRTC requirement)

# Global variable to store transcribed text
if 'transcribed_text' not in st.session_state:
    st.session_state.transcribed_text = None

def process_audio_chunks(audio_bytes_list, recognizer):
    """Combines and processes audio chunks using the speech_recognition library."""
    
    if not audio_bytes_list:
        return None
        
    # Concatenate all byte strings into a single byte string
    combined_bytes = b''.join(audio_bytes_list)
    
    # 1. Create AudioData object
    # Assuming 16000 sample rate and 2 bytes (16-bit) sample width, mono channel.
    # WebRTC typically uses these settings.
    try:
        audio_data = recognizer.AudioData(combined_bytes, 16000, 2)
    except Exception as e:
        st.error(f"Error creating audio data: {e}")
        return None
        
    # 2. Transcribe
    try:
        text = recognizer.recognize_google(audio_data)
        return text
    except sr.UnknownValueError:
        return "UnknownValueError"
    except sr.RequestError:
        return "RequestError"
# -----------------------------
# 🌿 App Config
# -----------------------------
st.set_page_config(page_title="Butterfly Spotting Guide 🦋", page_icon="🦋", layout="centered")

st.markdown(
    "<h1 style='text-align:center; color:#2E8B57;'>🦋 Butterfly Spotting Guide 🌿</h1>",
    unsafe_allow_html=True
)
st.write("Describe a butterfly, upload an image, or use your voice to identify it!")

# -----------------------------
# 🦋 Butterfly Data
# -----------------------------
# Use os.path.join to ensure the path is correctly constructed relative to the app.py file
# os.path.dirname(__file__) gets the directory where app.py is located.
IMAGE_DIR = os.path.join(os.path.dirname(__file__), "data", "sample_images")

butterflies = {
    "Monarch": os.path.join(IMAGE_DIR, "monarch.jpg"),
    "Swallowtail": os.path.join(IMAGE_DIR, "swallowtail.jpg"),
    "Blue Morpho": os.path.join(IMAGE_DIR, "blue_morpho.jpg"),
    "Painted Lady": os.path.join(IMAGE_DIR, "painted_lady.jpg"),
    "Common Jezebel": os.path.join(IMAGE_DIR, "common_jezebel.jpg"),
    "Peacock": os.path.join(IMAGE_DIR, "peacock.jpg"),
    "Red Admiral": os.path.join(IMAGE_DIR, "red_admiral.jpg"),
}
facts = {
    "Monarch": "🧭 Monarchs migrate over 3,000 miles from North America to Mexico!",
    "Swallowtail": "🌼 Swallowtails have tails that resemble a bird’s feathers!",
    "Blue Morpho": "✨ Their bright blue shimmer comes from reflected light!",
    "Painted Lady": "🌍 Found on every continent except Antarctica!",
    "Common Jezebel": "🎨 Famous for their red, yellow, and white wing patterns.",
    "Peacock": "👁️ Their wings have big eye-like spots to scare predators!",
    "Red Admiral": "🦋 Bold and territorial — they love basking in the sun!",
}

# -----------------------------
# 🌍 Migration Data
# -----------------------------
migration_data = {
    "Monarch": [
        {"month": "Jan", "lat": 19.4, "lon": -99.1, "place": "Mexico", "reason": "Overwintering in warm forests", "fact": "They love the sunshine here ☀️"},
        {"month": "Mar", "lat": 30.0, "lon": -90.0, "place": "Southern US", "reason": "Starting their northward journey", "fact": "They travel up to 100 miles a day! 💪"},
        {"month": "Jun", "lat": 44.9, "lon": -93.0, "place": "Midwest USA", "reason": "Breeding season", "fact": "They rest on milkweed fields 🌿"},
        {"month": "Sep", "lat": 35.7, "lon": -78.6, "place": "Southeast USA", "reason": "Heading south again", "fact": "Time to migrate home! 🧭"},
    ],
    "Swallowtail": [
        {"month": "Jan", "lat": 20.0, "lon": 78.0, "place": "India", "reason": "Staying warm", "fact": "They love tropical nectar! 🌺"},
        {"month": "Apr", "lat": 30.0, "lon": 100.0, "place": "China", "reason": "Breeding time", "fact": "They dance in spring breezes 💃"},
        {"month": "Jul", "lat": 45.0, "lon": 10.0, "place": "Europe", "reason": "Exploring meadows", "fact": "They flutter gracefully in fields 🌾"},
        {"month": "Oct", "lat": 25.0, "lon": 77.0, "place": "Back to India", "reason": "Return migration", "fact": "Home sweet home 🏡"},
    ],
    "Blue Morpho": [
        {"month": "Jan", "lat": -3.0, "lon": -60.0, "place": "Amazon", "reason": "Lives in rainforests", "fact": "Their wings shine like gems 💎"},
        {"month": "Jun", "lat": -5.0, "lon": -75.0, "place": "Peru", "reason": "Following humidity patterns", "fact": "They love misty mornings 🌫️"},
    ],
    "Painted Lady": [
        {"month": "Feb", "lat": 0.0, "lon": 35.0, "place": "Kenya", "reason": "Winter rest", "fact": "They chill where flowers bloom 🌸"},
        {"month": "May", "lat": 45.0, "lon": 2.0, "place": "France", "reason": "Migrating north", "fact": "They fly thousands of miles 🚀"},
        {"month": "Sep", "lat": 30.0, "lon": 31.0, "place": "Egypt", "reason": "Heading back south", "fact": "They love warm deserts ☀️"},
    ],
    "Common Jezebel": [
        {"month": "Mar", "lat": 13.0, "lon": 80.0, "place": "South India", "reason": "Breeding season", "fact": "They love blooming trees 🌳"},
        {"month": "Jun", "lat": 28.0, "lon": 77.0, "place": "North India", "reason": "Monsoon migration", "fact": "They follow the rains ☔"},
        {"month": "Oct", "lat": 19.0, "lon": 72.0, "place": "West India", "reason": "Settling before winter", "fact": "They enjoy coastal breezes 🌊"},
    ],
    "Peacock": [
        {"month": "Apr", "lat": 51.5, "lon": -0.1, "place": "UK", "reason": "Emerging from hibernation", "fact": "They love sunny walls ☀️"},
        {"month": "Jul", "lat": 48.8, "lon": 2.3, "place": "France", "reason": "Feeding on flowers", "fact": "They adore lavender fields 💜"},
        {"month": "Sep", "lat": 52.5, "lon": 13.4, "place": "Germany", "reason": "Preparing for winter", "fact": "They start hibernating soon ❄️"},
    ],
    "Red Admiral": [
        {"month": "Jan", "lat": 20.0, "lon": -15.0, "place": "West Africa", "reason": "Winter rest", "fact": "They soak in the warmth 🌞"},
        {"month": "May", "lat": 48.0, "lon": 11.0, "place": "Germany", "reason": "Breeding season", "fact": "They love stinging nettles 🌿"},
        {"month": "Oct", "lat": 41.9, "lon": 12.5, "place": "Italy", "reason": "Heading south again", "fact": "Ciao bella! 🇮🇹"},
    ],
}


# -----------------------------
# 🎙️ Voice Recognition
# -----------------------------

# Initialize the flag BEFORE the try block to avoid NameError
VOICE_AVAILABLE = False 

try:
    import speech_recognition as sr
    VOICE_AVAILABLE = True # Set to True only if the import is successful
    
    # Define the function only if the import succeeds
    def listen_to_voice():
        r = sr.Recognizer()
        try:
            with sr.Microphone() as source:
                st.info("🎤 Listening... describe the butterfly clearly (you have 5 seconds)...")
                r.adjust_for_ambient_noise(source, duration=1)
                # The problematic line that raises PyAudio errors during runtime:
                audio = r.listen(source, phrase_time_limit=5) 
                try:
                    text = r.recognize_google(audio)
                    st.success(f"🗣️ You said: {text}")
                    return text
                except sr.UnknownValueError:
                    st.error("😕 I couldn't understand that. Try again slowly.")
                except sr.RequestError:
                    st.error("⚠️ Speech service unavailable. Please use text input.")
            return None
        except Exception as e:
            # Catch PyAudio/PortAudio related errors that happen when sr.Microphone() is called
            st.error(f"⚠️ Voice input is not supported in this deployment environment. Please use Text or Image input.")
            # st.code(f"Error: {e}", language="text") # Optional: show the error for debugging
            return None
            
except Exception:
    # If the system dependency (PyAudio) is missing during import, this block executes.
    # VOICE_AVAILABLE remains False.
    
    # Define a placeholder function for the UI to call without crashing
    def listen_to_voice():
        st.error("⚠️ Voice input requires system libraries (PyAudio) that are not installed on this server. Please use Text or Image input.")
        return None

# -----------------------------
# 🔍 Smarter Identification
# -----------------------------
def identify_butterfly(description):
    if not description:
        return None

    desc = description.lower().strip()
    desc = re.sub(r"[^\w\s]", " ", desc)

    keywords = {
        "Monarch": ["orange", "black", "veins", "striped", "north america"],
        "Swallowtail": ["yellow", "black", "tail", "swallow", "wingtip"],
        "Blue Morpho": ["blue", "shiny", "metallic", "iridescent", "morpho"],
        "Painted Lady": ["painted", "lady", "brown", "orange", "spotted"],
        "Common Jezebel": ["white", "red", "yellow", "jezebel", "tree top"],
        "Peacock": ["brown", "eye", "eyespot", "peacock", "circle"],
        "Red Admiral": ["red", "admiral", "black", "white band", "bold"],
    }

    scores = {}
    for species, words in keywords.items():
        scores[species] = sum(word in desc for word in words)

    best_species = max(scores, key=scores.get)
    if scores[best_species] == 0:
        best_species = random.choice(list(keywords.keys()))
    return best_species

# -----------------------------
# 🦋 Interface
# -----------------------------
mode = st.radio("Choose input method:", ["Describe", "Voice", "Upload Image"])

if "history" not in st.session_state:
    st.session_state.history = []
if "identified" not in st.session_state:
    st.session_state.identified = False

species = None

if mode == "Describe":
    text = st.text_input("Describe your butterfly (e.g. 'orange with black veins'):")
    if st.button("Identify"):
        species = identify_butterfly(text)

elif mode == "Voice":
    st.markdown("### 🗣️ Real-Time Voice Input (via Browser Microphone)")
    st.info("Click START, speak your description, then click STOP to process.")
    
    # Initialize the WebRTC stream
    webrtc_ctx = webrtc_streamer(
        key="speech-rec-key",
        mode=WebRtcMode.SENDONLY,
        audio_processor_factory=SpeechToTextProcessor,
        media_stream_constraints={"video": False, "audio": True},
    )

    # Check if the stream is active and the processor is available
    if webrtc_ctx.state.playing and webrtc_ctx.audio_processor:
        processor: SpeechToTextProcessor = webrtc_ctx.audio_processor

        col1, col2 = st.columns(2)
        
        # Start button logic
        with col1:
            if st.button("🔴 START Recording", use_container_width=True):
                processor.audio_container = [] # Clear old data
                processor.is_recording = True
                st.session_state.transcribed_text = None
                st.session_state.voice_status = "Recording..."

        # Stop button logic
        with col2:
            if st.button("⏹️ STOP & Identify", use_container_width=True):
                processor.is_recording = False
                st.session_state.voice_status = "Processing..."
                
                # Immediately process the audio data
                if processor.audio_container:
                    transcribed_text = process_audio_chunks(processor.audio_container, sr)
                    
                    if transcribed_text not in ["UnknownValueError", "RequestError"]:
                        st.session_state.transcribed_text = transcribed_text
                    
                    # Clear the audio container immediately after processing
                    processor.audio_container = []
                
        # Display current status
        st.caption(f"Status: {st.session_state.get('voice_status', 'Ready')}")

        # Final identification based on transcribed text stored in session state
        if st.session_state.transcribed_text:
            st.success(f"🗣️ Transcribed: {st.session_state.transcribed_text}")
            
            # Use the transcribed text to identify the butterfly
            species = identify_butterfly(st.session_state.transcribed_text)
            st.session_state.transcribed_text = None # Clear after use

elif mode == "Upload Image":
    file = st.file_uploader("Upload image", type=["jpg", "png", "jpeg"])
    if file and st.button("Identify Uploaded Image"):
        filename = file.name.lower()
        species = identify_butterfly(filename)

if species:
    st.success(f"Species Identified: **{species}** 🦋")
    st.image(butterflies[species], caption=species, use_container_width=True)
    st.info(facts.get(species, "Lovely butterfly!"))
    st.session_state.history.append(species)
    st.session_state.identified = True

# -----------------------------
# 🌿 Recently Identified Gallery
# -----------------------------
if st.session_state.history:
    st.markdown("### 🕊️ Recently Identified Butterflies")
    cols = st.columns(3)
    recent = st.session_state.history[-6:][::-1]
    for i, past_species in enumerate(recent):
        with cols[i % 3]:
            st.image(butterflies[past_species], caption=past_species, use_container_width=True)

# -----------------------------
# 🌍 Migration Tracker
# -----------------------------
if st.session_state.identified:
    st.markdown("---")
    st.subheader("🧭 Migration Tracker")

    selected_species = st.selectbox("Select Butterfly:", list(migration_data.keys()))
    months = [d["month"] for d in migration_data[selected_species]]
    selected_month = st.select_slider("Select Month", options=months)

    df = pd.DataFrame(migration_data[selected_species])
    current = next(d for d in migration_data[selected_species] if d["month"] == selected_month)

    scatter = pdk.Layer(
        "ScatterplotLayer",
        df,
        get_position=["lon", "lat"],
        get_color=[46, 139, 87, 200],
        get_radius=300000,
        pickable=True,
    )
    path = pdk.Layer(
        "PathLayer",
        data=[{"path": [[r["lon"], r["lat"]] for r in migration_data[selected_species]]}],
        get_path="path",
        get_width=4,
        get_color=[0, 200, 0],
    )
    tooltip = {"text": "{place}\n{reason}\n💡 {fact}"}
    view = pdk.ViewState(latitude=current["lat"], longitude=current["lon"], zoom=3)
    deck = pdk.Deck(layers=[path, scatter], initial_view_state=view, map_style=None, tooltip=tooltip)
    st.pydeck_chart(deck, use_container_width=True)

    st.markdown(
        f"""
        <div style='background-color:#f0fff0;padding:12px;border-radius:10px;border-left:6px solid #2E8B57;margin-top:10px;'>
        <b>📍 Location:</b> {current['place']}<br>
        <b>🗓️ Month:</b> {current['month']}<br>
        <b>💡 Fun Fact:</b> {current['fact']}
        </div>
        """,
        unsafe_allow_html=True
    )

# -----------------------------
# 🎯 Quiz Section
# -----------------------------
st.markdown("---")
st.subheader("🎯 Butterfly Quiz")

if "quiz_species" not in st.session_state:
    st.session_state.quiz_species = random.choice(list(butterflies.keys()))

st.image(butterflies[st.session_state.quiz_species], caption="Guess the species 🦋", use_container_width=True)
guess = st.text_input("Your Guess:")
if st.button("Check Answer"):
    if guess.lower().strip() == st.session_state.quiz_species.lower():
        st.success("🎉 Correct! You know your butterflies!")
        st.balloons()
    else:
        st.error(f"❌ Oops! It was **{st.session_state.quiz_species}**.")
    st.session_state.quiz_species = random.choice(list(butterflies.keys()))

# -----------------------------
# 🌸 Footer
# -----------------------------
st.markdown("<hr>", unsafe_allow_html=True)
st.markdown("<p style='text-align:center; color:#2E8B57;'>Made with ❤️ and curiosity 🦋</p>", unsafe_allow_html=True)
