
from oauth2client import file, client, tools
from googleapiclient.discovery import build
import base64, os, mimetypes, httplib2
import email.mime.multipart, email.mime.image, email.mime.text, \
    email.mime.audio, email.mime.base, email.mime.application

class GmailAPI:
    def __init__(self):
        self.CLIENT_SECRET_FILE = 'client_secret.json'
        self.CREDENTIAL_FILE = 'python_gmail_api_credentials.json'
        self.APPLICATION_NAME = 'python-gmail-api'
        self.DEBUG = True

        # default to "plain" email
        self.content_type = 'plain'

        # default to no attachments
        self.attachments = []

        # Setup the Gmail API
        self.SCOPES = ['https://mail.google.com/',
                  'https://www.googleapis.com/auth/gmail.compose',
                  'https://www.googleapis.com/auth/gmail.modify',
                  'https://www.googleapis.com/auth/gmail.send']
        pass

    def send(self, from_addr, to_addr, subject, body):
        """
        The main function to be called from outside world to send email

        :param from_addr: Sender's email address
        :param to_addr: Receipent's email address
        :param subject: The subject of the email
        :param body: The main message of the email
        :return: void
        """
        if self.DEBUG:
            print('Sending message to: ' + to_addr + ', from: ' + from_addr)
            print("Using " + self.content_type + " format")

        body_message = body

        # check if "body" is passed in as a file or not, if file exist and readable,
        # get the content from the file as the content of the email
        if os.path.exists(body) and os.path.isfile(body):
            if self.DEBUG:
                print("Loading from file " + body)

            with open(body, 'r') as email_file:
                body_message = email_file.read()

        message = self.__create_message(from_addr, to_addr, subject, body_message)
        credentials = self.__get_credentials()
        service = self.__build_service(credentials)
        raw = message['raw']
        raw_decoded = raw.decode("utf-8")
        message = {'raw': raw_decoded}
        message_id = self.__send_message(service, 'me', message)

        if self.DEBUG:
            print('Message sent with ID: ' + message_id)

    def __get_credentials(self):
        """
        Gets valid user credentials from storage.
        If nothing has been stored, or if the stored credentials are invalid,
        the OAuth2 flow is completed to obtain the new credentials.

        :return: Credentials, the obtained credential
        """
        home_dir = os.path.expanduser('~')
        credential_dir = os.path.join(home_dir, '.credentials')
        if not os.path.exists(credential_dir):
            os.makedirs(credential_dir)
        credential_path = os.path.join(credential_dir, self.CREDENTIAL_FILE)
        store = file.Storage(credential_path)
        credentials = store.get()
        if not credentials or credentials.invalid:
            flow = client.flow_from_clientsecrets(self.CLIENT_SECRET_FILE, self.SCOPES)
            flow.user_agent = self.APPLICATION_NAME
            credentials = tools.run_flow(flow, store)

            if self.DEBUG:
                print('Storing credentials to ' + credential_path)
        return credentials

    def __create_message(self, sender, to, subject, message_text):
        """
        If we have attachments, use __create_message_with_attachment to create special
        message with attachment ability, otherwise, just create a normal message for email

        :param sender: Email address of the sender
        :param to: Email address of the receiver.
        :param subject: The subject of the email message.
        :param message_text: The text of the email message.
        :return: An object containing a base64url encoded email object.
        """
        if len(self.attachments) == 0:
            return self.__create_normal_message(sender, to, subject, message_text)

        return self.__create_message_with_attachment(sender, to, subject, message_text, self.attachments)

    def __create_normal_message(self, sender, to, subject, message_text):
        """
        Create a message for an email.

        :param sender: Email address of the sender
        :param to: Email address of the receiver.
        :param subject: The subject of the email message.
        :param message_text: The text of the email message.
        :return: An object containing a base64url encoded email object.
        """
        message = email.mime.text.MIMEText(message_text, self.content_type, 'utf-8')
        message['to'] = to
        message['from'] = sender
        message['subject'] = subject
        encoded_message = {'raw': base64.urlsafe_b64encode(message.as_string().encode("utf-8"))}
        return encoded_message

    def __create_message_with_attachment(self, sender, to, subject, message_text, attachments):
        """
        Create a message with ability to add attachments

        :param sender: Email address of the sender
        :param to: Email address of the receiver.
        :param subject: The subject of the email message.
        :param message_text: The text of the email message.
        :param attachments: A list of files to be attached to the email.
        :return: An object containing a base64url encoded email object.
        """
        message = email.mime.multipart.MIMEMultipart()
        message['to'] = to
        message['from'] = sender
        message['subject'] = subject
        msg = email.mime.text.MIMEText(message_text, self.content_type, 'utf-8')
        message.attach(msg)

        for file in attachments:
            if not os.path.exists(file):
                if self.DEBUG:
                    print("File: " + file + " not found")
                continue

            if not os.path.isfile(file):
                if self.DEBUG:
                    print(file + " is not a file, unable to attach")
                continue

            content_type, encoding = mimetypes.guess_type(file)
            if content_type is None or encoding is not None:
                content_type = 'application/octet-stream'

            if self.DEBUG:
                print("Attachment content type: " + content_type + " for file " + file)

            main_type, sub_type = content_type.split('/', 1)
            fp = open(file, 'rb')

            if main_type == 'text':
                msg = email.mime.text.MIMEText(fp.read(), _subtype=sub_type)
            elif main_type == 'image':
                msg = email.mime.image.MIMEImage(fp.read(), _subtype=sub_type)
            elif main_type == 'audio':
                msg = email.mime.audio.MIMEAudio(fp.read(), _subtype=sub_type)
            elif main_type == 'application':
                msg = email.mime.application.MIMEApplication(fp.read(), _subtype=sub_type)
            else:
                msg = email.mime.base.MIMEBase(main_type, sub_type)
                msg.set_payload(fp.read())

            fp.close()

            filename = os.path.basename(file)
            msg.add_header('Content-Disposition', 'attachment', filename=filename)
            message.attach(msg)

        return {'raw': base64.urlsafe_b64encode(message.as_string())}

    def __send_message(self, service, user_id, message):
        """

        :param service: Authorized Gmail API service instance.
        :param user_id: User's email address. The special value "me"
                        can be used to indicate the authenticated user.
        :param message: Message to be sent.
        :return: String, sent message ID
        """
        message = (service.users().messages().send(userId=user_id, body=message)
                  .execute())
        return message['id']

    def __build_service(self, credentials):
        """
        Build a Gmail service object.

        :param credentials: OAuth 2.0 credentials.
        :return: Gmail service object.
        """
        http = httplib2.Http()
        http = credentials.authorize(http)
        return build('gmail', 'v1', http=http)

    def set_content_type(self, content_type):
        """
        Interface function to set the content_type for the email

        :param content_type: The content type of the email, currently supports "plain" and "html"
        :return: GmailAPI
        """
        if content_type != 'html' and content_type != 'plain':
            content_type = 'plain'

        self.content_type = content_type
        return self

    def set_attachments(self, attachments):
        """
        Interface function to set the attachments for the email

        :param attachments: Can be either a string or list
        :return: GmailAPI
        """
        if isinstance(attachments, list):
            self.attachments = attachments
        elif isinstance(attachments, str):
            self.attachments = str(attachments).split(',')
        else:
            self.attachments = []

        return self
