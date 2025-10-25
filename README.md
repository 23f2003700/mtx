# Professional Interview Reminder 📅

Automated professional email reminders for SpanIdea Systems interview scheduled on October 13, 2025 at 10:00 AM IST.

## Features ✨

- 🕐 **Real-time Countdown**: Shows exact time remaining until interview
- 📧 **Professional Tone**: Business-appropriate greeting emails
- 🔄 **4 Daily Reminders**: Morning, Afternoon, Evening, Night
- 🎯 **Anonymous Sender**: Sends from email without revealing personal name
- ⏰ **Auto-stop**: Stops sending after interview date passes

## Interview Details

- **Company**: SpanIdea Systems
- **Date**: Monday, October 13, 2025
- **Time**: 10:00 AM IST
- **Recipients**: hr@spanidea.com, timbulb03@gmail.com

## Schedule

Reminders sent at:
- 🌅 8:00 AM IST (Good Morning)
- ☀️ 12:00 PM IST (Good Afternoon)
- 🌆 5:00 PM IST (Good Evening)
- 🌙 9:00 PM IST (Good Night)

## Setup

1. GitHub Secret `GMAIL_TOKEN_JSON` configured
2. Recipients configured in `recipients.json`
3. Automated workflow runs until October 13, 2025

## Usage

### Manual Trigger
1. Go to **Actions** tab
2. Select **Interview Reminder - SpanIdea**
3. Click **Run workflow**

### Local Testing
```bash
python interview_reminder.py
```

## Security 🔒

- Anonymous sender (no personal name revealed)
- Professional email format
- Secure token storage in GitHub Secrets

---

Good luck with your interview! 🍀
