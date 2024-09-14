import os
from flask import Flask, request,render_template, jsonify
from dotenv import load_dotenv
from PIL import Image
import openai

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = './uploads'  # Directory to store uploaded files
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg'}  # Allowed file extensions

# OpenAI API key setup
openai.api_key = os.getenv("OPENAI_API_KEY")

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

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

    print(request)
    print(request.files)
    
    # If user does not select a file
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    
    if file and allowed_file(file.filename):
        filename = file.filename
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)

        # Open and process the image file
        image = Image.open(filepath)
        
        # Here you can add code to analyze the image, for example:
        # - Convert it to text (OCR)
        # - Describe it using a vision model (like OpenAI’s DALL·E)
        # For this demo, we'll just send a simple text description
        image_description = "Image uploaded and processed."

        # Now, pass this to GPT-4-turbo (this example assumes you're sending text to GPT-4-turbo)
        response = openai.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are an image description assistant."},
                {"role": "user", "content": f"Describe this image: {image_description}"}
            ]
        )
        print(response)
        return jsonify({'response': response['choices'][0]['message']['content']})
    
    return jsonify({'error': 'File type not allowed'}), 400

if __name__ == '__main__':
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    app.run(debug=True)
