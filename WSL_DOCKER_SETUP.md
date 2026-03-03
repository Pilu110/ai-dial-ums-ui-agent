# Running DuckDuckGo MCP via WSL in Windows - Configuration Guide

## Problem
You're running the Python app on native Windows, but Docker (required for DuckDuckGo MCP) is in WSL. They can't communicate directly.

## Solution 1: Run Python App in WSL (Recommended) ⭐

This is the simplest and most reliable approach.

### Step 1: Setup Python in WSL

```bash
# In WSL terminal, navigate to project
cd /mnt/c/Users/IstvanVincze/PycharmProjects/ai-dial-ums-ui-agent

# Create Python virtual environment in WSL
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Step 2: Set Environment Variables

```bash
# In the WSL terminal
export DIAL_API_KEY="your-azure-openai-key"
export DIAL_ENDPOINT="https://ai-proxy.lab.epam.com"
export DIAL_MODEL="gpt-4o"
```

### Step 3: Run the Application

```bash
# Still in WSL terminal with venv activated
python -m agent.app
```

**Result**: The app will start successfully with:
- ✅ UMS MCP Server (HTTP)
- ✅ Fetch MCP Server (HTTP)
- ✅ DuckDuckGo MCP Server (Docker via WSL)

### Step 4: Access from Windows

Open your browser on Windows (not in WSL):
- **Frontend**: Open `C:\Users\IstvanVincze\PycharmProjects\ai-dial-ums-ui-agent\index.html`
- **API**: `http://localhost:8011`

The app runs in WSL but is accessible from Windows because localhost bridges between them.

---

## Solution 2: Keep Python on Windows, Skip DuckDuckGo

If you prefer to run Python on Windows, you can simply disable the DuckDuckGo client:

### Step 1: Set Environment Variable

```bash
# On Windows Command Prompt or PowerShell
set ENABLE_DUCKDUCKGO=false

# Or on PowerShell specifically
$env:ENABLE_DUCKDUCKGO = "false"
```

### Step 2: Run the App

```bash
# In Windows (not WSL)
python -m agent.app
```

**Result**: The app will start with:
- ✅ UMS MCP Server (HTTP)
- ✅ Fetch MCP Server (HTTP)
- ⊘ DuckDuckGo MCP Server (skipped)

All other functionality remains the same.

---

## Solution 3: Advanced - Configure Windows Docker Desktop WSL 2 Backend

If you have Docker Desktop installed on Windows:

### Prerequisites
- Docker Desktop for Windows with WSL 2 backend enabled
- WSL 2 Linux kernel installed

### Setup

1. **Open Docker Desktop Settings**
   - Settings → Resources → WSL Integration
   - Enable integration with your WSL distribution

2. **Verify Docker works in WSL**
   ```bash
   # In WSL terminal
   docker ps
   # Should list running containers without errors
   ```

3. **Run Python in WSL** (same as Solution 1)
   - This is still recommended even with Docker Desktop WSL 2 backend

---

## Comparison Table

| Approach | Setup Complexity | Docker Access | Recommended |
|----------|-----------------|----------------|-------------|
| **Run Python in WSL** | Low | ✅ Native | ⭐ YES |
| **Windows Python + ENABLE_DUCKDUCKGO=false** | Very Low | N/A | ⚠️ Works but no search |
| **Docker Desktop WSL 2 Backend** | High | ✅ Bridged | ❌ Over-complicated |

---

## Troubleshooting

### Issue: "Docker not found" error on Windows

**Solution**: This is expected. Use Solution 1 (WSL) or Solution 2 (disable DuckDuckGo).

### Issue: Can't connect to localhost:8011 from Windows

If running app in WSL, verify:
```bash
# In WSL terminal where app is running
netstat -tlnp | grep 8011
# Should show: 0.0.0.0:8011 LISTEN
```

If showing only `127.0.0.1:8011`, the app is only listening locally in WSL. Modify app.py host to `0.0.0.0`.

### Issue: Redis connection refused

Verify Redis is running in Docker:
```bash
# In WSL terminal
docker ps | grep redis
# Should see redis-ums running
```

---

## Quick Start Commands

### Option 1: Run Everything in WSL (Recommended)
```bash
# In WSL terminal
cd /mnt/c/Users/IstvanVincze/PycharmProjects/ai-dial-ums-ui-agent
source venv/bin/activate
export DIAL_API_KEY="your-key"
export DIAL_ENDPOINT="https://ai-proxy.lab.epam.com"
export DIAL_MODEL="gpt-4o"
python -m agent.app
```

### Option 2: Run on Windows without DuckDuckGo
```bash
# In Windows Command Prompt/PowerShell
cd C:\Users\IstvanVincze\PycharmProjects\ai-dial-ums-ui-agent
set ENABLE_DUCKDUCKGO=false
python -m agent.app
```

---

## My Recommendation

**Use Option 1** (Run Python in WSL):

✅ **Pros:**
- DuckDuckGo MCP works perfectly
- Docker accessible natively
- Better performance
- Aligns with development environment
- All tools available

❌ **Cons:**
- Small learning curve if new to WSL

**Why not Option 2?**
- You lose the DuckDuckGo search capability
- Limited tool set for the agent

**Why not Option 3?**
- Over-complicated for local development
- Docker Desktop adds overhead
- Still need WSL for proper Docker support

---

## Testing the Setup

Once you've chosen your approach, verify it works:

```bash
# Health check (from Windows, any terminal)
curl http://localhost:8011/health

# Should return:
# {"status":"healthy","conversation_manager_initialized":true}

# Create a test conversation
curl -X POST http://localhost:8011/conversations \
  -H "Content-Type: application/json" \
  -d '{"title":"Test"}'
```

If these work, your setup is correct! 🎉

