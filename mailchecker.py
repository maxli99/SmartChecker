#!/usr/bin/python
import re
import os
import time
import poplib
import cStringIO
import email
import base64
import string
import subprocess

reportFileName = "/home/smartchecker/SmartChecker/reports/mailChecker.html"

def getAddressList(line):
    addressList = []
    try:
        for col in re.split("(<\S+>)", line):
            rslt = re.match("<(\S+)>", col)
            if rslt is not None and rslt.group(1) != "logparser@yahoo.com":
                addressList.append(rslt.group(1))
    except:
        return []
    return addressList

def parse(logFileName, subject):
    try:
        global reportFileName
        """
        if re.match("NG_.*", subject):
            checkList = "check_ng_tn.ckl"
        if re.match("NS_.*", subject):
            checkList = "check_ns_tn.ckl"
        """
        checkList = subject
        os.system("rm -f /tmp/check_report.html")
        os.system("rm -rf /tmp/mailChecker");
        os.system("mkdir /tmp/mailChecker");
        os.chdir("/tmp/mailChecker")
        if re.match("\S+\.rar", logFileName):
            os.system("unrar e %s /tmp/mailChecker" % logFileName)
        if re.match("\S+\.gz", logFileName):
            os.system("gzip -d %s" % logFileName)
        if re.match("\S+\.zip", logFileName):
            os.system("unzip %s -d /tmp/mailChecker" % logFileName)

        os.chdir("/home/smartchecker/SmartChecker")
        for root,dirs,files in os.walk("/tmp/mailChecker"):
            if len(files) > 0 and re.match("\S+\.log", files[0]):
                print "Start parsing %s/%s with check list \'%s\'" % (root, files[0], checkList)
                print "/home/smartchecker/SmartChecker/smartchecker.py -r %s %s/%s --saveto %s --silent" % (checkList, root, files[0], reportFileName)
                errorcode = os.system("/home/smartchecker/SmartChecker/smartchecker.py -r %s %s/%s --saveto %s --silent" % (checkList, root, files[0], reportFileName))
                print "Parsing has been done. (error code:%d)" % errorcode
                if errorcode != 0:
                    raise "Error"
        #print "pandoc %s -o /tmp/check_report.html -s" % reportFileName
        #os.system("pandoc %s -o /tmp/check_report.html -s" % reportFileName)
        #os.system("pandoc %s -o /tmp/check_report.html -s --template=/home/smartchecker/SmartChecker/templates/common_report.html" % reportFileName)
        rslt = subprocess.check_output(["cat", reportFileName])
        return rslt
    except:
        return None

def sendMail(receiptor, cc, subject, message, reportFileName):
    import smtplib
    from email.mime.text import MIMEText
    from email.MIMEMultipart import MIMEMultipart
    from email.MIMEBase import MIMEBase
    from email.header import Header 
    from email import Encoders
    try:
        msg = MIMEMultipart('alternative')
        msg['Subject'] = Header("%s -- parsing result -- %s" % (subject, time.strftime("%Y-%m-%d %H:%M:%S")), 'utf-8')
        msg['From'] = 'logparser@yahoo.com'
        msg['To'] = string.join(receiptor,";")
        msg['Cc'] = string.join(cc,";")

        if reportFileName is not None:
            part = MIMEBase('application', "octet-stream")
            part.set_payload(open(reportFileName, "rb").read())
            Encoders.encode_base64(part)
            
            part.add_header('Content-Disposition', 'attachment; filename="%s"' % re.split("/",reportFileName)[-1])
            msg.attach(part)

        htmlPart = MIMEText(message, 'html', 'utf-8')
        msg.attach(htmlPart)

        s=smtplib.SMTP_SSL("smtp.mail.yahoo.com")
        s.login("logparser@yahoo.com", "justdumptome")
        s.sendmail("logparser@yahoo.com", receiptor+cc, msg.as_string())
    except Exception,R:
        print R     
        return R

for i in range(4):
    if i > 2:
        print "Failed to access the mail server."
        exit(-1)
    try:
        mail = poplib.POP3_SSL("plus.pop.mail.yahoo.com")
        mail.user("logparser@yahoo.com")
        mail.pass_("justdumptome")
        break
    except:
        pass
        time.sleep(5)
print mail.getwelcome()

#number of emails
numMessages=len(mail.list()[1])
print 'num of messages:',numMessages

mails = []

for i in range(numMessages):
    mails.append(mail.retr(i+1))

for m in mails:
    buf = cStringIO.StringIO()
    for j in m[1]:
        print >>buf,j
    buf.seek(0)
    
    msg = email.message_from_file(buf)
    From = None
    Cc = None
    Subject = None
    errorMsg = None
    print >>buf,j
    buf.seek(0)
    
    msg = email.message_from_file(buf)
    From = None
    To = None
    Cc = None
    Subject = None
    errorMsg = None
    for part in msg.walk():
        if part.get("From") is not None:
            rslt = re.match(".*<(\S+)>", part.get("From"))
            if rslt is not None:
                From = rslt.group(1)
                print "From: %s" % From
        if part.get("Subject") is not None:
            rslt = part.get("Subject")
            if rslt is not None:
                Subject = part.get("Subject")
                print "Subject: %s" % Subject
        if part.get("Cc") is not None:
            rslt = part.get("Cc")
            if rslt is not None:
                Cc = part.get("Cc")
                print "Cc: %s" % Cc
        if part.get("To") is not None:
            rslt = part.get("To")
            if rslt is not None:
                To = part.get("To")
                print "To: %s" % To

        contenttype = part.get_content_type()
        filename = part.get_filename()
        if filename and From and Subject:
            if os.system ("ls /home/smartchecker/SmartChecker/checklist/%s" % Subject) != 0:
                errorMsg = "The check list doesn't exist."
            if re.match("\S+\.(gz|zip|rar)", filename) is None or not (re.match("\S+octet\-stream", contenttype) or re.match("\S+x-gzip", contenttype) or re.match("application/x-zip-compressed", contenttype)):
                errorMsg = "invalid attachement: %s %s" % (filename, contenttype)
            #save
            if errorMsg is None:
                print "Received a request from %s" % From
                logfilename = "/tmp/mailchecker.%s" % filename
                f = open(logfilename,'wb')
                f.write(base64.decodestring(part.get_payload()))
                f.close()
                print "copy log to %s" % logfilename
                rslt = parse(logfilename, Subject)
                print "\nparsing has been finished."
                if rslt is not None:
                    sendMail(getAddressList(To) + [From], getAddressList(Cc), Subject, "Please find the report from the attachment.", reportFileName) 
                    os.system("rm %s" % reportFileName)
                else:
                    sendMail(getAddressList(To) + [From], getAddressList(Cc), Subject, "Faile to parse the log. Please contact the administrator.", None)
                os.system("mv %s /home/smartchecker/SmartChecker/archived" % logfilename)
                print "result hase been sent to %s" % From
            else:
                sendMail(getAddressList(To) + [From], getAddressList(Cc), Subject, errorMsg, None)
    if errorMsg is not None:
        print "------------------------------------------------------------"
        print "From: %s" % From
        print "Subject %s" % Subject
        print "Error Message: %s" % errorMsg
        print "------------------------------------------------------------"
     
n = len(mail.list()[1])

while n > 0:
    mail.dele(n)
    time.sleep(1)
    n -= 1

mail.quit()
