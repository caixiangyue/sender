import smtplib
from email.mime.text import MIMEText
from email.utils import formataddr
from contextlib import contextmanager
from .constant import SMTP_SERVER, PASSCODE, PORT, SENDER

class Mail:
    def __init__(self):
        self.server = smtplib.SMTP_SSL(SMTP_SERVER, PORT)
        self.server.login(SENDER, PASSCODE)

    def send_email(self, to: str, content: str):
        msg = MIMEText(content,'plain','utf-8')
        msg['subject'] = '来自 github action'
        msg['from'] = formataddr(['action',SENDER])
        msg['to']   = formataddr(['收件人昵称', to])
        self.server.sendmail(SENDER, [to], msg.as_string())
    
    def exit(self):
        self.server.quit()

@contextmanager
def make_mail():
    m = Mail()
    yield m
    m.exit()