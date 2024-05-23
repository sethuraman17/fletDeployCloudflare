import flet as ft
import cv2
import numpy as np
from cvzone.FaceMeshModule import FaceMeshDetector
from math import hypot
import threading
import time
import base64
import logging

# Configure logging
logging.basicConfig(level=logging.DEBUG)

# Key sets
keys_set = {0: "I", 1: "Don't", 2: "ok!", 3: "Yes", 4: "No",
            5: "car", 6: "want", 7: "Help", 8: "Come", 9: "Water",
            10: "am", 11: "Go", 12: "ok!", 13: "need", 14: "Fine"}

keys_set2 = {0: "Nope", 1: "Fuck", 2: "Suck!", 3: "Yes", 4: "No",
             5: "car", 6: "want", 7: "Help", 8: "Come", 9: "Water",
             10: "am", 11: "Go", 12: "ok!", 13: "need", 14: "Fine"}

keys_set3 = {0: "Maybe", 1: "Wow", 2: "Great!", 3: "Yes", 4: "No",
             5: "car", 6: "want", 7: "Help", 8: "Come", 9: "Water",
             10: "am", 11: "Go", 12: "ok!", 13: "need", 14: "Fine"}

key_set_mapping = {
    0: keys_set,
    1: keys_set2,
    2: keys_set3
}

frames = 0
blink_frame = 0
letter_index = 0
text = ""
current_set = keys_set
running = True

def update_ui(page, output_text, keyboard, webcam_image):
    global running, text, letter_index
    while running:
        logging.debug("Updating UI...")
        time.sleep(0.1)
        output_text.value = text
        for i in range(15):
            key_text = current_set[i]
            keyboard.controls[i].content.value = key_text
            if i == letter_index:
                keyboard.controls[i].bgcolor = ft.colors.WHITE
            else:
                keyboard.controls[i].bgcolor = ft.colors.BLUE
        page.update()

def process_video(page, webcam_image):
    global frames, blink_frame, letter_index, text, current_set, running
    cap = cv2.VideoCapture(0)
    detector = FaceMeshDetector(maxFaces=1, minDetectionCon=0.8)

    while running:
        logging.debug("Capturing frame...")
        success, img = cap.read()
        if not success:
            logging.error("Failed to capture image from webcam.")
            continue

        frames += 1
        img, faces = detector.findFaceMesh(img, draw=False)
        if faces:
            face = faces[0]
            left_right = face[243]
            left_left = face[130]
            left_up = face[27]
            left_down = face[23]

            hor_line_length = hypot((left_left[0] - left_right[0]), (left_left[1] - left_right[1]))
            ver_line_length = hypot((left_up[0] - left_down[0]), (left_up[1] - left_down[1]))

            ratio = hor_line_length / ver_line_length

            if ratio > 2.8:
                blink_frame += 1
                frames -= 1
                active_letter = current_set[letter_index]
                logging.debug(f"Active letter: {active_letter}")

                if active_letter == "I":
                    exec(open("testing.py").read())
                elif active_letter == "Don't":
                    current_set = key_set_mapping[2]
                    letter_index = 0
                elif active_letter == "Wow":
                    current_set = key_set_mapping[0]
                    letter_index = 0

                text += active_letter
                time.sleep(1)
            else:
                blink_frame = 0

            if frames == 20:
                letter_index = (letter_index + 1) % 15
                frames = 0

        # Convert frame to JPEG and base64 encode it
        _, buffer = cv2.imencode('.jpg', img)
        jpg_as_text = base64.b64encode(buffer).decode('utf-8')
        img_data_url = f"data:image/jpeg;base64,{jpg_as_text}"

        # Update the Flet image component
        webcam_image.src_base64 = img_data_url
        page.update()

    cap.release()
    cv2.destroyAllWindows()

def main(page: ft.Page):
    global running

    page.title = "Blink Detection Keyboard"
    page.vertical_alignment = ft.MainAxisAlignment.CENTER

    output_text = ft.Text(value=text, size=24)
    keyboard = ft.Row(wrap=True)
    for i in range(15):
        key = ft.Container(
            ft.Text(value=keys_set[i], size=24, color=ft.colors.RED),
            width=200,
            height=200,
            alignment=ft.alignment.center,
            bgcolor=ft.colors.BLUE
        )
        keyboard.controls.append(key)

    webcam_image = ft.Image()

    page.add(output_text, keyboard, webcam_image)

    threading.Thread(target=update_ui, args=(page, output_text, keyboard, webcam_image), daemon=True).start()
    threading.Thread(target=process_video, args=(page, webcam_image), daemon=True).start()

    def on_close(e):
        global running
        running = False
        logging.info("Application is closing...")

    page.on_close = on_close

if __name__ == "__main__":
    ft.app(target=main, view=ft.WEB_BROWSER)
