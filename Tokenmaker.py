from PyKakao import Message
API = Message(service_key = "REST API 키")

auth_url = API.get_url_for_generating_code()
print(auth_url)