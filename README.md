# 🕵️ Fake News Detection Web App

A powerful AI-based web app that detects whether a news article (text or image) is **REAL** or **FAKE** using **OCR + LLMs (Gemma via OpenAI-compatible API)**. Users can paste news text or upload a screenshot — the app extracts, cleans, and evaluates the content intelligently.

---

## 🧠 Features

- 🔎 **Fake News Detection using AI** (Google Gemma model via OpenRouter)
- 🖼️ **OCR from image uploads** using EasyOCR
- 🧼 Automatic **cleaning and translation** of OCR text
- 🌐 Supports multiple Indian and global languages in images
- 💬 Paste or type your own news to verify
- 🖥️ Simple and elegant Flask web interface

---

## 🚀 Technologies Used

- **Flask** – Web framework
- **EasyOCR** – Image text extraction (OCR)
- **OpenRouter** – GPT/Gemma LLM API wrapper
- **Gemma-3B** – Fake News classifier model
- **GoogleTranslator (deep_translator)** – Translate OCR text to English
- **HTML/CSS** – Frontend styling

---

## 🧪 Model Details

The app uses `google/gemma-3n-e2b-it:free` from **OpenRouter**, which is an OpenAI-compatible endpoint providing access to lightweight, instruction-tuned LLMs.

> 🔐 You'll need an [OpenRouter](https://openrouter.ai/) API key to run the app.

---

## 🛠️ Installation Guide

### 1. 📦 Clone the Project
```bash
git clone https://github.com/your-username/fake-news-detector.git
cd fake-news-detector

2. 🐍 Create & Activate Virtual Environment
bash

python -m venv myenv
source myenv/bin/activate   # On Windows: myenv\Scripts\activate


3. 📥 Install Dependencies
bash

pip install -r requirements.txt
Or manually install:

bash

pip install flask easyocr openai python-dotenv deep_translator Pillow


4. 🔑 Set Up API Key
Create a .env file in the root directory:

ini

OPENROUTER_API_KEY=your_openrouter_api_key_here
You can get your free API key from https://openrouter.ai/

▶️ Running the App
bash

python app.py
Then open your browser and go to:
http://localhost:5000
🧾 How to Use
📝 Option 1: Type or Paste News
Paste news into the textarea.

Click "Detect".

Get a one-word answer: REAL or FAKE.

🖼️ Option 2: Upload Screenshot
Upload an image of a news article.

The app will extract text via OCR, clean/translate it, and check authenticity.

🌍 Supported OCR Languages
Includes English + Indian and popular global languages:

English (en), Hindi (hi), Marathi (mr)

OCR is optimized using paragraph=True and cleanup via regex + translation.

📦 Deployment Ready
You can deploy this app on:

🔹 Fly.io – Recommended (Docker-based, free tier)

🔹 Railway – Beginner-friendly

🔹 Replit – For demos or testing

I can provide a Dockerfile and fly.toml if needed for deployment. Ask for it!

✅ Advantages
No external dataset or training needed

Model-based detection allows real-time verification

Multi-language OCR for image uploads

Easy-to-use UI for general users, researchers, or journalists

🤝 Credits
OpenRouter
EasyOCR
Deep Translator

📄 License
MIT License – Free to use, modify, and share.

🙋 Need Help?
Feel free to open an issue or ask:

“Help me deploy to Railway”
or
“Fix OCR errors”


