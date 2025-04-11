import json
import os
from typing import Optional

import requests

from md2blockkit import md2blockkit


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
    - content (str): Message content, supports Markdown syntax
    - channel (Optional[str]): Channel name, defaults to None, which will send the message to the default channel
        If multiple channels are provided, selects the first

    Returns:
        If message is successful, returns "Message sent"
        Otherwise, returns the error message as a string
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
            "blocks": md2blockkit(content),
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
