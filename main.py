from time import sleep, time
import cv2
from cvzone.HandTrackingModule import HandDetector

# Initialize camera
cap = cv2.VideoCapture(0)
cap.set(3, 1280)
cap.set(4, 720)

# Hand detector
detector = HandDetector(detectionCon=0.8, maxHands=2)

# Keyboard layout
keys = [["Q", "W", "E", "R", "T", "Y", "U", "I", "O", "P"],
        ["A", "S", "D", "F", "G", "H", "J", "K", "L", ";"],
        ["Z", "X", "C", "V", "B", "N", "M", ",", ".", "/"],
        ["SPACE", "BACKSPACE"]]

finalText = ""
debounce_time = 0.70  # Time in seconds between clicks
last_click_time = 0  # Store time of last click


# Button class
class Button:
    def __init__(self, pos, text, size=(85, 85)):
        self.pos = pos
        self.size = size
        self.text = text


# Initialize button list
buttonList = []
for i, row in enumerate(keys):
    for j, key in enumerate(row):
        # Assign larger size for the space and backspace keys
        if key == "SPACE":
            size = (400, 85)
            x = 350
        elif key == "BACKSPACE":
            size = (200, 85)
            x = 800
        else:
            size = (85, 85)
            x = 100 * j + 50
        y = 100 * i + 50
        buttonList.append(Button([x, y], key, size))


# Draw all buttons on the keyboard with translucent effect
def draw_buttons(img, buttonList, lmList=None):
    overlay = img.copy()
    for button in buttonList:
        x, y = button.pos
        w, h = button.size

        # Check if hovering over a button (change to darker gray)
        if lmList and x < lmList[8][0] < x + w and y < lmList[8][1] < y + h:
            color = (100, 100, 100)  # Darker gray for hover
        else:
            color = (128, 128, 128)  # Default translucent gray

        # Draw translucent button
        cv2.rectangle(overlay, (x, y), (x + w, y + h), color, cv2.FILLED)
        cv2.putText(overlay, button.text, (x + 20, y + 65), cv2.FONT_HERSHEY_SIMPLEX, 2, (255, 255, 255),
                    2)
    # Blend overlay with original image to make buttons translucent
    img = cv2.addWeighted(overlay, 0.5, img, 0.5, 0)
    return img


# Check for button clicks
def check_click(buttonList, lmList, img):
    global finalText, last_click_time
    for button in buttonList:
        x, y = button.pos
        w, h = button.size

        # Check if fingertip (index finger) is over a button
        if x < lmList[8][0] < x + w and y < lmList[8][1] < y + h:
            # Calculate distance between index and middle fingertips
            length, _, img = detector.findDistance(lmList[8][:2], lmList[12][:2], img)

            # Click action if distance is small enough
            current_time = time()
            if length < 30 and (current_time - last_click_time > debounce_time):
                if button.text == "SPACE":
                    finalText += " "
                elif button.text == "BACKSPACE":
                    finalText = finalText[:-1]  # Remove last character
                else:
                    finalText += button.text
                last_click_time = current_time
    return img


# Main loop
while True:
    success, img = cap.read()
    if not success:
        break

    # Detect hands and draw buttons
    hands, img = detector.findHands(img)
    lmList = hands[0]["lmList"] if hands else None  # Landmark list of the first hand
    img = draw_buttons(img, buttonList, lmList)

    if lmList:
        img = check_click(buttonList, lmList, img)

    # Display the typed text in a dark gray box
    cv2.rectangle(img, (50, 500), (1200, 600), (50, 50, 50), cv2.FILLED)
    cv2.putText(img, finalText, (60, 575), cv2.FONT_HERSHEY_PLAIN, 3, (255, 255, 255), 3)

    cv2.imshow("Image", img)
    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

cap.release()
cv2.destroyAllWindows()
