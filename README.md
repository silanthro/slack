# silanthro/slack

A tool to send Slack messages.

This requires the following environment variable:

- `SLACK_WEBHOOKS`: The webhook(s) used to send the Slack message. The tool will only be able to send messages to the channels supported by these webhooks. If only a single webhook is supported, pass the webhook as the environment variable. To allow multiple channels/webhooks, supply a strictly valid JSON-encoded object e.g. use double quotes: '{"general": "<WEBHOOK_TO_GENERAL_CHANNEL>", "random": "<WEBHOOK_TO_RANDOM_CHANNEL>"}'.


## Set up the webhooks

Follow the instructions [here](https://api.slack.com/messaging/webhooks) to set up a Slack app and create a webhook.

Each webhook supports a specific channel. To add more webhooks, navigate to "Incoming Webhooks" in your App Settings page and click on "Add New Webhook to Workspace".
