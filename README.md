# silanthro/slack

A tool to send Slack messages.

This requires the following environment variable:

- `SLACK_WEBHOOKS`: The webhooks used to send the Slack message. The tool will only be able to send messages to the channels supported by these webhooks. Supply a strictly valid JSON-encoded object e.g. use double quotes: '{"general": "<WEBHOOK_TO_GENERAL_CHANNEL>", "random": "<WEBHOOK_TO_RANDOM_CHANNEL>"}'. Channel names should not include the "#" prefix.


## Set up the webhooks

Follow the instructions [here](https://api.slack.com/messaging/webhooks) to set up a Slack app and create a webhook.

Each webhook supports a specific channel. To add more webhooks, navigate to "Incoming Webhooks" in your App Settings page and click on "Add New Webhook to Workspace".
