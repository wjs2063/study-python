import smtplib, ssl
from email.message import EmailMessage
import truststore
import os
import smtplib
from dotenv import load_dotenv

load_dotenv()

truststore.inject_into_ssl()
# 네이버 계정 정보
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 465
USER = os.getenv("MAIL_SEND")  # 메일 보내는 이메일
PASSWORD = os.getenv("GOOGLE_SMTP_KEY")  # 앱 비밀번호
# 메일 작성
ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
ctx.minimum_version = ssl.TLSVersion.TLSv1_2
ctx.check_hostname = True
ctx.verify_mode = ssl.CERT_REQUIRED
ctx.load_default_certs()

msg = EmailMessage()
msg["Subject"] = "테스트"
msg["From"] = USER
msg["To"] = "test@naver.com"
msg.set_content("hello")

with smtplib.SMTP_SSL(SMTP_SERVER, 465, context=ctx, timeout=20) as s:
    s.ehlo()
    s.login(USER, PASSWORD)  # 실패 시 USER.split("@")[0]도 시도 가능
    s.send_message(msg)

print("메일 전송 완료!")
