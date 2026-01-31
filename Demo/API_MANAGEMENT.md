# API Key Management & Integration Strategy

## 🛡️ Security Protocol
为了确保 `Gemini 3 Pro` API 密钥的安全性和易管理性，本项目采用环境变量注入与本地配置文件相结合的策略。严禁将 API Key 硬编码在源代码中。

## 🔑 Key Storage Architecture

### 1. Environment Variables (Primary)
在生产环境或 CI/CD 流程中，优先从系统环境变量中读取。
- **Variable Name**: `GOOGLE_API_KEY`
- **Integration**: Trae IDE 或其他集成工具会自动将此变量注入到运行环境中。

### 2. Local Configuration (Development Fallback)
在本地开发环境中，使用 `.env` 文件或专门的 `api_key.txt` 文件作为后备。
- **File Path**: `/Users/starryyu/Documents/Cargo/MVP/api_key.txt` (已存在)
- **Format**: 纯文本，仅包含密钥字符串，无空格或换行。
- **Git Ignore**: 确保 `api_key.txt` 和 `.env` 被添加到 `.gitignore` 中，防止泄露。

## 🔌 Implementation (Python)

我们将在 `MVP` 目录下创建一个统一的密钥管理模块 `key_manager.py` (建议新建)，或者在现有的 `survivor_jack.py` 中集成以下逻辑。

```python
import os

def get_gemini_key():
    """
    Retrieves the Gemini API Key with the following priority:
    1. Environment Variable 'GOOGLE_API_KEY'
    2. Local file 'MVP/api_key.txt'
    """
    # 1. Check Environment Variable
    api_key = os.getenv("GOOGLE_API_KEY")
    if api_key:
        print("[System] Using API Key from Environment Variable.")
        return api_key.strip()
    
    # 2. Check Local File
    key_file_path = os.path.join(os.path.dirname(__file__), "api_key.txt")
    if os.path.exists(key_file_path):
        try:
            with open(key_file_path, "r") as f:
                api_key = f.read().strip()
            if api_key:
                print("[System] Using API Key from local file.")
                return api_key
        except Exception as e:
            print(f"[Error] Failed to read api_key.txt: {e}")
            
    raise ValueError("No API Key found! Please set GOOGLE_API_KEY env var or update MVP/api_key.txt")

# Usage Example
# from key_manager import get_gemini_key
# genai.configure(api_key=get_gemini_key())
```

## 🤖 Model Configuration
所有大模型调用必须强制指定 `gemini-1.5-pro-latest` (注意: 用户提示提及 `Gemini 3 pro`，但当前公开可用或预览版通常为 1.5 Pro 或 Ultra，若确实有 3.0 访问权限，则使用 `gemini-3.0-pro-preview` 或对应标识符)。

**Current Configuration:**
- **Provider**: Google Generative AI
- **Model Name**: `gemini-1.5-pro-latest` (或者 `gemini-experimental`，需根据实际 access 调整)
- **Fallback**: 如果 API 调用失败，系统应进入 `Mock Mode` 以保证演示流畅性，并在 UI 上显示 "CONNECTION UNSTABLE" 警告。

## 🔄 Rotation & Monitoring
- **Rotation**: 建议每 30 天轮换一次 Key。
- **Monitoring**: 使用 Google Cloud Console 监控 Token 使用量，设置配额警报以防止意外超支。
