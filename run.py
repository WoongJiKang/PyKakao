import tkinter as tk  # Tkinter 모듈을 tk로 별칭(alias)하여 임포트합니다.
from tkinter import ttk  # Tkinter의 themed 위젯을 임포트합니다.
from tkinter.font import Font  # Tkinter의 폰트 관련 기능을 임포트합니다.
from PIL import Image, ImageTk  # PIL 패키지의 Image 모듈을 임포트하여 이미지 처리에 사용합니다.
import json  # JSON 데이터 형식을 처리하기 위한 모듈입니다.
import os  # 운영체제와 상호 작용하기 위한 모듈입니다.
from PyKakao import DaumSearch  # PyKakao 패키지에서 DaumSearch 클래스를 임포트합니다.
from PyKakao import KoGPT  # PyKakao 패키지에서 KoGPT 클래스를 임포트합니다.
import pandas as pd  # 데이터 분석 및 조작을 위한 패키지인 pandas를 임포트합니다.
import re  # 정규 표현식을 사용하기 위한 모듈입니다.
from datetime import datetime  # datetime 모듈에서 datetime 클래스를 임포트합니다. 이는 날짜 및 시간을 다루는 데 사용됩니다.
from PyKakao import Message # PyKakao 패키지에서 Message 클래스를 임포트합니다.

