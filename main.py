import copy
import os

from slack_bolt import App
from crontab import CronTab

import json
from dotenv import load_dotenv

from channel.get import get_channel_id

load_dotenv()

app = App(
    token=os.environ.get("SLACK_BOT_TOKEN"),
    signing_secret=os.environ.get("SLACK_SIGNING_SECRET"),
)


def get_user_ids_in_channel(channel_id, client):
    try:
        response = client.conversations_members(channel=channel_id)

        if response["ok"]:
            user_ids = response["members"]
            return user_ids
        else:
            return None
    except Exception as e:
        return None


def message_all_users_on_a_channel():
    channel = get_channel_id(os.environ.get("TARGET_CHANNEL_NAME"), app.client)
    users = get_user_ids_in_channel(client=app.client, channel_id=channel)
    for user in users:
        user_details = app.client.users_info(
            user=user
        )
        f = open('modals/ds_invitation.json')
        data = json.load(f)
        blocks = copy.deepcopy(data["blocks"])
        blocks[0]['text']['text'] = 'Hello ' + user_details['user']['real_name'] + blocks[0]['text']['text']
        app.client.chat_postMessage(channel=user, text="message from bot", blocks=blocks)


@app.action("invitation_received")
def open_ds_modal_from_invitation(body, ack):
    ack()

    f = open('modals/request.json')
    view = json.load(f)

    app.client.views_open(
        trigger_id=body["trigger_id"],
        view=view
    )


@app.command("/daily-standup")
def open_ds_modal(ack, body, client):
    ack()

    f = open('modals/request.json')
    view = json.load(f)

    app.client.views_open(
        trigger_id=body["trigger_id"],
        view=view
    )


# @app.view_submission()
# @app.view_closed()
@app.view("store_ds_response")
def handle_ds_submission(ack, body, client, view, logger):
    blocker_input = view['state']['values']['blockers']['blockers_input']['value']
    yesterday_input = view['state']['values']['yesterday']['yesterday_input']['value'].replace('\n', '\n>')
    today_input = view['state']['values']['today']['today_input']['value'].replace('\n', '\n>')
    user = body["user"]

    # errors = {}
    # if blocker_input is not None and len(blocker_input) <= 5:
    #     errors["blockers"] = "The value must be longer than 5 characters"
    # if len(errors) > 0:
    #     print(errors)
    #     ack(response_action="errors", errors=errors)
    #     return

    ack()

    try:
        f = open('modals/response.json')
        data = json.load(f)

        # user_details = app.client.users_info(
        #     user=user['id']
        # )
        # print(user_details)

        blocks = copy.deepcopy(data['blocks'])
        blocks[1]['text']['text'] = f"<@{user['id']}> posted an update for DS (Daily Standup)"
        blocks[2]['text']['text'] += yesterday_input
        blocks[3]['text']['text'] += today_input
        blocks[4]['text']['text'] += (blocker_input or "").replace('\n', '\n>')

        channel = get_channel_id(channel_name=os.environ.get("TARGET_CHANNEL_NAME"), client=app.client)
        app.client.chat_postMessage(
            channel=channel,
            text="hhh",
            blocks=blocks,
            as_user=True,
            username=user['username'],
        )
    except Exception as e:
        logger.exception(f"Failed to post a message {e}")


cron = CronTab(user=os.environ.get("CRON_USER"))
current_dir = os.getcwd()
file_path = os.path.join(current_dir, 'scheduler.py')
job = cron.new(command='crontab -r && cd {} && /bin/bash -c "source {} && python3 {}"'.format(current_dir, "venv/bin/activate", file_path))
job.setall('5 * * * *')
# job.setall('0 9 * * 0-4')
cron.write()


if __name__ == "__main__":
    app.start(port=int(os.environ.get("PORT", 3000)))
