from mcp.server.fastmcp import FastMCP
from pydantic import EmailStr
from dotenv import load_dotenv
import truststore
import os
import ssl
from email.message import EmailMessage
from aiosmtplib.smtp import SMTP
import truststore
load_dotenv()

truststore.inject_into_ssl()
# 네이버 계정 정보
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
USER = os.getenv("MAIL_SEND")  # 메일 보내는 이메일
PASSWORD = os.getenv("GOOGLE_SMTP_KEY")  # 앱 비밀번호
# 메일 작성
ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
ctx.minimum_version = ssl.TLSVersion.TLSv1_2
ctx.check_hostname = True
ctx.verify_mode = ssl.CERT_REQUIRED
ctx.load_default_certs()

mcp = FastMCP(name="mail mcp", host="0.0.0.0", port=8082)


def build_html_email(subject: str, body: str) -> str:
    """
    subject와 body를 받아 HTML 이메일 템플릿에 맞게 채워줍니다.
    """
    html = f"""\
<!doctype html>
<html lang="ko">
  <head>
    <meta charset="UTF-8">
    <meta name="color-scheme" content="light dark">
    <meta name="supported-color-schemes" content="light dark">
    <meta name="viewport" content="width=device-width, initial-scale=1.0"/>
    <title>{subject}</title>
  </head>
  <body style="margin:0;padding:0;background:#f8fafc;">
    <div style="display:none;max-height:0;overflow:hidden;opacity:0;">
      {subject} – 오늘의 핵심 소식을 간단히 확인하세요.
    </div>

    <table role="presentation" cellpadding="0" cellspacing="0" width="100%" style="background:#f8fafc;">
      <tr>
        <td align="center" style="padding:24px 16px;">
          <table role="presentation" cellpadding="0" cellspacing="0" width="100%" style="max-width:600px;background:#ffffff;border:1px solid #e5e7eb;border-radius:16px;">
            <!-- 헤더 -->
            <tr>
              <td style="padding:20px 20px 8px 20px;">
                <div style="font-size:20px;line-height:1.3;font-weight:800;color:#111827;">{subject}</div>
                <div style="margin-top:6px;font-size:13px;color:#6b7280;">핵심만 빠르게 확인하세요.</div>
              </td>
            </tr>
            <tr><td style="height:8px;"></td></tr>

            <!-- 본문 (기사 카드 1개 형태로) -->
            <tr>
              <td style="padding: 12px 16px 0 16px;">
                <table width="100%" cellpadding="0" cellspacing="0" role="presentation" style="border:1px solid #e9ecef;border-radius:12px;">
                  <tr>
                    <td style="padding:16px;">
                      <div style="font-size:15px;line-height:1.6;color:#374151;white-space:pre-line;">
                        {body}
                      </div>
                    </td>
                  </tr>
                </table>
              </td>
            </tr>
            <tr><td style="height:12px;"></td></tr>

            <!-- 푸터 -->
            <tr>
              <td style="padding:16px 20px 20px 20px;">
                <div style="font-size:12px;color:#6b7280;line-height:1.6;">
                  이 메일은 자동 발송되었습니다. 회신하지 마세요.<br/>
                  © 2025 My News AI Bot
                </div>
              </td>
            </tr>
          </table>
          <div style="height:20px;"></div>
        </td>
      </tr>
    </table>
  </body>
</html>
"""
    return html

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
    html_body = build_html_email(subject=subject,body=body)
    msg.add_alternative(html_body, subtype="html")

    smtp_client = SMTP(hostname=SMTP_SERVER, port=SMTP_PORT, username=USER, password=PASSWORD, tls_context=ctx)
    async with smtp_client:
        await smtp_client.send_message(msg)
    return {
        "to": to,
        "subject": subject,
        "body": body,
        "status": "success"
    }


if __name__ == "__main__":
    mcp.run(transport="streamable-http")
