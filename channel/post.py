from slack_sdk.errors import SlackApiError


def post_message(channel_id, client, message, blocks):
    try:
        result = client.chat_postMessage(
            channel=channel_id,
            text=message,
            blocks=blocks
        )

    except SlackApiError as e:
        print(f"Error: {e}")
