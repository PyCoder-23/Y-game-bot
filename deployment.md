# Deployment Guide: Game of Y Discord Bot

Follow these steps to set up and run your Game of Y Discord bot.

## 1. Create a Discord Application
1. Go to the [Discord Developer Portal](https://discord.com/developers/applications).
2. Click **New Application** and give it a name (e.g., "Game of Y Bot").
3. Navigate to the **Bot** tab on the left sidebar.
4. Click **Reset Token** (or **Copy Token**) to get your **Bot Token**. Save this securely; you will need it later.
5. Under the **Privileged Gateway Intents** section, enable:
   - **Message Content Intent** (Required to read commands like `!play`).
   - **Server Members Intent** (Recommended for managing challenges).
6. Click **Save Changes**.

## 2. Invite the Bot to Your Server
1. Navigate to the **OAuth2** -> **URL Generator** tab.
2. Under **Scopes**, select `bot`.
3. Under **Bot Permissions**, select:
   - `Send Messages`
   - `Embed Links`
   - `Attach Files`
   - `Read Message History`
4. Copy the generated URL and paste it into your browser to invite the bot to your server.

## 3. Prepare the Environment
Ensure you have Python 3.8+ installed.

1. **Install Dependencies**:
   Open your terminal and run:
   ```bash
   pip install -r requirements.txt
   ```

2. **Configure Your Token**:
   You can either:
   - **Option A (Recommended)**: Set an environment variable:
     ```bash
     export DISCORD_TOKEN='your_actual_token_here'
     ```
   - **Option B**: Open `bot.py` and replace `"YOUR_BOT_TOKEN_HERE"` with your actual token.

## 4. Run the Bot
Navigate to your project directory and run:
```bash
python bot.py
```
You should see a message in the terminal: `✅ Bot is online as Game of Y Bot`.

## 5. Playing the Game
Once the bot is online, use the following commands in any channel:
- `!help`: Shows the command list.
- `!challenge @user`: Starts the challenge flow.
- `!play <number>`: Places your stone on the board.

---

### Troubleshooting
- **Command not responding?**: Ensure the "Message Content Intent" is enabled in the Developer Portal.
- **Images not sending?**: Ensure the bot has "Attach Files" permission in the channel.
- **Error: ModuleNotFoundError**: Ensure you ran `pip install -r requirements.txt`.
