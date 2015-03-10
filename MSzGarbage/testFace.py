import cv2

def detect(cascade):
    cam = cv2.VideoCapture(0)
    img = cam.read()[1]
    
    rects = cascade.detectMultiScale(img, 1.3, 4, cv2.cv.CV_HAAR_SCALE_IMAGE, (20,20))
    
    if len(rects) == 0:
        return [], img
    rects[:, 2:] += rects[:, :2]
    
    
    return rects, img

def box(rects, img):
    for x1, y1, x2, y2 in rects:
        cv2.rectangle(img, (x1, y1), (x2, y2), (20, 255, 0), 5)
    

cascade = cv2.CascadeClassifier("haarcascade_frontalface_default.xml")
rects, img = detect(cascade)
box(rects, img)
winName = "face"
cv2.namedWindow(winName, cv2.CV_WINDOW_AUTOSIZE)
cv2.imshow( winName, img)
cv2.waitKey(10)

while True:
    
  cv2.imshow( winName, img)
  
  rects, img = detect(cascade)
  box(rects, img)

  key = cv2.waitKey(10)
  if key == 27:
    cv2.destroyWindow(winName)
    break

cv2.destroyWindow(winName)
