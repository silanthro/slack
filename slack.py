import json
import os
from typing import Optional

import requests


def _get_webhooks() -> dict:
    webhooks_str = os.environ.get("SLACK_WEBHOOKS")
    if not webhooks_str:
        raise ValueError("No webhooks provided via environment variable SLACK_WEBHOOKS")
    if "{" in webhooks_str:
        return json.loads(webhooks_str)
    else:
        return webhooks_str


WEBHOOKS = _get_webhooks()


def send_message(content: str, channel: Optional[str] = None) -> str:
    """
    Send a Slack message

    Args:
    - content (str): Message content, supports Slack mrkdwn syntax (see below)
    - channel (Optional[str]): Channel name, defaults to None, which will send the message to the default channel
        If multiple channels are provided, selects the first

    Returns:
        A string "Message sent"

    On mrkdwn syntax:
    _italic_ will produce italicized text
    *bold* will produce bold text
    ~strike~ will produce strikethrough text
    Highlight text as a block quote by using the > character at the beginning of one or more lines
    Highlight inline code using single backticks, or multi-line code blocks using 3 backticks
    Links:
        Links should be formatted like this: <http://www.example.com|This message is a link>
        URLs with spaces will break, so we recommend that you remove any spaces from your URL links.
    Escape characters:
        Slack uses &, <, and > as control characters for special parsing in text objects, so they must be converted to HTML entities.
        & -> &amp;
        < -> &lt;
        > -> &gt;
    """

    webhook = None
    if channel is None:
        if isinstance(WEBHOOKS, str):
            webhook = WEBHOOKS
        else:
            webhook = list(WEBHOOKS.values())[0]
    else:
        webhook = WEBHOOKS[channel]

    body = {
        "blocks": [
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": content,
                },
            },
        ],
    }

    requests.post(
        webhook,
        headers={
            "Content-type": "application/json",
        },
        data=json.dumps(body),
    )

    return "Message sent"
