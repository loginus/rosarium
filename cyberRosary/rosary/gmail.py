import base64
import os
import pickle
import threading
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from django.core.mail.backends.base import BaseEmailBackend
from django.core.mail.message import sanitize_address
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

from cyberRosary import settings

# Sending email using gmail API based on:
# https://developers.google.com/gmail/api/quickstart/python
# https://developers.google.com/gmail/api/guides/sending

SCOPES = ['https://www.googleapis.com/auth/gmail.send']


class GmailEmailBackend(BaseEmailBackend):

    def __init__(self, user_id=None,
                 fail_silently=False,
                 token_storage=None,
                 credentials_file=None,
                 **kwargs):
        super().__init__(fail_silently=fail_silently)
        self.user_id = settings.EMAIL_GMAIL_USER_ID if user_id is None else user_id
        self.service = None
        self.token_storage = settings.EMAIL_GMAIL_TOKEN_STORAGE if token_storage is None else token_storage
        self.credentials_file = settings.EMAIL_GMAIL_CREDENTIALS_FILE if credentials_file is None else credentials_file
        self._lock = threading.RLock()

    def get_credentials(self):
        # The file token.pickle stores the user's access and refresh tokens, and is
        # created automatically when the authorization flow completes for the first
        # time.
        creds = None
        if os.path.exists(self.token_storage):
            with open(self.token_storage, 'rb') as token:
                creds = pickle.load(token)
        # If there are no (valid) credentials available, let the user log in.
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    self.credentials_file, SCOPES)
                creds = flow.run_local_server(port=0)
            # Save the credentials for the next run
            with open(self.token_storage, 'wb') as token:
                pickle.dump(creds, token)
        return creds

    def open(self):
        if self.service:
            return False
        try:
            credentials = self.get_credentials()
            self.service = build('gmail', 'v1', credentials=credentials)
            return True
        except Exception:
            if not self.fail_silently:
                raise
            return False

    def close(self):
        if self.service is None:
            return
        self.service = None

    def send_messages(self, email_messages):
        """
        Send one or more EmailMessage objects and return the number of email
        messages sent.
        """
        if not email_messages:
            return 0
        with self._lock:
            new_conn_created = self.open()
            if not self.service or new_conn_created is None:
                # We failed silently on open().
                # Trying to send would be pointless.
                return 0
            num_sent = 0
            for message in email_messages:
                sent = self._send(message)
                if sent:
                    num_sent += 1
            if new_conn_created:
                self.close()
        return num_sent

    def _send(self, email_message):
        """A helper method that does the actual sending."""
        if not email_message.recipients():
            return False
        encoding = email_message.encoding or settings.DEFAULT_CHARSET
        from_email = sanitize_address(email_message.from_email, encoding)
        recipients = [sanitize_address(addr, encoding) for addr in email_message.recipients()]
        message_text = email_message.body
        subject = email_message.subject
        message = self.create_message_without_attachment(from_email, recipients, subject, message_text)
        try:
            message_sent = self.service.users().messages().send(userId=self.user_id, body=message).execute()
        except:
            return False
        return True

    def create_message_without_attachment(self, sender, to, subject, message_text_plain):
        message = MIMEMultipart('alternative')
        message['Subject'] = subject
        message['From'] = sender
        message['To'] = ','.join(to)

        message.attach(MIMEText(message_text_plain, 'plain'))

        raw_message_no_attachment = base64.urlsafe_b64encode(message.as_bytes())
        raw_message_no_attachment = raw_message_no_attachment.decode()
        body = {'raw': raw_message_no_attachment}
        return body
