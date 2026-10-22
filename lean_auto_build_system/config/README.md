# API Configuration Instructions

## Configuration File Location
`config/api_config.json`

## First Time Use

1. Copy the example configuration file:
```bash
cp config/api_config.example.json config/api_config.json
```

2. Edit `config/api_config.json` and fill in your API key:
```json
{
  "api_key": "your-actual-api-key-here",
  "base_url": "https://api.openai.com/v1",
  "model": "gpt-4"
}
```

## Configuration Fields

| Field | Description | Default Value |
|-------|-------------|---------------|
| `api_key` | API key (required) | - |
| `base_url` | API endpoint URL | `https://api.openai.com/v1` |
| `model` | Model name to use | `gpt-4` |

## Supported API Providers

### OpenAI
```json
{
  "api_key": "sk-xxxx",
  "base_url": "https://api.openai.com/v1",
  "model": "gpt-4"
}
```

### DeepSeek
```json
{
  "api_key": "sk-xxxx",
  "base_url": "https://api.deepseek.com",
  "model": "deepseek-chat"
}
```

### Other OpenAI API Compatible Services
Simply modify `base_url` and `model` as needed.

## Security Notes

⚠️ **Important**:
- `api_config.json` is in `.gitignore` and will not be committed to git
- Do not share configuration files containing real API keys with others
- Do not hardcode API keys into the code

## Obtaining API Keys

### OpenAI
1. Visit [https://platform.openai.com/api-keys](https://platform.openai.com/api-keys)
2. Login to your account
3. Create a new API key

### DeepSeek
1. Visit [https://platform.deepseek.com/](https://platform.deepseek.com/)
2. Register/login to your account
3. Create API key in the console
