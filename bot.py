import discord
from discord.ext import commands
import os
import time
import io
import storage
import game_logic
from dotenv import load_dotenv
load_dotenv()

# --- Bot Setup ---
TOKEN = os.getenv("DISCORD_TOKEN")
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents, help_command=None)

# --- Commands ---

@bot.command()
async def challenge(ctx, user: discord.Member):
    """Invite another user to a game."""
    if user == ctx.author:
        return await ctx.send("❌ You cannot challenge yourself!")
    if user.bot:
        return await ctx.send("❌ You cannot challenge bots!")
    
    # Check if either player is already in a game
    if storage.get_game_by_user(ctx.author.id):
        return await ctx.send("❌ You are already in an active game!")
    if storage.get_game_by_user(user.id):
        return await ctx.send(f"❌ {user.display_name} is already in an active game!")
    
    # Create pending challenge
    storage.pending_challenges[user.id] = {
        "challenger_id": ctx.author.id,
        "timestamp": time.time()
    }
    
    await ctx.send(f"⚔️ **{ctx.author.display_name}** has challenged **{user.mention}** to the Game of Y!\nUse `!accept` or `!reject` to respond.")

@bot.command()
async def accept(ctx):
    """Accept incoming challenge."""
    challenge = storage.pending_challenges.get(ctx.author.id)
    if not challenge:
        return await ctx.send("❌ You have no pending challenges.")
    
    challenger_id = challenge["challenger_id"]
    
    # Double check active games
    if storage.get_game_by_user(challenger_id):
        storage.pending_challenges.pop(ctx.author.id)
        return await ctx.send("❌ The challenger is now in another game.")
    
    # Start game
    game = storage.create_game(ctx.channel.id, challenger_id, ctx.author.id)
    storage.pending_challenges.pop(ctx.author.id)
    
    await ctx.send(f"✅ Game Started! <@{challenger_id}> (Red) vs {ctx.author.mention} (Blue).")
    
    # Send initial board
    buf = game_logic.get_board_image(game)
    file = discord.File(buf, filename="board.png")
    await ctx.send("🔴 **Red (Challenger)** to move first.", file=file)

@bot.command()
async def reject(ctx):
    """Reject incoming challenge."""
    if ctx.author.id in storage.pending_challenges:
        challenge = storage.pending_challenges.pop(ctx.author.id)
        challenger = await bot.fetch_user(challenge["challenger_id"])
        await ctx.send(f"❌ Challenge rejected. Sorry {challenger.mention}!")
    else:
        await ctx.send("❌ You have no pending challenges.")

@bot.command()
async def play(ctx, number: int):
    """Capture a numbered node."""
    game = storage.get_game_by_user(ctx.author.id)
    if not game:
        return await ctx.send("❌ You are not in an active game.")
    
    # Process move
    success, message, is_win, win_path = game_logic.process_move(game, ctx.author.id, number)
    
    if not success:
        return await ctx.send(f"❌ {message}")
    
    # Render and send updated board
    buf = game_logic.get_board_image(game, last_node=number, win_path=win_path)
    file = discord.File(buf, filename="board.png")
    
    await ctx.send(message, file=file)
    
    if is_win:
        storage.end_game(ctx.channel.id)

@bot.command()
async def swap(ctx):
    """Exercise the 'pie rule' to swap roles after the first move."""
    game = storage.get_game_by_user(ctx.author.id)
    if not game:
        return await ctx.send("❌ You are not in an active game.")
    
    if ctx.author.id != game["blue_player_id"]:
        return await ctx.send("❌ Only the second player (Blue) can use the swap rule.")
        
    success, message = game_logic.swap_players(game)
    if not success:
        return await ctx.send(f"❌ {message}")
        
    # Re-render the board (no new moves, but roles changed in logic)
    # The last move is still there, but now belongs to the new Red.
    last_node = game["move_history"][0][1]
    buf = game_logic.get_board_image(game, last_node=last_node)
    file = discord.File(buf, filename="board.png")
    
    await ctx.send(message, file=file)

@bot.command()
async def giveup(ctx):
    """Resign the current game."""
    game = storage.get_game_by_user(ctx.author.id)
    if not game:
        return await ctx.send("❌ You are not in an active game.")
    
    # Opponent wins
    winner_id = game["blue_player_id"] if ctx.author.id == game["red_player_id"] else game["red_player_id"]
    winner_color = "Blue" if winner_id == game["blue_player_id"] else "Red"
    
    await ctx.send(f"🏳️ **{ctx.author.display_name}** has resigned. **{winner_color} (<@{winner_id}>) wins!**")
    storage.end_game(ctx.channel.id)

@bot.command()
async def flag(ctx):
    """Claim timeout victory (300s)."""
    game = storage.get_game_by_user(ctx.author.id)
    if not game:
        return await ctx.send("❌ You are not in an active game.")
    
    # Check if it's opponent's turn and time has passed
    current_turn_id = game["red_player_id"] if game["turn"] == "R" else game["blue_player_id"]
    if ctx.author.id == current_turn_id:
        return await ctx.send("❌ You cannot flag yourself. It is your turn!")
    
    time_since_move = time.time() - game["last_move_timestamp"]
    TIMEOUT = 300 # 5 minutes
    
    if time_since_move >= TIMEOUT:
        winner_id = game["red_player_id"] if ctx.author.id == game["red_player_id"] else game["blue_player_id"]
        winner_color = "Red" if winner_id == game["red_player_id"] else "Blue"
        await ctx.send(f"⏰ **Timeout!** {ctx.author.mention} claims victory as the opponent failed to move within 300s. **{winner_color} wins!**")
        storage.end_game(ctx.channel.id)
    else:
        remaining = int(TIMEOUT - time_since_move)
        await ctx.send(f"❌ Opponent still has {remaining} seconds to move.")

@bot.command()
async def help(ctx):
    """Display help information."""
    embed = discord.Embed(title="🎮 Game of Y - Command List", color=0x3b82f6)
    embed.add_field(name="!challenge @user", value="Invite someone to a new game.", inline=False)
    embed.add_field(name="!accept / !reject", value="Respond to a pending challenge.", inline=False)
    embed.add_field(name="!play <number>", value="Capture a node (e.g. `!play 42`).", inline=False)
    embed.add_field(name="!swap", value="[Pie Rule] Swap roles with opponent after their first move.", inline=False)
    embed.add_field(name="!giveup", value="Resign your current game.", inline=False)
    embed.add_field(name="!flag", value="Win if the opponent takes >300s to move.", inline=False)
    embed.add_field(name="!help", value="Show this menu.", inline=False)
    embed.set_footer(text="Red starts first. Connect all three sides to win!")
    await ctx.send(embed=embed)

# --- Event Listeners ---

@bot.event
async def on_ready():
    print(f"✅ Bot is online as {bot.user}")
    await bot.change_presence(activity=discord.Game(name="Game of Y | !help"))

if __name__ == "__main__":
    if TOKEN == "YOUR_BOT_TOKEN_HERE":
        print("⚠️  Error: Please set your DISCORD_TOKEN in the environment variables or bot.py.")
    else:
        bot.run(TOKEN)
