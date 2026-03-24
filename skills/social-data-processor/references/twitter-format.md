# Twitter/X Export Format Notes

## Status
**Not yet implemented.** This is a stub for when Twitter/X support is added.

## How to Download Twitter/X Data

1. X Settings → Your Account → Download an archive of your data
2. Request archive → wait for email (can take 24-48 hours)
3. Download ZIP → extract

## Export Structure

```
twitter-export/
├── data/
│   ├── account.js
│   ├── tweets.js
│   ├── direct-messages.js
│   ├── direct-messages-group.js
│   ├── following.js
│   ├── follower.js
│   ├── like.js
│   └── ...many more...
└── assets/
```

## ⚠️ Important: JS File Format

Twitter exports `.js` files that are NOT valid JSON. They're JavaScript module assignments:

```javascript
window.YTD.direct_messages.part0 = [ ... ]
```

To parse, strip the assignment prefix before passing to `json.loads()`:

```python
def parse_twitter_js(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    # Strip "window.YTD.xxx.partN = " prefix
    json_start = content.index('[')
    return json.loads(content[json_start:])
```

## Direct Messages Format

```javascript
window.YTD.direct_messages.part0 = [
  {
    "dmConversation": {
      "conversationId": "123456-789012",
      "messages": [
        {
          "messageCreate": {
            "recipientId": "789012",
            "text": "message text",
            "createdAt": "2024-01-15T12:00:00.000Z",
            "mediaUrls": [],
            "senderId": "123456",
            "id": "msg-id"
          }
        }
      ]
    }
  }
]
```

## Following Format

```javascript
window.YTD.following.part0 = [
  {
    "following": {
      "accountId": "123456",
      "userLink": "https://twitter.com/intent/user?user_id=123456"
    }
  }
]
```

Note: Following export only has user IDs, not usernames. You'll need to resolve IDs to usernames via the Twitter API (if available) or browser scraping.

## Implementation Notes

1. Parse all `.js` files using the strip-prefix method above
2. DM conversation IDs are `senderID-recipientID` format
3. User IDs don't give you usernames — this is a known limitation
4. Following/follower counts are available; individual resolution requires API or browser
5. Update this file with discoveries from first real export
