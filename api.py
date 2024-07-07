from .user_types import *
from typing import Optional, Union
import aiohttp
from aiohttp.hdrs import METH_GET, METH_POST, METH_DELETE, METH_PUT

class Response():
    def __init__(self, status: int, json: Union[dict, None] = None):
        self.status_code = status
        self.json = json


class MarzbanApi():
    def __init__(self, user_name: str, passwoard: str, server_url: str, timeout: float = None):
        self.user_name = user_name
        self.passwoard = passwoard
        self.server_url = server_url
        self._timeout = timeout
        self.headers = {"accept": "application/json"}
        self._session = None

    async def get_new_session(self) -> aiohttp.ClientSession:
        return aiohttp.ClientSession()

    async def get_session(self) -> Optional[aiohttp.ClientSession]:
        if self._session is None or self._session.closed:
            self._session = await self.get_new_session()

        if not self._session._loop.is_running():
            await self._session.close()
            self._session = await self.get_new_session()

        return self._session

    async def make_request(self, method: str, url: str, data: dict = None, timeout: float = None, **kwarg):
        if timeout:
            timeout = aiohttp.ClientTimeout(timeout)
        else:
            timeout = self._timeout
        url = f'{self.server_url}/{url}'
        session = await self.get_session()
        async with session.request(method, url, data=data, timeout=timeout, headers=self.headers, **kwarg) as response:
            return Response(response.status, await response.json())
    
    async def authorize(self):
        data = {
            "username": self.user_name,
            "password": self.passwoard
        }
        response = await self.make_request(METH_POST, "api/admin/token", data)
        token = response.json.get("access_token")
        self.headers["Authorization"] = f"Bearer {token}"
        return response.json
    
    async def get_keys(self):
        response = await self.make_request(METH_GET, 'api/users')
        return [User(**user) for user in response.json.get('users')]
    
    async def create_key(self, key_name, data_limit=0) -> User:
        data = {
            "username": f'id{key_name}',
            "note":"",
            "proxies":{"vmess":{},"vless":{"flow":""},"trojan":{},"shadowsocks":{"method":"chacha20-ietf-poly1305"}},
            "data_limit":data_limit,
            "expire": None, 
            "data_limit_reset_strategy":"no_reset",
            "status":"active",
            "inbounds":{"vmess":["VMess TCP","VMess Websocket"],"vless":["VLESS TCP REALITY","VLESS GRPC REALITY"],"trojan":["Trojan Websocket TLS"],"shadowsocks":["Shadowsocks TCP"]}
        }
        response = await self.make_request(METH_POST, 'api/user', json=data)
        return User(**response.json)
    
    async def delete_key(self, key_name) -> bool:
        response = await self.make_request(METH_DELETE, f'api/user/id{key_name}')
        return response.status_code == 200
    
    async def get_key(self, key_name) -> User:
        response = await self.make_request(METH_GET, f'api/user/id{key_name}')
        return User(**response.json)
    
    async def add_data_limit(self, key_name: str, limit_bytes: int = 0, is_del = False) -> bool:
        if limit_bytes == 0 and not is_del:
            data = {"status": "disabled"}
        else:
            data = {"status": "active", 'data_limit': limit_bytes}
        response = await self.make_request(METH_PUT, f'api/user/id{key_name}', json=data)
        return response.status_code == 200
    
    async def delete_data_limit(self, key_name: str) -> bool:
        return await self.add_data_limit(key_name, is_del=True)
