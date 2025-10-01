from flask import Blueprint, render_template, Response, jsonify
import cv2
import numpy as np
import time

# Create a Blueprint for the cloak feature
cloak_bp = Blueprint(
    'cloak', 
    __name__,
    template_folder='../templates',
    static_folder='../static'
)

# --- Module-level variables for state management ---
cap = None
background_frame = None
camera_active = False
selected_color = 'blue'

# Color ranges dictionary
color_ranges = {
    'red': ([0, 120, 70], [10, 255, 255], [170, 120, 70], [180, 255, 255]),
    'green': ([35, 100, 100], [85, 255, 255]),
    'blue': ([90, 100, 100], [130, 255, 255]),
    'yellow': ([20, 100, 100], [30, 255, 255]),
    'pink': ([140, 100, 100], [170, 255, 255]),
    'white': ([0, 0, 200], [180, 30, 255])
}

def initialize_camera():
    """Initializes the camera if it's not already."""
    global cap
    if cap is None or not cap.isOpened():
        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            raise IOError("Cannot open webcam.")
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
        print("--- 📷 Camera initialized ---")

def release_camera():
    """Releases the camera and resets state."""
    global cap, camera_active, background_frame
    if cap is not None and cap.isOpened():
        cap.release()
    cap = None
    camera_active = False
    background_frame = None
    print("--- 📸 Camera released ---")

def create_placeholder_image(text):
    """Creates a black image with centered white text."""
    placeholder = np.zeros((720, 1280, 3), dtype=np.uint8)
    font = cv2.FONT_HERSHEY_SIMPLEX
    (text_width, text_height), _ = cv2.getTextSize(text, font, 2, 3)
    x = (1280 - text_width) // 2
    y = (720 + text_height) // 2
    cv2.putText(placeholder, text, (x, y), font, 2, (255, 255, 255), 3, cv2.LINE_AA)
    return placeholder

def capture_background_logic():
    """Captures the background after a delay."""
    global background_frame
    print("--- 📸 Capturing background in 5 seconds... ---")
    time.sleep(5) # Delay for user to clear the scene
    if cap and cap.isOpened():
        ret, frame = cap.read()
        if ret:
            background_frame = cv2.flip(frame, 1)
            print("--- ✅ Background captured successfully! ---")
        else:
            print("--- ❌ Failed to capture background. ---")

def generate_frames():
    """Generates video frames for the live stream."""
    while True:
        if not camera_active or not cap or not cap.isOpened():
            frame_bytes = cv2.imencode('.jpg', create_placeholder_image("Camera is Off"))[1].tobytes()
            yield (b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
            time.sleep(0.1)
            continue

        if background_frame is None:
            frame_bytes = cv2.imencode('.jpg', create_placeholder_image("Capturing Background..."))[1].tobytes()
            yield (b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
            time.sleep(0.1)
            continue

        ret, current_frame = cap.read()
        if not ret:
            break

        frame_flipped = cv2.flip(current_frame, 1)
        hsv = cv2.cvtColor(frame_flipped, cv2.COLOR_BGR2HSV)
        
        range_data = color_ranges.get(selected_color, color_ranges['blue'])
        if selected_color == 'red':
            lower1, upper1, lower2, upper2 = [np.array(x) for x in range_data]
            mask1, mask2 = cv2.inRange(hsv, lower1, upper1), cv2.inRange(hsv, lower2, upper2)
            final_mask = mask1 + mask2
        else:
            lower, upper = [np.array(x) for x in range_data]
            final_mask = cv2.inRange(hsv, lower, upper)
            
        kernel = np.ones((5, 5), np.uint8)
        final_mask = cv2.morphologyEx(final_mask, cv2.MORPH_OPEN, kernel, iterations=2)
        final_mask = cv2.morphologyEx(final_mask, cv2.MORPH_DILATE, kernel, iterations=1)
        
        inverted_mask = cv2.bitwise_not(final_mask)
        foreground = cv2.bitwise_and(frame_flipped, frame_flipped, mask=inverted_mask)
        background_replacement = cv2.bitwise_and(background_frame, background_frame, mask=final_mask)
        result = cv2.add(foreground, background_replacement)
        
        ret, buffer = cv2.imencode('.jpg', result)
        frame_bytes = buffer.tobytes()
        yield (b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')

# --- Routes for the Cloak Blueprint ---

@cloak_bp.route('/')
def index():
    return render_template('cloak.html')

@cloak_bp.route('/start_camera')
def start_camera():
    global camera_active
    if not camera_active:
        initialize_camera()
        camera_active = True
        capture_background_logic()
    return jsonify(success=True)

@cloak_bp.route('/stop_camera')
def stop_camera():
    release_camera()
    return jsonify(success=True)

@cloak_bp.route('/recapture_background')
def recapture_background():
    if camera_active:
        capture_background_logic()
        return jsonify(success=True)
    return jsonify(success=False, message="Camera is not active.")

@cloak_bp.route('/video_feed')
def video_feed():
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

@cloak_bp.route('/set_color/<color_name>')
def set_color(color_name):
    global selected_color
    if color_name in color_ranges:
        selected_color = color_name
        print(f"Color changed to: {color_name}")
        return jsonify(success=True)
    return jsonify(success=False, message="Invalid color.")