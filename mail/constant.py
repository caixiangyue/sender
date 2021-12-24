import os

SMTP_SERVER = 'smtp.qq.com'
PORT = 465

PASSCODE = os.environ['PASS_KEY']
SENDER = os.environ['SENDER']
TO = os.environ['TO']