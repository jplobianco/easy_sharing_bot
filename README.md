# EasySharingBot

EasySharingBot is a telegram bot that helps you share online accounts and credentials with friends and team members.


## How to run this bot

### Create a bot in Telegram using @BotFather

Talk to [@BotFather](https://telegram.me/botfather) to create your bot and get the token.


### Run the Bot using Docker

Now you are going to run the bot using docker and pass the token you created in last step.

```bash
docker container run -e BOT_TOKEN="YOUR_BOT_TOKEN_HERE" jplobianco/easy_sharing_bot
```

If you want to keep the database persistent, then:

```bash
docker create volume bot-db
docker container run -v bot-db:/app/bot.db -e BOT_TOKEN="YOUR_BOT_TOKEN_HERE" jplobianco/easy_sharing_bot
```

If you want to restrict the access to the bot for a specific set of chats, then pass the desired chat ids as an env variable to the container:

```bash
docker container run -v bot-db:/app/bot.db -e BOT_TOKEN="YOUR_BOT_TOKEN_HERE" -e ALLOWED_CHAT_IDS="COMMA_SEPARATED_IDS_ALLOWED_TO_USE_BOT" jplobianco/easy_sharing_bot
```

### Start using the bot and getting help

* Call your bot in a telegram chat or channel and type ```/start```
* To get help type ```/help```
