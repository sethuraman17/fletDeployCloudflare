import os
import flet as ft
import cv2
import threading
import base64
from io import BytesIO
from PIL import Image

def encode_frame(frame):
    _, buffer = cv2.imencode('.jpg', frame)
    jpg_as_text = base64.b64encode(buffer).decode('utf-8')
    return jpg_as_text

def capture_frames(frame_queue):
    cap = cv2.VideoCapture(0)
    while cap.isOpened():
        ret, frame = cap.read()
        if ret:
            frame_queue.append(frame)
        if len(frame_queue) > 1:
            frame_queue.pop(0)

def update_image(image_widget, frame_queue):
    while True:
        if frame_queue:
            frame = frame_queue[0]
            encoded_frame = encode_frame(frame)
            image_widget.src_base64 = f'data:image/jpeg;base64,{encoded_frame}'
            image_widget.update()
        else:
            continue

def main(page: ft.Page):
    frame_queue = []

    capture_thread = threading.Thread(target=capture_frames, args=(frame_queue,))
    capture_thread.daemon = True
    capture_thread.start()

    image_widget = ft.Image(src_base64='')

    update_thread = threading.Thread(target=update_image, args=(image_widget, frame_queue))
    update_thread.daemon = True
    update_thread.start()

    page.add(image_widget)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    ft.app(target=main, port=port, view=ft.WEB_BROWSER)
