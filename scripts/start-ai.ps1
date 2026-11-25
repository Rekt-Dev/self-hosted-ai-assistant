# Starts Ollama, Open WebUI and pre-warms the default model. Intended to run at logon (Task Scheduler).
param([string]$Root = 'D:\AI')

$env:OLLAMA_MODELS            = "$Root\models"
$env:OLLAMA_BASE_URL          = 'http://127.0.0.1:11434'
$env:OLLAMA_CONTEXT_LENGTH    = '49152'
$env:OLLAMA_NUM_PARALLEL      = '1'
$env:OLLAMA_MAX_LOADED_MODELS = '1'
$env:OLLAMA_MAX_QUEUE         = '4'
$env:OLLAMA_KEEP_ALIVE        = '-1'     # keep the model resident

$env:DATA_DIR                 = "$Root\webui-data"
$env:ENABLE_PERSISTENT_CONFIG = 'False'
# Disable background LLM calls (titles, tags, follow-ups, autocomplete, query generation) to save CPU time
foreach ($n in 'TITLE','TAGS','FOLLOW_UP','AUTOCOMPLETE','SEARCH_QUERY','RETRIEVAL_QUERY') { Set-Item "env:ENABLE_${n}_GENERATION" 'False' }

# Voice: local Whisper for speech-to-text, OpenAI-compatible TTS endpoint on localhost
$env:WHISPER_MODEL            = 'base.en'
$env:WHISPER_LANGUAGE         = 'en'
$env:WHISPER_VAD_FILTER       = 'true'
$env:AUDIO_TTS_ENGINE         = 'openai'
$env:AUDIO_TTS_OPENAI_API_BASE_URL = 'http://127.0.0.1:5050/v1'
$env:AUDIO_TTS_OPENAI_API_KEY = 'local'

# Tool environment (see docs/tools.md)
$env:AI_ROOT                  = $Root
$env:AI_WORKSPACE             = "$Root\workspace"
$env:AI_EMAIL_CFG             = "$Root\secrets\email.json"
$env:AI_TZ                    = 'UTC'

if (-not (Get-Process ollama -ErrorAction SilentlyContinue)) {
    Start-Process "$Root\ollama\ollama.exe" -ArgumentList 'serve' -WindowStyle Hidden `
        -RedirectStandardOutput "$Root\serve.log" -RedirectStandardError "$Root\serve.err"
}
Start-Sleep 5
if (-not (Get-NetTCPConnection -LocalPort 8080 -State Listen -ErrorAction SilentlyContinue)) {
    Start-Process "$Root\webui\Scripts\open-webui.exe" -ArgumentList 'serve','--host','0.0.0.0','--port','8080' -WindowStyle Hidden `
        -RedirectStandardOutput "$Root\webui.log" -RedirectStandardError "$Root\webui.err"
}
Start-Sleep 10
try { & "$Root\webui\Scripts\python.exe" "$PSScriptRoot\warm.py" } catch {}
