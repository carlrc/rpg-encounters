import asyncio
import logging

import boto3

from app.utils import get_or_throw

logger = logging.getLogger(__name__)

CHARSET = "UTF-8"
AWS_REGION = get_or_throw("AWS_REGION")
SOURCE_IDENTITY = get_or_throw("SES_IDENTITY")


class SimpleEmailService:
    def __init__(self):
        self.client = boto3.client("ses", region_name=AWS_REGION)

    async def send(
        self, subject: str, recipient_email: str, body_html: str, body_text: str
    ):
        try:

            def _send_email():
                return self.client.send_email(
                    Destination={
                        "ToAddresses": [
                            recipient_email,
                        ],
                    },
                    Message={
                        "Body": {
                            "Html": {
                                "Charset": CHARSET,
                                "Data": body_html,
                            },
                            "Text": {
                                "Charset": CHARSET,
                                "Data": body_text,
                            },
                        },
                        "Subject": {
                            "Charset": CHARSET,
                            "Data": subject,
                        },
                    },
                    Source=SOURCE_IDENTITY,
                )

            loop = asyncio.get_running_loop()
            response = await loop.run_in_executor(None, _send_email)
            return response

        except Exception as e:
            logger.error(f"Could not send SES email: {e}")
            raise
