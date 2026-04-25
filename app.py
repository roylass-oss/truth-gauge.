from flask import Flask, request, jsonify
from flask_cors import CORS
import google.generativeai as genai
import os

app = Flask(__name__)
CORS(app)

genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))
model = genai.GenerativeModel('gemini-pro')

@app.route('/analyze', methods=['POST'])
def analyze():
    data = request.json
    text = data.get("text", "")
    prompt = f"Analyze the following text for reliability. Return JSON with: score (0-100), reason (short explanation in Hebrew), color (Red/Yellow/Green). Text: {text}"
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return jsonify({"score": 50, "reason": "שגיאה בניתוח", "color": "Yellow"})

if __name__ == '__main__':
    app.run()