class App(tk.Tk):
    def __init__(self):
        # 생성자
        super().__init__()
        self.title("PyKakao 검색엔진")
        self.geometry("1500x700")
        self.resizable(False, False)

        self.search_term = tk.StringVar()
        self.service_key = ""  # 초기화

        self.notebook_visible = False
        self.gpt_frame_visible = False

        self.create_widgets()
        
        # API 키 로드
        self.service_key = self.load_service_key()
        self.service_key = self.api_key_entry.get() #최초 실행 시 api_key에 key값이 들어있다면 해당 값을 불러와서 service_key 변수에 저장
        # Daum 검색 API 인스턴스 생성
        self.daum = DaumSearch(service_key=self.service_key)
        # KoGPT API 인스턴스 생성
        self.gpt = KoGPT(service_key=self.service_key)

    def create_widgets(self):
        # 검색 프레임 생성
        search_frame = tk.Frame(self)
        search_frame.grid(row=0, column=0, pady=1, sticky="ew")

        # 로고 이미지 로드 및 크기 조정
        logo_path = os.path.join('assets', 'img', 'logo.png')
        logo_image = Image.open(logo_path)
        resized_logo_image = logo_image.resize((200, 90), Image.Resampling.LANCZOS)  # 크기 조정
        logo_photo = ImageTk.PhotoImage(resized_logo_image)

        # 로고 이미지 Frame, Label
        logo_frame = tk.Frame(search_frame)
        logo_frame.grid(row=0, column=0, pady=1, padx=1, sticky="w")
        logo_label = tk.Label(logo_frame, image=logo_photo)
        logo_label.image = logo_photo  # 참조 유지
        logo_label.grid(row=0, column=0)

        insert_frame = tk.Frame(search_frame)
        insert_frame.grid(row=0, column=1, pady=1, sticky="ew")
        tk.Label(insert_frame, text="검색어:").grid(row=0, column=1)
        tk.Entry(insert_frame, textvariable=self.search_term, width=50).grid(row=0, column=2)
        tk.Button(insert_frame, text="검색", command=self.perform_search).grid(row=0, column=3)
        tk.Button(insert_frame, text="도움말", command=self.information).grid(row=0, column=4)

        # Service Key Entry
        tk.Label(insert_frame, text="API KEY:").grid(row=1, column=1)
        self.api_key_entry = tk.Entry(insert_frame, width=50)
        self.api_key_entry.grid(row=1, column=2, padx=(0, 5))
        self.api_key_entry.insert(tk.END, self.service_key)

        # Load Button
        load_button = tk.Button(insert_frame, text="Load", command=self.load_service_key)
        load_button.grid(row=1, column=3)

        # Save Button
        save_button = tk.Button(insert_frame, text="Save", command=self.save_service_key)
        save_button.grid(row=1, column=4)

        # Delete Button
        delete_button = tk.Button(insert_frame, text="Delete", command=self.delete_service_key)
        delete_button.grid(row=1, column=5)

        # toggle_frame 생성
        toggle_frame = tk.Frame(search_frame)
        toggle_frame.grid(row=1, column=0, sticky="w")
        self.toggle_search_frame_button = tk.Button(toggle_frame, text="다음 검색 열기", command=self.toggle_search_frame)
        self.toggle_search_frame_button.grid(row=0, column=0, padx=5)

        self.toggle_gpt_frame_button = tk.Button(toggle_frame, text="KoGPT 검색 열기", command=self.toggle_gpt_frame)
        self.toggle_gpt_frame_button.grid(row=0, column=1)

        # 엔진 프레임 생성
        engine_frame = tk.Frame(self)
        engine_frame.grid(row=2, column=0, sticky="nsew")
        

        # notebook_frame 생성
        notebook_frame = tk.Frame(engine_frame)
        notebook_frame.grid(row=0, column=0, sticky="nsew")
        

        # 결과를 출력할 Table Type의 Display 추가
        self.notebook = ttk.Notebook(notebook_frame)
        self.notebook.pack(expand=True, fill='both')
        self.notebook.bind("<Double-1>", self.open_url_in_browser)  # 해당 행 더블 클릭 시 open_url_in_browser 함수 호출

        # Daum 검색 카테고리
        self.tabs = {}
        for idx, category in enumerate(["웹문서", "동영상", "이미지", "블로그", "책", "카페"]):
            frame = tk.Frame(self.notebook)
            self.tabs[category] = frame
            self.notebook.add(frame, text=category)

        # gpt_frame 생성
        gpt_frame = tk.Frame(engine_frame)
        gpt_frame.grid(row=0, column=1, padx=5, sticky="nsew")

        # KoGPT Label
        self.gpt_result_label = tk.Label(gpt_frame, text="KoGPT", bg="yellow", width=80)
        self.gpt_result_label.grid(row=0, column=0, columnspan=1, sticky="ew")

        # KoGPT 결과를 출력할 Text widget
        self.gpt_result_text = tk.Text(gpt_frame, wrap=tk.WORD, height=10, width=80, state=tk.DISABLED, bg="darkgray", fg="white")
        self.gpt_result_text.grid(row=1, column=0, pady=5, padx=10, sticky="nsew")

        # gpt_prompt_frame 생성
        gpt_prompt_frame = tk.Frame(gpt_frame)
        gpt_prompt_frame.grid(row=2, column=0, pady=5)

        # KoGPT 질문 Label
        self.gpt_prompt_label = tk.Label(gpt_prompt_frame, text="질문 입력:")
        self.gpt_prompt_label.grid(row=0, column=0)

        # KoGPT 질문 입력 Entry
        self.gpt_prompt_entry = tk.Entry(gpt_prompt_frame, width=50)
        self.gpt_prompt_entry.grid(row=0, column=1, pady=5, padx=10)

        # KoGPT 결과 출력 Button
        self.gpt_generate_button = tk.Button(gpt_prompt_frame, text="전송", command=self.generate_response)
        self.gpt_generate_button.grid(row=0, column=2, pady=5, padx=5, sticky="w")

        # notebook_frame과 gpt_frame 초기화 시 숨기기
        self.notebook.pack_forget()
        self.gpt_result_label.grid_remove()
        self.gpt_result_text.grid_remove()
        self.gpt_prompt_label.grid_remove()
        self.gpt_prompt_entry.grid_remove()
        self.gpt_generate_button.grid_remove()
    def information(self):
        info_window = tk.Toplevel(self)
        info_window.title("도움말")
        
        info_text = (
            "PyKakao Search_Engine\n"
            "PyKakao 원작자 : Woo il Jeong\n"
            "라이센스 : MIT License\n\n"
            "REST API 키 발급 방법\n\n"
            "PyKakao 라이브러리로 카카오 API를 사용하기 위해서는 Kakao Developers에 가입해야 합니다.\n"
            "가입 후 로그인한 상태에서 상단 메뉴의 내 애플리케이션을 선택합니다.\n"
            "'애플리케이션 추가하기'를 눌러 팝업창이 뜨면 '앱 이름', '사업자명'을 입력하고, "
            "운영정책에 동의 후 '저장'을 선택합니다.\n"
            "추가한 애플리케이션을 선택하면 '앱 키' 아래에 'REST API 키'가 생성된 것을 확인할 수 있습니다.\n\n"
            "API_KEY 관련 도움말\n\n"
            "Load : api_key.json에 저장된 API 키 값을 API 키 입력란에 붙여넣습니다.\n"
            "Save : API 키 입력란에 입력된 API 값을 api_key.json에 저장합니다.\n"
            "Delete : api_key.json을 기본값으로 되돌리고, API 키 입력란을 초기화합니다.\n\n"
            "Daum 검색 관련 도움말\n\n"
            "최초 실행 : API KEY 입력 -> Save -> 검색어 입력란에 검색어 입력 -> 검색\n"
            "(API KEY를 입력한 기록이 있는 경우 자동으로 API 키 값을 불러옵니다. Save누르지 않아도 됌)\n"
            "각 탭 별로 검색 기록이 표 형식으로 저장되고, 표에서 datetime 클릭 시 시간 순서대로 "
            "행 전체를 오름차순, 내림차순 정렬합니다.\n"
            "임의의 행 더블 클릭 시 해당 검색기록에 대한 URL을 이용해 해당 사이트에 접속하거나 "
            "카카오톡 나에게 링크 보내기 기능을 수행할 수 있는 창이 생성됩니다.\n\n"
            "KoGPT 검색 관련 도움말\n\n"
            "검색어 입력 후 검색을 누르면 검색어를 KoGPT에 질문합니다.\n"
            "KoGPT기능은 토큰값에 따라 답변 형식이 달라지는데 KoGPT는 GPT3 기반으로 "
            "다른 답변 형식들은 입력값과 유사하지 못한 답변이 발생하여\n"
            "그나마 유사한 응답이 가능한 질문&응답 토큰인 128을 기본값으로 지정하였습니다.\n"
            "검색어가 마음에 들지 않는 경우 '질문 입력:' 란을 이용하여 추가 질문 가능합니다."
        )

        tk.Label(info_window, text=info_text, justify=tk.LEFT, padx=10, pady=10).pack()

        button_frame = tk.Frame(info_window)
        button_frame.pack(pady=10)
        import webbrowser
        tk.Button(button_frame, text="MIT License", command=lambda: webbrowser.open("https://github.com/WoongJiKang/PyKakao/blob/main/LICENSE")).grid(row=0, column=0, padx=5)
        tk.Button(button_frame, text="PyKakao", command=lambda: webbrowser.open("https://github.com/WooilJeong/PyKakao")).grid(row=0, column=1, padx=5)
        tk.Button(button_frame, text="Kakao Developers", command=lambda: webbrowser.open("https://developers.kakao.com/")).grid(row=0, column=2, padx=5)
    def perform_search(self):
        # 입력받은 검색어을 검색엔진에 적용 후 실행
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
        # 카테고리 별로 검색어에 따른 검색결과 출력
        frame = self.tabs[category]  # 해당 카테고리의 프레임을 가져옵니다.

        for widget in frame.winfo_children():
            widget.destroy()  # 프레임 내의 모든 위젯을 제거합니다.

        # 검색 함수를 사용하여 데이터프레임을 가져옵니다.
        df = search_func(term, dataframe=True)

        if df is not None and not df.empty:  # 데이터프레임이 비어있지 않은 경우
            def clean_text(text):
                # 텍스트를 정리하여 반환하는 함수입니다.
                if isinstance(text, str):
                    text = re.sub(r'<\/?b>', '', text)  # <b> 태그 제거
                    text = re.sub(r'&#\d+;', '', text)  # &#숫자 형식 제거
                return text

            for column in ['contents', 'title']:
                if column in df.columns:
                    df[column] = df[column].apply(clean_text)  # 'contents'와 'title' 열의 불필요한 태그를 정리합니다.

            # 결과를 표시할 Treeview 위젯을 생성합니다.
            tree = ttk.Treeview(frame, columns=list(df.columns), show="headings")
            for col in df.columns:
                if col == 'datetime':  # datetime 컬럼에만 정렬 이벤트 바인딩
                    tree.heading(col, text=col, command=lambda _col=col: self.sort_column(tree, _col, False))
                else:
                    tree.heading(col, text=col)  # 다른 컬럼은 정렬 이벤트 없음
                tree.column(col, width=Font().measure(col) + 10)  # 각 열의 너비를 설정합니다.

            for i, row in df.iterrows():  # 데이터프레임의 각 행을 반복하며 Treeview에 추가합니다.
                tree.insert("", "end", values=list(row))

            tree.pack(fill='both', expand=True)  # Treeview를 프레임에 팩하여 표시합니다.
            tree.bind("<Double-1>", self.open_url_in_browser)  # 더블 클릭 이벤트에 함수를 바인딩합니다.
        else:
            # 검색 결과가 없는 경우 메시지를 표시합니다.
            label = tk.Label(frame, text="No results found.")
            label.pack(fill='both', expand=True)

    def load_service_key(self):
        # api_key_entry 입력란에 api_key.json 파일의 service_key 값으로 덮어쓰기
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
        # api_key 값을 api_key_entry에 적힌 내용으로 저장
        service_key = self.api_key_entry.get()
        with open('api_key.json', 'w') as f:
            json.dump({'service_key': service_key}, f)
        self.service_key = service_key
        self.daum = DaumSearch(service_key=self.service_key)

    def delete_service_key(self):
        # api_key 초기값으로 초기화 후 api_key_entry 공백으로 변경
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

            def show_kakao_frame():
                kakao_frame.pack(side="top", pady=10)

            def go_kakao_dev():
                kakao_dev_url = "https://developers.kakao.com/"
                import webbrowser
                webbrowser.open_new(kakao_dev_url)

            def send_auth_url():
                # 메시지 API 인스턴스 생성
                MSG = Message(service_key=self.service_key)

                # 카카오 인증코드 발급 URL 생성
                auth_url = MSG.get_url_for_generating_code()
                import webbrowser
                webbrowser.open_new(auth_url)

            # URL이 있는 경우 웹 브라우저에서 열기
            if url:
                # 새로운 창 생성
                url_window = tk.Toplevel(self)
                url_window.title("Open URL")
                url_window.geometry("600x500")
                url_window.resizable(False, False)

                def open_in_browser():
                    import webbrowser
                    webbrowser.open_new(url)
                    url_window.destroy()

                url_frame = tk.Frame(url_window)
                url_frame.pack(side="top", pady=10)
                # '웹 브라우저로 열기' 버튼
                open_button = tk.Button(url_frame, text="웹 브라우저로 열기", command=open_in_browser)
                open_button.pack(side="left")

                # '카톡 나에게 주소 보내기' 버튼
                open_kakao_button = tk.Button(url_frame, text="카톡 나에게 주소 보내기", command=show_kakao_frame)
                open_kakao_button.pack(side="left")

                # '카톡 나에게 주소 보내기' 프레임 생성 (기본값으로 보이지 않게 설정)
                kakao_frame = tk.Frame(url_window)
                # 초기에는 프레임을 보이지 않게 설정
                kakao_frame.pack_forget()
                kakao_option_frame = tk.Frame(kakao_frame)
                kakao_option_frame.pack(side="top", pady=1)
                kakao_dev_button = tk.Button(kakao_option_frame, text="카카오 디벨로퍼 이동", command=go_kakao_dev)
                kakao_dev_button.pack(side="left")
                kakao_auth_button = tk.Button(kakao_option_frame, text="카카오 인증코드 발급", command=send_auth_url)
                kakao_auth_button.pack(side="left")
                kakao_guide_frame = tk.Frame(kakao_frame)
                kakao_guide_frame.pack(side="top", pady=1)
                url_label = tk.Label(kakao_guide_frame, text="발급 버튼 누른 후 열린 사이트의 전체 URL")
                url_label.pack(side="left", fill='both')
                kakao_add_frame = tk.Frame(kakao_frame)
                kakao_add_frame.pack(side="top", pady=1)
                url_label2 = tk.Label(kakao_add_frame, text="URL:")
                url_label2.pack(side="left", fill='both')
                url_entry2 = tk.Entry(kakao_add_frame, width=30)
                url_entry2.pack(side="left", fill='both')
                kakao_guide2_frame = tk.Frame(kakao_frame)
                kakao_guide2_frame.pack(side="top", pady=1)

                lines = [
                    "!! 로그인 기능을 통한 엑세스 토큰 추출을 위해 다음 과정을 반드시 진행해주세요 !!",
                    "!! 일회성 토큰으로 중복 아이디로 재전송시 10번부터 다시 진행해주세요!  !!"
                ]
                for line in lines:
                    kakao_guide_label = tk.Label(kakao_guide2_frame, text=line, fg="red")
                    kakao_guide_label.pack(expand=True, fill='both')

                lines2 = [
                    "1. '카카오 디벨로퍼' 이동 버튼 클릭",
                    "2. 내 애플리케이션 선택 후 위에서 생성한 애플리케이션 선택",
                    "3. 내비게이션 메뉴에서 카카오 로그인 클릭 후 활성화 설정의 상태 버튼(OFF)을 클릭",
                    "4. 팝업 창에서 활성화 버튼 클릭",
                    "5. 카카오 로그인 화면 하단의 Redirect URI 등록 버튼 클릭",
                    "6. 팝업 창에서 Redirect URI 항목에 로컬 주소인 'https://localhost:5000' 입력 후 저장 버튼 클릭",
                    "7. 내비게이션 메뉴에서 카카오 로그인 하위의 동의항목을 클릭",
                    "8. 페이지 하단의 접근권한 이동 후 카카오톡 메시지 전송의 설정 클릭",
                    "9. 동의 단계를 이용 중 동의로 선택하고 동의 목적 작성 후 저장 버튼 클릭",
                    "10. '카카오 인증코드 발급' 클릭",
                    "최초 실행한 경우 모든 권한 동의 체크 후 '동의하고 계속하기' 클릭",
                    "11. 웹사이트 상단의 URL 주소를 모두 복사 후 URL: 입력란에 붙여넣고, '전송'버튼 클릭"
                ]
                # 여러 개의 라벨 생성하여 각 라벨에 텍스트 할당
                for index, line in enumerate(lines2):
                    if index < 9:
                        kakao_guide_label2 = tk.Label(kakao_guide2_frame, text=line)
                        kakao_guide_label2.pack(side="top", pady=1)
                    else:
                        kakao_guide_label2 = tk.Label(kakao_guide2_frame, text=line, fg="red")
                        kakao_guide_label2.pack(side="top", pady=1)

                def send_to_kakao():
                    # 메시지 API 인스턴스 생성
                    MSG = Message(service_key=self.service_key)

                    # 카카오 인증코드 발급 URL 접속 후 리다이렉트된 URL
                    redirected_url = url_entry2.get()

                    # 위 URL로 액세스 토큰 추출
                    access_token = MSG.get_access_token_by_redirected_url(redirected_url)

                    # 액세스 토큰 설정
                    MSG.set_access_token(access_token)

                    # 나에게 보내기 API 셋팅
                    message_type = "text"  # 메시지 유형 - 텍스트
                    text = url  # 전송할 텍스트 메시지 내용
                    """
                    link와 button_title을 제거하면 api에서 필수 구성이 없다고 판단하여 오류를 반환하기에 임의의 값 지정함
                    에러코드 : 400 Client Error: Bad Request for url: https://kapi.kakao.com/v2/api/talk/memo/default/send
                    """
                    link = {
                        "web_url": "Null",
                        "mobile_web_url": "Null",
                    }
                    button_title = "Null"  # 버튼 타이틀

                    MSG.send_message_to_me(
                        message_type=message_type,
                        text=text,
                        link=link,
                        button_title=button_title,
                    )
                    url_window.destroy()

                # '전송' 버튼
                send_button = tk.Button(kakao_add_frame, text="전송", command=send_to_kakao)
                send_button.pack(side="left", fill='both')

    def generate_response(self, term=None):
        # 업데이트된 service_key 적용
        self.service_key = self.api_key_entry.get()
        self.gpt = KoGPT(service_key=self.service_key)

        if term is None:
            term = self.gpt_prompt_entry.get()  # gpt_prompt_entry에서 term을 가져옴
        else:
            term = self.search_term.get()  # search_term에서 term을 가져옴

        if not term:
            return

        # KoGPT로 다음 문장 생성
        max_tokens = 128
        result = self.gpt.generate(term, max_tokens, temperature=0.7, top_p=0.8)
        
        # GPT 답변에 대한 헤더 텍스트
        prompt_result = "[" + term + "]" + "[질문에 대한 답변]\n"

        # 결과 출력
        filtered_result = self.filter_result(result)

        # 결과 출력
        self.gpt_result_text.config(state=tk.NORMAL)  # 텍스트 박스 활성화
        
        self.gpt_result_text.insert(tk.END, prompt_result)
        self.gpt_result_text.insert(tk.END, filtered_result + '\n\n')
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
        # 문자열에서 HTML 태그와 u200b 문자 제거
        clean = re.compile(r'<.*?>|\\u200b|\\')
        return re.sub(clean, '', text)

    def toggle_search_frame(self):
        # 다음 검색엔진 숨김, 열림 기능
        if self.notebook_visible:
            self.notebook.pack_forget()
            self.toggle_search_frame_button.config(text="다음 검색 열기")
        else:
            self.notebook.pack(expand=True, fill='both')
            self.toggle_search_frame_button.config(text="다음 검색 숨기기")
        self.notebook_visible = not self.notebook_visible

    def toggle_gpt_frame(self):
        # KoGPT 검색엔진 숨김, 열림 기능
        if self.gpt_frame_visible:
            self.gpt_result_label.grid_remove()
            self.gpt_result_text.grid_remove()
            self.gpt_prompt_label.grid_remove()
            self.gpt_prompt_entry.grid_remove()
            self.gpt_generate_button.grid_remove()
            self.toggle_gpt_frame_button.config(text="KoGPT 검색 열기")
        else:
            self.gpt_result_label.grid()
            self.gpt_result_text.grid()
            self.gpt_prompt_label.grid()
            self.gpt_prompt_entry.grid()
            self.gpt_generate_button.grid()
            self.toggle_gpt_frame_button.config(text="KoGPT 검색 숨기기")
        self.gpt_frame_visible = not self.gpt_frame_visible

if __name__ == "__main__":
    app = App()
    app.mainloop()
