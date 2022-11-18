import requests
import time
from lxml import etree

from common.utils import HEADERS

URL = 'https://legulegu.com/stockdata/marketcap-gdp'
URL1 = 'https://wallstreetcn.com/markets/codes/CN10YR.OTC'

class Crawler:
    def __init__(self) -> None:
        pass

    def get_gnp(self):
        retry_times = 3
        while retry_times > 0:
            try:
                r = requests.get(URL, headers=HEADERS)
                if r.status_code != 200:
                    retry_times -= 1
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
            gnp = data[0]
        ret += f'{gnp}\n'
        ret += self.get_suggest(gnp)
        ret += '-----------------------\n\n'
        return ret

    def get_ten_years(self):
        retry_times = 10
        while retry_times > 0:
            try:
                r = requests.get(URL1, headers=HEADERS)
                if r.status_code != 200:
                    retry_times -= 1
                    continue
                break
            except Exception as e:
                retry_times -= 1
                print(e)
                if retry_times == 0:
                    return ''
                time.sleep(1)

        ret = '十年期国债：\n'
        dom = etree.HTML(r.content)
        data = dom.xpath('//*[@id="app"]/div/div[1]/div[2]/div/div[1]/div[1]/div/div[1]/div[1]/div[2]/div[1]/text()')
        ten_rate=''
        if len(data) > 0:
            ten_rate = data[0].strip('\n').strip('\r').strip(' ')
        ret += f'{ten_rate}\n'
        if len(ret) > 0 and float(ten_rate) < 3.0:
            ret += '此时债券及其没有性价比，不建议买入\n'
        ret += '-----------------------\n\n'
        return ret
    
    def get_suggest(self, gnp: str) -> str:
        start = gnp.find('：')
        end = gnp.find('%')

        if start == -1 or end == -1:
            return ''
        
        gnp = float(gnp[start+1:end])
        if gnp > 80.0:
            return '此时不建议买入任何股票，买了就是大傻瓜\n'
        
        if gnp < 65.0:
            return '此时机会千载难逢\n'
        
        if gnp < 70.0:
            return '此时不买更待何时，绝佳买点，不买就是傻子\n'
        
        if gnp < 75.0:
            return '此时适合买入\n'
        
        if gnp < 80.0:
            return '此时适合定投，少量买入\n'


#c = Crawler()
#print(c.get_ten_years())
