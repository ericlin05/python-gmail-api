# Python Email Sender using Gmail API

A simple Python class to use Gmail API to send emails. The code base was based on Chris Brown's work @ [python-gmail-api](https://github.com/chris-brown-nz/python-gmail-api/blob/master/python_gmail_api.py).

For details on how to set it up, please refer to Chris Brown's [Read Me Page](https://github.com/chris-brown-nz/python-gmail-api) for instructions.

On top of Chris Brown's work, I have added the following new features:

1. Ability to pass a text file path to the "body" parameter and the class will be able to put the content from the file as the email body automatically.
2. Ability to add multiple attachments to emails.
3. Ability to send HTML email, rather than just plain text email.

## How to use the API?

See example below:

```
    from gmail_api import GmailAPI

    # content_type can be either "html" or "plain"
    # attachments can be None, String or Array
    # message can be String contains email content or a path to a file that contains the email content
    GmailAPI().set_content_type(content_type) \
              .set_attachments(attachments) \
              .send(
                  from_addr, to_addr,
                  subject, message
              )
```

## How to run send-mail.py file?

See example below:

```
python send-mail.py --to to@email.com --from from@email.com --subject "Gmail API Test" \
--message "This is a test, please ignore"
```

```
python send-mail.py --to to@email.com --from from@email.com --subject "Gmail API Test" \
--message /tmp/email-content-file.html --content-type html
```

```
python send-mail.py --to to@email.com --from from@email.com --subject "Gmail API Test" \
--message /tmp/email-content-file.html --content-type html \
--attachments "/path/to/file1.txt,/path/to/file2.pdf,/path/to/file3.mp3"
```