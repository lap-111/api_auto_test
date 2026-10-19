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
├── api/               # 业务层：接口对象封装（User/Product/Cart/Order/Admin）
├── core/             # 测试框架核心层
│   ├── config.py     # 环境配置加载（--env 切换 dev/test）
│   ├── logger.py     # 日志（控制台 + 文件）
│   ├── http_client.py# 请求封装（统一响应/token 注入/重试）
│   ├── assert_utils.py # 断言工具（状态码/code/字段/类型/长度）
│   ├── data_loader.py  # YAML 数据驱动加载器（占位符解析）
│   └── factory.py      # 测试数据工厂（造数 + 多用户 token 切换）
├── config/           # YAML 环境配置
├── data/             # YAML 用例数据（login/register/product_list/cart_add）
├── testcase/         # 用例层（pytest）
├── conftest.py       # 全局 fixture（config/client）
└── pytest.ini        # pytest 配置
```

## 当前进度

- [x] P0 商城 Mock 服务（接口文档见 `mock_server/docs/api.md`）
- [x] P1 框架骨架（请求封装/日志/配置/断言工具，冒烟用例跑通）
- [x] P2 接口对象 + 单接口用例（五大模块 84 条正反场景用例，接口全覆盖）
- [x] P3 数据驱动（YAML 用例数据 + pytest 参数化，参数用例数据与代码分离）
- [x] P4 全链路场景用例（完整购物流程/订单状态机/多用户隔离/支付与下架场景，数据工厂造数）
- [ ] P5 Allure 报告
- [ ] P6 CI 集成

## 启动 Mock 服务

```bash
pip install -r requirements.txt
python -m mock_server.app
```

默认地址 `http://127.0.0.1:5000`，种子账号：`admin/admin123`（管理员）、`user01/123456`（普通用户）。
