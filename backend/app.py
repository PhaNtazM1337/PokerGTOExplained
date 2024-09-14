import os
from flask import Flask, request,render_template, jsonify
from dotenv import load_dotenv
from PIL import Image
import openai
import base64
import requests
import json
import re

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = './uploads'  # Directory to store uploaded files
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg'}  # Allowed file extensions

# OpenAI API key setup
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

client = openai.OpenAI()

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

def encode_image(image_path):
    """Encodes image to base64 for inclusion in JSON payload."""
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/fill', methods = ['POST'])
def upload_autofill():
    # Check if the request contains a file
    if 'image' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    
    file = request.files['image']
    if file.filename == '':
            return jsonify({'error': 'No selected file'}), 400
        
    if file and allowed_file(file.filename):
        filename = file.filename
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        image_type = filepath.split('.')[-1]
        
        if image_type not in {'png', 'jpg', 'jpeg'}:
            return jsonify({'error': 'File type not allowed'}), 400
        base64_image = encode_image(filepath)
        
        headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {openai.api_key}"
        }
        
        with open("../prompts/Autofill.txt", "r") as f:
            Autofill = f.read()
        f.close()

        payload = {
        "model": "gpt-4o",
        "messages": [
            {
            "role": "user",
            "content": [
                {
                "type": "text",
                "text": Autofill
                },
                {
                "type": "image_url",
                "image_url": {
                    "url": f"data:image/{image_type};base64,{base64_image}"
                }
                }
            ]
            }
        ],
        "max_tokens": 300
        }

        response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload)
        output = response.json()['choices'][0]['message']['content']
        json_string = re.search(r'```json(.*?)```', output, re.DOTALL)
        if json_string:
            json_content = json_string.group(1).strip()  # Extract the JSON part
            print(json_content)
            return json_content, 200
        else:
            return jsonify({'error': 'Error: Invalid JSON format.'}), 400

    else:
        return jsonify({'error': 'File type not allowed'}), 400

# Route to upload an image
@app.route('/upload', methods=['POST'])
def upload_file():
    # Check if the request contains a file
    if 'image' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    
    file = request.files['image']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    
    if file and allowed_file(file.filename):
        filename = file.filename
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        image_type = filepath.split('.')[-1]
        
        if image_type not in {'png', 'jpg', 'jpeg'}:
            return jsonify({'error': 'File type not allowed'}), 400
        base64_image = encode_image(filepath)
        
        headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {openai.api_key}"
        }
        
        with open("../prompts/GTOextract.txt", "r") as f:
            GTOextract_prompt = f.read()
        f.close()

        payload = {
        "model": "gpt-4o-mini",
        "messages": [
            {
            "role": "user",
            "content": [
                {
                "type": "text",
                "text": GTOextract_prompt
                },
                {
                "type": "image_url",
                "image_url": {
                    "url": f"data:image/{image_type};base64,{base64_image}"
                }
                }
            ]
            }
        ],
        "max_tokens": 300
        }

        response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload)
        GTO_data = response.json()['choices'][0]['message']['content']

        # gpt4o (o1) for response
        with open("../prompts/GTOo1.txt", "r") as f:
            GTOo1_prompt = f.read()
        f.close()
        GTOo1_prompt = GTOo1_prompt.format(GTO_data = GTO_data)
        response = client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "user", "content": GTOo1_prompt}
                ]
            )
        content = response.choices[0].message.content
        # print(content)
        content = content.split("```")[1]
        content = content[content.find("{"):]
        # ans = json.loads(content)
        # print(ans)
        return content, 200
    else:
        return jsonify({'error': 'File type not allowed'}), 400

if __name__ == '__main__':
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    app.run(debug=True)
