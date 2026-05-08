import os
import requests
import time
import asyncio
import aiohttp
from lxml import etree
from contextlib import contextmanager
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import date, timedelta

import akshare as ak

from common.utils import HEADERS, REQUEST_TIMEOUT
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
PROXY_ENV_KEYS = (
    "http_proxy",
    "https_proxy",
    "HTTP_PROXY",
    "HTTPS_PROXY",
    "all_proxy",
    "ALL_PROXY",
)
AKSHARE_TIMEOUT = 8
AKSHARE_MAX_WORKERS = 4

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

    @contextmanager
    def _without_proxy(self):
        old_env = {key: os.environ.get(key) for key in PROXY_ENV_KEYS}
        try:
            for key in PROXY_ENV_KEYS:
                os.environ.pop(key, None)
            yield
        finally:
            for key, value in old_env.items():
                if value is None:
                    os.environ.pop(key, None)
                else:
                    os.environ[key] = value

    def _call_akshare(self, func, **kwargs):
        with self._without_proxy():
            return func(**kwargs)

    def _normalize_stock_symbol(self, symbol: str) -> tuple[str, str]:
        stock_symbol = symbol.strip().upper()
        if not stock_symbol:
            raise ValueError("股票代码不能为空")

        if stock_symbol.startswith("SH") and stock_symbol[2:].isdigit():
            if stock_symbol[2:].startswith("000"):
                return "INDEX", stock_symbol
            return "A", stock_symbol[2:]

        if stock_symbol.startswith("SZ") and stock_symbol[2:].isdigit():
            if stock_symbol[2:].startswith("399"):
                return "INDEX", stock_symbol
            return "A", stock_symbol[2:]

        if stock_symbol.startswith("BJ") and stock_symbol[2:].isdigit():
            return "A", stock_symbol[2:]

        if stock_symbol.startswith("HK") and stock_symbol[2:].isdigit():
            return "HK", stock_symbol[2:].zfill(5)

        if stock_symbol.isdigit():
            if len(stock_symbol) == 6:
                return "A", stock_symbol
            if len(stock_symbol) <= 5:
                return "HK", stock_symbol.zfill(5)

        if "." in stock_symbol and stock_symbol.split(".", 1)[0].isdigit():
            return "US", stock_symbol.split(".", 1)[1]

        if any(char.isalpha() for char in stock_symbol):
            return "US", stock_symbol

        raise ValueError(f"不支持的股票代码格式: {symbol}")

    @staticmethod
    def _find_first_value(dataframe, column: str):
        if column not in dataframe.columns:
            return None
        series = dataframe[column].dropna()
        if series.empty:
            return None
        return series.iloc[0]

    @staticmethod
    def _find_last_value(dataframe, column: str):
        if column not in dataframe.columns:
            return None
        series = dataframe[column].dropna()
        if series.empty:
            return None
        return series.iloc[-1]

    @staticmethod
    def _find_item_value(dataframe, item_name: str):
        if dataframe.empty or "item" not in dataframe.columns or "value" not in dataframe.columns:
            return None
        row = dataframe[dataframe["item"] == item_name]
        if row.empty:
            return None
        return row.iloc[0]["value"]

    @staticmethod
    def _to_float(value):
        try:
            if value is None or value == "":
                return None
            return float(value)
        except (TypeError, ValueError):
            return None

    def _to_xq_symbol(self, market: str, symbol: str) -> str:
        if market == "INDEX":
            return symbol
        if market == "A":
            if symbol.startswith(("4", "8")):
                return f"BJ{symbol}"
            if symbol.startswith(("6", "9")):
                return f"SH{symbol}"
            return f"SZ{symbol}"
        return symbol

    def _get_history_symbol(self, market: str, original_symbol: str, normalized_symbol: str) -> str:
        if market == "INDEX":
            return normalized_symbol[2:]
        if market in {"A", "HK"}:
            return normalized_symbol
        stock_symbol = original_symbol.strip().upper()
        if "." in stock_symbol and stock_symbol.split(".", 1)[0].isdigit():
            return stock_symbol
        return normalized_symbol

    def _get_ten_year_price_stats(self, market: str, original_symbol: str, normalized_symbol: str) -> dict:
        if market == "INDEX":
            return {"ten_year_price_basis": None}

        start_date = (date.today() - timedelta(days=3652)).strftime("%Y%m%d")
        end_date = date.today().strftime("%Y%m%d")
        hist_symbol = self._get_history_symbol(market, original_symbol, normalized_symbol)

        if market == "A":
            hist_df = self._call_akshare(
                ak.stock_zh_a_hist,
                symbol=hist_symbol,
                period="monthly",
                start_date=start_date,
                end_date=end_date,
                adjust="hfq",
                timeout=AKSHARE_TIMEOUT,
            )
            price_basis = "hfq"
        elif market == "HK":
            hist_df = self._call_akshare(
                ak.stock_hk_hist,
                symbol=hist_symbol,
                period="monthly",
                start_date=start_date,
                end_date=end_date,
                adjust="hfq",
            )
            price_basis = "hfq"
        else:
            hist_df = self._call_akshare(
                ak.stock_us_hist,
                symbol=hist_symbol,
                period="monthly",
                start_date=start_date,
                end_date=end_date,
                adjust="hfq",
            )
            price_basis = "hfq"

        if hist_df.empty or "收盘" not in hist_df.columns:
            return {}

        close_series = hist_df["收盘"].dropna()
        if close_series.empty:
            return {}

        ten_year_low = float(close_series.min())
        ten_year_high = float(close_series.max())
        ten_year_current_price = float(close_series.iloc[-1])
        return {
            "ten_year_price_basis": price_basis,
            "ten_year_low": ten_year_low,
            "ten_year_high": ten_year_high,
            "ten_year_current_price": ten_year_current_price,
        }

    def _get_stock_info_from_xq(self, market: str, original_symbol: str, normalized_symbol: str) -> dict:
        xq_symbol = self._to_xq_symbol(market, normalized_symbol)
        quote_df = self._call_akshare(
            ak.stock_individual_spot_xq, symbol=xq_symbol, timeout=AKSHARE_TIMEOUT
        )
        name = self._find_item_value(quote_df, "名称")
        price = self._to_float(self._find_item_value(quote_df, "现价"))
        pb = self._to_float(self._find_item_value(quote_df, "市净率"))
        dividend_yield = self._to_float(self._find_item_value(quote_df, "股息率(TTM)"))
        ten_year_stats = self._get_ten_year_price_stats(market, original_symbol, normalized_symbol)
        ten_year_price_basis = ten_year_stats.get("ten_year_price_basis")
        ten_year_low = ten_year_stats.get("ten_year_low")
        ten_year_high = ten_year_stats.get("ten_year_high")
        ten_year_current_price = ten_year_stats.get("ten_year_current_price")
        ten_year_percentile = None
        if (
            ten_year_current_price is not None
            and ten_year_low is not None
            and ten_year_high is not None
            and ten_year_high > ten_year_low
        ):
            ten_year_percentile = round(
                (
                    (ten_year_current_price - ten_year_low)
                    / (ten_year_high - ten_year_low)
                )
                * 100,
                2,
            )

        return {
            "market": market,
            "symbol": normalized_symbol,
            "name": name,
            "price": price,
            "pb": pb,
            "dividend_yield": dividend_yield,
            "ten_year_price_basis": ten_year_price_basis,
            "ten_year_low": ten_year_low,
            "ten_year_high": ten_year_high,
            "ten_year_current_price": ten_year_current_price,
            "ten_year_percentile": ten_year_percentile,
        }

    def _get_single_stock_info_safe(self, original_symbol: str, market: str, normalized_symbol: str) -> dict:
        try:
            return self._get_stock_info_from_xq(market, original_symbol, normalized_symbol)
        except ValueError:
            raise
        except Exception as exc:
            price_basis = "index" if market == "INDEX" else "hfq"
            return {
                "market": market,
                "symbol": normalized_symbol,
                "name": None,
                "price": None,
                "pb": None,
                "dividend_yield": None,
                "ten_year_price_basis": price_basis,
                "ten_year_low": None,
                "ten_year_high": None,
                "ten_year_current_price": None,
                "ten_year_percentile": None,
                "error": f"{original_symbol} 查询失败: {exc.__class__.__name__}",
            }

    def get_stock_infos_akshare(self, symbols: list[str]) -> list[dict]:
        normalized_items = []
        for symbol in symbols:
            market, normalized_symbol = self._normalize_stock_symbol(symbol)
            normalized_items.append((symbol, market, normalized_symbol))

        result = [None] * len(normalized_items)
        with ThreadPoolExecutor(max_workers=min(AKSHARE_MAX_WORKERS, len(normalized_items) or 1)) as executor:
            future_to_index = {
                executor.submit(
                    self._get_single_stock_info_safe,
                    original_symbol,
                    market,
                    normalized_symbol,
                ): index
                for index, (original_symbol, market, normalized_symbol) in enumerate(normalized_items)
            }
            for future in as_completed(future_to_index):
                index = future_to_index[future]
                result[index] = future.result()
        return result

    def get_stock_info_akshare(self, symbol: str) -> dict:
        """
        使用 akshare 获取单只股票的基础信息。

        支持的输入格式:
        - A 股: 600519, SH600519, SZ000001
        - 港股: 00700, HK00700
        - 美股: AAPL, MSFT, 105.MSFT
        """
        return self.get_stock_infos_akshare([symbol])[0]

    def monitor(self):
        retry_times = 3
        while retry_times > 0:
            try:
                r = requests.get(URL3, headers=HEADERS, timeout=REQUEST_TIMEOUT)
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
                r = requests.get(
                    f'{URL4}{code}', headers=HEADERS, cookies=cookies, timeout=REQUEST_TIMEOUT
                )
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
                r = requests.get(URL, headers=HEADERS, timeout=REQUEST_TIMEOUT)
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
                r = requests.get(URL1, headers=HEADERS1, timeout=REQUEST_TIMEOUT)
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
                r = requests.get(URL2, headers=HEADERS, timeout=REQUEST_TIMEOUT)
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
