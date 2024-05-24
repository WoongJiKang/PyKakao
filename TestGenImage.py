import tkinter as tk
from tkinter import messagebox
from PyKakao import Karlo
from PIL import Image
import io
import base64

def generate_image():
    service_key = service_key_entry.get()
    if not service_key:
        messagebox.showwarning("경고", "서비스 키를 입력하세요.")
        return

    api = Karlo(service_key=service_key)
    text = "Cute magical flying cat, soft golden fur, fantasy art drawn by Pixar concept artist, Toy Story main character, clear and bright eyes, sharp nose"

    try:
        img_dict = api.text_to_image(text, 1)
        img_str = img_dict.get("images")[0].get('image')

        img_data = base64.b64decode(img_str)
        img = Image.open(io.BytesIO(img_data)).convert('RGBA')
        img.save("./original.png")

        messagebox.showinfo("성공", "이미지가 생성되어 original.png로 저장되었습니다.")
    except Exception as e:
        messagebox.showerror("오류","오류가 발생했습니다: {e}")

root = tk.Tk()
root.title("Karlo API 이미지 생성기")

tk.Label(root, text="서비스 키:").grid(row=0, column=0, padx=10, pady=10)
service_key_entry = tk.Entry(root, width=50)
service_key_entry.grid(row=0, column=1, padx=10, pady=10)

generate_button = tk.Button(root, text="이미지 생성", command=generate_image)
generate_button.grid(row=1, columnspan=2, pady=20)

root.mainloop()
