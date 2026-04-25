# Discord Y Board Game Bot

A polished, fully functional Discord bot for playing the connection board game "Y" on a 93-node visually rendered board.

## Features
- **Multiplayer Challenge System:** Challenge other users in your server.
- **Simultaneous Games:** Supports multiple games across different channels.
- **Professional Image Rendering:** Real-time generation of the game board using `Pillow`, outputting a Discord-friendly PNG.
- **Graph-Based Win Detection:** Uses BFS graph traversal to detect when a player connects all three sides of the triangular board.
- **Timeout Management:** Players can use `!flag` to claim victory if an opponent is inactive for 5 minutes.

## Project Structure
- `bot.py` - The main discord bot setup and command definitions.
- `game_logic.py` - Defines board rules, moves, and graph-based win detection.
- `renderer.py` - Pillow-based code for drawing the board, stones, and node numbers.
- `board_graph.json` - The generated topology and coordinate mapping of the 93 nodes on the board.
- `generate_graph.py` - The Python script used to mathematically generate the 93-node geodesic triangulation.

## Setup Instructions

1. **Prerequisites:**
   Make sure you have Python 3.9+ installed.

2. **Install Dependencies:**
   Run the following command in your terminal to install the necessary libraries:
   ```bash
   pip install -r requirements.txt
   ```

3. **Get a Discord Bot Token:**
   - Go to the [Discord Developer Portal](https://discord.com/developers/applications).
   - Click "New Application", name it, and go to the "Bot" tab.
   - Click "Reset Token" and copy your bot token.
   - Enable the **Message Content Intent** in the "Privileged Gateway Intents" section.

4. **Run the Bot:**
   Set the `DISCORD_TOKEN` environment variable and run the bot.
   
   On Mac/Linux:
   ```bash
   export DISCORD_TOKEN="your_token_here"
   python bot.py
   ```
   
   On Windows (PowerShell):
   ```powershell
   $env:DISCORD_TOKEN="your_token_here"
   python bot.py
   ```

## How to Play
Once the bot is online, invite it to your server and use the following commands:
- `!challenge @user` - Challenge another player.
- `!accept` / `!reject` - Accept or reject a challenge.
- `!play <node_number>` - Place your stone on the given node (1-93).
- `!board` - Resend the latest visual rendering of the board.
- `!giveup` - Resign the game.
- `!flag` - Win by timeout if the opponent takes over 5 minutes.
- `!help` - Show all commands.

## Future Expansions (AI / Tournaments)
To extend the bot later to include AI opponents:
1. Open `game_logic.py` and import or implement a Minimax/Monte Carlo Tree Search (MCTS) engine.
2. In `bot.py`, add a command like `!playbot easy`.
3. When the bot's turn is triggered, call the AI function to select the best move and pass it to `make_move(board, node, color)`.
4. Since the state is represented purely as a string (`"-" * 93`) and logic is decoupled from rendering, AI simulations can be run very efficiently.
# Y-game
