# Research: Google Home / Home Assistant Integration
*Queued 2026-03-26 by Alex*

## The Goal
Get Debra controlling smart home devices via Google Home and/or Home Assistant.

## Why It Matters
- "She runs the damn show" needs to include the HOUSE
- Voice control via Google Home speakers
- Automation triggers (leave house, arrive home, bedtime, etc.)
- Ties into Mirror vision (ambient intelligence)

## Options to Research
1. **Home Assistant** - open source, local control, massive device support
   - REST API for OpenClaw integration
   - Can expose to Google Home via cloud or Nabu Casa
   - Runs on Pi, Mac mini, Docker
2. **Google Home API** - direct integration
   - Google Home Developer Console
   - Matter/Thread support
   - Routines and automations
3. **Both** - HA as the brain, Google Home as the voice interface

## Questions
- What smart devices does Alex currently have?
- Google Home speakers/hubs in the apartment?
- Preference: local-first (HA) vs cloud (Google)?
- Budget for hardware (HA hub, sensors, etc.)?

## Status
- [ ] Research HA + OpenClaw integration options
- [ ] Inventory Alex's current smart home setup
- [ ] Prototype basic control (lights, thermostat)
