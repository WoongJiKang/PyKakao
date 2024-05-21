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
    query = entry.get("1.0", tk.END).strip()
    if query:
        search_results['웹문서'] = DAUM.search_web(query, dataframe=True)
        search_results['동영상'] = DAUM.search_vclip(query, dataframe=True)
        search_results['이미지'] = DAUM.search_image(query, dataframe=True)
        search_results['블로그'] = DAUM.search_blog(query, dataframe=True)
        search_results['책'] = DAUM.search_book(query, dataframe=True)
        search_results['카페'] = DAUM.search_cafe(query, dataframe=True)
        result_label.config(text="검색 완료! 카테고리 버튼을 눌러 결과를 확인하세요.")
        display_results('웹문서')

def display_results(category):
    for row in tree.get_children():
        tree.delete(row)
    
    if category in search_results:
        df = search_results[category]
        df = df.sort_values(by="datetime", ascending=False)  # 날짜 기준 내림차순 정렬
        for index, row in df.iterrows():
            title = row["title"]
            contents = row["contents"]
            datetime = row.get("datetime", "")  # datetime이 없을 경우 빈 문자열로 설정
            url = row["url"]
            tree.insert("", "end", values=(title, contents, datetime, url))

def on_treeview_click(event):
    item = tree.selection()[0]
    link = tree.item(item, "values")[3]
    webbrowser.open(link)

# GUI 초기 설정
root = tk.Tk()
root.title("Daum Search App")
root.configure(bg="lightgrey")  # 최상위 프레임 배경색 설정

# 제목 프레임
title_frame = tk.Frame(root, bg="lightgrey")
title_frame.pack(pady=10)

# 이미지 추가 및 크기 조정
image = Image.open(image_path)
image = image.resize((100, 100), Image.LANCZOS)  # 크기를 2배로 조정
search_icon = ImageTk.PhotoImage(image)

image_label = tk.Label(title_frame, image=search_icon, bg="lightgrey")
image_label.pack(side=tk.LEFT, padx=10)

# 제목 라벨
title_label = tk.Label(title_frame, text="Daum API 활용 검색기", font=("Arial", 18), bg="lightgrey", fg="black")
title_label.pack(side=tk.LEFT)

# 검색어 입력 부분
top_frame = tk.Frame(root, bg="lightgrey")
top_frame.pack(pady=10)

label = tk.Label(top_frame, text="Search:", font=("Arial", 12), bg="lightgrey", fg="black")
label.pack(side=tk.LEFT)

entry = tk.Text(top_frame, width=50, height=1, font=("Arial", 14))  # 입력칸의 크기 및 폰트 설정
entry.pack(side=tk.LEFT, padx=10)

search_button = tk.Button(top_frame, text="검색", command=search_daum, font=("Arial", 12))
search_button.pack(side=tk.LEFT)

# 검색 결과 상태 표시 라벨
result_label = tk.Label(root, text="", bg="lightgrey", fg="black")
result_label.pack(pady=10)

# 카테고리 버튼
button_frame = tk.Frame(root, bg="lightgrey")
button_frame.pack(anchor='w', padx=10, pady=5)

categories = ["웹문서", "동영상", "이미지", "블로그", "책", "카페"]
for category in categories:
    button = tk.Button(button_frame, text=category, command=lambda c=category: display_results(c), bg="lightblue", font=("Arial", 10))
    button.pack(side=tk.LEFT, padx=2)

# 검색 결과 표시 창
columns = ("title", "contents", "datetime", "url")
tree = ttk.Treeview(root, columns=columns, show="headings", height=20)  # 높이 조정
tree.heading("title", text="Title")
tree.heading("contents", text="Contents")
tree.heading("datetime", text="Datetime")
tree.heading("url", text="URL")

tree.pack(expand=True, fill='both', pady=10, padx=10)
tree.bind("<Double-1>", on_treeview_click)

# 스크롤바 추가
scrollbar = ttk.Scrollbar(root, orient="vertical", command=tree.yview)
scrollbar.pack(side='right', fill='y')
tree.configure(yscroll=scrollbar.set)

root.mainloop()
