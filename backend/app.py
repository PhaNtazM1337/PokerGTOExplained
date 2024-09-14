import os
from flask import Flask, request,render_template, jsonify
from dotenv import load_dotenv
from PIL import Image
import openai
import base64
import requests

app = Flask(__name__) #1
app.config['UPLOAD_FOLDER'] = './uploads'  # Directory to store uploaded files
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg'}  # Allowed file extensions

# OpenAI API key setup
openai.api_key = os.getenv("OPENAI_API_KEY")
print(openai.api_key)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

def encode_image(image_path):
    """Encodes image to base64 for inclusion in JSON payload."""
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

@app.route('/')
def index():
    return render_template('index.html')

# Route to upload an image
@app.route('/upload', methods=['POST'])
def upload_file():
    # Check if the request contains a file
    if 'image' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    
    file = request.files['image']

    # print(request)
    # print(request.files)
    
    # If user does not select a file
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    
    if file and allowed_file(file.filename):
        filename = file.filename
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)

        # print(filepath)
        # mime_type = file.mimetype
        # print(mime_type)
        base64_image = encode_image(filepath)
        # print(base64_image)
        
        # Here you can add code to analyze the image, for example:
        # - Convert it to text (OCR)
        # - Describe it using a vision model (like OpenAI’s DALL·E)
        # For this demo, we'll just send a simple text description
        # image_description = "Image uploaded and processed."

        # Now, pass this to GPT-4-turbo (this example assumes you're sending text to GPT-4-turbo)
        # response = openai.chat.completions.create(
        #     model="gpt-4o",
        #     messages=[
        #         {"role": "system", "content": "You are an image description assistant."},
        #         {"role": "user", "content": f"Describe this image: {image_description}"}
        #     ]
        # )
        # response = openai.chat.completions.create(
        #     model="gpt-4o",
        #     messages=[
        #         {"role": "system", "content": "You are a helpful assistant who can see and analyze images."},
        #         {"role": "user", "content": "Please analyze this image and describe what you see."}
        #     ],
        #     files=[{"file": image_data, "type": mime_type}]
        # )
        payload = {
            "model": "gpt-4o-mini", 
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": "What's in this image?"
                        },
                        {
                            "type": "image_url",
                            "image_url": f"data:image/png;base64,{base64_image}"  # Using the base64-encoded image
                        }
                    ]
                }
            ],
            "max_tokens": 300
        }
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {openai.api_key}"
        }
        response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload)
        print(response.json())
        return jsonify({'response': response['choices'][0]['message']['content']})
    
    return jsonify({'error': 'File type not allowed'}), 400

if __name__ == '__main__':
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    app.run(debug=True)
