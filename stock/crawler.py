import os
import requests
import time
import asyncio
import aiohttp
from lxml import etree
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import date, timedelta

import akshare as ak

from common.utils import HEADERS, REQUEST_TIMEOUT
# HEADERS = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36"}
HEADERS1 = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.121 Safari/537.36", "Referer":"https://stock.finance.sina.com.cn/forex/globalbd/gcny10.html"}
DANJUAN_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36",
    "Referer": "https://danjuanfunds.com/rn/value-center",
}

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
        self._hk_spot_cache = None

    @staticmethod
    def _to_display_market(market: str):
        return {
            "A": "A股",
            "HK": "港股",
            "US": "美股",
            "INDEX": "指数",
        }.get(market, market)

    @staticmethod
    def _to_display_price_basis(price_basis: str | None):
        return {
            "hfq": "后复权",
            "index": "指数点位",
        }.get(price_basis, price_basis)

    def _format_stock_info_output(self, data: dict) -> dict:
        result = {
            "市场": self._to_display_market(data.get("market")),
            "代码": data.get("display_symbol") or data.get("symbol"),
            "名称": data.get("name"),
            "价格": data.get("price"),
            "市净率": data.get("pb"),
            "股息率": data.get("dividend_yield"),
            "错误": data.get("error"),
        }
        if data.get("market") != "INDEX":
            result.update(
                {
                    "十年价格口径": self._to_display_price_basis(data.get("ten_year_price_basis")),
                    "十年最低价": data.get("ten_year_low"),
                    "十年最高价": data.get("ten_year_high"),
                    "十年当前价": data.get("ten_year_current_price"),
                    "十年分位": data.get("ten_year_percentile"),
                    "十年分位错误": data.get("ten_year_error"),
                }
            )
        if data.get("market") == "INDEX":
            result.update(
                {
                    "蛋卷市盈率": data.get("danjuan_pe"),
                    "蛋卷市净率": data.get("danjuan_pb"),
                    "蛋卷市盈率分位": data.get("danjuan_pe_percentile"),
                    "蛋卷市净率分位": data.get("danjuan_pb_percentile"),
                    "蛋卷股息率": data.get("danjuan_dividend_yield"),
                    "蛋卷ROE": data.get("danjuan_roe"),
                    "蛋卷估值判断": data.get("danjuan_eva_type"),
                    "蛋卷更新时间": data.get("danjuan_update_time"),
                    "蛋卷估值错误": data.get("danjuan_error"),
                }
            )
        return result

    def _call_akshare(self, func, **kwargs):
        return func(**kwargs)

    def _normalize_stock_symbol(self, symbol: str) -> tuple[str, str]:
        stock_symbol = symbol.strip().upper()
        if not stock_symbol:
            raise ValueError("股票代码不能为空")

        us_index_aliases = {
            "SP500": ".INX",
            "S&P500": ".INX",
            "NASDAQ": ".IXIC",
            "IXIC": ".IXIC",
            "DJIA": ".DJI",
            "DJI": ".DJI",
        }
        if stock_symbol in us_index_aliases:
            return "INDEX", us_index_aliases[stock_symbol]

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

        if stock_symbol.startswith("HK") and not stock_symbol[2:].isdigit():
            return "INDEX", stock_symbol

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

    @staticmethod
    def _extract_xq_token_from_cookie(cookie: str | None):
        if not cookie:
            return None
        for item in cookie.split(";"):
            key, sep, value = item.strip().partition("=")
            if sep and key == "xq_a_token" and value:
                return value
        return None

    def _get_xq_token(self):
        return (
            os.getenv("XQ_A_TOKEN")
            or os.getenv("XUEQIU_A_TOKEN")
            or self._extract_xq_token_from_cookie(os.getenv("XUEQIU_COOKIE"))
        )

    @staticmethod
    def _get_danjuan_index_code(original_symbol: str, normalized_symbol: str) -> str:
        stock_symbol = original_symbol.strip().upper()
        if stock_symbol in {"SP500", "S&P500", "NASDAQ", "IXIC", "DJIA", "DJI"}:
            return stock_symbol
        return normalized_symbol

    def _to_xq_symbol(self, market: str, symbol: str) -> str:
        if market == "INDEX":
            return symbol
        if market == "A":
            if symbol.startswith(("4", "8")):
                return f"BJ{symbol}"
            if symbol.startswith(("6", "9")):
                return f"SH{symbol}"
            return f"SZ{symbol}"
        if market == "HK":
            return f"HK{symbol}"
        return symbol

    def _get_hk_spot_cache(self):
        if self._hk_spot_cache is None:
            try:
                self._hk_spot_cache = self._call_akshare(ak.stock_hk_spot)
            except Exception:
                self._hk_spot_cache = self._call_akshare(ak.stock_hk_spot_em)
        return self._hk_spot_cache

    def _get_stock_info_from_hk_spot(self, original_symbol: str, normalized_symbol: str) -> dict:
        quote_df = self._get_hk_spot_cache()
        if quote_df.empty or "代码" not in quote_df.columns:
            raise ValueError(f"{original_symbol} 港股实时行情为空")
        target_row = quote_df[quote_df["代码"].astype(str).str.zfill(5) == normalized_symbol]
        if target_row.empty:
            raise ValueError(f"{original_symbol} 未在港股实时行情中找到")
        row = target_row.iloc[0]
        name = row.get("名称")
        if name is None:
            name = row.get("中文名称")
        price = row.get("最新价")
        ten_year_error = None
        try:
            ten_year_stats = self._get_ten_year_price_stats("HK", original_symbol, normalized_symbol)
        except Exception as exc:
            ten_year_stats = {}
            ten_year_error = f"{exc.__class__.__name__}: {exc}"
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
        return self._format_stock_info_output({
            "market": "HK",
            "display_symbol": original_symbol.strip().upper(),
            "symbol": normalized_symbol,
            "name": name,
            "price": self._to_float(price),
            "pb": None,
            "dividend_yield": None,
            "ten_year_price_basis": ten_year_price_basis,
            "ten_year_low": ten_year_low,
            "ten_year_high": ten_year_high,
            "ten_year_current_price": ten_year_current_price,
            "ten_year_percentile": ten_year_percentile,
            "ten_year_error": ten_year_error,
        })

    def _get_history_symbol(self, market: str, original_symbol: str, normalized_symbol: str) -> str:
        if market == "INDEX":
            return normalized_symbol[2:]
        if market in {"A", "HK"}:
            return normalized_symbol
        stock_symbol = original_symbol.strip().upper()
        if "." in stock_symbol and stock_symbol.split(".", 1)[0].isdigit():
            return stock_symbol
        return normalized_symbol

    @staticmethod
    def _build_ten_year_stats_from_close_series(close_series, price_basis: str) -> dict:
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

    def _get_a_history_stats_from_tx(self, normalized_symbol: str, start_date: str, end_date: str) -> dict:
        tx_symbol = self._to_xq_symbol("A", normalized_symbol).lower()
        hist_df = self._call_akshare(
            ak.stock_zh_a_hist_tx,
            symbol=tx_symbol,
            start_date=start_date,
            end_date=end_date,
            adjust="hfq",
            timeout=AKSHARE_TIMEOUT,
        )
        if hist_df.empty or "close" not in hist_df.columns:
            return {}
        close_series = hist_df["close"].dropna()
        return self._build_ten_year_stats_from_close_series(close_series, "hfq")

    def _get_hk_history_stats_from_sina(self, normalized_symbol: str, start_date: str, end_date: str) -> dict:
        hist_df = self._call_akshare(
            ak.stock_hk_daily,
            symbol=normalized_symbol,
            adjust="hfq",
        )
        if hist_df.empty or "close" not in hist_df.columns:
            return {}
        hist_df = hist_df.copy()
        if "date" in hist_df.columns:
            hist_df["date"] = hist_df["date"].astype(str).str.replace("-", "", regex=False)
            hist_df = hist_df[(hist_df["date"] >= start_date) & (hist_df["date"] <= end_date)]
        close_series = hist_df["close"].dropna()
        return self._build_ten_year_stats_from_close_series(close_series, "hfq")

    def _get_danjuan_index_valuation(self, danjuan_symbol: str) -> dict:
        response = requests.get(
            f"https://danjuanfunds.com/djapi/index_eva/detail/{danjuan_symbol}",
            headers=DANJUAN_HEADERS,
            timeout=REQUEST_TIMEOUT,
        )
        response.raise_for_status()
        payload = response.json()
        data = payload.get("data")
        if not isinstance(data, dict):
            raise ValueError(f"{danjuan_symbol} 不在蛋卷估值覆盖范围内")
        timestamp = data.get("ts")
        update_time = None
        if timestamp:
            try:
                update_time = time.strftime("%Y-%m-%d", time.localtime(timestamp / 1000))
            except (TypeError, ValueError, OSError):
                update_time = None
        return {
            "danjuan_pe": self._to_float(data.get("pe")),
            "danjuan_pb": self._to_float(data.get("pb")),
            "danjuan_pe_percentile": self._to_float(data.get("pe_percentile")),
            "danjuan_pb_percentile": self._to_float(data.get("pb_percentile")),
            "danjuan_dividend_yield": self._to_float(data.get("yeild")),
            "danjuan_roe": self._to_float(data.get("roe")),
            "danjuan_eva_type": data.get("eva_type"),
            "danjuan_update_time": update_time,
        }

    def _get_ten_year_price_stats(self, market: str, original_symbol: str, normalized_symbol: str) -> dict:
        if market == "INDEX":
            return {"ten_year_price_basis": None}

        start_date = (date.today() - timedelta(days=3652)).strftime("%Y%m%d")
        end_date = date.today().strftime("%Y%m%d")
        hist_symbol = self._get_history_symbol(market, original_symbol, normalized_symbol)

        if market == "A":
            try:
                hist_df = self._call_akshare(
                    ak.stock_zh_a_hist,
                    symbol=hist_symbol,
                    period="monthly",
                    start_date=start_date,
                    end_date=end_date,
                    adjust="hfq",
                    timeout=AKSHARE_TIMEOUT,
                )
                if hist_df.empty or "收盘" not in hist_df.columns:
                    return self._get_a_history_stats_from_tx(normalized_symbol, start_date, end_date)
                close_series = hist_df["收盘"].dropna()
                return self._build_ten_year_stats_from_close_series(close_series, "hfq")
            except Exception as em_exc:
                try:
                    return self._get_a_history_stats_from_tx(normalized_symbol, start_date, end_date)
                except Exception as tx_exc:
                    raise ConnectionError(f"em={em_exc}; tx={tx_exc}") from tx_exc
        elif market == "HK":
            try:
                hist_df = self._call_akshare(
                    ak.stock_hk_hist,
                    symbol=hist_symbol,
                    period="monthly",
                    start_date=start_date,
                    end_date=end_date,
                    adjust="hfq",
                )
                if hist_df.empty or "收盘" not in hist_df.columns:
                    return self._get_hk_history_stats_from_sina(normalized_symbol, start_date, end_date)
            except Exception as em_exc:
                try:
                    return self._get_hk_history_stats_from_sina(normalized_symbol, start_date, end_date)
                except Exception as sina_exc:
                    raise ConnectionError(f"em={em_exc}; sina={sina_exc}") from sina_exc
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
        return self._build_ten_year_stats_from_close_series(close_series, price_basis)

    def _get_stock_info_from_xq(self, market: str, original_symbol: str, normalized_symbol: str) -> dict:
        xq_symbol = self._to_xq_symbol(market, normalized_symbol)
        token = self._get_xq_token()
        quote_df = self._call_akshare(
            ak.stock_individual_spot_xq,
            symbol=xq_symbol,
            token=token,
            timeout=AKSHARE_TIMEOUT,
        )
        name = self._find_item_value(quote_df, "名称")
        price = self._to_float(self._find_item_value(quote_df, "现价"))
        pb = self._to_float(self._find_item_value(quote_df, "市净率"))
        dividend_yield = self._to_float(self._find_item_value(quote_df, "股息率(TTM)"))
        ten_year_error = None
        try:
            ten_year_stats = self._get_ten_year_price_stats(market, original_symbol, normalized_symbol)
        except Exception as exc:
            ten_year_stats = {}
            ten_year_error = f"{exc.__class__.__name__}: {exc}"
        ten_year_price_basis = ten_year_stats.get("ten_year_price_basis")
        ten_year_low = ten_year_stats.get("ten_year_low")
        ten_year_high = ten_year_stats.get("ten_year_high")
        ten_year_current_price = ten_year_stats.get("ten_year_current_price")
        danjuan_data = {}
        danjuan_error = None
        if market == "INDEX":
            try:
                danjuan_symbol = self._get_danjuan_index_code(original_symbol, normalized_symbol)
                danjuan_data = self._get_danjuan_index_valuation(danjuan_symbol)
            except Exception as exc:
                danjuan_error = f"{exc.__class__.__name__}: {exc}"
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

        return self._format_stock_info_output({
            "market": market,
            "display_symbol": original_symbol.strip().upper(),
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
            "ten_year_error": ten_year_error,
            "danjuan_pe": danjuan_data.get("danjuan_pe"),
            "danjuan_pb": danjuan_data.get("danjuan_pb"),
            "danjuan_pe_percentile": danjuan_data.get("danjuan_pe_percentile"),
            "danjuan_pb_percentile": danjuan_data.get("danjuan_pb_percentile"),
            "danjuan_dividend_yield": danjuan_data.get("danjuan_dividend_yield"),
            "danjuan_roe": danjuan_data.get("danjuan_roe"),
            "danjuan_eva_type": danjuan_data.get("danjuan_eva_type"),
            "danjuan_update_time": danjuan_data.get("danjuan_update_time"),
            "danjuan_error": danjuan_error,
        })

    def _get_single_stock_info_safe(self, original_symbol: str, market: str, normalized_symbol: str) -> dict:
        try:
            if market == "HK":
                return self._get_stock_info_from_hk_spot(original_symbol, normalized_symbol)
            return self._get_stock_info_from_xq(market, original_symbol, normalized_symbol)
        except ValueError:
            raise
        except Exception as exc:
            price_basis = "index" if market == "INDEX" else "hfq"
            return self._format_stock_info_output({
                "market": market,
                "display_symbol": original_symbol.strip().upper(),
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
                "ten_year_error": None,
                "danjuan_pe": None,
                "danjuan_pb": None,
                "danjuan_pe_percentile": None,
                "danjuan_pb_percentile": None,
                "danjuan_dividend_yield": None,
                "danjuan_roe": None,
                "danjuan_eva_type": None,
                "danjuan_update_time": None,
                "danjuan_error": None,
                "error": f"{original_symbol} 查询失败: {exc.__class__.__name__}: {exc}",
            })

    def get_stock_infos_akshare(self, symbols: list[str]) -> list[dict]:
        normalized_items = []
        for symbol in symbols:
            market, normalized_symbol = self._normalize_stock_symbol(symbol)
            normalized_items.append((symbol, market, normalized_symbol))
        if any(market == "HK" for _, market, _ in normalized_items):
            try:
                self._get_hk_spot_cache()
            except Exception:
                pass

        result = [None] * len(normalized_items)
        parallel_items = []
        serial_items = []
        for index, item in enumerate(normalized_items):
            if item[1] == "HK":
                serial_items.append((index, item))
            else:
                parallel_items.append((index, item))

        if parallel_items:
            max_workers = min(AKSHARE_MAX_WORKERS, len(parallel_items))
            with ThreadPoolExecutor(max_workers=max_workers) as executor:
                future_to_index = {
                    executor.submit(
                        self._get_single_stock_info_safe,
                        original_symbol,
                        market,
                        normalized_symbol,
                    ): index
                    for index, (original_symbol, market, normalized_symbol) in parallel_items
                }
                for future in as_completed(future_to_index):
                    index = future_to_index[future]
                    result[index] = future.result()

        for index, (original_symbol, market, normalized_symbol) in serial_items:
            result[index] = self._get_single_stock_info_safe(
                original_symbol,
                market,
                normalized_symbol,
            )
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
