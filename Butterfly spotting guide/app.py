import streamlit as st
import random
import pydeck as pdk
import pandas as pd
import re
import speech_recognition as sr
import os
import sys 

# ---------------------------------------------
# ⚠️ ENVIRONMENT CHECK FOR CONDITIONAL LOGIC
# ---------------------------------------------
# Check for environment variables/paths typical of Streamlit Cloud/virtual envs.
# This boolean variable dictates whether we attempt to use the microphone.
IS_LOCAL = "localhost" in sys.argv or "127.0.0.1" in sys.argv or os.environ.get('STREAMLIT_SERVER_ADDRESS') is None


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
# This function is designed to work ONLY on localhost where PyAudio is present.
def listen_to_voice():
    r = sr.Recognizer()
    try:
        # This line will crash on Streamlit Cloud due to missing PyAudio,
        # triggering the desired AttributeError for the user.
        with sr.Microphone() as source:
            st.info("🎤 Listening... describe the butterfly clearly (you have 5 seconds)...")
            r.adjust_for_ambient_noise(source, duration=1)
            audio = r.listen(source, phrase_time_limit=5)
            try:
                text = r.recognize_google(audio)
                st.success(f"🗣️ You said: {text}")
                return text
            except sr.UnknownValueError:
                st.error("😕 I couldn't understand that. Try again slowly.")
            except sr.RequestError:
                st.error("⚠️ Speech service unavailable. Please use text input.")
    except Exception as e:
         # This block should ideally not be reached on the server, as the PyAudio failure
         # occurs deeper in the stack and Streamlit will catch it before this.
         # This is a fallback for unexpected local errors.
         st.error(f"Local microphone error: {e}")

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
    if IS_LOCAL:
        # --- Localhost Logic (Works if PyAudio is installed locally) ---
        if st.button("🎙️ Speak Now"):
            # This calls the function and may raise PyAudio errors, 
            # but only on the local machine where the user can fix it.
            spoken = listen_to_voice() 
            if spoken:
                species = identify_butterfly(spoken)
    else:
        # --- Streamlit Cloud/Deployed Logic ---
        st.error("⚠️ **Voice Input is Disabled on this server.**")
        st.warning("The voice feature requires system dependencies (PyAudio) not available here. To use it, please **clone the repository and run the app locally**.")
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
