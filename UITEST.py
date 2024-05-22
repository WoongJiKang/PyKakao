import os
import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
from PyKakao import DaumSearch
import webbrowser

# 현재 파일의 디렉토리 경로 얻기
current_directory = os.path.dirname(os.path.abspath(__file__))
image_path = os.path.join(current_directory, "example.png")

# Daum 검색 API 인스턴스 생성
API_KEY = ''
DAUM = DaumSearch(service_key=API_KEY)

# 검색 결과 저장용 변수
search_results = {}

def search_daum():
    query = search_entry.get("1.0", tk.END).strip()
    if query:
        search_results['웹문서'] = DAUM.search_web(query, dataframe=True)
        search_results['동영상'] = DAUM.search_vclip(query, dataframe=True)
        search_results['이미지'] = DAUM.search_image(query, dataframe=True)
        search_results['블로그'] = DAUM.search_blog(query, dataframe=True)
        search_results['책'] = DAUM.search_book(query, dataframe=True)
        search_results['카페'] = DAUM.search_cafe(query, dataframe=True)
        search_result_label.config(text="검색 완료! 카테고리 버튼을 눌러 결과를 확인하세요.")
        display_results('웹문서')

def display_results(category):
    for row in search_tree.get_children():
        search_tree.delete(row)
    
    if category in search_results:
        df = search_results[category]
        df = df.sort_values(by="datetime", ascending=False)  # 날짜 기준 내림차순 정렬
        for index, row in df.iterrows():
            title = row["title"]
            contents = row["contents"]
            datetime = row.get("datetime", "")  # datetime이 없을 경우 빈 문자열로 설정
            url = row["url"]
            search_tree.insert("", "end", values=(title, contents, datetime, url))

def on_treeview_click(event):
    item = search_tree.selection()[0]
    link = search_tree.item(item, "values")[3]
    webbrowser.open(link)

def show_frame(frame):
    frame.tkraise()

# GUI 초기 설정
root = tk.Tk()
root.title("Multi-Function Test App")
root.geometry("800x600")

# 컨테이너 프레임 설정
container = tk.Frame(root)
container.pack(side="top", fill="both", expand=True)

# 모든 프레임 리스트
frames = {}

class StartPage(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller
        label = tk.Label(self, text="Multi-Function Test App", font=("Arial", 18))
        label.pack(pady=10)
        
        search_button = tk.Button(self, text="Search", command=lambda: show_frame(frames["SearchPage"]))
        search_button.pack(pady=10)
        
        other_button = tk.Button(self, text="Other Function", command=lambda: show_frame(frames["OtherPage"]))
        other_button.pack(pady=10)

class SearchPage(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller
        
        title_frame = tk.Frame(self)
        title_frame.pack(pady=10)
        
        image = Image.open(image_path)
        image = image.resize((100, 100), Image.LANCZOS)
        search_icon = ImageTk.PhotoImage(image)
        
        image_label = tk.Label(title_frame, image=search_icon)
        image_label.image = search_icon
        image_label.pack(side=tk.LEFT, padx=10)
        
        title_label = tk.Label(title_frame, text="api활용 검색기", font=("Arial", 18))
        title_label.pack(side=tk.LEFT)
        
        top_frame = tk.Frame(self)
        top_frame.pack(pady=10)
        
        label = tk.Label(top_frame, text="Search:", font=("Arial", 12))
        label.pack(side=tk.LEFT)
        
        global search_entry
        search_entry = tk.Text(top_frame, width=50, height=1, font=("Arial", 14))
        search_entry.pack(side=tk.LEFT, padx=10)
        
        search_button = tk.Button(top_frame, text="검색", command=search_daum, font=("Arial", 12))
        search_button.pack(side=tk.LEFT)

        back_button = tk.Button(top_frame, text="Back", command=lambda: show_frame(frames["StartPage"]), font=("Arial", 12))
        back_button.pack(side=tk.LEFT, padx=10)

        global search_result_label
        search_result_label = tk.Label(self, text="")
        search_result_label.pack(pady=10)
        
        button_frame = tk.Frame(self)
        button_frame.pack(anchor='w', padx=10, pady=5)
        
        categories = ["웹문서", "동영상", "이미지", "블로그", "책", "카페"]
        for category in categories:
            button = tk.Button(button_frame, text=category, command=lambda c=category: display_results(c), bg="lightblue", font=("Arial", 10))
            button.pack(side=tk.LEFT, padx=2)
        
        columns = ("title", "contents", "datetime", "url")
        global search_tree
        search_tree = ttk.Treeview(self, columns=columns, show="headings", height=20)
        search_tree.heading("title", text="Title")
        search_tree.heading("contents", text="Contents")
        search_tree.heading("datetime", text="Datetime")
        search_tree.heading("url", text="URL")
        
        search_tree.pack(expand=True, fill='both', pady=10, padx=10)
        search_tree.bind("<Double-1>", on_treeview_click)
        
        scrollbar = ttk.Scrollbar(self, orient="vertical", command=search_tree.yview)
        scrollbar.pack(side='right', fill='y')
        search_tree.configure(yscroll=scrollbar.set)

class OtherPage(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller
        
        label = tk.Label(self, text="Other Function", font=("Arial", 18))
        label.pack(pady=10)
        
        back_button = tk.Button(self, text="Back", command=lambda: show_frame(frames["StartPage"]), font=("Arial", 12))
        back_button.pack(anchor='w', padx=10, pady=10)

# 프레임 초기화 및 설정
frames["StartPage"] = StartPage(container, root)
frames["SearchPage"] = SearchPage(container, root)
frames["OtherPage"] = OtherPage(container, root)

frames["StartPage"].grid(row=0, column=0, sticky="nsew")
frames["SearchPage"].grid(row=0, column=0, sticky="nsew")
frames["OtherPage"].grid(row=0, column=0, sticky="nsew")

# 초기 프레임 설정
show_frame(frames["StartPage"])

root.mainloop()
