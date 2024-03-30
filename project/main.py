import cv2
import mediapipe as mp
import pyautogui
import math
import tkinter as tk
from tkinter import Canvas
from PIL import Image, ImageTk


# Функция для нажатия ПКМ
def right_click():
    pyautogui.mouseDown(button='right')
    pyautogui.mouseUp(button='right')


# Функция для нажатия ЛКМ
def left_click():
    pyautogui.mouseDown(button='left')
    pyautogui.mouseUp(button='left')


def hand_is_right(p5x, p9x):
    if p5x < p9x:
        return True
    else:
        return False


def update_position_labels():
    xPose.config(text=f"X:{pyautogui.position()[0]}")
    yPose.config(text=f"Y:{pyautogui.position()[1]}")
    root.after(10, update_position_labels)  # Update every 1000 milliseconds (1 second)


def find_angle(a, b, c, d):
    vector_ab = (b[0] - a[0], b[1] - a[1])
    vector_cd = (d[0] - c[0], d[1] - c[1])

    dot_product = vector_ab[0] * vector_cd[0] + vector_ab[1] * vector_cd[1]

    magnitude_ab = math.sqrt(vector_ab[0]**2 + vector_ab[1]**2)
    magnitude_cd = math.sqrt(vector_cd[0]**2 + vector_cd[1]**2)

    cosine_angle = dot_product / (magnitude_ab * magnitude_cd)

    angle_rad = math.acos(cosine_angle)
    angle_deg = math.degrees(angle_rad)

    return abs(angle_deg - 180)


def find_distance(a, b):
    dist = math.sqrt((b[0] - a[0]) ** 2 + (b[1] - a[1]) ** 2)
    return dist


def normalize(dist):
    max_value = 1.15
    min_value = 0.30
    new_max = 1
    new_min = 0
    _dist = dist*(1/3.85)
    normalized_value = (_dist - min_value) / (max_value - min_value) * (new_max - new_min) + new_min
    return normalized_value


def moving_up_down(angle):
    current_x, current_y = pyautogui.position()
    pyautogui.moveTo(current_x, (angle-3)*22)


def moving_left_right(distance, x5, x9):
    if hand_is_right(x5, x9):
        current_x, current_y = pyautogui.position()
        pyautogui.moveTo(screen_width * (1 - distance), current_y)
    else:
        current_x, current_y = pyautogui.position()
        pyautogui.moveTo(screen_width*distance, current_y)


def update_camera_feed():
    hand_detected = False
    success, img = cap.read()
    img = cv2.flip(img, 1)

    imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    results = hands.process(imgRGB)

    if not hand_detected and results.multi_hand_landmarks:
        num_hands = len(results.multi_hand_landmarks)
        if num_hands == 1:
            for handLms in results.multi_hand_landmarks:
                for id, lm in enumerate(handLms.landmark):
                    h, w, c = img.shape
                    cx, cy = int(lm.x * w), int(lm.y * h)

                    if id == 5:
                        x5, y5 = cx, cy
                    if id == 8:
                        x8, y8 = cx, cy
                    if id == 9:
                        x9, y9 = cx, cy
                    if id == 12:
                        x12, y12 = cx, cy
                    if id == 4:
                        x4, y4 = cx, cy
                    if id == 14:
                        x14, y14 = cx, cy

                        angle = find_angle((x8, y8), (x5, y5), (x9, y9), (x12, y12))
                        moving_up_down(angle)
                        distance4_15 = find_distance((x14, y14), (x4, y4))
                        distance5_9 = find_distance((x5, y5), (x9, y9))
                        distance5_8_norm = find_distance((x5, y5), (x8, y8)) / distance5_9
                        distance9_12_norm = find_distance((x9, y9), (x12, y12)) / distance5_9

                        print("5-8:", distance5_8_norm)
                        print("9-12:", distance9_12_norm)

                        if distance5_8_norm < 3:
                            left_click()
                        if distance9_12_norm < 3:
                            right_click()

                        m_dist = distance4_15 / distance5_9
                        moving_left_right(normalize(m_dist), x5, x9)


                    if id == 5 or id == 8 or id == 9 or id == 12:
                        cv2.circle(img, (cx, cy), 10, (255, 0, 255), cv2.FILLED)
                    if id == 4 or id == 14:
                        cv2.circle(img, (cx, cy), 10, (255, 0, 0), cv2.FILLED)

                npDraw.draw_landmarks(img, handLms, mpHands.HAND_CONNECTIONS)

    # Display the image on the Tkinter canvas
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)  # Convert to RGB for Tkinter
    photo = ImageTk.PhotoImage(image=Image.fromarray(img))
    canvas.create_image(0, 0, image=photo, anchor=tk.NW)
    canvas.image = photo

    # Update the camera feed periodically
    canvas.after(10, update_camera_feed)


# Create a Tkinter window
root = tk.Tk()
root.title("Hand Tracking Cursor Control")
root.resizable(False, False)
root.iconbitmap("fixiki.ico")

# Create a Canvas widget to display the camera feed
canvas = Canvas(root, width=640, height=480)
canvas.grid(row=0, column=0, columnspan=2)

# show cursor position
xPose = tk.Label(root, text=f"X:{pyautogui.position()[0]}", font=("Arial", 14, "bold"), fg="red")
yPose = tk.Label(root, text=f"Y:{pyautogui.position()[1]}", font=("Arial", 14, "bold"), fg="blue")
xPose.grid(row=1, column=0)
yPose.grid(row=1, column=1)

update_position_labels()

screen_width, screen_height = pyautogui.size()

cap = cv2.VideoCapture(0)
cap.set(3, 640)  # Width
cap.set(4, 480)  # Length
cap.set(10, 100)  # Brightness

mpHands = mp.solutions.hands
hands = mpHands.Hands(False)
npDraw = mp.solutions.drawing_utils

pyautogui.FAILSAFE = False

update_camera_feed()

root.mainloop()

cap.release()
cv2.destroyAllWindows()
cv2.waitKey(1)
