import os
from mail.constant import SENDER, TO, TO1, SEND_KEY
from mail.mail import make_mail
from weather.crawler import Crawler as weatherCrawler
from github.crawler import Crawler as githubCrawler
from stock.crawler import Crawler as stockCrawler
from yiyan.crawler import Crawler as yiyanCrawler
from date.commemoration import get_together_days_msg
from date.crawler import Crawler as holidayCrawler
from wechat.wechat import Wechat

if __name__ == "__main__":
    msg = get_together_days_msg()
    w = weatherCrawler()
    g = githubCrawler()
    s = stockCrawler()
    y = yiyanCrawler()
    h = holidayCrawler()
    msg += h.get_holiday_time()
    msg += w.get_weather_msg()
    msg += y.get_msg()
    msg += s.get_gnp()
    msg += s.get_sh()
    msg += s.monitor()
    msg += s.get_ten_years()
    p = os.popen('./cu -wb')
    msg += p.read()
    msg += g.get_trending_msg()
    wechat = Wechat('机器人', msg, SEND_KEY)
    wechat.send()
    with make_mail() as m:
        m.send_email(TO, msg)
        m.send_email(SENDER, msg)
        index = msg.find('\n')
        if index != -1 and index > 30:
            m.send_email(TO1, msg[index+1:])

