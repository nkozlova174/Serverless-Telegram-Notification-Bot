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

## Key Features
* No manual intervention needed — runs fully hands-off once deployed.
* No servers to manage or pay for when idle — serverless, pay-per-execution.
* Word sets and images are just data (S3 objects / config), so new predictions and pictures can be added without changing or redeploying code.
* Every run is fully unpredictable — no repeats guaranteed, thanks to independent random selection of each word and image.
