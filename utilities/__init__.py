from config import Config
import smtplib

def send_email(message,subject):
    s = smtplib.SMTP(Config.EMAIL_HOSTNAME, 587)
    # start TLS for security
    s.starttls()
    # Authentication
    s.login(Config.EMAIL_USERNAME, Config.EMAIL_PASSWORD)
    message = 'Subject: {}\n\n{}'.format(subject, message)
    # sending the mail
    s.sendmail(Config.EMAIL_FROM, Config.EMAIL_TO, message)
    # terminating the session
    s.quit()

if __name__=='__main__':
    send_email('test','test')
