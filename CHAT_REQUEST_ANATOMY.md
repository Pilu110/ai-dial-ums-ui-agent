# Chat Request Body - Detailed Anatomy

## The Exact Structure

```json
{
  "message": {
    "role": "user",
    "content": "Find user with ID 1"
  },
  "stream": false
}
```

---

## Mapping to Python Code

This request body maps to the `ChatRequest` model in `agent/app.py`:

```python
class ChatRequest(BaseModel):
    message: Message           # ← The "message" field
    stream: bool = True        # ← The "stream" field (optional, defaults to True)
```

And the `Message` model in `agent/models/message.py`:

```python
class Message(BaseModel):
    role: str                  # ← "user", "assistant", "system", or "tool"
    content: Optional[str]     # ← Your actual message text
    tool_calls: Optional[...] = None
    tool_call_id: Optional[str] = None
    name: Optional[str] = None
```

---

## Breaking It Down

### 1. The `message` Object

This is the actual message you're sending to the AI.

```json
{
  "message": {
    "role": "user",           ← Who is sending this message
    "content": "Find user..." ← What the message says
  }
}
```

#### `role` Field

Must be one of:
- `"user"` - **You should use this** when sending messages from the UI
- `"assistant"` - Used for AI responses (you don't create these in requests)
- `"system"` - Used for system prompts (you don't need this in chat requests)
- `"tool"` - Used for tool results (automatically added by the system)

#### `content` Field

- **Type**: String
- **Required**: Yes, must not be empty
- **What it contains**: Your question, command, or statement
- **Examples**:
  - `"Find user with ID 1"`
  - `"Search for users named John"`
  - `"Create a new user with name Alice"`
  - `"Delete user 42"`

---

### 2. The `stream` Field

Tells the server how to send the response.

```json
{
  "stream": true
}
```

#### Options

| Value | Behavior | Response Type |
|-------|----------|---------------|
| `true` | Sends response progressively in chunks | Server-Sent Events (SSE) |
| `false` | Sends complete response all at once | Single JSON object |

**Default**: If omitted, defaults to `true`

#### When to Use

- **`stream: true`** - Best for UI/web applications (show response as it arrives)
- **`stream: false`** - Best for scripts, APIs, or when you need the full response at once

---

## Complete Examples with Explanations

### Example 1: Simple Search (No Streaming)

```json
{
  "message": {
    "role": "user",
    "content": "Find user with ID 1"
  },
  "stream": false
}
```

**What happens**:
1. AI receives your message
2. AI asks UMS MCP to get user with ID 1
3. Tool executes and returns user data
4. AI formats the response
5. Server sends complete response in one go

**Response format**:
```json
{
  "content": "Here is the user with ID 1: Name: John Doe, Email: john@example.com, ...",
  "conversation_id": "abc123"
}
```

---

### Example 2: Streaming Response

```json
{
  "message": {
    "role": "user",
    "content": "Search for users named Alice"
  },
  "stream": true
}
```

**What happens**:
1. AI receives your message
2. AI asks UMS MCP to search for "Alice"
3. Tool executes and returns matching users
4. AI formats the response
5. Server sends response in multiple chunks

**Response format** (Server-Sent Events):
```
data: {"conversation_id":"abc123"}

data: {"choices":[{"delta":{"content":"I"},"index":0,"finish_reason":null}]}

data: {"choices":[{"delta":{"content":" found"},"index":0,"finish_reason":null}]}

data: {"choices":[{"delta":{"content":" 3"},"index":0,"finish_reason":null}]}

data: {"choices":[{"delta":{"content":" users"},"index":0,"finish_reason":null}]}

...more chunks...

data: {"choices":[{"delta":{},"index":0,"finish_reason":"stop"}]}

data: [DONE]
```

---

### Example 3: Create User (Complex)

```json
{
  "message": {
    "role": "user",
    "content": "Add a new user: name John, surname Doe, email john@example.com, phone +1234567890, about_me Software Engineer"
  },
  "stream": false
}
```

**What happens**:
1. AI receives the message
2. AI extracts parameters from the natural language
3. AI calls the `add_user` tool with the parameters
4. Tool creates the user in the system
5. AI returns a success message

**Response**:
```json
{
  "content": "Successfully created new user John Doe with email john@example.com",
  "conversation_id": "abc123"
}
```

---

## Field Validation

When you send a request, the server validates:

```
✓ message exists
  ✓ message.role is exactly "user"
  ✓ message.content is a non-empty string
✓ stream is boolean (true or false)
```

If validation fails, you get a `422 Unprocessable Entity` error.

---

## In the Code Flow

Here's how your request flows through the application:

```
Browser/Client
    ↓
POST /conversations/{id}/chat
    ↓
FastAPI receives request
    ↓
Pydantic validates ChatRequest
    {
      "message": Message,  ← Validated as Message object
      "stream": bool       ← Validated as boolean
    }
    ↓
conversation_manager.chat() method
    ↓
dial_client.response() or dial_client.stream_response()
    ↓
Azure OpenAI API
    ↓
MCP Tools executed
    ↓
Response sent back
```

---

## Python Code Reference

### Request Handler
```python
@app.post("/conversations/{conversation_id}/chat")
async def chat(conversation_id: str, request: ChatRequest):
    """Chat endpoint with streaming support"""
    
    # request.message contains:
    # - role: str = "user"
    # - content: str = your message
    
    # request.stream contains:
    # - bool = True or False
    
    result = await conversation_manager.chat(
        user_message=request.message,  # ← Your Message object
        conversation_id=conversation_id,
        stream=request.stream          # ← Your stream setting
    )
    
    if request.stream:
        return StreamingResponse(result, media_type="text/event-stream")
    else:
        return ChatResponse(**result)
```

### Message Model
```python
class Message(BaseModel):
    role: str                          # ← "user"
    content: Optional[str] = None      # ← Your message text
    tool_calls: Optional[...] = None   # ← Added by AI automatically
    tool_call_id: Optional[str] = None # ← Added automatically
    name: Optional[str] = None         # ← Added automatically
    
    def to_dict(self):
        """Convert to dict for OpenAI API"""
        return {
            "role": self.role,
            "content": self.content,
            # ... tool_calls if present
        }
```

---

## Summary

| Part | Required | Type | Value | Notes |
|------|----------|------|-------|-------|
| `message` | ✅ Yes | Object | See below | Contains role + content |
| `message.role` | ✅ Yes | String | `"user"` | Always this value |
| `message.content` | ✅ Yes | String | Your text | Can't be empty |
| `stream` | ⚠️ Optional | Boolean | `true`/`false` | Defaults to `true` |

---

## Quick Copy-Paste Templates

### Template 1: Non-Streaming Search
```json
{
  "message": {
    "role": "user",
    "content": "Search for users with name John"
  },
  "stream": false
}
```

### Template 2: Streaming Query
```json
{
  "message": {
    "role": "user",
    "content": "Get details for user with ID 1"
  },
  "stream": true
}
```

### Template 3: Create User
```json
{
  "message": {
    "role": "user",
    "content": "Add new user: name Jane, surname Smith, email jane@example.com, about_me Product Manager"
  },
  "stream": false
}
```

### Template 4: Update User
```json
{
  "message": {
    "role": "user",
    "content": "Update user 5 with new email newemail@example.com"
  },
  "stream": false
}
```

### Template 5: Delete User
```json
{
  "message": {
    "role": "user",
    "content": "Delete user with ID 99"
  },
  "stream": false
}
```

---

**Need help?** See `CHAT_REQUEST_QUICK.md` or `CHAT_REQUEST_GUIDE.md`

