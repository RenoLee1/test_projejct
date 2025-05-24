import smtplib
import socket
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional

class EmailSender:
    def __init__(self, smtp_server: str, smtp_port: int, username: str, password: str, from_email: Optional[str] = None):
        self.smtp_server = smtp_server
        self.smtp_port = smtp_port
        self.username = username
        self.password = password
        self.from_email = from_email or username

    def send_email(self, to: str, subject: str, body: str, html: Optional[str] = None):
        print(f"[DEBUG] Preparing email to: {to}")

        msg = MIMEMultipart("alternative")
        msg["From"] = self.from_email
        msg["To"] = to
        msg["Subject"] = subject

        msg.attach(MIMEText(body, "plain"))
        if html:
            msg.attach(MIMEText(html, "html"))

        try:
            with smtplib.SMTP(self.smtp_server, self.smtp_port, timeout=10) as server:
                # server.set_debuglevel(1)
                server.starttls()
                server.login(self.username, self.password)
                server.send_message(msg)
                print(f"[SMTP] ✅ Email sent to {to}")

        except smtplib.SMTPAuthenticationError as e:
            print(f"[SMTP] ❌ Authentication failed: {e}")
        except smtplib.SMTPConnectError as e:
            print(f"[SMTP] ❌ Connection failed: {e}")
        except smtplib.SMTPRecipientsRefused as e:
            print(f"[SMTP] ❌ Invalid recipient(s): {e.recipients}")
        except smtplib.SMTPException as e:
            if isinstance(e.args, tuple) and len(e.args) >= 2:
                code, msg = e.args[:2]
                if code == -1 and msg == b'\x00\x00\x00':
                    print("[SMTP] ⚠️ Ignored harmless socket error after QUIT. Email was sent successfully.")
                    return  # ✅ 主动返回，不再继续执行下面
            print(f"[SMTP] ❌ General SMTP error: {e}")
        except socket.timeout:
            print("[SMTP] ❌ Connection timed out.")
        except socket.gaierror as e:
            print(f"[SMTP] ❌ Network error: {e}")
        except Exception as e:
            if isinstance(e.args, tuple) and len(e.args) >= 2:
                code, msg = e.args[:2]
                if code == -1 and msg == b'\x00\x00\x00':
                    print("[SMTP] ⚠️ Ignored harmless socket error after QUIT. Email was sent successfully.")
                else:
                    print(f"[SMTP] ❌ Unexpected exception: {e}")
            else:
                print(f"[SMTP] ❌ Unknown error: {e}")
