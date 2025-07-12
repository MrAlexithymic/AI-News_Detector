import streamlit as st
import os
from PIL import Image
import easyocr
from deep_translator import GoogleTranslator
from openai import OpenAI
from dotenv import load_dotenv
import re
import unicodedata
import numpy as np

# Load environment variables
load_dotenv()

# Initialize OpenAI client
client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.getenv("OPENAI_API_KEY")
)

# Initialize EasyOCR
reader = easyocr.Reader(['en', 'hi', 'mr'])

# Helper Functions
def fix_common_ocr_errors(text):
    corrections = {
        '0': 'O', '1': 'I', '|': 'I', '5': 'S', '8': 'B',
        '“': '"', '”': '"', '‘': "'", '’': "'"
    }
    return ''.join(corrections.get(char, char) for char in text)

def clean_ocr_text(text):
    text = unicodedata.normalize("NFKD", text)
    text = text.encode("ascii", "ignore").decode()
    text = re.sub(r"http\S+|www\S+|https\S+", "", text)
    text = re.sub(r"\s+", " ", text)
    text = re.sub(r"[^\w\s.,!?\"'’]", "", text)
    return text.strip()

def translate_to_english(text):
    try:
        return GoogleTranslator(source='auto', target='en').translate(text)
    except:
        return text

def ask_gpt(news_text):
    prompt = f"""
You are a reliable fake news detection AI.

The following input is a piece of news or social media post extracted using OCR from an image. It may contain typos or broken formatting, but your job is to **ignore those surface errors** and evaluate only the content's factual nature and logical plausibility.

IMPORTANT:
- Internally rephrase the text as needed to understand it.
- Determine whether the news appears realistic, logical, and plausible.
- ONLY answer with one word: REAL or FAKE
- Do NOT explain, justify, or include any other text.
- Focus on **fact-checking**, NOT grammar or formatting.

OCR Extracted Text:
\"\"\"{news_text}\"\"\"

Answer with one word only: REAL or FAKE
"""
    response = client.chat.completions.create(
        model="google/gemma-3n-e2b-it:free",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.2
    )
    return response.choices[0].message.content.strip().upper()

# Streamlit Page Settings and CSS
st.set_page_config(page_title="Fake News Detector", layout="centered")

st.markdown("""
    <style>
    html, body, [class*="css"]  {
        font-family: 'Segoe UI', sans-serif;
        background: linear-gradient(to right, #fdfcfb, #e2d1c3);
    }
    .container {
        background-color: #ffffff;
        top: 50px;
        border-radius: 15px;
        box-shadow: 0 0 25px rgba(0, 0, 0, 0.05);
        border: 2px dotted #b5d4e5;
        width: 100%;
        max-width: 700px;
        margin: auto;
        margin-top: 3rem;
        text-align: center;
        color:black;
        font-size: 2rem;
        font-weight: bold;
        font-family: 'Comic Sans MS', cursive, sans-serif;
    }

    .stTextArea textarea {
        border-radius: 10px;
        border: 1px solid #ccc;
        padding: 1rem;
    }
    .uploaded-label {
        display: block;
        background-color: #e0f7fa;
        padding: 0.8rem;
        text-align: center;
        border-radius: 10px;
        color: #2c3e50;
        border: 2px dashed #aaa;
        font-weight: 600;
        
    }
    .custom-btn button {
        background-color: #b2fefa !important;
        border-radius: 10px;
        padding: 0.6rem 1rem;
        font-weight: bold;
        font-size: 1.1rem;
        width: 100%;
        color: black !important;
    }
    </style>
""", unsafe_allow_html=True)

# --- UI ---
st.markdown('<div class="container">Fake News Detector</div>', unsafe_allow_html=True)
st.markdown("### Paste or Type News Article:")

input_text = st.text_area("Type or paste the news article here...", label_visibility="collapsed")

st.markdown("### <center>OR</center>", unsafe_allow_html=True)
st.markdown("### Upload a Screenshot / Image:")

uploaded_file = st.file_uploader("", type=["jpg", "png", "jpeg"])
if uploaded_file:
    st.markdown('<div class="uploaded-label">Uploaded</div>', unsafe_allow_html=True)

st.markdown('<div class="custom-btn">', unsafe_allow_html=True)
detect = st.button("🔍 Detect")
st.markdown('</div></div>', unsafe_allow_html=True)  # close button div & container

# --- Detection Logic ---
if detect:
    with st.spinner("Analyzing..."):
        if uploaded_file:
            img = Image.open(uploaded_file)
            img_array = np.array(img)
            ocr_text = ' '.join(reader.readtext(img_array, detail=0, paragraph=True))
            news_input = ocr_text
        elif input_text.strip():
            news_input = input_text
        else:
            st.error("❌ Please upload an image or paste some news text.")
            st.stop()

        cleaned = clean_ocr_text(news_input)
        translated = translate_to_english(cleaned)
        fixed = fix_common_ocr_errors(translated)
        prediction = ask_gpt(fixed)

    st.success(f" Prediction: **{prediction}**")
    st.markdown("### 📝 Processed Text")
    st.info(fixed)
