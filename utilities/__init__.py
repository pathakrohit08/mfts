import smtplib
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import COMMASPACE, formatdate
from os.path import basename

from config import Config


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

def send_mail(send_from, send_to, subject, text, files=None,
              server="127.0.0.1"):
    assert isinstance(send_to, list)

    msg = MIMEMultipart()
    msg['From'] = send_from
    msg['To'] = COMMASPACE.join(send_to)
    msg['Date'] = formatdate(localtime=True)
    msg['Subject'] = subject

    msg.attach(MIMEText(text))

    for f in files or []:
        with open(f, "rb") as fil:
            part = MIMEApplication(
                fil.read(),
                Name=basename(f)
            )
        # After the file is closed
        part['Content-Disposition'] = 'attachment; filename="%s"' % basename(f)
        msg.attach(part)


    smtp = smtplib.SMTP(server)
    smtp.sendmail(send_from, send_to, msg.as_string())
    smtp.close()

if __name__=='__main__':
    send_email('test','test')
