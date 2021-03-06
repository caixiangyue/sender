import requests
import time
from lxml import etree

from common.utils import HEADERS

URL = "https://github.com/trending"

class Crawler:
    def __init__(self) -> None:
        pass

    def get_trending_msg(self):
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

        ret = '获取 github trending 。。。\n'
        dom = etree.HTML(r.content)
        div = dom.xpath('//div[@class="Box"]/div[2]')
        for i in range(20):
            text_list = div[0].xpath(f'//article[{i+1}]/h1/a/text()')
            href_list = div[0].xpath(f'//article[{i+1}]/h1/a/@href')
            if len(text_list) == 0 or len(href_list) == 0:
                break

            p_list = div[0].xpath(f'//article[{i+1}]/p/text()')
            href = f'https://github.com{href_list[0]}'
            
            text = ''
            for t in text_list:
                text += t.strip().replace('\n', '')
            desc = ''
            for p in p_list:
                desc += p
            
            ret += f'{i+1} {text}\n'
            ret += f'{desc}\n'
            ret += f'{href}\n'
        ret += '\n'
        return ret

            

# c = Crawler()
# print(c.get_trending_msg())