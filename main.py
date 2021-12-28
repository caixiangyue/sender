from mail.constant import SENDER, TO
from mail.mail import make_mail
from weather.crawler import Crawler as weatherCrawler
from github.crawler import Crawler as githubCrawler
from date.commemoration import get_together_days_msg

if __name__ == "__main__":
    msg = get_together_days_msg()
    w = weatherCrawler()
    g = githubCrawler()
    msg += w.get_weather_msg()
    msg += g.get_trending_msg()
    with make_mail() as m:
        m.send_email(TO, msg)
        m.send_email(SENDER, msg)