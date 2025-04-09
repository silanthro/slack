import json
import os
from typing import Optional

import requests


def _get_webhooks() -> dict:
    webhooks_str = os.environ.get("SLACK_WEBHOOKS")
    if not webhooks_str:
        raise ValueError("No webhooks provided via environment variable SLACK_WEBHOOKS")
    return json.loads(webhooks_str)


WEBHOOKS = _get_webhooks()


def get_available_channels() -> list[str]:
    """
    Retrieve the list of available Slack channels

    Returns:
        A list of strings representing available Slack channels
    """
    return list(WEBHOOKS.keys())


def send_message(content: str, channel: Optional[str] = None) -> str:
    """
    Send a Slack message

    Args:
    - content (str): Message content, supports Slack mrkdwn syntax (see below)
    - channel (Optional[str]): Channel name, defaults to None, which will send the message to the default channel
        If multiple channels are provided, selects the first

    Returns:
        If message is successful, returns "Message sent"
        Otherwise, returns the error message as a string

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

    try:
        if channel is None:
            webhook = list(WEBHOOKS.values())[0]
        else:
            try:
                webhook = WEBHOOKS[channel]
            except KeyError:
                return f'Channel "{channel}" either does not exist or is unavailable. Please pass a channel from the following available list {get_available_channels()}'

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
    except Exception as e:
        return str(e)
