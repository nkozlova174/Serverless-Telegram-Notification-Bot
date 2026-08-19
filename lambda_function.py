import json
import os
import urllib.request
import random
import boto3


s3 = boto3.client("s3")
BUCKET = "my-telegram-bot-images-12345"


def generate_message():
    with open("words.txt", "r") as file:
        lines = file.read().split('\n')

    message = ''

    for line in lines:
        message += random.choice(line.split(', '))
        message += ' '

    return message


def generate_image_url():
    image_number = random.randint(1, 7)
    key = f"{image_number}.png"

    image_url = s3.generate_presigned_url(
        "get_object",
        Params={
            "Bucket": BUCKET,
            "Key": key
        },
        ExpiresIn=300
    )

    return image_url


def lambda_handler(event, context):
    BOT_TOKEN = os.environ["TOKEN"]
    CHAT_ID = os.environ["UID"]

    # Send message
    message = generate_message()

    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"

    data = json.dumps({
        "chat_id": CHAT_ID,
        "text": message
    }).encode("utf-8")

    request = urllib.request.Request(
        url,
        data=data,
        headers={
            "Content-Type": "application/json"
        },
        method="POST"
    )

    with urllib.request.urlopen(request) as response:
        print("Message:", response.read().decode("utf-8"))


    # Send image
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendPhoto"

    image_url = generate_image_url()

    data = json.dumps({
        "chat_id": CHAT_ID,
        "photo": image_url
    }).encode("utf-8")

    request = urllib.request.Request(
        url,
        data=data,
        headers={
            "Content-Type": "application/json"
        },
        method="POST"
    )

    with urllib.request.urlopen(request) as response:
        print("Image:", response.read().decode("utf-8"))


    return {
        "statusCode": 200,
        "body": json.dumps("Message and image sent successfully!")
    }