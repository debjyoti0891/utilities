#!/usr/bin/python

def send_email(user, pwd, recipient, subject, body):
    import smtplib
    import time

    gmail_user = user
    gmail_pwd = pwd
    FROM = user
    TO = recipient if type(recipient) is list else [recipient]
    SUBJECT = subject
    TEXT = body

    # Prepare actual message
    message = """\From: %s\nTo: %s\nSubject: %s\n\n%s
    """ % (FROM, ", ".join(TO), SUBJECT, TEXT)
    while True:
		try:
		    server = smtplib.SMTP("smtp.gmail.com", 587)
		    server.ehlo()
		    server.starttls()
		    server.login(gmail_user, gmail_pwd)
		    server.sendmail(FROM, TO, message)
		    server.close()
		    print 'successfully sent the mail'
		    break
		except:
			print "failed to send mail"
			time.sleep(10)
		

def get_ip():
	import subprocess
	return subprocess.check_output(['ifconfig','-a'])

def get_time():
	import time
	localtime = time.asctime( time.localtime(time.time()) )
	return localtime
uname = 'username@gmail.com'
password = 'pwd'	   
destUname = 'touser@something.com'
send_email(uname,password,destUname,'IP:',get_time()+"\n"+get_ip())
