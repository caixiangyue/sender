import os
import smtplib
from email.mime.text import MIMEText
from email.utils import formataddr

SERVER = 'smtp.qq.com'
PORT = 465

PASSCODE = os.environ['PASS_KEY']
SENDER = os.environ['SENDER']
to = SENDER


def send_email():
    msg = MIMEText('为了您的健康,起来活动活动,喝点儿水!!!啦啦啦啦啦啦啦啦啦.....此程序每隔一个小时会自动给您发送一封邮件','plain','utf-8')
    msg['subject'] = '来自专属python程序的亲切问候^_^'
    msg['from'] = formataddr(['发件人昵称',SENDER])
    msg['to']   = formataddr(['收件人昵称',to])
    server = smtplib.SMTP_SSL(SERVER, PORT)
    # server.set_debuglevel(1)
    server.login(SENDER, PASSCODE)
    server.sendmail(SENDER,[SENDER, to], msg.as_string())
    server.quit()

if __name__ == "__main__":
    send_email()