import tkinter as tk
from tkinter import ttk
from tkinter.font import Font
from PIL import Image, ImageTk  #pil 패키지 사용
import json
import os
from PyKakao import DaumSearch
import pandas as pd
import re

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Daum 검색")
        self.geometry("1100x700")
        self.resizable(False, False)

        self.search_term = tk.StringVar()
        self.service_key = ""  # 초기화

        self.create_widgets()
        
        # API 키 로드
        self.service_key = self.load_service_key()
        self.service_key = self.api_key_entry.get() #최초 실행 시 api_key에 key값이 들어있다면 해당 값을 불러와서 service_key 변수에 저장
        # Daum 검색 API 인스턴스 생성
        self.daum = DaumSearch(service_key=self.service_key)

    def create_widgets(self):
        search_frame = tk.Frame(self)
        search_frame.grid(row=0, column=0, pady=1, padx=1, sticky="ew")

        # 로고 이미지 로드 및 크기 조정
        logo_path = os.path.join('assets', 'img', 'Daum_logo.png')
        logo_image = Image.open(logo_path)
        resized_logo_image = logo_image.resize((100, 50), Image.Resampling.LANCZOS)  # 크기 조정
        logo_photo = ImageTk.PhotoImage(resized_logo_image)

        # 로고 이미지 레이블
        logo_label = tk.Label(search_frame, image=logo_photo)
        logo_label.image = logo_photo  # 참조 유지
        logo_label.grid(row=0, column=0, padx=(0, 10))

        tk.Label(search_frame, text="검색어:").grid(row=0, column=1)
        tk.Entry(search_frame, textvariable=self.search_term, width=50).grid(row=0, column=2)
        tk.Button(search_frame, text="검색", command=self.perform_search).grid(row=0, column=3)

        # Service Key Entry
        tk.Label(search_frame, text="API KEY:").grid(row=1, column=1)
        self.api_key_entry = tk.Entry(search_frame, width=50)
        self.api_key_entry.grid(row=1, column=2, padx=(0, 5))
        self.api_key_entry.insert(tk.END, self.service_key)

        # Load Button
        load_button = tk.Button(search_frame, text="Load", command=self.load_service_key)
        load_button.grid(row=1, column=3)

        # Save Button
        save_button = tk.Button(search_frame, text="Save", command=self.save_service_key)
        save_button.grid(row=1, column=4)

        # Delete Button
        delete_button = tk.Button(search_frame, text="Delete", command=self.delete_service_key)
        delete_button.grid(row=1, column=5)

        # 결과를 출력할 Table Type의 Display 추가
        self.notebook = ttk.Notebook(self)
        self.notebook.grid(row=2, column=0, sticky="nsew")
        self.notebook.grid_rowconfigure(0, weight=1)
        self.notebook.grid_columnconfigure(0, weight=1)
        self.notebook.bind("<Double-1>", self.open_url_in_browser)  #해당 행 더블 클릭 시 open_url_in_browser 함수 호출

        self.tabs = {}
        for idx, category in enumerate(["웹문서", "동영상", "이미지", "블로그", "책", "카페"]):
            frame = tk.Frame(self.notebook)
            self.tabs[category] = frame
            self.notebook.add(frame, text=category)

    def perform_search(self):
        term = self.search_term.get()
        if not term:
            return

        self.search_and_display(term, "웹문서", self.daum.search_web)
        self.search_and_display(term, "동영상", self.daum.search_vclip)
        self.search_and_display(term, "이미지", self.daum.search_image)
        self.search_and_display(term, "블로그", self.daum.search_blog)
        self.search_and_display(term, "책", self.daum.search_book)
        self.search_and_display(term, "카페", self.daum.search_cafe)

    def search_and_display(self, term, category, search_func):
        frame = self.tabs[category]

        for widget in frame.winfo_children():
            widget.destroy()

        df = search_func(term, dataframe=True)

        if df is not None and not df.empty:
        # <b> 태그 및 &#숫자 형식 제거
            def clean_text(text):
                if isinstance(text, str):
                    text = re.sub(r'<\/?b>', '', text)  # <b> 태그 제거
                    text = re.sub(r'&#\d+;', '', text)  # &#숫자 형식 제거
                return text

            for column in ['contents', 'title']:
                if column in df.columns:
                    df[column] = df[column].apply(clean_text)

            tree = ttk.Treeview(frame, columns=list(df.columns), show="headings")
            for col in df.columns:
                tree.heading(col, text=col)
                tree.column(col, width=Font().measure(col) + 10)

            for i, row in df.iterrows():
                tree.insert("", "end", values=list(row))

            tree.pack(fill='both', expand=True)
            tree.bind("<Double-1>", self.open_url_in_browser)
        else:
            label = tk.Label(frame, text="No results found.")
            label.pack(fill='both', expand=True)

    def load_service_key(self):
        try:
            with open('api_key.json', 'r') as f:
                service_key = json.load(f)['service_key']
        except (FileNotFoundError, KeyError, json.JSONDecodeError):
            service_key = ''
        self.api_key_entry.delete(0, tk.END)
        self.api_key_entry.insert(tk.END, service_key)
        self.service_key = service_key
        self.daum = DaumSearch(service_key=self.service_key)

    def save_service_key(self):
        service_key = self.api_key_entry.get()
        with open('api_key.json', 'w') as f:
            json.dump({'service_key': service_key}, f)
        self.service_key = service_key
        self.daum = DaumSearch(service_key=self.service_key)

    def delete_service_key(self):
        default_content = {"service_key": "YOUR_SERVICE_KEY_HERE"}
        with open('api_key.json', 'w') as f:
            json.dump(default_content, f)
        self.api_key_entry.delete(0, tk.END)
        self.service_key = "YOUR_SERVICE_KEY_HERE"
        self.daum = DaumSearch(service_key=self.service_key)
    
    def open_url_in_browser(self, event):
        # 현재 선택된 탭 인덱스 가져오기
        current_tab_index = self.notebook.index(self.notebook.select())
        category = list(self.tabs.keys())[current_tab_index]
        frame = self.tabs[category]

        # 현재 선택된 트리뷰(Treeview) 위젯 가져오기
        tree = frame.winfo_children()[0]

        # 선택된 아이템 확인
        selected_item = tree.selection()
        if selected_item:
            # 선택된 아이템의 값(튜플) 가져오기
            item_values = tree.item(selected_item, 'values')

            # URL 열의 인덱스 확인 후 URL 가져오기
            url_columns = ['url', 'doc_url']
            url = None
            for col in url_columns:
                if col in tree['columns']:
                    url_index = tree['columns'].index(col)
                    url = item_values[url_index]
                    break

            # URL이 있는 경우 웹 브라우저에서 열기
            if url:
                # 새로운 창 생성
                new_window = tk.Toplevel(self)
                new_window.title("Open URL")
                new_window.geometry("300x100")

                def open_in_browser():
                    import webbrowser
                    webbrowser.open_new(url)
                    new_window.destroy()

                # '웹 브라우저로 열기' 버튼
                open_button = tk.Button(new_window, text="웹 브라우저로 열기", command=open_in_browser)
                open_button.pack(pady=10)

                # '카톡 나에게 주소 보내기' 버튼 (구현은 사용자에 따라 추가 가능)
                send_button = tk.Button(new_window, text="카톡 나에게 주소 보내기")
                send_button.pack(pady=10)

if __name__ == "__main__":
    app = App()
    app.mainloop()
