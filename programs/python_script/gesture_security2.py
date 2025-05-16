import cv2
import mediapipe as mp
import serial
import time

# === Serial Setup ===
ser = serial.Serial('COM12', 9600, timeout=1)  # Change COM port as needed
time.sleep(2)  # Wait for Arduino reset

# === Mediapipe Setup ===
mp_hands = mp.solutions.hands
mp_face = mp.solutions.face_detection
hands = mp_hands.Hands(max_num_hands=1)
face = mp_face.FaceDetection()
mp_draw = mp.solutions.drawing_utils

# === Camera Setup ===
cap = cv2.VideoCapture(0)

# === State Tracking ===
stage = 0
last_detected = 0
password_sequence = [4, 1, 2]
input_sequence = []
last_count = -1
hold_start = None

face_detected = False
prev_face_detected = False

def count_fingers(hand_landmarks):
    """Only count index to pinky fingers"""
    tips = [8, 12, 16, 20]
    count = 0
    for tip in tips:
        if hand_landmarks.landmark[tip].y < hand_landmarks.landmark[tip - 2].y:
            count += 1
    return count

while True:
    success, frame = cap.read()
    if not success:
        break

    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    face_results = face.process(frame_rgb)
    hand_results = hands.process(frame_rgb)

    now = time.time()

    # === FACE DETECTION ===
    face_detected = bool(face_results.detections)
    if face_detected != prev_face_detected:
        if face_detected:
            ser.write(b"FACE_ON\n")
            stage = 1
            print("Stage 1: Face detected")
        else:
            ser.write(b"FACE_OFF\n")
            print("Face lost")
        prev_face_detected = face_detected

    # === HAND DETECTION & PASSWORD ENTRY ===
    if stage == 1 and hand_results.multi_hand_landmarks:
        hand = hand_results.multi_hand_landmarks[0]
        mp_draw.draw_landmarks(frame, hand, mp_hands.HAND_CONNECTIONS)
        count = count_fingers(hand)

        if count == 4:
            if now - last_detected > 2:
                ser.write(b"READY\n")
                stage = 2
                input_sequence = []
                hold_start = None
                last_count = -1
                print("Stage 2: Ready for password")
        else:
            last_detected = now

    elif stage == 2 and hand_results.multi_hand_landmarks:
        hand = hand_results.multi_hand_landmarks[0]
        mp_draw.draw_landmarks(frame, hand, mp_hands.HAND_CONNECTIONS)
        count = count_fingers(hand)

        if count != last_count:
            hold_start = now
            last_count = count

        if hold_start:
            hold_time = int(3 - (now - hold_start))
            hold_time = max(0, hold_time)
            ser.write(f"FINGERS:{count},{hold_time}\n".encode())

            if now - hold_start > 3:
                if count > 0:
                    input_sequence.append(count)
                    print("Input so far:", input_sequence)
                    hold_start = None
                    last_count = -1

                if len(input_sequence) == len(password_sequence):
                    if input_sequence == password_sequence:
                        ser.write(b"PASS_OK\n")
                        stage = 0
                        print("Stage 3: Password correct")
                    else:
                        ser.write(b"PASS_FAIL\n")
                        stage = 1
                        print("Stage 3: Wrong password")

    # === Display Camera Feed ===
    cv2.imshow("Gesture Lock", frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# === Cleanup ===
cap.release()
cv2.destroyAllWindows()
ser.close()
