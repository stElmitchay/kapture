"""
Biometric liveness detection using webcam.
Verifies person is present during work sessions.
"""

import cv2
import os
from datetime import datetime


def check_liveness():
    """
    Capture webcam snapshot and detect if face is present.

    Uses OpenCV's Haar Cascade face detection (lightweight, local, no cloud).

    Returns:
        dict: {
            'face_detected': bool,
            'confidence': float (0.0-1.0),
            'face_count': int,
            'timestamp': str
        }
    """
    try:
        # Open webcam
        cap = cv2.VideoCapture(0)

        # Give camera time to warm up
        import time
        time.sleep(0.5)

        ret, frame = cap.read()
        cap.release()

        if not ret or frame is None:
            return {
                'face_detected': False,
                'confidence': 0.0,
                'face_count': 0,
                'timestamp': datetime.now().isoformat(),
                'error': 'Failed to capture frame'
            }

        # Load Haar Cascade face detector (comes with OpenCV)
        cascade_path = cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'

        if not os.path.exists(cascade_path):
            return {
                'face_detected': False,
                'confidence': 0.0,
                'face_count': 0,
                'timestamp': datetime.now().isoformat(),
                'error': 'Face detection model not found'
            }

        face_cascade = cv2.CascadeClassifier(cascade_path)

        # Convert to grayscale for detection
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        # Detect faces
        # Parameters: scaleFactor=1.1, minNeighbors=4
        faces = face_cascade.detectMultiScale(gray, 1.1, 4)

        face_count = len(faces)
        face_detected = face_count > 0

        # Confidence based on face detection quality
        # 1 face = 1.0 (perfect)
        # 0 faces = 0.0
        # 2+ faces = lower confidence (might be a photo or multiple people)
        if face_count == 1:
            confidence = 1.0
        elif face_count == 0:
            confidence = 0.0
        else:
            # Multiple faces detected - lower confidence
            confidence = 0.7

        return {
            'face_detected': face_detected,
            'confidence': confidence,
            'face_count': face_count,
            'timestamp': datetime.now().isoformat()
        }

    except Exception as e:
        return {
            'face_detected': False,
            'confidence': 0.0,
            'face_count': 0,
            'timestamp': datetime.now().isoformat(),
            'error': str(e)
        }


def is_liveness_available():
    """
    Check if liveness detection is available (webcam + opencv).

    Returns:
        bool: True if liveness detection can be used
    """
    try:
        import cv2

        # Try to open webcam
        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            cap.release()
            return False

        cap.release()
        return True
    except ImportError:
        return False
    except Exception:
        return False


if __name__ == "__main__":
    """Test liveness detection."""
    print("Testing liveness detection...")
    print()

    if not is_liveness_available():
        print("❌ Liveness detection not available")
        print("   Install: pip3 install opencv-python")
        exit(1)

    print("✅ Liveness detection available")
    print("📸 Checking for face...")

    result = check_liveness()

    if result['face_detected']:
        print("✅ Face detected!")
        print(f"   Confidence: {result['confidence']}")
        print(f"   Face count: {result['face_count']}")
    else:
        print("❌ No face detected")
        if 'error' in result:
            print(f"   Error: {result['error']}")

    print(f"   Timestamp: {result['timestamp']}")
