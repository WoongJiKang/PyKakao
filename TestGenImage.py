import tkinter as tk
from tkinter import messagebox
from tkinter import Label
from PIL import Image, ImageTk
import io
import base64
from PyKakao import Karlo

def generate_and_display_image():
    service_key = "Key"  
    api = Karlo(service_key=service_key)
    text = "Cute magical flying cat, soft golden fur, fantasy art drawn by Pixar concept artist, Toy Story main character, clear and bright eyes, sharp nose"

    try:
        # 이미지 생성
        img_dict = api.text_to_image(text, 1)
        if "images" not in img_dict or not img_dict["images"]:
            raise ValueError("API 응답에 이미지가 없습니다")
        img_str = img_dict["images"][0].get('image')
        if not img_str:
            raise ValueError("API 응답에 이미지 데이터가 없습니다")

        img_data = base64.b64decode(img_str)
        img = Image.open(io.BytesIO(img_data)).convert('RGBA')
        img.save("./original.png")

        img_tk = ImageTk.PhotoImage(img)
        img_label.config(image=img_tk)
        img_label.image = img_tk

        messagebox.showinfo("성공", "이미지가 생성되어 original.png로 저장되었습니다.")
    except Exception as e:
        messagebox.showerror("오류", f"오류가 발생했습니다: {str(e)}")

root = tk.Tk()
root.title("Karlo API 이미지 생성기")

generate_button = tk.Button(root, text="이미지 생성", command=generate_and_display_image)
generate_button.grid(row=0, column=0, padx=20, pady=20)

img_label = Label(root)
img_label.grid(row=1, column=0, padx=20, pady=20)

root.mainloop()
