import tkinter as tk
from tkinter import ttk
from tkinter.font import Font
from PIL import Image, ImageTk  #pil 패키지 사용
import json
import os
from PyKakao import DaumSearch
from PyKakao import KoGPT
import pandas as pd
import re
from datetime import datetime  # datetime 모듈 임포트

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Daum 검색")
        self.geometry("1500x700")
        self.resizable(False, False)

        self.search_term = tk.StringVar()
        self.service_key = ""  # 초기화

        self.create_widgets()
        
        # API 키 로드
        self.service_key = self.load_service_key()
        self.service_key = self.api_key_entry.get() #최초 실행 시 api_key에 key값이 들어있다면 해당 값을 불러와서 service_key 변수에 저장
        # Daum 검색 API 인스턴스 생성
        self.daum = DaumSearch(service_key=self.service_key)
        # KoGPT API 인스턴스 생성
        self.gpt = KoGPT(service_key=self.service_key)

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

        # notebook_frame 생성
        notebook_frame = tk.Frame(self)
        notebook_frame.grid(row=1, column=0, sticky="nsew")
        notebook_frame.grid_rowconfigure(0, weight=1)
        notebook_frame.grid_columnconfigure(0, weight=1)

        # 결과를 출력할 Table Type의 Display 추가
        self.notebook = ttk.Notebook(notebook_frame)
        self.notebook.pack(expand=True, fill='both')
        self.notebook.bind("<Double-1>", self.open_url_in_browser)  # 해당 행 더블 클릭 시 open_url_in_browser 함수 호출

        self.tabs = {}
        for idx, category in enumerate(["웹문서", "동영상", "이미지", "블로그", "책", "카페"]):
            frame = tk.Frame(self.notebook)
            self.tabs[category] = frame
            self.notebook.add(frame, text=category)

        # gpt_frame 생성
        gpt_frame = tk.Frame(self)
        gpt_frame.grid(row=1, column=1, pady=5)

        # KoGPT Label
        self.gpt_result_label = tk.Label(gpt_frame, text="KoGPT")
        self.gpt_result_label.grid(row=0, column=0)

        # KoGPT 결과를 출력할 Text widget
        self.gpt_result_text = tk.Text(gpt_frame, wrap=tk.WORD, height=10, width=80, state=tk.DISABLED)
        self.gpt_result_text.grid(row=1, column=0, pady=5, padx=10, sticky="nsew")

        # KoGPT 질문 Label
        self.gpt_prompt_label = tk.Label(gpt_frame, text="질문 입력")
        self.gpt_prompt_label.grid(row=2, column=0)

        # KoGPT 질문 입력 Entry
        self.gpt_prompt_entry = tk.Entry(gpt_frame, width=50)
        self.gpt_prompt_entry.grid(row=3, column=0, pady=5, padx=10)

        # KoGPT 결과 출력 Button
        self.gpt_generate_button = tk.Button(gpt_frame, text="전송", command=self.generate_response)
        self.gpt_generate_button.grid(row=3, column=1, pady=5, padx=5, sticky="w")

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

        # KoGPT에 검색어 전달하여 결과 생성
        self.generate_response(term)

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
                if col == 'datetime':  # datetime 컬럼에만 정렬 이벤트 바인딩
                    tree.heading(col, text=col, command=lambda _col=col: self.sort_column(tree, _col, False))
                else:
                    tree.heading(col, text=col)  # 다른 컬럼은 정렬 이벤트 없음
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
    
    def sort_column(self, tree, col, reverse):
        # 모든 아이템을 가져와서 정렬
        l = [(tree.set(k, col), k) for k in tree.get_children('')]
        
        # 날짜 열인 경우 datetime으로 변환하여 정렬
        if col == 'datetime':
            try:
                l.sort(key=lambda t: datetime.fromisoformat(t[0]), reverse=reverse)
            except ValueError:
                l.sort(reverse=reverse)
        else:
            l.sort(reverse=reverse)

        # 정렬된 순서대로 아이템을 재배치
        for index, (val, k) in enumerate(l):
            tree.move(k, '', index)

        # 다음 번 클릭 때는 반대 방향으로 정렬되도록 설정
        tree.heading(col, command=lambda: self.sort_column(tree, col, not reverse))

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

                # '카톡 나에게 주소 보내기' 버튼 (미구현)
                send_button = tk.Button(new_window, text="카톡 나에게 주소 보내기")
                send_button.pack(pady=10)

    def generate_response(self, term):
        # 입력 받은 검색어 가져오기
        term = self.search_term.get()

        # 검색어 엔트리에 입력 받은 prompt 가져오기
        prompt = term

        # KoGPT로 다음 문장 생성
        max_tokens = 128
        result = self.gpt.generate(prompt, max_tokens, temperature=0.7, top_p=0.8)
        
        # GPT 답변에 대한 헤더 텍스트
        prompt_result = "["+ prompt +"]" + "[질문에 대한 답변]\n"

        # 결과 출력
        filtered_result = self.filter_result(result)

        # 결과 출력
        self.gpt_result_text.config(state=tk.NORMAL)  # 텍스트 박스 활성화
        
        self.gpt_result_text.insert(tk.END, prompt_result)
        self.gpt_result_text.insert(tk.END, filtered_result)
        self.gpt_result_text.insert(tk.END, '\n')
        self.gpt_result_text.config(state=tk.DISABLED)  # 텍스트 박스 읽기 전용으로 다시 설정

    def filter_result(self, result):
        # 결과 필터링
        excluded_chars = ['[', ']', '{', '}', "'"]
        excluded_keys = ['id', 'tokens', 'usage', 'prompt_tokens', 'generated_tokens', 'total_tokens']
        filtered_result = {}  # 필터링된 결과를 저장할 빈 사전 생성
        for key, value in result.items():
            if key not in excluded_keys:  # 제외할 키가 아닌 경우에만 결과에 추가
                if key == 'generations':
                    # 'generations' 키의 값이 리스트인 경우에만 처리
                    if isinstance(value, list):
                        # 각 요소에서 'text' 키에 해당하는 값을 가져와서 리스트로 저장
                        text_values = [generation['text'] for generation in value if 'text' in generation]
                        # 리스트가 비어있지 않은 경우에만 결과에 추가
                        if text_values:
                            filtered_result[key] = text_values
                else:
                    filtered_result[key] = value

        # 문자 제거 및 HTML 태그 제거
        for char in excluded_chars:
            filtered_result = str(filtered_result).replace(char, '')
        
        # HTML 태그 제거
        filtered_result = self.remove_html_tags(filtered_result)

        return filtered_result

    def remove_html_tags(self, text):
        # 문자열에서 HTML 태그와 이스케이프 문자 제거
        clean = re.compile(r'<.*?>|\\u200b|\\')
        return re.sub(clean, '', text)

if __name__ == "__main__":
    app = App()
    app.mainloop()
