import flet as ft
import cv2
import numpy as np
from cvzone.FaceMeshModule import FaceMeshDetector
from math import hypot
import threading
import time

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

def update_ui(page, output_text, keyboard):
    global running, text, letter_index
    while running:
        time.sleep(0.1)
        output_text.value = text
        for i in range(15):
            key_text = current_set[i]
            keyboard.controls[i].content.value = key_text  # Update the key text
            if i == letter_index:
                keyboard.controls[i].bgcolor = ft.colors.WHITE
            else:
                keyboard.controls[i].bgcolor = ft.colors.BLUE
        page.update()

def process_video():
    global frames, blink_frame, letter_index, text, current_set, running
    cap = cv2.VideoCapture(0)
    detector = FaceMeshDetector(maxFaces=1, minDetectionCon=0.8)

    while running:
        success, img = cap.read()
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

                if active_letter == "I":
                    pass
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

    cap.release()

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

    page.add(output_text, keyboard)

    threading.Thread(target=update_ui, args=(page, output_text, keyboard), daemon=True).start()
    threading.Thread(target=process_video, daemon=True).start()

    def on_close(e):
        global running
        running = False

    page.on_close = on_close

if __name__ == "__main__":
    ft.app(target=main, view=ft.WEB_BROWSER)
