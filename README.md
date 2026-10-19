# 接口自动化测试项目

面向测开岗位的个人练手项目：自建 Flask 商城 Mock 服务作为被测系统，搭建 pytest + requests 接口自动化测试框架。

## 项目结构

```
api_auto_test/
├── mock_server/      # 被测系统：商城 Mock 服务
│   ├── app.py        # 服务入口
│   ├── config.py     # 配置
│   ├── models.py     # 数据模型（用户/商品/购物车/订单）
│   ├── auth.py       # JWT 鉴权
│   ├── response.py   # 统一响应结构与错误码
│   ├── routes/       # 五大业务模块路由
│   ├── seed.py       # 种子数据
│   └── docs/         # 接口文档
└── (后续阶段新增测试框架目录)
```

## 当前进度

- [x] P0 商城 Mock 服务（接口文档见 `mock_server/docs/api.md`）
- [ ] P1 框架骨架
- [ ] P2 接口对象 + 单接口用例
- [ ] P3 数据驱动
- [ ] P4 全链路场景用例
- [ ] P5 Allure 报告
- [ ] P6 CI 集成

## 启动 Mock 服务

```bash
pip install -r requirements.txt
python -m mock_server.app
```

默认地址 `http://127.0.0.1:5000`，种子账号：`admin/admin123`（管理员）、`user01/123456`（普通用户）。
