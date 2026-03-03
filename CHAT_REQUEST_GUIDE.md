# Chat Endpoint Request Guide

## Endpoint Overview

**POST** `/conversations/{conversation_id}/chat`

This endpoint sends a message to the AI agent and gets a response.

---

## Request Body Structure

```json
{
  "message": {
    "role": "user",
    "content": "Your message here"
  },
  "stream": true
}
```

### Field Explanations

| Field | Type | Required | Description | Example |
|-------|------|----------|-------------|---------|
| `message` | Object | ✅ Yes | Message object with role and content | See below |
| `message.role` | String | ✅ Yes | Must be `"user"` for your messages | `"user"` |
| `message.content` | String | ✅ Yes | Your actual message/question | `"Find user with email john@example.com"` |
| `stream` | Boolean | ⚠️ Optional | If `true`: streaming response (SSE). If `false`: single response | `true` or `false` |

---

## Examples

### Example 1: Simple Message (Non-Streaming)

```bash
curl -X POST http://localhost:8011/conversations/YOUR_CONVERSATION_ID/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": {
      "role": "user",
      "content": "Search for users named John"
    },
    "stream": false
  }'
```

**Response:**
```json
{
  "content": "I found 5 users named John. Here are their details...",
  "conversation_id": "YOUR_CONVERSATION_ID"
}
```

---

### Example 2: Streaming Response

```bash
curl -X POST http://localhost:8011/conversations/YOUR_CONVERSATION_ID/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": {
      "role": "user",
      "content": "Get user with ID 42"
    },
    "stream": true
  }'
```

**Response (Server-Sent Events):**
```
data: {"conversation_id":"YOUR_CONVERSATION_ID"}

data: {"choices":[{"delta":{"content":"I"},"index":0,"finish_reason":null}]}

data: {"choices":[{"delta":{"content":" will"},"index":0,"finish_reason":null}]}

data: {"choices":[{"delta":{"content":" get"},"index":0,"finish_reason":null}]}

...more chunks...

data: {"choices":[{"delta":{},"index":0,"finish_reason":"stop"}]}

data: [DONE]
```

---

### Example 3: Real-World UMS Operations

#### Search for a user by email

```bash
curl -X POST http://localhost:8011/conversations/YOUR_CONVERSATION_ID/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": {
      "role": "user",
      "content": "Find me the user with email john.doe@example.com"
    },
    "stream": false
  }'
```

#### Add a new user

```bash
curl -X POST http://localhost:8011/conversations/YOUR_CONVERSATION_ID/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": {
      "role": "user",
      "content": "Create a new user with name John, surname Doe, email john.doe@example.com, and about_me as Software Engineer"
    },
    "stream": false
  }'
```

#### Update a user

```bash
curl -X POST http://localhost:8011/conversations/YOUR_CONVERSATION_ID/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": {
      "role": "user",
      "content": "Update user 42 with new email newemail@example.com"
    },
    "stream": false
  }'
```

#### Delete a user

```bash
curl -X POST http://localhost:8011/conversations/YOUR_CONVERSATION_ID/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": {
      "role": "user",
      "content": "Delete user with ID 42"
    },
    "stream": false
  }'
```

---

## JavaScript/Fetch API Example

Here's how to do it from JavaScript (browser):

```javascript
const conversationId = "YOUR_CONVERSATION_ID";
const userMessage = "Find all users from the Engineering department";

const requestBody = {
  message: {
    role: "user",
    content: userMessage
  },
  stream: false
};

fetch(`http://localhost:8011/conversations/${conversationId}/chat`, {
  method: "POST",
  headers: {
    "Content-Type": "application/json"
  },
  body: JSON.stringify(requestBody)
})
.then(response => response.json())
.then(data => {
  console.log("AI Response:", data.content);
  console.log("Conversation ID:", data.conversation_id);
})
.catch(error => console.error("Error:", error));
```

---

## Streaming in JavaScript

For streaming responses:

```javascript
const conversationId = "YOUR_CONVERSATION_ID";
const userMessage = "Search for users with surname Smith";

const requestBody = {
  message: {
    role: "user",
    content: userMessage
  },
  stream: true
};

