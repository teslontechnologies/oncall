import requests
import time
from datetime import datetime, timedelta
from apscheduler.schedulers.background import BackgroundScheduler
import os
from dotenv import load_dotenv
load_dotenv()

email_username = os.getenv('EMAIL_USERNAME')
email_password = os.getenv('EMAIL_PASSWORD')
roster_api_url = os.getenv('ROSTER_API_URL')
team_name = os.getenv('TEAM_NAME')

def send_email():
    # 1. Fetch on-call roster details
    try:
      api_url = f"{roster_api_url}/api/v0/teams/{team_name}/summary"
      response = requests.get(api_url)
      rosterDetails = response.json()
    except Exception as e:
      print(f"Error fetching roster details: {e}")
      return

    userEmailList = []
    tomorrow = datetime.now() + timedelta(days=1)
    date = tomorrow.strftime('%d-%m-%Y')

    for role, users in rosterDetails.get('next', {}).items():
      for user in users:
          userEmailList.append(user['user_contacts']['email'])

    # Optional override (for testing)
    # userEmailList = ['nagesh@teslon.io', 'atheeq@teslon.io']

    import smtplib
    from email.mime.text import MIMEText

    html_content = """
    <!DOCTYPE html>
    <html>
      <body style="font-family: Arial, sans-serif; color: #333;">
        <h2 style="color: #004080;">📅 Weekend On-Call Roster : {}</h2>

        <p>Hi Team,</p>

        <p>
          Please ensure availability and responsiveness during your scheduled day.
          If any conflicts arise, coordinate with your team and notify me in advance.
        </p>

        <p>Thanks for your support!</p>

        <p>Best regards,<br>
        Teslon</p>
      </body>
    </html>
    """.format(date)

    msg = MIMEText(html_content, 'html')
    msg['Subject'] = 'Weekend On-Call Roster.'
    msg['From'] = email_username
    msg['To'] = ', '.join(userEmailList)

    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    server.login(email_username, email_password)
    server.sendmail(email_username, userEmailList, msg.as_string())
    server.quit()

# Optional: Run once on startup
# send_email()

# Schedule the job to run every Friday and Saturday at 5 PM
sched = BackgroundScheduler()
sched.add_job(send_email, 'cron', day_of_week='5,6', hour=17, minute=0)

# For testing: run every minute
# sched.add_job(send_email, 'interval', minutes=1)

sched.start()

# Keep the script running indefinitely
try:
    while True:
        pass
except KeyboardInterrupt:
    print("Exiting script...")
    sched.shutdown()
    exit(0)

if __name__ == "__main__":
    send_email()
