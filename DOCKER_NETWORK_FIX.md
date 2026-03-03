# Docker Configuration Fix

## Problem
The UMS MCP server couldn't connect to the userservice because it was trying to reach `host.docker.internal:8041`, which doesn't work in WSL 2.

## Error Message
```
Failed to resolve 'host.docker.internal' ([Errno -2] Name does not resolve)
```

## Solution Applied
Changed `docker-compose.yml` line 27:

**Before:**
```yaml
- USERS_MANAGEMENT_SERVICE_URL=${USERS_MANAGEMENT_SERVICE_URL:-http://host.docker.internal:8041}
```

**After:**
```yaml
- USERS_MANAGEMENT_SERVICE_URL=${USERS_MANAGEMENT_SERVICE_URL:-http://userservice:8000}
```

## Why This Works
- `userservice` is the Docker service name defined in the same compose file
- Within Docker's internal network, services can reference each other by name
- Port `8000` is the internal port (8041 is only the host mapping)
- This is the proper way to configure inter-container communication in Docker Compose

## What to Do Next

1. **Stop the old containers:**
   ```bash
   docker-compose down
   ```

2. **Start new containers with the fixed configuration:**
   ```bash
   docker-compose up -d
   ```

3. **Wait for services to be healthy** (about 40 seconds for userservice healthcheck)

4. **Test the application again:**
   - Try adding a user via the chat interface
   - The tool should now successfully reach the userservice

## Verification
After restarting, the tool calls should:
- ✅ Reach the UMS MCP server correctly
- ✅ MCP server reaches userservice via Docker network
- ✅ User creation/search operations work

If it still fails, check:
```bash
docker ps        # Verify all containers are running
docker logs ums-mcp-server  # Check MCP server logs
```

