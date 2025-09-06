from mcp.server.fastmcp import FastMCP
from pydantic import EmailStr
from dotenv import load_dotenv
import truststore
import os
import ssl
from email.message import EmailMessage
import smtplib
import truststore
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

mcp = FastMCP(name="mail mcp", host="0.0.0.0", port=8080)


@mcp.tool()
async def send_email(to: EmailStr, subject: str, body: str):
    """
    메일을 전달해주는 smtp 메일전달 도구입니다.
    수신자이메일과 주제, 본문을 받아 전달합니다.

    Args:
        to: 수신자 이메일
        subject:  주제
        body: 내용

    Returns:

    """
    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = USER
    msg["To"] = to
    msg.set_content(body)
    with smtplib.SMTP_SSL(SMTP_SERVER, 465, context=ctx, timeout=20) as s:
        s.ehlo()
        s.login(USER, PASSWORD)
        s.send_message(msg)
    return {
        "to": to,
        "subject": subject,
        "body": body,
        "status": "success"
    }


if __name__ == "__main__":
    mcp.run(transport="streamable-http")
