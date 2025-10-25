import base64
import json
import os
import sys
from datetime import datetime, timedelta
import pytz
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

class InterviewReminder:
    def __init__(self):
        self.service = None
        self.sender_email = "aaryanisbaby@gmail.com"
        # Interview details
        self.interview_date = datetime(2025, 10, 27, 10, 0, 0, tzinfo=pytz.timezone('Asia/Kolkata'))
        self.initialize_service()
    
    def initialize_service(self):
        """Initialize Gmail API service with OAuth credentials"""
        try:
            creds = None
            
            # Load credentials from environment variable (GitHub Secret)
            token_json = os.environ.get('GMAIL_TOKEN_JSON')
            if token_json:
                token_data = json.loads(base64.b64decode(token_json))
                creds = Credentials.from_authorized_user_info(token_data)
            
            # Refresh token if expired
            if creds and creds.expired and creds.refresh_token:
                print("🔄 Refreshing expired token...")
                creds.refresh(Request())
                
                new_token = {
                    'token': creds.token,
                    'refresh_token': creds.refresh_token,
                    'token_uri': creds.token_uri,
                    'client_id': creds.client_id,
                    'client_secret': creds.client_secret,
                    'scopes': creds.scopes
                }
                print("✅ Token refreshed successfully!")
                
                new_token_b64 = base64.b64encode(json.dumps(new_token).encode()).decode()
                if os.environ.get('GITHUB_OUTPUT'):
                    with open(os.environ['GITHUB_OUTPUT'], 'a') as f:
                        f.write(f"new_token={new_token_b64}\n")
                else:
                    print(f"New token available: {new_token_b64[:50]}...")
            
            if not creds or not creds.valid:
                raise Exception("Invalid credentials. Please check your token.")
            
            self.service = build('gmail', 'v1', credentials=creds)
            print("✅ Gmail API service initialized successfully!")
            
        except Exception as e:
            print(f"❌ Failed to initialize Gmail service: {str(e)}")
            sys.exit(1)
    
    def get_time_remaining(self):
        """Calculate time remaining until interview"""
        tz = pytz.timezone('Asia/Kolkata')
        now = datetime.now(tz)
        
        # If interview has passed, return None
        if now >= self.interview_date:
            return None
        
        time_diff = self.interview_date - now
        
        days = time_diff.days
        hours, remainder = divmod(time_diff.seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        
        return {
            'days': days,
            'hours': hours,
            'minutes': minutes,
            'total_hours': days * 24 + hours,
            'formatted': f"{days} days, {hours} hours, {minutes} minutes"
        }
    
    def create_message(self, to_email, subject, body_text, body_html=None):
        """Create email message with HTML support"""
        message = MIMEMultipart('alternative')
        
        # Anonymous sender - no name
        message['From'] = self.sender_email
        message['To'] = to_email
        message['Subject'] = subject
        message['Reply-To'] = self.sender_email
        message['Importance'] = 'normal'
        
        # Add plain text part
        part1 = MIMEText(body_text, 'plain', 'utf-8')
        message.attach(part1)
        
        # Add HTML part if provided
        if body_html:
            part2 = MIMEText(body_html, 'html', 'utf-8')
            message.attach(part2)
        
        return {'raw': base64.urlsafe_b64encode(message.as_bytes()).decode('utf-8')}
    
    def send_email(self, to_email, subject, body_text, body_html=None):
        """Send email using Gmail API"""
        try:
            message = self.create_message(to_email, subject, body_text, body_html)
            result = self.service.users().messages().send(
                userId='me',
                body=message
            ).execute()
            print(f"✅ Email sent to {to_email} - Message ID: {result['id']}")
            return True
        except HttpError as error:
            print(f"❌ Failed to send email to {to_email}: {error}")
            return False
        except Exception as e:
            print(f"❌ Unexpected error sending to {to_email}: {str(e)}")
            return False
    
    def get_greeting_content(self):
        """Get greeting based on current time (IST)"""
        tz = pytz.timezone('Asia/Kolkata')
        current_time = datetime.now(tz)
        hour = current_time.hour
        
        greetings = {
            'morning': {
                'time_range': (5, 12),
                'subject': 'Good Morning - Interview Reminder',
                'emoji': '🌅',
                'greeting': 'Good Morning',
                'message': 'Wishing you a productive day ahead.'
            },
            'afternoon': {
                'time_range': (12, 17),
                'subject': 'Good Afternoon - Interview Reminder',
                'emoji': '☀️',
                'greeting': 'Good Afternoon',
                'message': 'Hope your day is going well.'
            },
            'evening': {
                'time_range': (17, 21),
                'subject': 'Good Evening - Interview Reminder',
                'emoji': '🌆',
                'greeting': 'Good Evening',
                'message': 'Hope you had a productive day.'
            },
            'night': {
                'time_range': (21, 24),
                'subject': 'Good Night - Interview Reminder',
                'emoji': '🌙',
                'greeting': 'Good Night',
                'message': 'Wishing you a restful evening.'
            }
        }
        
        # Determine current greeting
        for key, value in greetings.items():
            start, end = value['time_range']
            if start <= hour < end:
                return value
        
        return greetings['night']
    
    def create_email_content(self, greeting_data, time_remaining):
        """Create professional email content"""
        
        if time_remaining is None:
            # Interview has passed - send follow-up message
            plain_text = f"""
{greeting_data['greeting']}! {greeting_data['message']}

I would love to work and contribute with your company.

Looking forward to the opportunity to be part of your team and make meaningful contributions.

Thank you for your consideration.
"""
            html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        body {{
            margin: 0;
            padding: 0;
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Arial, sans-serif;
            line-height: 1.6;
            color: #333333;
            background-color: #f5f5f5;
        }}
        
        .container {{
            max-width: 500px;
            margin: 20px auto;
            background-color: #ffffff;
            border-radius: 12px;
            padding: 30px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }}
        
        .greeting {{
            font-size: 20px;
            font-weight: bold;
            color: #1e40af;
            margin-bottom: 10px;
        }}
        
        .message {{
            font-size: 16px;
            color: #4b5563;
            margin-bottom: 20px;
        }}
        
        .interest-box {{
            background: linear-gradient(135deg, #dbeafe 0%, #bfdbfe 100%);
            border: 2px solid #3b82f6;
            padding: 20px;
            border-radius: 8px;
            text-align: center;
        }}
        
        .interest-text {{
            font-size: 18px;
            font-weight: bold;
            color: #1e40af;
            margin-bottom: 15px;
        }}
        
        .contribution-text {{
            font-size: 15px;
            color: #1e3a8a;
            line-height: 1.8;
        }}
        
        .thank-you {{
            font-size: 14px;
            color: #6b7280;
            margin-top: 20px;
            text-align: center;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="greeting">{greeting_data['greeting']}! {greeting_data['emoji']}</div>
        <div class="message">{greeting_data['message']}</div>
        
        <div class="interest-box">
            <div class="interest-text">💼 I would love to work and contribute with your company</div>
            <div class="contribution-text">
                Looking forward to the opportunity to be part of your team and make meaningful contributions.
            </div>
        </div>
        
        <div class="thank-you">Thank you for your consideration.</div>
    </div>
</body>
</html>
"""
            return plain_text, html_content
        
        plain_text = f"""
{greeting_data['greeting']}! {greeting_data['message']}

⏰ TIME REMAINING
{time_remaining['formatted']}
({time_remaining['total_hours']} hours remaining)
"""
        
        html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        body {{
            margin: 0;
            padding: 0;
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Arial, sans-serif;
            line-height: 1.6;
            color: #333333;
            background-color: #f5f5f5;
        }}
        
        .container {{
            max-width: 500px;
            margin: 20px auto;
            background-color: #ffffff;
            border-radius: 12px;
            padding: 30px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }}
        
        .greeting {{
            font-size: 20px;
            font-weight: bold;
            color: #1e40af;
            margin-bottom: 10px;
        }}
        
        .message {{
            font-size: 16px;
            color: #4b5563;
            margin-bottom: 25px;
        }}
        
        .countdown {{
            background: linear-gradient(135deg, #fee2e2 0%, #fecaca 100%);
            border: 2px solid #ef4444;
            padding: 20px;
            border-radius: 8px;
            text-align: center;
        }}
        
        .countdown-title {{
            font-size: 14px;
            font-weight: bold;
            color: #991b1b;
            margin-bottom: 10px;
        }}
        
        .countdown-value {{
            font-size: 22px;
            font-weight: bold;
            color: #dc2626;
            margin: 10px 0;
        }}
        
        .countdown-hours {{
            font-size: 16px;
            color: #991b1b;
            margin-top: 8px;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="greeting">{greeting_data['greeting']}! {greeting_data['emoji']}</div>
        <div class="message">{greeting_data['message']}</div>
        
        <div class="countdown">
            <div class="countdown-title">⏰ TIME REMAINING</div>
            <div class="countdown-value">{time_remaining['formatted']}</div>
            <div class="countdown-hours">({time_remaining['total_hours']} hours remaining)</div>
        </div>
    </div>
</body>
</html>
"""
        
        return plain_text, html_content
    
    def send_reminders(self):
        """Send reminder emails to all recipients"""
        # Load recipients
        try:
            with open('recipients.json', 'r') as f:
                recipients = json.load(f)
        except FileNotFoundError:
            print("❌ recipients.json not found.")
            sys.exit(1)
        
        # Check if interview has passed
        time_remaining = self.get_time_remaining()
        
        # Get current greeting
        greeting_data = self.get_greeting_content()
        
        # Statistics
        total = len([r for r in recipients if r.get('active', True)])
        sent = 0
        failed = 0
        
        print(f"\n{'='*60}")
        print(f"📧 Interview Reminder Campaign: {greeting_data['greeting']}")
        print(f"👥 Total recipients: {total}")
        if time_remaining:
            print(f"⏰ Time remaining: {time_remaining['formatted']}")
        else:
            print(f"💼 Post-interview follow-up message")
        print(f"🕐 Current time: {datetime.now(pytz.timezone('Asia/Kolkata')).strftime('%Y-%m-%d %H:%M:%S IST')}")
        print(f"{'='*60}\n")
        
        # Create email content
        plain_text, html_content = self.create_email_content(greeting_data, time_remaining)
        
        # Send to each recipient
        for recipient in recipients:
            if not recipient.get('active', True):
                print(f"⏩ Skipping {recipient['email']} (inactive)")
                continue
            
            # Send email
            if self.send_email(
                recipient['email'],
                greeting_data['subject'],
                plain_text,
                html_content
            ):
                sent += 1
            else:
                failed += 1
        
        # Print summary
        print(f"\n{'='*60}")
        print(f"📊 Campaign Summary:")
        print(f"✅ Successfully sent: {sent}/{total}")
        print(f"❌ Failed: {failed}/{total}")
        print(f"{'='*60}\n")
        
        return sent, failed

def main():
    """Main execution function"""
    print("""
    ╔══════════════════════════════════════════╗
    ║     Professional Interview Reminder      ║
    ║            MTX Group Interview           ║
    ╚══════════════════════════════════════════╝
    """)
    
    # Check for required environment variable
    if not os.environ.get('GMAIL_TOKEN_JSON'):
        print("❌ Error: GMAIL_TOKEN_JSON environment variable not found!")
        print("Please add your token.json content as a GitHub Secret.")
        sys.exit(1)
    
    # Initialize and run
    reminder = InterviewReminder()
    sent, failed = reminder.send_reminders()
    
    # Exit with error code if all emails failed
    if sent == 0 and failed > 0:
        sys.exit(1)

if __name__ == "__main__":
    main()
