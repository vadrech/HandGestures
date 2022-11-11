import cv2
import mediapipe as mp
import time
import pyautogui
import math
import osascript

#sliding window kind of thing of length 10
#format: [isHand (Bool), isLeft (Bool), ]

#bugs: multihand bug, restart bug

#needs brew install brightness

cap = cv2.VideoCapture(0)

mpHands = mp.solutions.hands
hands = mpHands.Hands(static_image_mode=False, max_num_hands=1, min_detection_confidence=0.5, min_tracking_confidence=0.5)
mpDraw = mp.solutions.drawing_utils

x_val = 0
y_val_scroll = 0

num_0 = 0
angle = 0

volume_trigger = False
brightness_trigger = False
cursor_mode = False

app_name = "Gesture Control"

while True:
    success, img = cap.read()
    imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    results = hands.process(imgRGB)

    try:
        isLeft = bool(int(str(results.multi_handedness).split()[3]))
        num_0 = 0
#        print(isLeft)

    except:
        num_0 += 1

        if num_0 > 4:
            x_val = 0
            y_val_scroll = 0
            angle = 0

        if volume_trigger:
            volume_trigger = False
            osascript.osascript('display notification "Volume Control Off" with title "{}"'.format(app_name))

        if brightness_trigger:
            brightness_trigger = False
            osascript.osascript('display notification "Brightness Control Off" with title "{}"'.format(app_name))

    if results.multi_hand_landmarks:
        for handLms in results.multi_hand_landmarks:
            for id, lm in enumerate(handLms.landmark):
                #print(id,lm)
                h, w, c = img.shape
                cx, cy = int(lm.x *w), int(lm.y*h)
                #if id ==0:
                cv2.circle(img, (cx,cy), 3, (255,0,255), cv2.FILLED)

            mpDraw.draw_landmarks(img, handLms, mpHands.HAND_CONNECTIONS)
            
            if x_val == 0:
                x_val = float(f'{handLms.landmark[mpHands.HandLandmark(0).value]}'.split()[1])
                y_val_scroll = float(f'{handLms.landmark[mpHands.HandLandmark(12).value]}'.split()[3])
                angle = math.atan((float(f'{handLms.landmark[mpHands.HandLandmark(0).value]}'.split()[1]) - float(f'{handLms.landmark[mpHands.HandLandmark(12).value]}'.split()[1]))/(float(f'{handLms.landmark[mpHands.HandLandmark(0).value]}'.split()[3]) - float(f'{handLms.landmark[mpHands.HandLandmark(12).value]}'.split()[3])))
                
            else:
                if volume_trigger:
                    set_volume = (math.atan(diff_x/diff_y) + math.pi/2) * 100 / math.pi
                    osascript.osascript("set volume output volume " + str(set_volume))

                elif brightness_trigger:
                    set_brightness = (math.atan(diff_x/diff_y) + math.pi/2) / math.pi
                    osascript.osascript('do shell script "/usr/local/bin/brightness ' + str(set_brightness) + '"')

                elif x_val - float(f'{handLms.landmark[mpHands.HandLandmark(0).value]}'.split()[1]) > 0.2:
                    pyautogui.hotkey('ctrl', 'left')

                elif x_val - float(f'{handLms.landmark[mpHands.HandLandmark(0).value]}'.split()[1]) < -0.2:
                    pyautogui.hotkey('ctrl', 'right')

                elif y_val_scroll - float(f'{handLms.landmark[mpHands.HandLandmark(12).value]}'.split()[3]) > 0.3 and isLeft:
                    pyautogui.scroll(-20)

                elif y_val_scroll - float(f'{handLms.landmark[mpHands.HandLandmark(12).value]}'.split()[3]) < -0.3 and isLeft:
                    pyautogui.scroll(20)

                elif angle - math.atan((float(f'{handLms.landmark[mpHands.HandLandmark(0).value]}'.split()[1]) - float(f'{handLms.landmark[mpHands.HandLandmark(12).value]}'.split()[1]))/(float(f'{handLms.landmark[mpHands.HandLandmark(0).value]}'.split()[3]) - float(f'{handLms.landmark[mpHands.HandLandmark(12).value]}'.split()[3]))) > 1.0 and not isLeft:
                    if cursor_mode:
                        cursor_mode = False
                        osascript.osascript('display notification "Cursor Control Off" with title "{}"'.format(app_name))

                    else:
                        cursor_mode = True
                        osascript.osascript('display notification "Cursor Control On" with title "{}"'.format(app_name))

                else:                    
                    diff_x = float(f'{handLms.landmark[mpHands.HandLandmark(0).value]}'.split()[1]) - float(f'{handLms.landmark[mpHands.HandLandmark(12).value]}'.split()[1])
                    diff_y = float(f'{handLms.landmark[mpHands.HandLandmark(0).value]}'.split()[3]) - float(f'{handLms.landmark[mpHands.HandLandmark(12).value]}'.split()[3])

#                    a = int((''.join([i for i in osascript.osascript('get volume settings')[1].split()[1] if i.isdigit()])))
                    x_wrist = float(f'{handLms.landmark[mpHands.HandLandmark(0).value]}'.split()[1])
                    y_wrist = float(f'{handLms.landmark[mpHands.HandLandmark(0).value]}'.split()[3])

                    distance = math.sqrt(diff_x**2 + diff_y**2)                    

                    if cursor_mode:
                        #screen dimensions 1680 * 1050, but set with some room
                        pyautogui.moveTo(1680 * (1.7 * (0.5 - x_wrist) + 0.5), (1050 - 1050 * (1.7 * (0.5 - y_wrist) + 0.5)))

                    if distance < 0.25:
                        if cursor_mode:
                            pyautogui.click()
                    
                    if distance < 0.09:
                        if not cursor_mode:
                            if isLeft:
                                brightness_trigger = True
                                osascript.osascript('display notification "Brightness Control On" with title "{}"'.format(app_name))

                            else:                        
                                volume_trigger = True
                                osascript.osascript('display notification "Volume Control On" with title "{}"'.format(app_name))

                x_val = float(f'{handLms.landmark[mpHands.HandLandmark(0).value]}'.split()[1])
                
                y_val_scroll = float(f'{handLms.landmark[mpHands.HandLandmark(12).value]}'.split()[3])
                
                diff_x = float(f'{handLms.landmark[mpHands.HandLandmark(0).value]}'.split()[1]) - float(f'{handLms.landmark[mpHands.HandLandmark(12).value]}'.split()[1])
                diff_y = float(f'{handLms.landmark[mpHands.HandLandmark(0).value]}'.split()[3]) - float(f'{handLms.landmark[mpHands.HandLandmark(12).value]}'.split()[3])

                angle = math.atan(diff_x/diff_y)
                
    cv2.imshow("Image", img)

    k = cv2.waitKey(30) & 0xff
    
    if k == 27:
        break

cap.release()
cv2.destroyAllWindows()
