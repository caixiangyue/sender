import requests
import time
from lxml import etree

from common.utils import HEADERS
# HEADERS = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36"}
URL = "https://github.com/trending"
URL1 = 'https://github.com/ruanyf/weekly/tree/master/docs'

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
        
        jsons = r.json()
        max_num = 0
        if jsons:
            items = jsons['payload']['tree']['items']
            for item in items:
                path = item['path']
                # ''.lstrip
                Num = path.rstrip('.md').lstrip('docs/issue-')
                if Num[0] >= '0' and Num[0] <= '9':
                    max_num = max(max_num, int(Num))
        ret += f'周刊: https://github.com/ruanyf/weekly/blob/master/docs/issue-{max_num}.md\n'
        return ret


# c = Crawler()
# print(c.get_trending_msg())