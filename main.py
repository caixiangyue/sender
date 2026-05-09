import os
import argparse
from stock.crawler import Crawler as stockCrawler
from weather.crawler import Crawler as weatherCrawler
from github.crawler import Crawler as githubCrawler
from stock.crawler import Crawler as stockCrawler
from yiyan.crawler import Crawler as yiyanCrawler
from date.commemoration import get_together_days_msg
from date.crawler import Crawler as holidayCrawler
from wechat.wechat import Wechat

STOCK_SYMBOLS = [
    "600519",  # 贵州茅台
    "000858",  # 五粮液
    "600329",  # 达仁堂
    "600036",  # 招商银行
    "600938",  # 中国海油
    "00700",   # 腾讯控股
    "600900",  # 长江电力
    "00941",   # 中国移动
    "159545",  # 恒生红利低波ETF
    "159332",  # 央企红利ETF
    "SH000922",  # 中证红利指数
    "SZ399997",
    "SZ399975",
    "HKHSTECH",
    "SP500",
]


def get_stock_info_msg(crawler):
    stock_infos = crawler.get_stock_infos_akshare(STOCK_SYMBOLS)
    return "\n".join(str(item) for item in stock_infos) + "\n"

def get_msg():
    msg = get_together_days_msg()
    g = githubCrawler()
    w = weatherCrawler()
    s = stockCrawler()
    y = yiyanCrawler()
    h = holidayCrawler()

    msg += s.get_gnp()
    msg += s.get_sh()
    # msg += '\n'
    msg += s.get_ten_years()
    msg += get_stock_info_msg(s)
    # msg += g.get_trending_msg()
    # msg += g.get_weekly()
    return msg

def send_msg():
    msg = get_together_days_msg()
    w = weatherCrawler()
    g = githubCrawler()
    s = stockCrawler()
    y = yiyanCrawler()
    h = holidayCrawler()
    msg += h.get_holiday_time()
    msg += w.get_weather_msg()
    msg += y.get_msg()
    msg += g.get_weekly()
    msg += s.get_gnp()
    msg += s.get_sh()
    msg += s.get_ten_years()
    msg += get_stock_info_msg(s)
    # msg += s.monitor()
    msg += '\n'
    p = os.popen('./cu -wb')
    msg += p.read()
    msg += g.get_trending_msg()
    wechat = Wechat('机器人', msg, SEND_KEY)
    wechat.send()
    with make_mail() as m:
        m.send_email(TO, msg)
        m.send_email(SENDER, msg)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='sender')
    parser.add_argument('-g', action="store_true")
    args = parser.parse_args()
    if args.g:
        # s = stockCrawler()
        # print(s.monitor())
        print(get_msg())
    else:
        from mail.mail import make_mail
        from mail.constant import SENDER, TO, TO1, SEND_KEY
        send_msg()
