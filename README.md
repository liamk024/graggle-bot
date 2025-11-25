# Graggle bot

This is the repository for the graggle discord bot.

## Features

### OpenAI Responses

 - Pinging the bot will send your message to it as a prompt and send the response in chat
 - Last 10 messages sent as context, but only the original message will be sent as context if message type is reply
 - Prompts can be selected using the `/openai_response` commands:
     - `/openai_response set <name> <url>` Sets the prompt profile with name \<name\> to the contents of \<url\>. This includes any html if present, so the page should be plaintext only
     - `/openai_response remove <name>` Removes the profile with name \<name\> as long as it isn't the only profile
     - `/openai_response switch <name>` Switches the active prompt profile to \<name\>
     - `/openai_response list` Lists all available prompt profiles

### Website Monitoring
 - Automatically checks websites every 60 seconds to check if they're down
 - Monitored websites can be configured using the `/website_check` commands:
    - `/website_check add <url> <channel>` Sets the status of the website at \<url\> to be monitored in \<channel\>
    - `/website_check remove <url>` Removes monitoring for \<url\> 
    - `/website_check list` Lists all currently monitored websites
    - `/website_check silent` Toggles suppression of notifications for monitored websites going down. Does not stop monitoring.

## Requirements

Built for ARM64 and AMD64 systems, recommended to be run inside of a docker container using the latest tag.\
Dev branch is only built for ARM64 systems and may be unstable or outdated. It is available using the dev tag.

## Options

Options can be set using environment variables. They can either be loaded directly from the host system, from a
`.env` file, or as environment options passed through to a docker container.

- DISCORD_TOKEN: Required token to connect to a discord bot
- OPENAI_API_KEY: Required api key for openai to complete chat messages
- OPENAI_MODEL: Optional variable to change model used (str default='gpt-5-nano')
- MAX_RESPONSE_TOKENS: Optional variable to change max response tokens from openai (str default='256')
- WEBSITE_CHECK_INTERVAL: How long to wait in between pinging websites in seconds (int default=60.0)