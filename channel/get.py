from slack_sdk.errors import SlackApiError


def get_channel_id(channel_name, client):
    conversation_id = None
    try:
        for result in client.conversations_list():
            if conversation_id is not None:
                break
            for channel in result["channels"]:
                if channel["name"] == channel_name:
                    conversation_id = channel["id"]
                    # print(f"Found conversation ID: {conversation_id}")
                    break
        return conversation_id

    except SlackApiError as e:
        print(f"Error: {e}")
