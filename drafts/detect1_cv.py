import serial.tools.list_ports
import cv2
from cvzone.FaceDetectionModule import FaceDetector
cap = cv2.VideoCapture(0)
detector = FaceDetector()

ports = serial.tools.list_ports.comports()
serialInst = serial.Serial()
portsList = []



for one in ports:
    portsList.append(str(one))
    print(str(one))


com = '12'

for i in range(len(portsList)):
    if portsList[i].startswith("COM" + str(com)):
        use = "COM" + str(com)
        print(use)


serialInst.baudrate = 9600
serialInst.port = use
serialInst.open()

# command = input("Enter command (ON/OFF/exit): ")
# serialInst.write(command.encode('utf-8'))

# if command == "exit":
#     exit()
# else:
# abc = '0'
while True:
    success, img = cap.read()
    img, bboxs = detector.findFaces(img)


    cv2.imshow("Image", img)
    cv2.waitKey(1)


    if bboxs:
        # serialInst.write('ON'.encode('utf-8'))
        serialInst.write(b"ON\n")
    else:
        # serialInst.write('OFF'.encode('utf-8'))
        serialInst.write(b"OFF\n")

        # if bboxs:
        #     serialInst.write(b'1')
        # else:
        #     serialInst.write(b'0')

        





