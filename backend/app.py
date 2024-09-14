import os
from flask import Flask, request,render_template, jsonify
from dotenv import load_dotenv
from PIL import Image
import openai
import base64
import requests
import json
import re
import importlib.util
import sys
from pathlib import Path


module_path = Path('postflop-solver/main.py')

# Dynamically load the module
spec = importlib.util.spec_from_file_location("my_module", module_path)
solver = importlib.util.module_from_spec(spec)
sys.modules["my_module"] = solver
spec.loader.exec_module(solver)


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

@app.route('/submit', methods = ['POST'])
def submit():
    def convert_numerical_strings_to_int(d):
        for key, value in d.items():
            if isinstance(value, str) and value.isdigit():  # Check if value is a digit string
                d[key] = int(value)  # Convert to integer
        return d

    d = request.form.to_dict()
    data = convert_numerical_strings_to_int(d)
    del data['hole_cards']
    data['flop_cards'] = data['flop_cards'].replace(",", '')
    # data = {
    #     "effective_stack": 900,
    #     "pot_before_flop": 200,
    #     "preflop_action": "BTN,SB,BB,SB",
    #     "flop_cards": "Td9d6h",
    #     "flop_bet": 120,  # Example value
    #     "turn_card": "Qc",
    #     "turn_bet": 200,  # Example value
    #     "river_card": "7s",
    #     "river_bet": 300,  # Example value
    # }
    res = solver.process(data)
    print(res)
    return jsonify(res), 200

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
        "model": "gpt-4o",
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

        with open("../prompts/sample_response.txt", "r") as f:
            sample_response = f.read()
        f.close()
        GTOo1_prompt = GTOo1_prompt.format(GTO_data = GTO_data, sample_response = sample_response)
        response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "user", "content": GTOo1_prompt}
                ]
            )
        content = response.choices[0].message.content
        # print(content)
        content = content.split("```")[1]
        content = content[content.find("{"):]
        print(content)
        return content, 200
    else:
        return jsonify({'error': 'File type not allowed'}), 400

if __name__ == '__main__':
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    app.run(debug=True)
