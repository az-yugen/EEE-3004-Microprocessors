import cv2
from cvzone.FaceDetectionModule import FaceDetector
cap = cv2.VideoCapture(0)
detector = FaceDetector()
# arduino = SerialObject()


while True:
    success, img = cap.read()
    img, bboxs = detector.findFaces(img)

    # if bboxs:
    #     arduino.sendData([1])
    # else:
    #     arduino.sendData([0])

    cv2.imshow("Image", img)
    cv2.waitKey(1)



