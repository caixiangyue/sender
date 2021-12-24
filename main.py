from mail.constant import SENDER, TO
from mail.mail import make_mail
from weather.crawler import Crawler

if __name__ == "__main__":
    c = Crawler()
    msg = c.get_weather()
    with make_mail() as m:
        m.send_email(TO, msg)
        m.send_email(SENDER, msg)