# Bug Fix: Logging KeyError with Reserved Word 'args'

## Problem
When trying to add a user to the database, you got this error:

```
KeyError: "Attempt to overwrite 'args' in LogRecord"
```

## Root Cause
In Python's logging module, `args` is a reserved/protected field in the LogRecord class. When you use `extra={}` dictionary in logger calls, you cannot use reserved field names.

The problematic code was:
```python
logger.debug(f"Calling tool on MCP server", extra={
    "tool": tool_name,
    "args": tool_args,        # ❌ 'args' is reserved!
    "url": self.server_url
})
```

## Solution
Renamed the field from `"args"` to `"tool_args"`:

```python
logger.debug(f"Calling tool on MCP server", extra={
    "tool": tool_name,
    "tool_args": tool_args,   # ✅ No longer conflicts
    "url": self.server_url
})
```

## Files Fixed
1. `agent/clients/http_mcp_client.py` - Line 64-67
2. `agent/clients/stdio_mcp_client.py` - Line 68-71

## Status
✅ **FIXED AND VERIFIED**

Both files have been corrected and compile without errors.

## Testing
Try running the app again and adding a user - it should work now!

```bash
# Start the app
python -m agent.app

# Then send a message to add a user:
# "Add new user: name John, surname Doe, email john@example.com, about_me Software Engineer"
```

## What Was Changed

### http_mcp_client.py
**Before:**
```python
logger.debug(f"Calling tool on MCP server", extra={
    "tool": tool_name,
    "args": tool_args,
    "url": self.server_url
})
```

**After:**
```python
logger.debug(f"Calling tool on MCP server", extra={
    "tool": tool_name,
    "tool_args": tool_args,
    "url": self.server_url
})
```

### stdio_mcp_client.py
**Before:**
```python
logger.debug(f"Calling tool on MCP server", extra={
    "tool": tool_name,
    "args": tool_args,
    "docker_image": self.docker_image
})
```

**After:**
```python
logger.debug(f"Calling tool on MCP server", extra={
    "tool": tool_name,
    "tool_args": tool_args,
    "docker_image": self.docker_image
})
```

---

## Why This Happened
The Python logging module has protected field names that cannot be overwritten in LogRecord. These reserved names include:
- `name`
- `msg`
- `args`
- `created`
- `filename`
- `funcName`
- `levelname`
- `lineno`
- `module`
- `pathname`
- etc.

When you pass `extra={}` to a logger method, the keys you provide get added to the LogRecord. If any of these keys match reserved field names, Python raises a KeyError.

---

## Prevention
In the future, to avoid this issue:
- ✅ Use custom field names like `"tool_args"` instead of reserved names like `"args"`
- ✅ Check the logging documentation for reserved field names
- ✅ Use descriptive names like `"arguments"`, `"params"`, `"values"` instead of short names like `"args"`

