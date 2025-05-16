import cv2
import serial

ser = serial.Serial('COM12', 9600)  # Replace COM3 with your port

face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
prev_command = ""

cap = cv2.VideoCapture(0)

while True:
    ret, frame = cap.read()
    if not ret:
        break

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(gray, 1.3, 5)

    command = ""
    if len(faces) == 0:
        command = "OFF\n"
    elif len(faces) == 1:
        command = "ONE\n"
    else:
        command = "TWO\n"

    if command != prev_command:
        ser.write(command.encode())
        prev_command = command

    for (x, y, w, h) in faces:
        cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 0, 0), 2)

    cv2.imshow('Face Detection', frame)
    if cv2.waitKey(1) == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
ser.close()
