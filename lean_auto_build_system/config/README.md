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
  "base_url": "http://113.45.39.247:3001/v1",
  "model": "gpt-5.6-sol"
}
```

## 配置项说明

| 字段 | 说明 | 默认值 |
|------|------|--------|
| `api_key` | API密钥（必填） | - |
| `base_url` | API端点URL | `http://113.45.39.247:3001/v1` |
| `model` | 使用的模型名称 | `gpt-5.6-sol` |

## 支持的API提供商

### 内部服务器（默认）
```json
{
  "api_key": "sk-xxxx",
  "base_url": "http://113.45.39.247:3001/v1",
  "model": "gpt-5.6-sol"
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

⚠️ **重要**：
- `api_config.json` 已被加入 `.gitignore`，不会被提交到git
- 不要将包含真实API密钥的配置文件分享给他人
- 不要将API密钥硬编码到代码中

## 获取API密钥

请联系系统管理员获取内部服务器的API密钥。
