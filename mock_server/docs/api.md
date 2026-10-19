# 商城 Mock 服务接口文档

基础地址：`http://127.0.0.1:5000`

## 1. 通用约定

### 1.1 统一响应结构

所有接口返回 JSON：

```json
{"code": 0, "msg": "success", "data": {...}}
```

| 字段 | 说明 |
|------|------|
| code | 业务错误码，0 表示成功 |
| msg  | 提示信息 |
| data | 业务数据，失败时为 null |

### 1.2 HTTP 状态码约定

| HTTP 状态 | 含义 |
|-----------|------|
| 200 | 请求成功，或业务失败（以 code 判断） |
| 400 | 参数错误（code=1001） |
| 401 | 未登录或 token 无效/过期（code=1002） |
| 403 | 无权限（code=1003） |

### 1.3 错误码表

| code | 含义 |
|------|------|
| 0    | 成功 |
| 1001 | 参数缺失/类型/格式错误 |
| 1002 | 未登录或 token 无效/过期 |
| 1003 | 无权限 |
| 2001 | 用户名已存在 |
| 2002 | 用户不存在 |
| 2003 | 密码错误 |
| 3001 | 商品不存在 |
| 3002 | 商品已下架 |
| 3003 | 库存不足 |
| 4001 | 购物车为空 |
| 4002 | 购物车项不存在 |
| 5001 | 订单不存在 |
| 5002 | 订单状态不允许该操作 |
| 5003 | 余额不足 |
| 5004 | 订单已支付（重复支付） |

### 1.4 鉴权方式

登录类接口返回 `data.token`，后续请求在请求头携带：

```
Authorization: Bearer <token>
```

### 1.5 订单状态机

```
pending(待支付) --取消--> canceled(已取消)
pending(待支付) --支付--> paid(已支付) --确认收货--> completed(已完成)
```

| 当前状态 | 可执行操作 |
|----------|-----------|
| pending  | 取消、支付 |
| paid     | 确认收货 |
| completed / canceled | 不可再操作 |

## 2. 用户模块 `/api/users`

### 2.1 注册

- `POST /api/users/register`
- 参数（JSON）：`username`(必填,3-20字符)、`password`(必填,6-20字符)、`nickname`(可选)
- 成功：`code=0`，返回用户信息；用户名已存在返回 `code=2001`

### 2.2 登录

- `POST /api/users/login`
- 参数（JSON）：`username`、`password`
- 成功：`code=0`，返回 `{token, user}`；用户不存在 `code=2002`；密码错误 `code=2003`

### 2.3 获取当前用户信息

- `GET /api/users/me`（需登录）
- 成功：`code=0`，返回用户信息（含余额 balance）

### 2.4 修改当前用户资料

- `PUT /api/users/me`（需登录）
- 参数（JSON）：`nickname`(必填)
- 成功：`code=0`，返回更新后的用户信息

## 3. 商品模块 `/api/products`

### 3.1 商品列表

- `GET /api/products`
- Query 参数：`page`(默认1)、`page_size`(默认10)、`category`、`keyword`（名称模糊搜索）
- 仅返回上架商品，成功返回 `{total, page, page_size, items}`

### 3.2 商品详情

- `GET /api/products/{id}`
- 商品不存在返回 `code=3001`

## 4. 购物车模块 `/api/cart`（均需登录）

### 4.1 加购

- `POST /api/cart/items`
- 参数（JSON）：`product_id`(必填)、`quantity`(默认1,正整数)
- 商品不存在 `code=3001`；已下架 `code=3002`；超库存 `code=3003`

### 4.2 查看购物车

- `GET /api/cart`
- 返回 `{items: [{id, product_id, product_name, price, quantity, total}]}`

### 4.3 修改数量

- `PUT /api/cart/items/{id}`
- 参数（JSON）：`quantity`(必填,正整数)
- 购物车项不存在 `code=4002`

### 4.4 删除购物车项

- `DELETE /api/cart/items/{id}`
- 购物车项不存在 `code=4002`

## 5. 订单模块 `/api/orders`（均需登录）

### 5.1 下单

- `POST /api/orders`
- 参数（JSON）：`cart_item_ids`(可选，指定购物车项，默认全部)
- 从购物车创建订单，扣减库存并清空购物车项；购物车为空 `code=4001`；库存不足 `code=3003`
- 成功返回订单信息（含 `order_no`、`status=pending`、`total_amount`、`items` 快照）

### 5.2 订单列表

- `GET /api/orders`
- Query 参数：`page`(默认1)、`page_size`(默认10)
- 仅返回本人订单，返回 `{total, page, page_size, items}`

### 5.3 订单详情

- `GET /api/orders/{id}`
- 仅本人可见，订单不存在 `code=5001`

### 5.4 取消订单

- `POST /api/orders/{id}/cancel`
- 仅 `pending` 可取消，返还库存；非 `pending` 返回 `code=5002`

### 5.5 支付订单

- `POST /api/orders/{id}/pay`
- 仅 `pending` 可支付，校验并扣减余额；余额不足 `code=5003`；重复支付 `code=5004`；其他状态 `code=5002`

### 5.6 确认收货

- `POST /api/orders/{id}/confirm`
- 仅 `paid` 可确认，变为 `completed`；其他状态 `code=5002`

## 6. 后台管理 `/api/admin`

### 6.1 管理员登录

- `POST /api/admin/login`
- 参数（JSON）：`username`、`password`
- 仅 `role=admin` 可登录成功，否则 `code=1003`；成功返回 `{token, user}`

### 6.2 新增商品（需管理员）

- `POST /api/admin/products`
- 参数（JSON）：`name`(必填)、`price`(必填,>0)、`stock`(必填,>=0整数)、`category`(必填)、`description`(可选)

### 6.3 上架/下架商品（需管理员）

- `PUT /api/admin/products/{id}/status`
- 参数（JSON）：`status`(必填, `on`/`off`)
- 普通用户调用返回 HTTP 403 / `code=1003`
