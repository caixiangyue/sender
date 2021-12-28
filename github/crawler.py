import requests
import time
from lxml import etree

URL = "https://github.com/trending"

class Crawler:
    def __init__(self) -> None:
        pass

    def get_trending_msg(self):
        retry_times = 3
        while retry_times > 0:
            try:
                r = requests.get(URL)
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
        for i in range(25):
            text = div[0].xpath(f'//article[{i+1}]/h1/a/text()')[2]
            href = div[0].xpath(f'//article[{i+1}]/h1/a/@href')[0]
            p = div[0].xpath(f'//article[{i+1}]/p/text()')
            href = f'https://github.com{href}'
            desc = ''
            for d in p:
                desc += d
            
            ret += f'{i+1} {text}\n'
            ret += f'{desc}\n'
            ret += f'{href}\n'
        ret += '\n'
        return ret

            

# c = Crawler()
# print(c.get_trending_msg())