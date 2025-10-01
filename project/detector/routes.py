from flask import Blueprint, render_template, request, flash
import os
from PIL import Image, ImageOps
import numpy as np
from tensorflow.keras.models import load_model
import base64
import io

detector_bp = Blueprint('detector', __name__, template_folder='../templates')

# --- Load Model and Class Names ONCE on startup ---
MODEL_PATH = os.path.join('project', 'ml_models', 'detector', 'pneumonia_classifier.h5')
LABELS_PATH = os.path.join('project', 'ml_models', 'detector', 'labels.txt')

# Load the trained model
try:
    model = load_model(MODEL_PATH)
except Exception as e:
    model = None
    print(f"Error loading model: {e}")

# Load class names
try:
    with open(LABELS_PATH, 'r') as f:
        class_names = [a.strip().split(' ')[1] for a in f.readlines()]
except Exception as e:
    class_names = ['PNEUMONIA', 'NORMAL'] # Fallback
    print(f"Error loading labels: {e}")


def classify(image, model, class_names_list):
    """
    This is your original classification function, slightly adapted.
    """
    if model is None:
        return "Model not loaded", 0.0

    # CORRECTED: Resize image to (256, 256) to match the model's expected input
    image = ImageOps.fit(image, (256, 256), Image.Resampling.LANCZOS)

    # Convert image to numpy array and normalize
    image_array = np.asarray(image)
    normalized_image_array = (image_array.astype(np.float32) / 127.5) - 1

    # CORRECTED: Prepare data with the shape (1, 256, 256, 3)
    data = np.ndarray(shape=(1, 256, 256, 3), dtype=np.float32)
    data[0] = normalized_image_array

    # Make prediction
    prediction = model.predict(data)
    
    # Use your custom threshold logic
    index = 0 if prediction[0][0] > 0.95 else 1
    class_name = class_names_list[index]
    confidence_score = prediction[0][index]

    return class_name, confidence_score

@detector_bp.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('No file part')
            return render_template('detector.html')
        
        file = request.files['file']
        
        if file.filename == '':
            flash('No selected file')
            return render_template('detector.html')
            
        if file:
            try:
                image = Image.open(file.stream).convert('RGB')
                class_name, conf_score = classify(image, model, class_names)
                
                buffered = io.BytesIO()
                image.save(buffered, format="JPEG")
                img_str = base64.b64encode(buffered.getvalue()).decode("utf-8")
                
                return render_template(
                    'detector.html', 
                    prediction=class_name,
                    confidence=int(conf_score * 100),
                    image_data=img_str
                )
            except Exception as e:
                flash(f'An error occurred: {e}')
                return render_template('detector.html')

    return render_template('detector.html')