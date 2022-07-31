import requests
import time
from lxml import etree

from common.utils import HEADERS

URL = 'https://legulegu.com/stockdata/marketcap-gdp'

class Crawler:
    def __init__(self) -> None:
        pass

    def get_gnp(self):
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

        ret = '获取巴菲特指数：\n'
        dom = etree.HTML(r.content)
        data = dom.xpath('//*[@id="data-description"]/text()')
        if len(data) > 0:
            ret += data[0]
        ret += '\n'
        return ret


# c = Crawler()
# print(c.get_gnp())