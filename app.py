from flask import Flask, render_template, request
from openai import OpenAI
import os
from PIL import Image
import easyocr
import re
import unicodedata
from dotenv import load_dotenv
from deep_translator import GoogleTranslator

load_dotenv()

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.getenv("OPENROUTER_API_KEY")
)

app = Flask(__name__)
UPLOAD_FOLDER = os.path.join(os.getcwd(), 'uploads')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Initialize EasyOCR once (reuse for better performance)
reader = easyocr.Reader(['en', 'hi', 'mr'])
korean_reader = easyocr.Reader(['en', 'ko'])  # causes shape mismatch sometimes
telgu_reader = easyocr.Reader(['en', 'te'])  
east_asian_reader = easyocr.Reader([ 'ja'])     # Japanese only with English

bengali_reader = easyocr.Reader(['en', 'bn'])

def fix_common_ocr_errors(text):
    corrections = {
        '0': 'O',
        '1': 'I',
        '|': 'I',
        '5': 'S',
        '8': 'B',
        '“': '"', '”': '"',
        '‘': "'", '’': "'",
    }
    for wrong, right in corrections.items():
        text = text.replace(wrong, right)
    return text


# Text Cleaning Function
def clean_ocr_text(text):
    # Normalize unicode characters
    text = unicodedata.normalize("NFKD", text)

    # Remove non-ASCII characters
    text = text.encode("ascii", "ignore").decode()

    # Remove URLs
    text = re.sub(r"http\S+|www\S+|https\S+", "", text)

    # Remove extra whitespace and line breaks
    text = re.sub(r"\s+", " ", text)

    # Remove unwanted special characters but keep common punctuation
    text = re.sub(r"[^\w\s.,!?\"'’]", "", text)

    # Strip leading and trailing spaces
    return text.strip()

#translation
def translate_to_english(text):
    try:
        return GoogleTranslator(source='auto', target='en').translate(text)
    except Exception as e:
        print("Translation failed:", e)
        return text  # Fallback to original text if error occurs


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
    news_text = request.form.get('news', '')
    image = request.files.get('image')

     # If image uploaded
    if image and image.filename != '':
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], image.filename)
        image.save(filepath)

        ocr_result = reader.readtext(filepath, detail=0, paragraph=True)
        extracted_text = ' '.join(ocr_result)
        cleaned_text = clean_ocr_text(extracted_text)
        english_text = translate_to_english(cleaned_text)
        news_text = english_text

    # If typed input
    else:
        cleaned_text = clean_ocr_text(news_text)
        english_text = translate_to_english(cleaned_text)
        news_text = english_text


    if not news_text:
        return render_template("result.html", prediction="Error: No input provided", news="")

    prediction = ask_gpt(news_text)
    return render_template("result.html", prediction=prediction, news=news_text)

if __name__ == '__main__':
    app.run(debug=True)
