# Chat Request - Quick Reference

## 🎯 Simplest Form

```json
{
  "message": {
    "role": "user",
    "content": "Your question or command here"
  },
  "stream": false
}
```

---

## 📋 Field Breakdown

```
┌─────────────────────────────────────┐
│  Chat Request Body                  │
├─────────────────────────────────────┤
│                                     │
│  ✓ message (REQUIRED)               │
│    ├─ role: "user" (ALWAYS THIS)    │
│    └─ content: "Your message"       │
│                                     │
│  ✓ stream (OPTIONAL)                │
│    ├─ true  → Progressive response  │
│    └─ false → Complete response     │
│                                     │
└─────────────────────────────────────┘
```

---

## 🔄 Complete Workflow

```
1. Create Conversation
   POST /conversations
   Body: {"title": "My Chat"}
   ↓ Get conversation_id

2. Send Message
   POST /conversations/{id}/chat
   Body: {
     "message": {"role": "user", "content": "..."},
     "stream": false
   }
   ↓ Get response

3. (Optional) Send Another Message
   POST /conversations/{id}/chat
   (Same conversation keeps history)
```

---

## 📱 Real Examples

### Find User by Email
```json
{
  "message": {
    "role": "user",
    "content": "Find the user with email john@example.com"
  },
  "stream": false
}
```

### Create New User
```json
{
  "message": {
    "role": "user",
    "content": "Add a new user: name John, surname Doe, email john@example.com, about_me Senior Developer"
  },
  "stream": false
}
```

### Search Users
```json
{
  "message": {
    "role": "user",
    "content": "Show me all users from the Sales department"
  },
  "stream": true
}
```

### Delete User
```json
{
  "message": {
    "role": "user",
    "content": "Delete user with ID 42"
  },
  "stream": false
}
```

---

## 🧪 Test with curl

### Step 1: Create Conversation
```bash
curl -X POST http://localhost:8011/conversations \
  -H "Content-Type: application/json" \
  -d '{"title":"Test"}'
```

Copy the `id` from response (e.g., `abc123`)

### Step 2: Send Message
```bash
curl -X POST http://localhost:8011/conversations/abc123/chat \
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

## ✅ What You Need to Know

| Aspect | Value | Notes |
|--------|-------|-------|
| Method | `POST` | Always POST |
| URL Path | `/conversations/{id}/chat` | Replace {id} with real ID |
| Content-Type | `application/json` | Required header |
| message.role | `"user"` | Always exactly this |
| message.content | Your text | Can be a question or command |
| stream | `true` or `false` | Optional, defaults to false |

---

## 🎨 In the Browser UI

You don't need to manually create this body! Just:

1. Open `index.html`
2. Type your message
3. Press Enter
4. App handles everything automatically ✨

---

## 🚨 Common Mistakes

❌ **Wrong**: `"role": "assistant"` 
✅ **Right**: `"role": "user"`

❌ **Wrong**: Missing `message` object
✅ **Right**: Include the entire `message` with `role` and `content`

❌ **Wrong**: Empty `content`
✅ **Right**: `"content": "Find user with ID 1"`

❌ **Wrong**: Wrong conversation ID
✅ **Right**: Use ID from `/conversations` endpoint

---

## 📖 Full Guide

See `CHAT_REQUEST_GUIDE.md` for:
- Detailed examples
- JavaScript/Fetch examples
- Streaming examples
- Complete workflows
- Troubleshooting

