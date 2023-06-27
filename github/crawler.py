import requests
import time
from lxml import etree

from common.utils import HEADERS
# HEADERS = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36"}
URL = "https://github.com/trending"
URL1 = 'https://github.com/ruanyf/weekly/blob/master/README.md'

class Crawler:
    def __init__(self) -> None:
        pass

    def get_trending_msg(self):
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

        ret = '获取 github trending 。。。\n'
        dom = etree.HTML(r.content)
        div = dom.xpath('//div[@class="Box"]/div[2]')
        for i in range(25):
            text_list = div[0].xpath(f'//article[{i+1}]/h2/a/text()')

            href_list = div[0].xpath(f'//article[{i+1}]/h2/a/@href')
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

    def get_weekly(self):
        retry_times = 3
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

        ret = ''
        dom = etree.HTML(r.content)
        res = dom.xpath('//*[@id="readme"]/article/ul[1]/li[1]/a')
        if len(res) > 0:
            title = res[0].xpath('./text()')[0]
            href = res[0].xpath('./@href')[0]
        ret += f'{title}: https://github.com{href}\n'
        return ret


# c = Crawler()
# print(c.get_trending_msg())