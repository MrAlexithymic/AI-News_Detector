from flask import Flask, render_template, request
from openai import OpenAI
import os
import re
import unicodedata
from PIL import Image
import easyocr
from dotenv import load_dotenv
from deep_translator import GoogleTranslator

# Load environment variables
load_dotenv()

# Initialize OpenAI client
client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.getenv("OPENROUTER_API_KEY")
)

# Initialize Flask app
app = Flask(__name__)
UPLOAD_FOLDER = os.path.join(os.getcwd(), 'uploads')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Initialize a single EasyOCR reader
reader = easyocr.Reader(['en', 'hi', 'mr'])

# More efficient OCR error fix
def fix_common_ocr_errors(text):
    corrections = {
        '0': 'O', '1': 'I', '|': 'I', '5': 'S', '8': 'B',
        '“': '"', '”': '"', '‘': "'", '’': "'"
    }
    return ''.join(corrections.get(char, char) for char in text)

# Clean OCR text
def clean_ocr_text(text):
    text = unicodedata.normalize("NFKD", text)
    text = text.encode("ascii", "ignore").decode()
    text = re.sub(r"http\S+|www\S+|https\S+", "", text)
    text = re.sub(r"\s+", " ", text)
    text = re.sub(r"[^\w\s.,!?\"'’]", "", text)
    return text.strip()

# Translate to English
def translate_to_english(text):
    try:
        return GoogleTranslator(source='auto', target='en').translate(text)
    except Exception as e:
        print("Translation failed:", e)
        return text

# GPT Prompt
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
"""
    response = client.chat.completions.create(
        model="google/gemma-3n-e2b-it:free",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.2
    )
    return response.choices[0].message.content.strip().upper()

# Routes
@app.route('/')
def index():
    return render_template("index.html")

@app.route('/predict', methods=['POST'])
def predict():
    news_text = request.form.get('news', '').strip()
    image = request.files.get('image')

    # Handle image input
    if image and image.filename.strip():
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], image.filename)
        image.save(filepath)
        ocr_result = reader.readtext(filepath, detail=0, paragraph=True)
        news_text = ' '.join(ocr_result)

    # If no input provided
    if not news_text:
        return render_template("result.html", prediction="Error: No input provided", news="")

    # Clean and translate
    cleaned_text = clean_ocr_text(news_text)
    translated_text = translate_to_english(cleaned_text)
    final_text = fix_common_ocr_errors(translated_text)

    prediction = ask_gpt(final_text)
    return render_template("result.html", prediction=prediction, news=final_text)

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(debug=True, host='0.0.0.0', port=port)
