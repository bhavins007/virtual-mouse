import os
import cv2
import mediapipe as mp
import pyautogui
import numpy as np
import time
import speech_recognition as sr
import threading
import platform
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(max_num_hands=1, min_detection_confidence=0.75, min_tracking_confidence=0.75)
mp_drawing = mp.solutions.drawing_utils
cap = cv2.VideoCapture(0)
smooth_factor = 5
screen_width, screen_height = pyautogui.size()
prev_cursor_x, prev_cursor_y = screen_width // 2, screen_height // 2
dragging = False
scrolling = False
palm_closed = False
last_frame_time = 0
frame_skip = 2
recognizer = sr.Recognizer()
def listen_for_voice_commands():
    while True:
        with sr.Microphone() as source:
            print("Listening for voice commands...")
            recognizer.adjust_for_ambient_noise(source, duration=0.5)
            try:
                audio = recognizer.listen(source, timeout=5)
                command = recognizer.recognize_google(audio).lower()
                print(f"Recognized command: {command}")
                process_voice_command(command)
            except sr.UnknownValueError:
                print("Sorry, I didn't catch that.")
            except sr.RequestError as e:
                print(f"Could not request results; {e}")
            except sr.WaitTimeoutError:
                print("Listening timed out, restarting...")
def process_voice_command(command):
    command = command.strip()
    print(f"Processing command: {command}")
    if "left click" in command:
        pyautogui.click()
    elif "right click" in command:
        pyautogui.rightClick()
    elif "double click" in command:
        pyautogui.doubleClick()
    elif "scroll up" in command:
        pyautogui.scroll(500)
    elif "scroll down" in command:
        pyautogui.scroll(-500)
    elif "shutdown" in command:
        shutdown_system()
    elif "close" in command:
        close_active_window()
    elif "sleep" in command:
        put_system_to_sleep()
    elif "increase volume" in command:
        adjust_volume("up")
    elif "decrease volume" in command:
        adjust_volume("down")
    elif "open notepad" in command:
        open_application("notepad")
    elif "open calculator" in command:
        open_application("calc")
    elif "lock system" in command:
        lock_system()
    else:
        print(f"Command '{command}' not recognized.")
def adjust_volume(direction):
    if platform.system() == "Windows":
        if direction == "up":
            pyautogui.press("volumeup")
        elif direction == "down":
            pyautogui.press("volumedown")

def open_application(app_name):
    if platform.system() == "Windows":
        os.system(f"start {app_name}")

def lock_system():
    print("Locking system...")
    if platform.system() == "Windows":
        os.system("rundll32.exe user32.dll,LockWorkStation")

def shutdown_system():
    print("Shutting down system...")
    if platform.system() == "Windows":
        os.system("shutdown /s /t 1")
    elif platform.system() == "Linux":
        os.system("sudo shutdown -h now")
    elif platform.system() == "Darwin":
        os.system("sudo shutdown -h now")
def close_active_window():
    print("Closing active window...")
    pyautogui.hotkey('alt', 'f4')
def put_system_to_sleep():
    print("Putting system to sleep...")
    if platform.system() == "Windows":
        os.system("rundll32.exe powrprof.dll,SetSuspendState 0,1,0")
    elif platform.system() == "Linux":
        os.system("systemctl suspend")
    elif platform.system() == "Darwin":
        os.system("pmset sleepnow")
    
def detect_gestures(landmarks, h, w):
    global prev_cursor_x, prev_cursor_y, dragging, scrolling, palm_closed, brightness_level, last_index_y

    index_finger_tip = landmarks[mp_hands.HandLandmark.INDEX_FINGER_TIP]
    middle_finger_tip = landmarks[mp_hands.HandLandmark.MIDDLE_FINGER_TIP]
def is_finger_bent(landmarks, finger_tip, finger_joint):
    return landmarks[finger_tip].y > landmarks[finger_joint].y
