# VVQuest API 文档

## 目录

1. [接口概览](#接口概览)
2. [接口详情](#接口详情)
3. [API 配置文件说明](#api-配置文件说明)

## 接口概览

| 接口路径           | 方法 | 描述                     |
|--------------------|------|--------------------------|
| `/search`          | POST | 执行图片搜索             |
| `/generate-cache`  | POST | 触发缓存生成（后台任务） |
| `/config`          | GET  | 获取当前配置             |
| `/api-config`      | PUT  | 更新API配置              |
| `/download-model`  | POST | 下载指定模型             |
| `/models`          | GET  | 获取可用模型列表         |
| `/mode/{mode}`     | PUT  | 切换运行模式             |
| `/model/{model_id}`| PUT  | 切换本地模型             |

## 接口详情

### 1. 搜索图片

- **路径**: `/search`
- **方法**: POST
- **描述**: 执行图片搜索
- **请求体** (application/json):

  ```json
  {
    "query": "搜索关键词",
    "n_results": 5  // 可选，默认值 5
  }
  ```

- **成功响应**
  - 状态码: 200
  - 内容: JSON 格式数据（具体字段需参考实现）

- **错误响应**
  - 状态码: 422 (请求体验证失败)

### 2. 生成缓存

- **路径**: `/generate-cache`
- **方法**: POST
- **描述**: 触发后台缓存生成任务
- **成功响应**
  - 状态码: 200
  - 内容: JSON 格式空对象

### 3. 获取配置

- **路径**: `/config`
- **方法**: GET
- **描述**: 获取当前API配置
- **成功响应**
  - 状态码: 200
  - 内容: JSON 格式配置信息

### 4. 更新配置

- **路径**: `/api-config`
- **方法**: PUT
- **描述**: 更新API配置
- **请求体** (application/json):

  ```json
  {
    "api_key": "新的API密钥",  // 可选（可为 null）
    "base_url": "新的基础URL"  // 可选（可为 null）
  }
  ```

- **成功响应**
  - 状态码: 200
  - 内容: JSON 格式空对象

- **错误响应**
  - 状态码: 422 (请求体验证失败)

### 5. 下载模型

- **路径**: `/download-model`
- **方法**: POST
- **描述**: 下载指定模型
- **请求体** (application/json):

  ```json
  {
    "model_id": "模型ID"
  }
  ```

- **成功响应**
  - 状态码: 200
  - 内容: JSON 格式空对象

- **错误响应**
  - 状态码: 422 (请求体验证失败)

### 6. 模型列表

- **路径**: `/models`
- **方法**: GET
- **描述**: 获取可用模型列表
- **成功响应**
  - 状态码: 200
  - 内容: JSON 格式模型列表

### 7. 切换模式

- **路径**: `/mode/{mode}`
- **方法**: PUT
- **描述**: 切换系统运行模式
- **路径参数**
  - `mode` (字符串): 目标模式名称
- **成功响应**
  - 状态码: 200
  - 内容: JSON 格式空对象

- **错误响应**
  - 状态码: 422 (参数验证失败)

### 8. 切换模型

- **路径**: `/model/{model_id}`
- **方法**: PUT
- **描述**: 切换本地使用的模型
- **路径参数**
  - `model_id` (字符串): 目标模型ID
- **成功响应**
  - 状态码: 200
  - 内容: JSON 格式空对象

- **错误响应**
  - 状态码: 422 (参数验证失败)

## API 配置文件说明

API 配置文件为 `/config/api_config.yaml` ，用于配置 API 的行为。

### 全局配置

```yaml
api:
  generate_cache: False      # 是否自动生成缓存（默认关闭）
```

- **作用**
  - 当 `generate_cache: True` 时，系统启动后自动执行缓存生成任务。

### 端点权限控制

```yaml
protected_mode: False      # 是否启用保护模式（默认关闭）
allowed_endpoints:
  - "/search"                # 允许访问的API端点（仅保护模式开启时生效）
```

- **作用**
  - 当 `protected_mode: True` 时，仅列出的端点可被外部访问。
  - 默认允许 `/search`，其他接口需手动添加（如 `/config`）。

### 请求限流配置

```yaml
rate_limit:
  enabled: True              # 是否启用请求限流
  requests: 10               # 每分钟最大请求数
  window: 60                 # 时间窗口（单位：秒）
  storage: "memory"          # 限流计数存储方式（支持 memory/redis）
```

- **参数说明**

  | 字段       | 类型   | 可选值            | 说明                          |
  |------------|--------|-------------------|-------------------------------|
  | `enabled`  | bool   | `True`/`False`    | 是否启用限流                  |
  | `requests` | int    | 正整数            | 单位时间窗口内允许的最大请求数 |
  | `window`   | int    | 正整数（秒）      | 限流时间窗口长度              |
  | `storage`  | string | `memory`/`redis`  | 计数器存储方式                |

- **示例场景**
  - `requests: 10` + `window: 60` 表示每60秒最多处理 10 次请求。
  - 若使用 `redis` 存储，需确保 Redis 服务已配置并连接。

### 运行模式配置

```yaml
mode: "local"                # 系统运行模式（api/local）
api_mode_config:
  default_api_key: "your-key-here"     # API 默认密钥
  default_base_url: "https://api.example.com"  # API 默认服务地址
model: "bge-m3"            # 当前使用的模型ID（需与模型列表匹配）
```

- **模式说明**

  | 模式值    | 描述                                                                 |
  |-----------|----------------------------------------------------------------------|
  | `local`   | 本地模式，优先使用本地模型和资源                                     |
  | `api`     | API 模式，依赖外部服务（需配置 `api_mode_config` 中的密钥和基础URL） |

- **API 模式专用配置**
  - `default_api_key`: 调用外部 API 所需的身份凭证（建议通过环境变量注入）。
  - `default_base_url`: 外部 API 服务的基础地址（例如 OpenAI 兼容接口）。

- **本地模式专用配置**
  - `model`: 当前使用的模型ID（需与 `models` 配置中的模型ID一致）。

> 修改配置后，请重启服务以生效。
