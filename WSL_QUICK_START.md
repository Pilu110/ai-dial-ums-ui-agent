# Running DuckDuckGo in WSL - Quick Reference

## TL;DR - Just Tell Me What to Do

### Best Option: Run Python App in WSL

```bash
# Open WSL terminal and run these commands:
cd /mnt/c/Users/IstvanVincze/PycharmProjects/ai-dial-ums-ui-agent

# Setup
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Configure
export DIAL_API_KEY="your-key"
export DIAL_ENDPOINT="https://ai-proxy.lab.epam.com"
export DIAL_MODEL="gpt-4o"

# Run
python -m agent.app

# Then open in Windows browser:
# - Frontend: file:///C:/Users/IstvanVincze/PycharmProjects/ai-dial-ums-ui-agent/index.html
# - API: http://localhost:8011
```

**Result**: ✅ Full functionality including DuckDuckGo search

---

## Alternative Option: Skip DuckDuckGo (Windows Only)

If you must run Python on Windows (native):

```bash
# Windows Command Prompt or PowerShell
cd C:\Users\IstvanVincze\PycharmProjects\ai-dial-ums-ui-agent
set ENABLE_DUCKDUCKGO=false
python -m agent.app
```

**Result**: ✅ Works but no DuckDuckGo search capability

---

## Why WSL Works Better

| Aspect | Windows Python | WSL Python |
|--------|---|---|
| Docker access | ❌ No | ✅ Yes |
| DuckDuckGo MCP | ❌ Fails | ✅ Works |
| Setup complexity | Low | Low |
| Performance | Good | Better |

---

## What I've Changed in Your Code

Your `app.py` now has **graceful fallback**:

```python
# If DuckDuckGo isn't available, the app still starts
try:
    duckduckgo_client = await StdioMCPClient.create("mcp/duckduckgo:latest")
    # ... load tools
except FileNotFoundError:
    logger.warning("DuckDuckGo MCP not available. Continuing without it.")
```

You can also disable it explicitly:
```bash
export ENABLE_DUCKDUCKGO=false
```

---

## Testing

Once running, test it works:

```bash
# From any terminal (Windows or WSL)
curl http://localhost:8011/health

# Should return:
# {"status":"healthy","conversation_manager_initialized":true}
```

---

## Full Documentation

See `WSL_DOCKER_SETUP.md` for complete setup instructions, troubleshooting, and advanced options.

