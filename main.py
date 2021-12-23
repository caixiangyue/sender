import os
import smtplib
from email.mime.text import MIMEText
from email.utils import formataddr

SERVER = 'smtp.qq.com'
PORT = 465

PASSCODE = os.environ['PASS_KEY']
SENDER = os.environ['SENDER']
TO = os.environ['TO']


def send_email(server, to):
    # server.set_debuglevel(1)
    msg = MIMEText('这是一个测试!!!','plain','utf-8')
    msg['subject'] = '来自 github action'
    msg['from'] = formataddr(['action',SENDER])
    msg['to']   = formataddr(['收件人昵称', to])
    server.sendmail(SENDER, [to], msg.as_string())
    

if __name__ == "__main__":
    server = smtplib.SMTP_SSL(SERVER, PORT)
    server.login(SENDER, PASSCODE)
    send_email(server, SENDER)
    send_email(server, TO)
    server.quit()