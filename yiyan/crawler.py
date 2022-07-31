import requests
import time

from common.utils import HEADERS

URL = 'https://v1.hitokoto.cn/'

class Crawler:
    def __init__(self):
        pass

    def get_msg(self) -> str:
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
            
        json_dict = r.json()
        ret = ''
        if 'hitokoto' in json_dict and 'from' in json_dict:
            ret += f'{json_dict["hitokoto"]}        ——{json_dict["from"]}\n'
        ret += '-----------------------\n\n'
        return ret

# c = Crawler()
# print(c.get_msg())