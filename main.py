from mail.constant import SENDER
from mail.mail import make_mail

if __name__ == "__main__":
    with make_mail() as m:
        m.send_email(SENDER, 'hello')