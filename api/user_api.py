"""用户模块接口对象"""


class UserApi:

    def __init__(self, client):
        self.client = client

    def register(self, username, password, nickname=None):
        """注册"""
        data = {"username": username, "password": password}
        if nickname is not None:
            data["nickname"] = nickname
        return self.client.post("/api/users/register", json=data)

    def login(self, username, password):
        """登录，返回含 token 的响应"""
        return self.client.post("/api/users/login", json={"username": username, "password": password})

    def get_me(self):
        """获取当前用户信息"""
        return self.client.get("/api/users/me")

    def update_me(self, nickname):
        """修改昵称"""
        return self.client.put("/api/users/me", json={"nickname": nickname})
