"""
3004-MICROPROCESSORS. GROUP PROJECT.

220702706 - Ahmad Zameer Nazarı
220702705 - Ahmed Mahmoud Elsayed Hussein
210702725 - Fevzi Keshta
210702723 - Mohamed Shawki Eid Elsayed

Gesture Detection-Based Security System

"""

# Libraries and module imports
import cv2
import mediapipe as mp
import serial
import time

# Serial port setup
ser = serial.Serial('COM12', 9600, timeout=1) 
time.sleep(2)

# Mediapipe setup
mp_hands = mp.solutions.hands
mp_face = mp.solutions.face_detection
hands = mp_hands.Hands(max_num_hands=1)
face = mp_face.FaceDetection()
mp_draw = mp.solutions.drawing_utils

# OpenCV setup
cap = cv2.VideoCapture(0)

# Initializations
stage = 0                           # keep track of stage
last_detected = 0                   # last detected finger gesture
password_sequence = [4, 1, 2]       # predefined finger gesture password sequence. can be changed
input_sequence = []
last_count = -1
hold_start = None

# Function to count fingers
def count_fingers(hand_landmarks):
    tips = [8, 12, 16, 20]
    count = 0
    for tip in tips:
        if hand_landmarks.landmark[tip].y < hand_landmarks.landmark[tip - 2].y:
            count += 1
    return count

# main loop
while True:
    success, frame = cap.read()
    if not success:
        break

    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    face_results = face.process(frame_rgb)
    hand_results = hands.process(frame_rgb)

    now = time.time()

    # Stage 0: Face Detection
    if stage == 0 and face_results.detections:
        ser.write(b"FACE_ON\n")
        stage = 1
        print("Stage 1: Face detected")

    # Stage 1: Wait for open hand (4 fingers)
    elif stage == 1 and hand_results.multi_hand_landmarks:
        hand = hand_results.multi_hand_landmarks[0]
        mp_draw.draw_landmarks(frame, hand, mp_hands.HAND_CONNECTIONS)
        count = count_fingers(hand)

        # begin counting when open hand is detected (thumb excluded, 4 fingers)
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

    # Stage 2: Password entry
    elif stage == 2 and hand_results.multi_hand_landmarks:
        hand = hand_results.multi_hand_landmarks[0]
        mp_draw.draw_landmarks(frame, hand, mp_hands.HAND_CONNECTIONS)
        count = count_fingers(hand)

        if count != last_count:
            hold_start = now
            last_count = count

        # 3 seconds to hold gesture. send finger count to arduino serially
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


    # OpenCV. Display video window
    cv2.imshow("Gesture Lock", frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break


cap.release()
cv2.destroyAllWindows()
ser.close()
