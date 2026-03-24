# Facebook Export Format Notes

## Status
**Not yet implemented.** This is a stub for when Facebook support is added.

## How to Download Facebook Data

1. Facebook Settings → Your Facebook Information → Download Your Information
2. Select: Messages, Friends, Following and Followers
3. Format: JSON, date range: All Time, Media Quality: Low (saves space)
4. Download and extract ZIP

## Expected Structure

```
facebook-export/
├── messages/
│   └── inbox/
│       └── [name_hash]/
│           ├── message_1.json
│           └── photos/
├── friends/
│   ├── friends.json
│   └── removed_friends.json
├── following_and_followers/
│   └── following.json
└── profile_information/
    └── profile_information.json
```

## Message Format (Expected — similar to Instagram)

```json
{
  "participants": [{"name": "Full Name"}, {"name": "Alex Abell"}],
  "messages": [
    {
      "sender_name": "Full Name",
      "timestamp_ms": 1234567890000,
      "content": "message text",
      "type": "Generic"
    }
  ],
  "title": "Full Name",
  "is_still_participant": true,
  "thread_type": "Regular",
  "thread_path": "inbox/Name_hash"
}
```

## Encoding Notes

Facebook exports do NOT have Instagram's encoding bug — strings should be clean UTF-8.
Verify on first real export.

## Implementation Notes

When implementing:
1. Follow the same workflow as Instagram in SKILL.md
2. No encoding fix needed (verify)
3. Friends list maps roughly to Instagram followers
4. Update this file with actual format details discovered
