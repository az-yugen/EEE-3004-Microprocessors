import serial
from ultralytics import YOLO
import cv2

# Setup
ser = serial.Serial('COM12', 9600)  # Change COM port as needed
model = YOLO('yolov8n.pt')  # Load pretrained model
cap = cv2.VideoCapture(0)

last_command = ""

while True:
    ret, frame = cap.read()
    if not ret:
        break

    results = model(frame, verbose=False)[0]
    detected = [model.names[int(cls)] for cls in results.boxes.cls]

    # Flags for objects
    person_count = detected.count('person')
    book = 'book' in detected
    cup = 'cup' in detected
    pencil = 'pen' in detected or 'pencil' in detected  # YOLO might call it 'pen'

    # Decide what to send
    commands = []

    if person_count == 1:
        commands.append("P1")
    elif person_count >= 2:
        commands.append("P2")

    if book:
        commands.append("BOOK")
    if pencil:
        commands.append("PEN")
    if cup:
        commands.append("CUP")

    command = "|".join(commands) if commands else "OFF"

    if command != last_command:
        ser.write((command + "\n").encode())
        last_command = command


    # Show result
    annotated = results.plot()
    cv2.imshow("YOLO Detection", annotated)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
ser.close()
