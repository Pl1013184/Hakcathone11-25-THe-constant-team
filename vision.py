import cv2, numpy as np, os, subprocess

TARGET = "moveclass.py"

cap = cv2.VideoCapture(1)

while True:
    ok, frame = cap.read()
    if not ok:
        break
    mask = cv2.inRange(cv2.cvtColor(frame, cv2.COLOR_BGR2HSV), (35, 80, 40), (85, 255, 255))
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    boxes = []
    for c in contours:
        if cv2.contourArea(c) > 50:
            x, y, w, h = cv2.boundingRect(c)
            area = w / float(h)
            if 0.8 < area < 1.25:
                boxes.append((x,y,w,h))
    if boxes:
        bottoms = [y+h for (_,y,_,h) i n boxes]
        m = max(bottoms)
        if bottoms.count(m) == 1:
            subprocess.Popen(["python3", os.path.join(os.path.dirname(__file__), TARGET)])
            break    #cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

cap.release()
cv2.destroyAllWindows()
