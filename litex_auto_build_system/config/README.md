# API配置说明

## 配置文件位置
`config/api_config.json`

## 首次使用

1. 复制示例配置文件：
```bash
cp config/api_config.example.json config/api_config.json
```

2. 编辑 `config/api_config.json`，填入你的API密钥：
```json
{
  "api_key": "your-actual-api-key-here",
  "base_url": "https://api.deepseek.com",
  "model": "deepseek-chat"
}
```

## 配置项说明

| 字段 | 说明 | 默认值 |
|------|------|--------|
| `api_key` | API密钥（必填） | - |
| `base_url` | API端点URL | `https://api.deepseek.com` |
| `model` | 使用的模型名称 | `deepseek-chat` |

## 支持的API提供商

### DeepSeek（默认）
```json
{
  "api_key": "sk-xxxx",
  "base_url": "https://api.deepseek.com",
  "model": "deepseek-chat"
}
```

### OpenAI
```json
{
  "api_key": "sk-xxxx",
  "base_url": "https://api.openai.com/v1",
  "model": "gpt-4"
}
```

### 其他兼容OpenAI API的服务
只需修改 `base_url` 和 `model` 即可。

## 安全注意事项

## 获取API密钥

### DeepSeek
1. 访问 [https://platform.deepseek.com/](https://platform.deepseek.com/)
2. 注册/登录账号
3. 在控制台创建API密钥

### OpenAI
1. 访问 [https://platform.openai.com/api-keys](https://platform.openai.com/api-keys)
2. 登录账号
3. 创建新的API密钥
