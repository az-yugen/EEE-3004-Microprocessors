import cv2
import mediapipe as mp
import serial

ser = serial.Serial('COM12', 9600)
cap = cv2.VideoCapture(0)

mp_hands = mp.solutions.hands
hands = mp_hands.Hands()
mp_draw = mp.solutions.drawing_utils

def count_fingers(hand_landmarks):
    finger_tips = [8, 12, 16, 20]
    count = 0
    for tip in finger_tips:
        if hand_landmarks.landmark[tip].y < hand_landmarks.landmark[tip - 2].y:
            count += 1
    # Thumb
    if hand_landmarks.landmark[4].x < hand_landmarks.landmark[3].x:
        count += 1
    return count

prev_speed = -1

while True:
    success, img = cap.read()
    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    result = hands.process(img_rgb)

    speed = 0  # Default: motor off

    if result.multi_hand_landmarks:
        fingers = count_fingers(result.multi_hand_landmarks[0])
        speed = int((fingers / 5.0) * 255)  # Map 0–5 fingers to 0–255 PWM
        # speed = int(255)

        mp_draw.draw_landmarks(img, result.multi_hand_landmarks[0], mp_hands.HAND_CONNECTIONS)

    if speed != prev_speed:
        ser.write(f"{speed}\n".encode())
        prev_speed = speed

    cv2.imshow("Hand Detection", img)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
ser.close()
