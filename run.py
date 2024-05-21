import tkinter as tk
from tkinter import ttk
from tkinter.font import Font
import json
import os
from PyKakao import DaumSearch
import pandas as pd

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Daum 검색")
        self.geometry("800x600")

        self.search_term = tk.StringVar()
        self.service_key = self.load_service_key()
        
        # Daum 검색 API 인스턴스 생성
        self.daum = DaumSearch(service_key=self.service_key)

        self.create_widgets()

    def create_widgets(self):
        search_frame = tk.Frame(self)
        search_frame.pack(pady=10, padx=10, fill=tk.X)

        tk.Label(search_frame, text="Search:").pack(side=tk.LEFT)
        tk.Entry(search_frame, textvariable=self.search_term, width=50).pack(side=tk.LEFT)
        tk.Button(search_frame, text="Search", command=self.perform_search).pack(side=tk.LEFT)

        api_key_frame = tk.Frame(self)
        api_key_frame.pack(pady=10, padx=10, fill=tk.X)

        tk.Label(api_key_frame, text="Service Key:").pack(side=tk.LEFT)
        self.api_key_entry = tk.Entry(api_key_frame, width=50)
        self.api_key_entry.pack(side=tk.LEFT)
        self.api_key_entry.insert(tk.END, self.service_key)

        load_button = tk.Button(api_key_frame, text="Load", command=self.load_service_key)
        load_button.pack(side=tk.LEFT)

        save_button = tk.Button(api_key_frame, text="Save", command=self.save_service_key)
        save_button.pack(side=tk.LEFT)

        delete_button = tk.Button(api_key_frame, text="Delete", command=self.delete_service_key)
        delete_button.pack(side=tk.LEFT)

        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill='both', expand=True)

        self.tabs = {}
        for category in ["웹문서", "동영상", "이미지", "블로그", "책", "카페"]:
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
            tree = ttk.Treeview(frame, columns=list(df.columns), show="headings")
            for col in df.columns:
                tree.heading(col, text=col)
                tree.column(col, width=Font().measure(col) + 20)

            for i, row in df.iterrows():
                tree.insert("", "end", values=list(row))

            tree.pack(fill='both', expand=True)
        else:
            label = tk.Label(frame, text="No results found.")
            label.pack(fill='both', expand=True)

    def load_service_key(self):
        try:
            with open('api_key.json', 'r') as f:
                service_key = json.load(f)['service_key']
        except (FileNotFoundError, KeyError):
            service_key = ''
        return service_key

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

if __name__ == "__main__":
    app = App()
    app.mainloop()
