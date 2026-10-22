# API Configuration Instructions

## Configuration File Location

`config/api_config.json`

## First Time Use

1. Copy the example configuration file:

```bash
cp config/api_config.example.json config/api_config.json
```

1. Edit `config/api_config.json` and fill in your API key:

```json
{
  "api_key": "your-actual-api-key-here",
  "base_url": "https://api.deepseek.com",
  "model": "deepseek-chat"
}
```

## Configuration Fields

| Field      | Description        | Default Value              |
| ---------- | ------------------ | -------------------------- |
| `api_key`  | API key (required) | -                          |
| `base_url` | API endpoint URL   | `https://api.deepseek.com` |
| `model`    | Model name to use  | `deepseek-chat`            |

## Supported API Providers

### DeepSeek (Default)

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

### Other OpenAI API Compatible Services

Simply modify `base_url` and `model` as needed.

## Security Notes

- **Never commit** `api_config.json` to version control
- The file is already in `.gitignore`
- Keep your API key secure and private

## Obtaining API Keys

### DeepSeek

1. Visit <https://platform.deepseek.com/>
2. Register/login to your account
3. Create API key in the console

### OpenAI

1. Visit <https://platform.openai.com/api-keys>
2. Login to your account
3. Create a new API key
