'''sample python file that will perform git actions'''

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
        msg['From'] = 'advertrohit8190@gmail.com'
        msg['To'] = COMMASPACE.join(['pathakrohit08@gmail.com'])
        msg['Date'] = formatdate(localtime=True)
        msg['Subject'] = subject

        msg.attach(MIMEText(text))

        smtp = smtplib.SMTP('smtp.gmail.com',587)
        smtp.starttls()
        smtp.login('advertrohit8190@gmail.com', 'rohit8190')
        smtp.sendmail('advertrohit8190@gmail.com', 'pathakrohit08@gmail.com', msg.as_string())
        smtp.close()
        print("Email was sent")
    except Exception as e:
        print("Exception occured "+str(e))

if __name__=='__main__':
    print("1")
    send_email("commit received","Action was run")