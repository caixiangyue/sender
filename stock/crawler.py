import requests
import time
import asyncio
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
SXG = 'SH603896'
YZGF = 'SH603886'
async def get_data_current(name, cookies, code):
        retry_times = 3
        while retry_times > 0:
            try:
                r = requests.get(f'{URL4}{code}', headers=HEADERS, cookies=cookies)
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
        json_data = r.json()
        if json_data is None:
            return ''
        current = json_data['data']['quote']['current']
        chg = json_data['data']['quote']['chg']
        if chg >= 0.0:
            chg_str = f'📈{chg}'
        else:
            chg_str = f'📉{abs(chg)}'
        wave = round((abs(chg) / current) * 100, 2)
        wave_str = ''
        if wave > 1.0:
            wave_str = f'，波动{str(wave)}个点'

        ret = f"{name}: {str(current)}，{chg_str}{wave_str}"
        print(ret)
        return ret

async def get_all(cookie):
    f = await asyncio.gather(
        get_data_current('伊利股份', cookie, YLGF),
        get_data_current('海螺水泥', cookie, HLSN),
        get_data_current('双汇发展', cookie, SHFZ),
        get_data_current('农业银行', cookie, NH),
        get_data_current('中国石化', cookie, ZSH),
        get_data_current('大秦铁路', cookie, DQTL),
        get_data_current('招商银行', cookie, ZSYH),
        get_data_current('贵州茅台', cookie, GZMT),
        get_data_current('腾讯控股', cookie, TXKG),
        get_data_current('羚锐制药', cookie, LRZY),
        get_data_current('甘李药业', cookie, GLYY),
        get_data_current('长江电力', cookie, CJDL),
        get_data_current('上海机场', cookie, SHJC),
        get_data_current('元祖股份', cookie, YZGF),
        get_data_current('雅戈尔', cookie, YGER),
        get_data_current('唐山港', cookie, TSG),
        get_data_current('寿仙谷', cookie, SXG),
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
        # ret = '中国石化：'
        # ret += self._get_data_current(r.cookies, ZSH)
        # ret += '\n'
        # ret += '农业银行：'
        # ret += self._get_data_current(r.cookies, NH)
        # ret += '\n'
        # ret += '大秦铁路：'
        # ret += self._get_data_current(r.cookies, DQTL)
        # ret += '\n---------------\n'
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
                break
            except Exception as e:
                retry_times -= 1
                print(e)
                if retry_times == 0:
                    return ''
                time.sleep(1)
        json_data = r.json()
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
