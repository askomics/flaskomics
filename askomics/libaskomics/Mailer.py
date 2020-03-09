import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from askomics.libaskomics.Params import Params


class Mailer(Params):
    """Send mail

    Attributes
    ----------
    host : str
        SMTP host
    password : str
        SMTP password
    port : int
        SMTP port
    user : str
        SMTP user
    """

    def __init__(self, app, session):
        """init

        Parameters
        ----------
        app : Flask
            flask app
        session
            AskOmics session, contain the user
        """
        Params.__init__(self, app, session)
        try:
            self.host = self.settings.get('askomics', 'smtp_host')
            self.port = self.settings.get('askomics', 'smtp_port')
        except Exception:
            self.host = None
            self.port = None

        try:
            self.user = self.settings.get('askomics', 'smtp_user')
            self.password = self.settings.get('askomics', 'smtp_password')
        except Exception:
            self.user = None
            self.password = None

        try:
            self.sender = self.settings.get('askomics', 'smtp_sender')
        except Exception:
            self.sender = None

        try:
            self.connection = self.settings.get('askomics', 'smtp_connection')
        except Exception:
            self.connection = None

    def check_mailer(self):
        """Check if a smtp server is set

        Returns
        -------
        bool
            True if SMTP is set
        """
        if not self.host or not self.port or not self.sender:
            return False
        return True

    def send_mail(self, receiver, subject, body):
        """Send a mail

        Parameters
        ----------
        receiver : str
            receiver email adress
        subject : str
            email subject
        body : str
            Mail content
        """
        if self.check_mailer:
            pass
        message = MIMEMultipart('alternative')
        message.set_charset("utf-8")
        message["FROM"] = self.sender
        message["To"] = receiver
        message["Subject"] = subject

        _attach = MIMEText(body.encode('utf-8'), 'plain', 'UTF-8')
        message.attach(_attach)

        smtp = smtplib.SMTP(host=self.host, port=self.port)
        smtp.connect(self.host, self.port)

        if self.connection == "starttls":
            smtp.starttls()

        if self.user and self.password:
            smtp.login(self.user, self.password)

        smtp.sendmail(self.sender, receiver, message.as_string())
