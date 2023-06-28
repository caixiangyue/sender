import requests
import time

from common.utils import HEADERS

URL = 'http://t.weather.itboy.net/api/weather/city/101010100'

class Crawler:
    def __init__(self):
        pass

    def get_weather_msg(self) -> str:
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

        json_dict = r.json()
        json_data = json_dict.get('data', None)
        if json_data is None:
            return ''
        json_forecast = json_data['forecast']
        ret = f'查询北京天气。。。\n'
        ret += f'{json_forecast[0]["week"]}\n'
        ret += f'空气质量：{json_data["quality"]}\n'
        ret += f'提示：{json_data["ganmao"]}\n'
        ret += f'{json_forecast[0]["type"]} {json_forecast[0]["low"]} {json_forecast[0]["high"]}\n'
        ret += f'{json_forecast[0]["fx"]} {json_forecast[0]["fl"]}\n'
        ret += f'日出 {json_forecast[0]["sunrise"]} 日落 {json_forecast[0]["sunset"]}\n'
        ret += '-----------------------\n\n'
        return ret
