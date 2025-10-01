from flask import Blueprint, render_template, Response, jsonify
import cv2
import mediapipe as mp
import numpy as np  # <-- ADDED THIS LINE
import time         # <-- ADDED THIS LINE

anonymizer_bp = Blueprint('anonymizer', __name__, template_folder='../templates')

# --- Module-level variables for state management ---
cap = None
camera_active = False

# --- Initialize MediaPipe Face Detection ---
mp_face_detection = mp.solutions.face_detection
face_detection = mp_face_detection.FaceDetection(model_selection=0, min_detection_confidence=0.5)

def process_img(img, face_detection_model):
    """
    This is your core logic for detecting and blurring faces.
    """
    H, W, _ = img.shape
    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    out = face_detection_model.process(img_rgb)

    if out.detections is not None:
        for detection in out.detections:
            location_data = detection.location_data
            bbox = location_data.relative_bounding_box

            x1, y1, w, h = bbox.xmin, bbox.ymin, bbox.width, bbox.height

            # Convert relative coordinates to absolute pixel values
            x1 = int(x1 * W)
            y1 = int(y1 * H)
            w = int(w * W)
            h = int(h * H)

            # Ensure coordinates are within image boundaries
            if x1 < 0: x1 = 0
            if y1 < 0: y1 = 0
            
            # Apply a heavy blur to the face region
            img[y1:y1 + h, x1:x1 + w, :] = cv2.blur(img[y1:y1 + h, x1:x1 + w, :], (40, 40))

    return img

def create_placeholder_image(text):
    """Creates a black image with centered white text."""
    placeholder = np.zeros((720, 1280, 3), dtype=np.uint8)
    font = cv2.FONT_HERSHEY_SIMPLEX
    (text_width, text_height), _ = cv2.getTextSize(text, font, 2, 3)
    x = (1280 - text_width) // 2
    y = (720 + text_height) // 2
    cv2.putText(placeholder, text, (x, y), font, 2, (255, 255, 255), 3, cv2.LINE_AA)
    return placeholder

def generate_frames():
    """Generates frames for the live video stream."""
    global cap
    while True:
        if not camera_active or cap is None or not cap.isOpened():
            frame_bytes = cv2.imencode('.jpg', create_placeholder_image("Camera is Off"))[1].tobytes()
            yield (b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
            time.sleep(0.1)
            continue

        success, frame = cap.read()
        if not success:
            break
        
        # Process the frame to find and blur faces
        frame = process_img(frame, face_detection)

        # Encode the frame in JPEG format
        ret, buffer = cv2.imencode('.jpg', frame)
        frame_bytes = buffer.tobytes()

        # Yield the frame in the multipart format
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')

# --- Flask Routes ---

@anonymizer_bp.route('/')
def index():
    """Renders the main page for the face anonymizer."""
    return render_template('anonymizer.html')

@anonymizer_bp.route('/video_feed')
def video_feed():
    """Video streaming route."""
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

@anonymizer_bp.route('/start_camera')
def start_camera():
    """Starts the camera feed."""
    global cap, camera_active
    if not camera_active:
        cap = cv2.VideoCapture(0) # Use camera index 0
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
        camera_active = True
        print("Anonymizer camera started.")
    return jsonify(success=True)

@anonymizer_bp.route('/stop_camera')
def stop_camera():
    """Stops the camera feed."""
    global cap, camera_active
    if cap is not None:
        cap.release()
    camera_active = False
    print("Anonymizer camera stopped.")
    return jsonify(success=True)