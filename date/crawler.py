import requests
import time
from lxml import etree

from common.utils import HEADERS
# HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.121 Safari/537.36"}

URL = "https://www.daojishi321.com"

class Crawler:
    def __init__(self) -> None:
        pass

    def get_holiday_time(self):
        retry_times = 3
        while retry_times > 0:
            try:
                r = requests.get(URL, headers=HEADERS)
                if r.status_code != 200:
                    continue
                break
            except Exception as e:
                retry_times -= 1
                print(e)
                if retry_times == 0:
                    return ''
                time.sleep(1)
        ret = '距离'
        dom = etree.HTML(r.content)
        holiday_name = dom.xpath('/html/body/div[1]/div[2]/div/div[2]/div[2]/div/span[1]/span[2]/strong[1]/a/text()')
        if len(holiday_name) > 0:
            ret += holiday_name[0]
        holiday_date = dom.xpath('/html/body/div[1]/div[2]/div/div[2]/div[2]/div/span[1]/span[2]/strong[2]/text()')
        if len(holiday_date) > 0:
            ret += '('
            ret += holiday_date[0]
            ret += ')还有'

        time_day = dom.xpath('/html/body/div[1]/div[2]/div/div[2]/div[2]/div/span[2]/span[1]/text()')
        if len(time_day) > 0:
            ret += time_day[0]
            ret += '天'
        time_hour = dom.xpath('/html/body/div[1]/div[2]/div/div[2]/div[2]/div/span[2]/span[3]/text()')
        if len(time_hour) > 0:
            ret += time_hour[0]
            ret += '时'
        time_min = dom.xpath('/html/body/div[1]/div[2]/div/div[2]/div[2]/div/span[2]/span[5]/text()')
        if len(time_min) > 0:
            ret += time_min[0]
            ret += '分\n\n'
        return ret

# c = Crawler()
# print(c.get_holiday_time())