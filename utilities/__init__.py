from config import Config
import smtplib
import os
from os.path import basename
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import COMMASPACE, formatdate


def send_email(subject, text, file_name=''):
    try:
        print("Sending email,please wait ....")
        
        msg = MIMEMultipart()
        msg['From'] = Config.EMAIL_FROM
        msg['To'] = COMMASPACE.join([Config.EMAIL_TO])
        msg['Date'] = formatdate(localtime=True)
        msg['Subject'] = subject

        msg.attach(MIMEText(text))
        if file_name:
            with open(os.path.join(os.getcwd(),"reports",file_name), "rb") as fil:
                part = MIMEApplication(
                    fil.read(),
                    Name=basename(file_name)
                )
            # After the file is closed
            part['Content-Disposition'] = 'attachment; filename="%s"' % basename(file_name)
            msg.attach(part)


        smtp = smtplib.SMTP(Config.EMAIL_HOSTNAME,587)
        smtp.starttls()
        smtp.login(Config.EMAIL_USERNAME, Config.EMAIL_PASSWORD)
        smtp.sendmail(Config.EMAIL_FROM, Config.EMAIL_TO, msg.as_string())
        smtp.close()
        print("Email was sent")
    except Exception as e:
        print("Exception occured "+str(e))

if __name__=='__main__':
    send_email('test','test')
    #send_mail("rohit","pathakrohit08@gmail.com","test with attachement","this is test email",'reports/2021-07-30-backup.log')
