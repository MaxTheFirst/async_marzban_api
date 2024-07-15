from dataclasses import dataclass

@dataclass
class __URLs:
    vwess_tcp: str
    vwess_ws: str
    vless_tcp: str
    vless_ws: str
    trojan: str
    shadowsocks: str


class URLs(__URLs):
    def __init__(self, *urls):
        self.urls = self.__clear_urls(urls)
        super().__init__(*self.urls)

    def __clear_urls(self, urls):
        urls =  list(urls)
        for index in range(len(urls)):
            if '#' in urls[index]:
                urls[index] = urls[index].split('#')[0]
        return urls

class User:
    def __init__(self, username, data_limit=0, used_traffic=None, links=[], *args, **kwargs):
        self.name: str = username
        self.user_id = self.__get_user_id(username)
        try:
            self.access_urls = URLs(*links)
        except TypeError:
            self.access_urls = None
        self.used_bytes: int = used_traffic
        self.data_limit: int = data_limit
    
    def __get_user_id(self, name: str):
        if 'id' in name:
            return int(name.replace('id', '').replace('m', '-'))