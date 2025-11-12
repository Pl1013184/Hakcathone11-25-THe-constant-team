import cv2, numpy as np

cap = cv2.VideoCapture(1)

while True:
    ok, frame = cap.read()
    if not ok:
        break
    mask = cv2.inRange(cv2.cvtColor(frame, cv2.COLOR_BGR2HSV), (35, 80, 40), (85, 255, 255))
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    for c in contours:
        if cv2.contourArea(c) > 50:
            x, y, w, h = cv2.boundingRect(c)
            area = w / float(h)
            if 0.8 < area < 1.25:
                cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
    cv2.imshow("Works", frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
