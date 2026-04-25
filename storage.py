import time

# In-memory storage for active games and pending challenges
# In a production environment, this would use Redis or a Database.

# active_games[channel_id] = { ... }
active_games = {}

# pending_challenges[challenged_user_id] = { challenger_id, timestamp }
pending_challenges = {}

# user_to_game[user_id] = channel_id
# Ensures one user is only in one game at a time
user_to_game = {}

def create_game(channel_id, red_id, blue_id):
    game = {
        "channel_id": channel_id,
        "red_player_id": red_id,
        "blue_player_id": blue_id,
        "turn": "R",
        "board": "E" * 93,
        "move_history": [],
        "last_move_timestamp": time.time(),
        "started_at": time.time()
    }
    active_games[channel_id] = game
    user_to_game[red_id] = channel_id
    user_to_game[blue_id] = channel_id
    return game

def end_game(channel_id):
    if channel_id in active_games:
        game = active_games[channel_id]
        user_to_game.pop(game["red_player_id"], None)
        user_to_game.pop(game["blue_player_id"], None)
        active_games.pop(channel_id)

def get_game_by_user(user_id):
    channel_id = user_to_game.get(user_id)
    return active_games.get(channel_id) if channel_id else None

def get_game_by_channel(channel_id):
    return active_games.get(channel_id)
