# 📥 INBOX

Drop anything here. I'll process it.

Brain dumps, ideas, tasks, honey-dos, random thoughts at 3am. Just get it out of your head.

I'll sort it into the right place. That's my job.

---

## Unsorted

### 1. LinkedIn Cleanup
- 20K connections, many from automation (Duck Soup or similar)
- Tons of junk messages, people selling stuff
- Also legit messages that needed replies, some 10+ years old
- Want me to get into LinkedIn via browser and help clean up messages
- Goal: meaningful network, not vanity metrics

### 2. Contacts Cleanup
- Pipedrive CRM contacts from Lunchpool merged with personal contacts
- Tried Dex as personal CRM, didn't stick
- Autofill pulls random prospects instead of his own email
- Want: clean contacts, birthday reminders for important people, nudges to call/text friends and family who haven't heard from him in a while
- Basically a personal CRM (could be built into second brain or use Dex)

### 3. Gmail / Email Management
- Previous attempt at email checking got the Gmail account flagged as a bot
- Need to use the proper Google API (not scraping)
- gog skill exists for this, need to set up properly

### 4. Google Drive Cleanup
- "A nightmare" — needs organizing
- Details TBD

### 5. Recurring: Remind Alex to return Avie's clothes to Annika
- Every time Avie goes back to Annika's, check if there are clothes to send back
- This is a real pain point in the co-parenting logistics

### 6. ~~Voice Memo Reply Format (Debra → Alex)~~ ✅ FIXED
- Custom Debra ElevenLabs voice works (voice_id: w6INrsHCejnExFzTH8Nm)
- Transcription of incoming voice notes works (Whisper)
- ~~PROBLEM: outbound voice memos show as audio bubble but won't play~~ FIXED
- Solution: built-in tts tool with full ElevenLabs config (modelId + voiceSettings) sends playable voice memos
- Manual curl → ElevenLabs → mp3 also works as audio file attachment

### 6. OpenClaw PR — ElevenLabs + iMessage Voice Memo Guide
- Document the full working config for custom ElevenLabs voice + iMessage voice memos via BlueBubbles
- Repo forked to alex-abell/openclaw, ready to branch
- Include: config example, voice settings, troubleshooting (format issues, playback)
- Maybe also BlueBubbles PR if format fix is confirmed

### 7. Abellminded.com — Living Brain Map
- NOT a consulting website. it's a real-time public-friendly visualization of Alex's mind.
- Interactive graph view showing topics, projects, concepts, connections
- Easter egg: clicking "mind" in "abellminded" takes you to the live graph
- Feeds from the second brain pipeline (filtered for public-friendly content)
- As Alex talks about new topics (via transcription/perception pipelines), new nodes appear in real-time
- Consulting (AI-enhanced business growth strategy) becomes an offshoot entity, not the main brand
- Abellminded = personal brand umbrella for all brain children
- The website IS the mind. The brand IS the person.

### 7. Debra Avatar / Video Presence
- FaceTime or video call with an AI avatar (HeyGen, Synthesia, or similar)
- Near-realtime API so it feels like a real conversation
- Give Debra a visual "form" when needed
- Research: HeyGen interactive avatar, Tavus, D-ID, Simli
- Would pair with ElevenLabs voice for full audiovisual presence
- Someday/maybe but would be cool as fuck

