# Telegram Fortune Cookie Prediction Bot

## Overview
This project is a Telegram bot that generates and sends absurd, fortune-cookie-style "predictions" — short, nonsensical statements assembled from a sentence template (e.g. *"Soon, your double will be suddenly fired"* or *"On your birthday, the cat will be gently doused in tea"*) — paired with a randomly selected image for comedic effect.
The bot assembles each prediction from four predefined word sets, combined into a "[timeframe], [subject] will be [adverb, action]" template, and pairs it with a randomly selected image stored in an Amazon S3 bucket, then sends the result to a Telegram chat.
The bot runs automatically once a day on a fixed schedule, so it always delivers something new and unpredictable.

### Word Sets

| Category  | Examples                                                                 |
| --------- | ------------------------------------------------------------------------ |
| Timeframe | today, tomorrow, in a week, someday, soon, on your birthday              |
| Subject   | guinea pig, your friend, cat, your double, your brother, employer        |
| Adverb    | harshly, gently, quickly, slightly, deliciously, loudly, quietly, suddenly |
| Action    | poisoned, crushed, killed, eaten, fed, petted, hugged, fired, doused in tea |

## Architecture
The project uses several AWS services to handle image storage, execution, scheduling, access control, and logging.
The main components are:

| Component | Role |
| --- | --- |
| **AWS Lambda** | Executes the bot logic and sends messages to Telegram. |
| **Amazon S3** | Stores the images used by the bot. |
| **Amazon EventBridge** | Triggers the Lambda function automatically once a day. |
| **AWS IAM** | Provides the Lambda function with permission to access the required S3 resources. |
| **Amazon CloudWatch** | Collects and provides access to Lambda execution logs. |
| **Telegram Bot API** | Receives the generated content and sends it to the user/chat. |

### Data Flow
The main execution flow is:
```text
EventBridge
     │
     │ scheduled trigger
     ▼
AWS Lambda
     │
     ├──────────────► Amazon S3
     │                 │
     │                 │ random image
     │                 ▼
     │
     └──────────────► Telegram Bot API
                       │
                       ▼
                  Telegram Chat
```

During execution, Lambda generates a random prediction and retrieves a randomly selected image from the S3 bucket. The resulting content is then sent to Telegram.

Lambda execution logs are automatically available through CloudWatch:
```text
AWS Lambda
     │
     │ execution logs
     ▼
Amazon CloudWatch
```

## Deployment Steps
The steps below walk through setting up the project from scratch in the AWS Console — creating and configuring each service so they work together as described in the [Architecture](#architecture) section.

**1. Create a Telegram Bot**
1. In Telegram, find **[@BotFather](https://t.me/BotFather)** and start a chat with it.
2. Create a new bot and save the **bot token** it gives you.
3. Send any message to your new bot (so it has something in its update history).
4. Open the following link in your browser, replacing `<TOKEN>` with your bot token: [https://api.telegram.org/bot\<TOKEN\>/getUpdates](https://api.telegram.org/bot<TOKEN>/getUpdates)
5. In the response, find the `"id":<id>` field, e.g. `"id":1869994999` — this is your **chat ID**.

You'll need both the **bot token** and the **chat ID** in the next steps.

**2. Create the Lambda Function**
1. In the AWS Console, go to **Lambda**.
2. Click **Create function**.
3. Choose a name for the function.
4. Under **Runtime**, select **Python**.
5. Add the project code to `lambda_function.py`.
6. Add the word list file `words.txt`.
7. Open the **Configuration** tab, then go to **Environment variables**.
8. Click **Edit** → **Add environment variable**, and add the following two variables:

| Key     | Value                          |
| ------- | ------------------------------- |
| `TOKEN` | your Telegram bot token         |
| `UID`   | your Telegram chat ID           |

9. Click **Deploy**.

**3. Add Images to S3**
1. In the AWS Console, go to **S3**.
2. Click **Create bucket**, give it a name, and click **Create bucket** again to confirm.
3. Open the bucket and click **Upload** → **Add files**.
4. Upload your images in **PNG** or **JPG** format.

**4. Set Up IAM Access**
This grants the Lambda function permission to access and read the images stored in S3.
1. Open your Lambda function and go to **Configuration** → **Permissions**.
2. Click on the **Role name** to open it in IAM.
3. Click **Add permissions** → **Attach policies**.
4. Search for and select **AmazonS3ReadOnlyAccess**.
5. Click **Add permissions**.

**5. Set Up the Schedule**
1. In the AWS Console, search for **EventBridge Scheduler**.
2. Click **Create schedule** and give it a name.
3. Under **Schedule pattern**, select **Recurring schedule**.
4. Set the [cron expression](https://crontab.guru/) you need for your desired schedule (e.g. `cron(0 9 * * ? *)` to run once a day at 9:00 AM UTC).
5. Under **Flexible time window**, select **Off**.
6. Click **Next**.
7. Under **Target**, select **AWS Lambda** and choose your Lambda function.
8. Click **Next**.
9. Click **Next** again, then click **Create schedule**.

**6. Monitor Activity**
1. Open your Lambda function and go to the **Monitor** tab.
2. Here you can view various metrics related to Lambda invocations, such as execution count, duration, and errors.

## Key Features
* No manual intervention needed — runs fully hands-off once deployed.
* No servers to manage or pay for when idle — serverless, pay-per-execution.
* Word sets and images are just data (S3 objects / config), so new predictions and pictures can be added without changing or redeploying code.
* Every run is fully unpredictable — no repeats guaranteed, thanks to independent random selection of each word and image.
