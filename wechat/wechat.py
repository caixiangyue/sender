import requests
HEADERS = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36", "Content-Type": "application/x-www-form-urlencoded"}


class Wechat:
    def __init__(self, title, msg, send_key):
        self.url = 'https://sctapi.ftqq.com/'
        self.msg = msg
        self.send_key = send_key
        self.title = title 
        
    def send(self):
        url = f'{self.url}{self.send_key}.send'
        data = {'title':self.title, 'desp':self.msg}
        requests.post(url=url, headers=HEADERS, data=data)


