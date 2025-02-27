import cv2
import face_recognition

def recognize_user():
    """Recognize the user using webcam"""
    print("Face recognition script is running...")
    cap = cv2.VideoCapture(0)

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        face_locations = face_recognition.face_locations(rgb_frame)

        if face_locations:
            cap.release()
            cv2.destroyAllWindows()
            return "User Recognized"  # Replace with actual user identification logic

    cap.release()
    cv2.destroyAllWindows()
    return None
