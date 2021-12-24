import requests
import json

URL = 'http://t.weather.itboy.net/api/weather/city/101010100'

class Crawler:
    def __init__(self):
        pass

    def get_weather(self) -> str:
        r = requests.get(URL)
        json_dict = r.json()
        json_data = json_dict['data']
        json_forecast = json_data['forecast']
        ret = f'查询北京天气。。。。返回码：{r.status_code}\n'
        ret += f'{json_forecast[0]["week"]}\n'
        ret += f'空气质量：{json_data["quality"]}\n'
        ret += f'提示：{json_data["ganmao"]}\n'
        ret += f'{json_forecast[0]["type"]} {json_forecast[0]["low"]} {json_forecast[0]["high"]}\n'
        ret += f'{json_forecast[0]["fx"]} {json_forecast[0]["fl"]}\n'
        ret += f'日出 {json_forecast[0]["sunrise"]} 日落 {json_forecast[0]["sunset"]}\n'
        ret += '-----------------------\n'
        ret += f'{json_forecast[1]["week"]}\n'
        ret += f'{json_forecast[1]["type"]} {json_forecast[1]["low"]} {json_forecast[1]["high"]}\n'
        ret += f'{json_forecast[1]["fx"]} {json_forecast[1]["fl"]}\n'
        ret += f'日出 {json_forecast[1]["sunrise"]} 日落 {json_forecast[1]["sunset"]}\n'
        return ret
