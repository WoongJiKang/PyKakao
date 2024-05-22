from PyKakao import Message

# 메시지 API 인스턴스 생성
MSG = Message(service_key = "APIKEY")
auth_url = MSG.get_url_for_generating_code()

url = "TOKEN URI"

access_token = MSG.get_access_token_by_redirected_url(url)

# 액세스 토큰 설정
MSG.set_access_token(access_token)

# 1. 나에게 보내기 API - 텍스트 메시지 보내기 예시
message_type = "text" # 메시지 유형 - 텍스트
text = send_url # 전송할 텍스트 메시지 내용
link = {
  "web_url": "https://developers.kakao.com",
  "mobile_web_url": "https://developers.kakao.com",
}

MSG.send_message_to_me(
    message_type=message_type, 
    text=text,
    link=link,
)

