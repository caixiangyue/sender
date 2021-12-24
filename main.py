from mail.constant import SENDER, TO
from mail.mail import make_mail
from weather.crawler import Crawler as weatherCrawler
from date.commemoration import get_together_days_msg

if __name__ == "__main__":
    c = weatherCrawler()
    msg = get_together_days_msg()
    msg += c.get_weather_msg()
    with make_mail() as m:
        m.send_email(TO, msg)
        m.send_email(SENDER, msg)