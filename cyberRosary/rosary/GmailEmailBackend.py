from django.core.mail.backends.base import BaseEmailBackend


class GmailEmailBackend(BaseEmailBackend):
    def send_messages(self, email_messages):
        pass