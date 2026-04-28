import requests
import time
import asyncio
import aiohttp
from lxml import etree

from common.utils import HEADERS
# HEADERS = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36"}
HEADERS1 = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.121 Safari/537.36", "Referer":"https://stock.finance.sina.com.cn/forex/globalbd/gcny10.html"}

URL = 'https://legulegu.com/stockdata/marketcap-gdp'
URL1 = 'https://hq.sinajs.cn/?rn=1670838672882&list=globalbd_gcny10'
URL2 = 'https://stock.xueqiu.com/v5/stock/realtime/quotec.json?symbol=HKHSI,SH000001,.IXIC'
URL3 = 'https://xueqiu.com'
URL4 = 'https://stock.xueqiu.com/v5/stock/quote.json?symbol='
ZSH = 'SH600028'
NH = 'SH601288'
DQTL = 'SH601006'
YLGF = 'SH600887'
HLSN = 'SH600585'
SHFZ = 'SZ000895'
ZSYH = 'SH600036'
GZMT = 'SH600519'
YGER = 'SH600177'
TSG = 'SH601000'
TXKG = '00700'
LRZY = 'SH600285'
CJDL = 'SH600900'
SHJC = 'SH600009'
GLYY = 'SH603087'
YZGF = 'SH603886'
ZZHL = 'SH000922'
FAN = 'SZ002327'
MDJT = 'SZ000333'
XYYH = 'SH601166'
GLDQ = 'SZ000651'
SXMY = 'SH601225'
ZGPA = 'SH601318'
YNBY = 'SZ000538'
SZZS = 'SH000001'
HKHSHYLV = 'HKHSHYLV'
BDH = 'SH600598'
JHGT = 'SH601816'

async def get_data_current(cookies, code):
    async with aiohttp.ClientSession() as session:
        async with session.get(f'{URL4}{code}&extend=detail', headers=HEADERS, cookies=cookies) as response:
            # html = await response.text()
            json_data = await response.json()
            print(json_data)
    if json_data is None or json_data.get('data', None) == None:
        return ''
    print(json_data)
    quote = json_data['data']['quote']
    current = quote['current']
    chg = quote['chg']
    percent = quote['percent']
    low52w = quote['low52w']
    name = quote['name']
    market_capital = quote['market_capital']
    dividend_yield = quote.get('dividend_yield', '无')
    pb = quote.get('pb', '无')
    if chg >= 0.0:
        chg_str = f'📈{chg}'
    else:
        chg_str = f'📉{abs(chg)}'
    percent_str = ''
    if abs(percent) > 1.0:
        percent_str = f'，{str(percent)}个点'

    cheap_value = int(100-(abs(current-low52w)/current)*100)
    if market_capital is None:
        market_capital_str = ''
    else:
        market_capital = int(market_capital / 100000000)
        market_capital_str = f'，市值{str(market_capital)}亿'


    ret = f"{name}: {str(current)}，{chg_str}{percent_str}{market_capital_str}，最低{low52w}，pb{pb}，股息率{str(dividend_yield)}，便宜度{str(cheap_value)}"
    print(ret)
    return ret


async def get_all(cookie):
    f = await asyncio.gather(
        get_data_current(cookie, JHGT),
        get_data_current(cookie, BDH),
        get_data_current(cookie, SZZS),
        get_data_current(cookie, SXMY),
        get_data_current(cookie, GLDQ),
        get_data_current(cookie, MDJT),
        get_data_current(cookie, SHFZ),
        get_data_current(cookie, NH),
        get_data_current(cookie, ZSH),
        get_data_current(cookie, DQTL),
        get_data_current(cookie, ZSYH),
        get_data_current(cookie, GZMT),
        get_data_current(cookie, TXKG),
        get_data_current(cookie, LRZY),
        get_data_current(cookie, CJDL),
        get_data_current(cookie, SHJC),
        get_data_current(cookie, TSG),
        get_data_current(cookie, ZZHL),
        get_data_current(cookie, HKHSHYLV),
    )
    return f
class Crawler:
    def __init__(self) -> None:
        pass

    def monitor(self):
        retry_times = 3
        while retry_times > 0:
            try:
                r = requests.get(URL3, headers=HEADERS)
                if r.status_code != 200:
                    print(r.status_code)
                    retry_times -= 1
                    continue
                break
            except Exception as e:
                retry_times -= 1
                print(e)
                if retry_times == 0:
                    return ''
                time.sleep(1)
        f = asyncio.run(get_all(r.cookies))
        return '\n'.join(f)

    def _get_data_current(self,cookies, code):
        retry_times = 3
        while retry_times > 0:
            try:
                r = requests.get(f'{URL4}{code}', headers=HEADERS, cookies=cookies)
                if r.status_code != 200:
                    print(r.status_code)
                    retry_times -= 1
                    continue
                json_data = r.json()
                break
            except Exception as e:
                retry_times -= 1
                print(e)
                if retry_times == 0:
                    return ''
                time.sleep(1)
        if json_data is None:
            return ''
        return str(json_data['data']['quote']['current'])


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
        ret += self._get_suggest(gnp)
        ret += '-----------------------\n\n'
        return ret

    def get_ten_years(self):
        retry_times = 10
        while retry_times > 0:
            try:
                r = requests.get(URL1, headers=HEADERS1)
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

        data = r.content.decode('gbk').split(',')
        ten_rate=''
        if len(data) > 3:
            ten_rate = data[3]
        ret += f'{ten_rate}\n'
        if len(ten_rate) > 0 and float(ten_rate) < 3.0 and float(ten_rate) > 2.7:
            ret += '此时债券及其没有性价比，不建议买入\n'
        elif len(ten_rate) > 0 and float(ten_rate) < 2.7:
            ret += '建议分批卖出债券\n'
        ret += '-----------------------\n\n'
        return ret

    def _get_suggest(self, gnp: str) -> str:
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

    def get_sh(self):
        retry_times = 10
        while retry_times > 0:
            try:
                r = requests.get(URL2, headers=HEADERS)
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

        ret = '恒生指数：'
        json_data = r.json()
        data = json_data['data'][0]
        ret += str(data['current'])
        ret += '\n上证指数：'
        data = json_data['data'][1]
        ret += str(data['current'])
        ret += '\n纳斯达克指数：'
        data = json_data['data'][2]
        ret += str(data['current'])
        ret += '\n-----------------------\n\n'
        return ret


# c = Crawler()
# print(c.monitor())
