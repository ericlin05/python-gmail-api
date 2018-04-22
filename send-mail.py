"""
Simple script to use GmailAPI to send emails
"""

from __future__ import print_function
from gmail_api import GmailAPI
from argparse import ArgumentParser

def main():
    parser = ArgumentParser()
    parser.add_argument("--to",action="store", help="To address.", dest="to_addr")
    parser.add_argument("--from", action="store", help="From address.", dest="from_addr")
    parser.add_argument("--subject", action="store", help="To address.", dest="subject")
    parser.add_argument("--message", action="store", help="The message you want to send.", dest="message")
    parser.add_argument("--content-type", action="store",
                        help="Content type of email, default to plain, can also be html.", dest="content_type")
    parser.add_argument("--attachments", action="store",
                        help="A list of files as attachment.", dest="attachments")

    args = parser.parse_args()

    if args.to_addr is None:
        raise Exception("No to address defined")

    if args.from_addr is None:
        raise Exception("No from address defined")

    if args.subject is None:
        raise Exception("No subject defined")

    if args.message is None:
        raise Exception("No message defined")

    GmailAPI().set_content_type(args.content_type) \
              .set_attachments(args.attachments) \
              .send(
                  args.from_addr, args.to_addr,
                  args.subject, args.message
              )

if __name__ == '__main__':
    main()
