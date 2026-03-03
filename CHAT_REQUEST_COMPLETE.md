# Chat Endpoint - Complete Understanding

## TL;DR - 30 Second Version

To send a message to the chat endpoint:

```json
POST /conversations/{id}/chat

{
  "message": {
    "role": "user",
    "content": "Your message here"
  },
  "stream": false
}
```

That's it! Replace `{id}` with your conversation ID.

---

## The Four Required Steps

### Step 1: Create a Conversation

```bash
curl -X POST http://localhost:8011/conversations \
  -H "Content-Type: application/json" \
  -d '{"title": "My Session"}'
```

You get back:
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "title": "My Session",
  ...
}
```

**Save this `id`!**

---

### Step 2: Prepare Your Message

Think about what you want to ask:

```
Examples:
- "Find user with ID 1"
- "Search for users named John"
- "Create a new user named Alice"
- "Delete user with ID 42"
```

---

### Step 3: Format the Request Body

```json
{
  "message": {
    "role": "user",
    "content": "Your message from Step 2"
  },
  "stream": false
}
```

---

### Step 4: Send the Request

```bash
curl -X POST http://localhost:8011/conversations/550e8400-e29b-41d4-a716-446655440000/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": {
      "role": "user",
      "content": "Find user with ID 1"
    },
    "stream": false
  }'
```

---

## Understanding Each Field

| Field | What is it? | Example | Required? |
|-------|-----------|---------|-----------|
| `message` | Container for your message | `{...}` | ✅ Yes |
| `message.role` | Who is speaking | `"user"` | ✅ Yes |
| `message.content` | What you're saying | `"Find user..."` | ✅ Yes |
| `stream` | How to get response | `true` or `false` | ⚠️ Optional* |

*If you omit `stream`, it defaults to `true`

---

## The Two Response Modes

### Mode 1: Non-Streaming (`stream: false`)

```json
Request Body:
{
  "message": {"role": "user", "content": "Find user 1"},
  "stream": false
}

Response (received all at once):
{
  "content": "Here is the user with ID 1: ...",
  "conversation_id": "550e8400-..."
}
```

**When to use**: Scripts, APIs, when you need the full answer at once

---

### Mode 2: Streaming (`stream: true`)

```json
Request Body:
{
  "message": {"role": "user", "content": "Find user 1"},
  "stream": true
}

Response (chunks):
data: {"conversation_id":"550e8400-..."}
data: {"choices":[{"delta":{"content":"Here"}}]}
data: {"choices":[{"delta":{"content":" is"}}]}
data: {"choices":[{"delta":{"content":" the"}}]}
...
data: [DONE]
```

**When to use**: Web UI, showing real-time progress

---

## The Message Object

```
message: {
  "role": "user",      ← Must be exactly "user"
  "content": "...",    ← Your actual text
}
```

### Valid role values:
- `"user"` - You (the person asking)
- `"assistant"` - The AI (don't use in requests)
- `"system"` - System instructions (don't use in requests)
- `"tool"` - Tool results (don't use in requests)

---

## Common Content Examples

```
Search operations:
  "Find user with ID 1"
  "Search for users with name John"
  "Find users from the Engineering department"

Create operations:
  "Add new user: name John, surname Doe, email john@example.com, about_me Software Engineer"

Update operations:
  "Update user 42 with email newemail@example.com"

Delete operations:
  "Delete user with ID 42"

Combinations:
  "Find all users, then show me John Doe's full details"
```

---

## Conversation Context

Important: Each conversation maintains **history**!

```
Conversation: abc123

Message 1:
  "Search for users named John"
  → Response: "Found 5 Johns"

Message 2 (same conversation):
  "Show me John Smith's email"
  → Response: "John Smith's email is..." (AI remembers context!)

Message 3 (same conversation):
  "Delete him"
  → Response: "Deleted John Smith" (AI knows who "him" is)
```

Just send multiple requests to the **same conversation ID**.

---

## Complete Curl Example

```bash
# 1. Create conversation
CONV_ID=$(curl -s -X POST http://localhost:8011/conversations \
  -H "Content-Type: application/json" \
  -d '{"title":"My Chat"}' | jq -r '.id')

echo "Conversation ID: $CONV_ID"

# 2. Send message
curl -X POST "http://localhost:8011/conversations/$CONV_ID/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "message": {
      "role": "user",
      "content": "Find user with ID 1"
    },
    "stream": false
  }' | jq

# 3. Send another message (same conversation)
curl -X POST "http://localhost:8011/conversations/$CONV_ID/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "message": {
      "role": "user",
      "content": "What is their email?"
    },
    "stream": false
  }' | jq
```

---

## JavaScript/Fetch Example

```javascript
// 1. Create conversation
const convResponse = await fetch('http://localhost:8011/conversations', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ title: 'My Chat' })
});
const convData = await convResponse.json();
const conversationId = convData.id;

// 2. Send message
const chatRequest = {
  message: {
    role: 'user',
    content: 'Find user with ID 1'
  },
  stream: false
};

const chatResponse = await fetch(
  `http://localhost:8011/conversations/${conversationId}/chat`,
  {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(chatRequest)
  }
);
const chatData = await chatResponse.json();
console.log('AI Response:', chatData.content);
```

---

## The Real UI Way

The easiest way? Just use the HTML UI:

```
1. Open file:///C:/Users/IstvanVincze/PycharmProjects/ai-dial-ums-ui-agent/index.html
2. Click "New Chat"
3. Type your message
4. Press Enter
5. Done! ✨

(The UI handles all the request formatting automatically)
```

---

## Troubleshooting

### "Conversation not found"
- Make sure `{id}` in the URL is real
- Use an ID from a conversation you created with `POST /conversations`

### "Invalid request"
- Check that `message.role` is exactly `"user"`
- Check that `message.content` is not empty
- Validate JSON with JSONLint.com

### No response from server
- Make sure app is running: `python -m agent.app`
- Check health: `curl http://localhost:8011/health`
- Check server logs for errors

### Response seems incomplete
- This might be streaming mode. Keep reading until you see `[DONE]`

---

## Quick Checklist

Before sending a request:

- [ ] Do I have a valid conversation ID?
- [ ] Is `message.role` exactly `"user"`?
- [ ] Does `message.content` have actual text?
- [ ] Is `stream` either `true` or `false` (or omitted)?
- [ ] Is the JSON valid (use JSONLint.com)?
- [ ] Is the server running (`python -m agent.app`)?

---

## Summary

| Aspect | Value |
|--------|-------|
| **HTTP Method** | `POST` |
| **URL** | `/conversations/{id}/chat` |
| **Required Headers** | `Content-Type: application/json` |
| **Required Body Fields** | `message` (object), `message.role`, `message.content` |
| **Optional Body Fields** | `stream` (boolean, defaults to true) |
| **Conversation Persistence** | Yes - history is maintained |

---

## Where to Go from Here

- **Quick ref**: `CHAT_REQUEST_QUICK.md`
- **Detailed guide**: `CHAT_REQUEST_GUIDE.md`
- **Anatomy**: `CHAT_REQUEST_ANATOMY.md`
- **Visual**: `CHAT_REQUEST_VISUAL.md` (shown above)

🎉 **You've got this!**

