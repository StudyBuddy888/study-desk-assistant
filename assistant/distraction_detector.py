import cv2
import face_recognition
import time

def detect_distraction():
    """Detect if the user is distracted (looking away, closing eyes)"""
    print("Distraction detection is running...")
    cap = cv2.VideoCapture(0)
    
    if not cap.isOpened():
        print("Error: Camera not detected!")
        return

    distraction_start = None
    distraction_threshold = 30  # 30 seconds of looking away
    max_session_time = 5 * 60  # 5 minutes max before auto-exit
    start_time = time.time()

    while True:
        if time.time() - start_time > max_session_time:
            print("Session ended automatically after 5 minutes.")
            break

        ret, frame = cap.read()
        if not ret:
            break

        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        face_locations = face_recognition.face_locations(rgb_frame)

        if face_locations:
            distraction_start = None  # Reset if face is detected
            print("User is focused.")
        else:
            if distraction_start is None:
                distraction_start = time.time()  # Start timing distraction

            elapsed_time = time.time() - distraction_start
            print(f"User is distracted for {int(elapsed_time)} seconds.")

            if elapsed_time >= distraction_threshold:
                print("ALERT: User has been distracted for too long!")
                break

        cv2.imshow("Distraction Detector", frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    detect_distraction()
