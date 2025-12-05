import zulip
import random

RESPONSES = [
    "It is certain.",
    "It is decidedly so.",
    "Without a doubt.",
    "Yes – definitely.",
    "You may rely on it.",
    "As I see it, yes.",
    "Most likely.",
    "Outlook good.",
    "Yes.",
    "Signs point to yes.",
    "Reply hazy, try again.",
    "Ask again later.",
    "Better not tell you now.",
    "Cannot predict now.",
    "Concentrate and ask again.",
    "Don’t count on it.",
    "My reply is no.",
    "My sources say no.",
    "Outlook not so good.",
    "Very doubtful.",
]

def handle_message(event: dict, client: zulip.Client, bot_email: str) -> None:
    if event["type"] != "message":
        return

    msg = event["message"]

    # Don't reply to our own messages
    if msg["sender_email"] == bot_email:
        return

    content = msg["content"].lower()
    msg_type = msg["type"]  # "private" or "stream"

    is_private = (msg_type == "private")
    mentioned = "magic8-bot" in content

    # For DMs/group PMs: respond to any message in the convo.
    # For streams: only respond if mentioned.
    if not (is_private or mentioned):
        return

    response = random.choice(RESPONSES)
    reply_text = f"🎱 *The Magic 8 Ball says:* “{response}”"

    if is_private:
        # Reply into the SAME private conversation (1-1 or group)
        # display_recipient is a list of user dicts for private messages
        recipients = [u["email"] for u in msg["display_recipient"]]
        client.send_message({
            "type": "private",
            "to": recipients,
            "content": reply_text,
        })
    else:
        # Reply back into the same stream + topic
        client.send_message({
            "type": "stream",
            "to": msg["display_recipient"],  # stream name
            "topic": msg.get("topic") or msg.get("subject") or "(no topic)",
            "content": f"@**{msg['sender_full_name']}**\n{reply_text}",
        })

def main() -> None:
    client = zulip.Client(config_file="zuliprc")
    profile = client.get_profile()
    bot_email = profile["email"]

    print("Magic 8 Bot running…")
    client.call_on_each_event(
        lambda event: handle_message(event, client, bot_email),
        event_types=["message"],
    )

if __name__ == "__main__":
    main()