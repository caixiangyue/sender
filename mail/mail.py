import smtplib
from email.mime.text import MIMEText
from email.utils import formataddr
from contextlib import contextmanager
from .constant import SMTP_SERVER, PASSCODE, PORT, SENDER

SUBJECT = '可爱的机器人'

class Mail:
    def __init__(self):
        self.server = smtplib.SMTP_SSL(SMTP_SERVER, PORT)
        self.server.login(SENDER, PASSCODE)

    def send_email(self, to: str, content: str):
        msg = MIMEText(content,'plain','utf-8')
        msg['subject'] = SUBJECT
        msg['from'] = formataddr(['小菜',SENDER])
        msg['to']   = formataddr(['to', to])
        self.server.sendmail(SENDER, [to], msg.as_string())
    
    def exit(self):
        self.server.quit()

@contextmanager
def make_mail():
    m = Mail()
    yield m
    m.exit()