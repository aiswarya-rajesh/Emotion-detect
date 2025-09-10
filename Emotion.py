import cv2
import mediapipe as mp
import pyautogui
import time
import keyboard  # for simulating hotkeys

# Initialize MediaPipe
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(max_num_hands=1, min_detection_confidence=0.7)
mp_draw = mp.solutions.drawing_utils

# Webcam
cap = cv2.VideoCapture(0)

# Cooldown setup
last_gesture_time = 0
cooldown = 1.5  # in seconds

# Get finger states (up or down)
def fingers_up(hand_landmarks):
    finger_tips = [8, 12, 16, 20]     # Index, Middle, Ring, Pinky
    finger_dips = [6, 10, 14, 18]     # Before tip joints
    fingers = []

    for tip, dip in zip(finger_tips, finger_dips):
        fingers.append(int(hand_landmarks.landmark[tip].y < hand_landmarks.landmark[dip].y))

    # Thumb: check x-coordinates (left/right)
    thumb_open = hand_landmarks.landmark[4].x < hand_landmarks.landmark[3].x
    fingers.insert(0, int(thumb_open))

    return fingers

# Main loop
while True:
    success, frame = cap.read()
    if not success:
        break

    frame = cv2.flip(frame, 1)
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = hands.process(rgb)

    gesture_text = ""

    if results.multi_hand_landmarks:
        for hand_landmarks in results.multi_hand_landmarks:
            mp_draw.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)
            fingers = fingers_up(hand_landmarks)

            current_time = time.time()

            # Define gestures and actions
            if fingers == [0, 0, 0, 0, 0]:  # ✊ Fist
                gesture_text = "Play/Pause"
                if current_time - last_gesture_time > cooldown:
                    pyautogui.press('playpause')
                    last_gesture_time = current_time

            elif fingers == [0, 1, 1, 0, 0]:  # ✌️ Two fingers
                gesture_text = "Volume Up"
                if current_time - last_gesture_time > cooldown:
                    pyautogui.press('volumeup')
                    last_gesture_time = current_time

            elif fingers == [0, 1, 0, 0, 0]:  # ☝️ One finger
                gesture_text = "Volume Down"
                if current_time - last_gesture_time > cooldown:
                    pyautogui.press('volumedown')
                    last_gesture_time = current_time

            elif fingers == [1, 1, 1, 1, 1]:  # 🖐️ Open palm
                gesture_text = "Stop"
                if current_time - last_gesture_time > cooldown:
                    pyautogui.press('stop')
                    last_gesture_time = current_time

            elif fingers == [1, 1, 0, 0, 0]:  # 👉 Thumb + Index
                gesture_text = "Next Track"
                if current_time - last_gesture_time > cooldown:
                    pyautogui.press('nexttrack')
                    last_gesture_time = current_time

            elif fingers == [1, 0, 0, 0, 1]:  # 👈 Thumb + Pinky
                gesture_text = "Previous Track"
                if current_time - last_gesture_time > cooldown:
                    pyautogui.press('prevtrack')
                    last_gesture_time = current_time

            elif fingers == [0, 1, 0, 0, 1]:  # 🤟 Index + Pinky
                gesture_text = "Mute"
                if current_time - last_gesture_time > cooldown:
                    pyautogui.press('volumemute')
                    last_gesture_time = current_time

            elif fingers == [0, 1, 1, 1, 0]:  # ➕ Speed Up
                gesture_text = "Speed Up"
                if current_time - last_gesture_time > cooldown:
                    # For YouTube: Shift + .
                    keyboard.press_and_release('shift+.')
                    # For VLC: use `keyboard.press_and_release(']')` instead
                    last_gesture_time = current_time

            # Show gesture name
            cv2.putText(frame, f'Gesture: {gesture_text}', (10, 40),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 128, 255), 2)

    cv2.imshow("AI Hand Gesture Media Controller", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Cleanup
cap.release()
cv2.destroyAllWindows()