def detect_gestures(landmarks, h, w):
    global prev_cursor_x, prev_cursor_y, dragging, scrolling, palm_closed
    index_finger_tip = landmarks[mp_hands.HandLandmark.INDEX_FINGER_TIP]
    middle_finger_tip = landmarks[mp_hands.HandLandmark.MIDDLE_FINGER_TIP]
    cursor_x = int((index_finger_tip.x + middle_finger_tip.x) / 2 * screen_width)
    cursor_y = int((index_finger_tip.y + middle_finger_tip.y) / 2 * screen_height)
    cursor_x = int(prev_cursor_x + (cursor_x - prev_cursor_x) / smooth_factor)
    cursor_y = int(prev_cursor_y + (cursor_y - prev_cursor_y) / smooth_factor)
    pyautogui.moveTo(cursor_x, cursor_y)
    prev_cursor_x, prev_cursor_y = cursor_x, cursor_y
    index_bent = is_finger_bent(landmarks, mp_hands.HandLandmark.INDEX_FINGER_TIP, mp_hands.HandLandmark.INDEX_FINGER_PIP)
    middle_bent = is_finger_bent(landmarks, mp_hands.HandLandmark.MIDDLE_FINGER_TIP, mp_hands.HandLandmark.MIDDLE_FINGER_PIP)
    if index_bent and not middle_bent:
        pyautogui.click()
    elif middle_bent and not index_bent:
        pyautogui.rightClick()
    elif abs(index_finger_tip.x - middle_finger_tip.x) < 0.02 and abs(index_finger_tip.y - middle_finger_tip.y) < 0.02:
        pyautogui.doubleClick()
    thumb_tip = landmarks[mp_hands.HandLandmark.THUMB_TIP]
    thumb_pos = (int(thumb_tip.x * w), int(thumb_tip.y * h))
    index_pos = (int(index_finger_tip.x * w), int(index_finger_tip.y * h))
    pinch_distance = np.linalg.norm(np.array(thumb_pos) - np.array(index_pos))
    if pinch_distance < 40:
        if not dragging:
            pyautogui.mouseDown()
            dragging = True
        else:
            pyautogui.moveTo(cursor_x, cursor_y)
    else:
        if dragging:
            pyautogui.mouseUp()
            dragging = False
    fingers_bent = [
        is_finger_bent(landmarks, mp_hands.HandLandmark.THUMB_TIP, mp_hands.HandLandmark.THUMB_IP),
        is_finger_bent(landmarks, mp_hands.HandLandmark.INDEX_FINGER_TIP, mp_hands.HandLandmark.INDEX_FINGER_PIP),
        is_finger_bent(landmarks, mp_hands.HandLandmark.MIDDLE_FINGER_TIP, mp_hands.HandLandmark.MIDDLE_FINGER_PIP),
        is_finger_bent(landmarks, mp_hands.HandLandmark.RING_FINGER_TIP, mp_hands.HandLandmark.RING_FINGER_PIP),
        is_finger_bent(landmarks, mp_hands.HandLandmark.PINKY_TIP, mp_hands.HandLandmark.PINKY_PIP)
    ]

    if all(fingers_bent) and not palm_closed:
        pyautogui.keyDown('ctrl')
        pyautogui.mouseDown()
        pyautogui.mouseUp()
        pyautogui.keyUp('ctrl')
        palm_closed = True
    elif not all(fingers_bent):
        palm_closed = False
voice_thread = threading.Thread(target=listen_for_voice_commands, daemon=True)
voice_thread.start()
while cap.isOpened():
    current_time = time.time()
    if current_time - last_frame_time < 1 / 30:
        continue
    last_frame_time = current_time

    success, frame = cap.read()
    if not success:
        break
    frame = cv2.flip(frame, 1)
    h, w, _ = frame.shape
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    result = hands.process(rgb_frame)
    if result.multi_hand_landmarks:
        for hand_landmarks in result.multi_hand_landmarks:
            mp_drawing.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)
            detect_gestures(hand_landmarks.landmark, h, w)
    cv2.imshow('Gesture Controlled Virtual Mouse', frame)
    if cv2.waitKey(1) & 0xFF == 27:
        break
cap.release()
cv2.destroyAllWindows()