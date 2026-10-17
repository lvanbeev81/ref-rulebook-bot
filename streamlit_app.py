import os
import time
import streamlit as st
from dotenv import load_dotenv
from google import genai

load_dotenv()

# Page configuration for a clean mobile look
st.set_page_config(
    page_title="High School Ref Assistant",
    page_icon="🏀",
    layout="centered"
)

st.title("🏀 High School Ref Assistant")
st.caption("NFHS Basketball Rulebook & Case Adjudication Engine")

@st.cache_resource(show_spinner=False)
def get_gemini_client():
    return genai.Client()

@st.cache_resource(show_spinner=False)
def load_and_upload_rulebook(file_path="rulebook.pdf"):
    """Uploads and indexes the rulebook once, caching it across runs."""
    client = get_gemini_client()
    if not os.path.exists(file_path):
        return None

    uploaded_file = client.files.upload(file=file_path)
    while uploaded_file.state.name == "PROCESSING":
        time.sleep(2)
        uploaded_file = client.files.get(name=uploaded_file.name)
        
    if uploaded_file.state.name == "FAILED":
        return None
    return uploaded_file

client = get_gemini_client()

# Check and index the PDF
with st.spinner("Checking and indexing rulebook..."):
    pdf_doc = load_and_upload_rulebook("rulebook.pdf")

if not pdf_doc:
    st.error("⚠️ `rulebook.pdf` not found! Please ensure your rulebook is in the project folder.")
    st.stop()

st.success("Rulebook loaded & ready!", icon="✅")

# Quick pre-set scenario buttons for fast testing
st.markdown("##### Quick Test Scenarios")
col1, col2 = st.columns(2)

example_scenario = ""
with col1:
    if st.button("🏀 Backcourt Throw-in"):
        example_scenario = "Team A is executing a throw-in from the frontcourt sideline. Player A1 passes toward the backcourt, and A2 catches it while standing in the backcourt. Is this a violation?"
with col2:
    if st.button("⏱️ Bonus Free Throws"):
        example_scenario = "Team A commits its 5th foul of the 2nd quarter on the floor during non-shooting action. What is the free-throw penalty under current NFHS rules?"

# Input text area
scenario = st.text_area(
    "Describe the on-court scenario:",
    value=example_scenario,
    placeholder="E.g., Player A1 drives, crashes into defender B1 who established legal guarding position with both feet on the court...",
    height=120
)

if st.button("Adjudicate Play", type="primary", use_container_width=True):
    if not scenario.strip():
        st.warning("Please enter a game scenario to evaluate.")
    else:
        with st.spinner("Consulting NFHS Rulebook & analyzing mechanics..."):
            prompt = f"""
You are an expert high school sports official and rules interpreter.
Adjudicate the following game scenario strictly based on the attached NFHS Basketball Rules Book PDF.

--- GAME SCENARIO ---
{scenario}

Provide a structured official ruling using clean Markdown formatting:
### 1. Ruling
State the call clearly (Personal Foul, Player-Control Foul, Violation, Legal Play, etc.).

### 2. Applicable Rule & Citation
Cite the exact Rule, Section, and Article numbers, with specific rule text.

### 3. Official Mechanic & Next Step
Describe the exact whistle, arm signal, reporting procedure to the table, and ball/free-throw administration.
"""
            try:
                response = client.models.generate_content(
                    model="gemini-3.8-flash",
                    contents=[pdf_doc, prompt],
                )
                st.markdown("---")
                st.markdown(response.text)
            except Exception as e:
                st.error(f"Error evaluating scenario: {e}")