fetch(`http://localhost:8011/conversations/${conversationId}/chat`, {
  method: "POST",
  headers: {
    "Content-Type": "application/json"
  },
  body: JSON.stringify(requestBody)
})
.then(response => {
  const reader = response.body.getReader();
  const decoder = new TextDecoder();

  return reader.read().then(function processStream({ done, value }) {
    if (done) return;

    const chunk = decoder.decode(value);
    console.log("Received:", chunk);

    return reader.read().then(processStream);
  });
})
.catch(error => console.error("Error:", error));
```

---

## Complete Workflow

### Step 1: Create a Conversation

```bash
curl -X POST http://localhost:8011/conversations \
  -H "Content-Type: application/json" \
  -d '{
    "title": "User Search Session"
  }'
```

**Response:**
```json
{
  "id": "abc123def456",
  "title": "User Search Session",
  "messages": [],
  "created_at": "2026-03-03T15:47:00.000000+00:00",
  "updated_at": "2026-03-03T15:47:00.000000+00:00"
}
```

Save the `id` value (e.g., `abc123def456`)

### Step 2: Send a Message to That Conversation

```bash
curl -X POST http://localhost:8011/conversations/abc123def456/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": {
      "role": "user",
      "content": "Find users with name John"
    },
    "stream": false
  }'
```

### Step 3: See the Response

```json
{
  "content": "I found the following users with the name John...",
  "conversation_id": "abc123def456"
}
```

### Step 4: Continue the Conversation

Send another message to the **same conversation ID**:

```bash
curl -X POST http://localhost:8011/conversations/abc123def456/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": {
      "role": "user",
      "content": "Show me the full details of the first John"
    },
    "stream": false
  }'
```

The conversation history is automatically maintained! 🎉

---

## Message Role Values

**Valid values for `message.role`:**

- `"user"` - Messages from you (the user)
- `"assistant"` - Messages from the AI (automatically generated)
- `"system"` - System prompts (don't use this in chat requests)
- `"tool"` - Tool execution results (automatically added)

**You should only use `"user"`** when making chat requests.

---

## Stream Parameter

### `"stream": false` (Default)
- Returns the complete response at once
- Faster for short responses
- Good for non-UI integrations
- Response format: `{"content": "...", "conversation_id": "..."}`

### `"stream": true`
- Returns response in real-time chunks (SSE format)
- Better user experience (progressive rendering)
- Good for UI/web applications
- Response format: Server-Sent Events

---

## Common Message Examples

```javascript
// Simple search
{ "role": "user", "content": "Find user with ID 1" }

// Complex query
{ "role": "user", "content": "Search for users named John from the USA" }

// Create user
{ "role": "user", "content": "Add a new user: name=Alice, surname=Smith, email=alice@example.com, about_me=Data Scientist" }

// Update user
{ "role": "user", "content": "Update user 42: change email to newemail@test.com" }

// Delete user
{ "role": "user", "content": "Delete user with ID 99" }

// Ask a question
{ "role": "user", "content": "How many users do we have?" }
```

---

## Testing in the Browser UI

The UI (index.html) already handles all this for you! You just need to:

1. Open `index.html` in your browser
2. Click "New Chat"
3. Type your message in the input box
4. Press Enter or click Send
5. The app automatically:
   - Creates a conversation (if needed)
   - Sends the message with proper format
   - Handles streaming responses
   - Displays the AI response

---

## Troubleshooting

### Error: "Conversation not found"
- Make sure you're using the correct conversation ID
- The ID must be from a conversation created with `POST /conversations`

### Error: "Invalid request"
- Check that `message.role` is exactly `"user"`
- Check that `message.content` is not empty
- Make sure JSON is valid (use JSONLint.com to validate)

### No response
- Make sure the API server is running (`python -m agent.app`)
- Check that you can access `http://localhost:8011/health`
- Check the server logs for errors

### Response is incomplete (streaming)
- This is normal! Streaming sends chunks progressively
- Keep reading until you get `data: [DONE]`

---

## API Response Codes

| Code | Meaning | Example |
|------|---------|---------|
| 200 | Success | Message processed, response returned |
| 404 | Not Found | Conversation ID doesn't exist |
| 503 | Service Unavailable | Server not initialized |
| 500 | Internal Error | Check server logs |


