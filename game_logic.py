import time
from board_engine import render_board
from wincheck import check_win
import io

def process_move(game, player_id, node_id):
    """
    Processes a move in an active game.
    Returns (success, message, is_win, win_path)
    """
    # 1. Verify it is user's turn
    player_color = 'R' if player_id == game["red_player_id"] else 'B'
    if player_color != game["turn"]:
        return False, "It is not your turn!", False, None
    
    # 2. Verify node number valid
    if not (1 <= node_id <= 93):
        return False, "Invalid node number. Must be between 1 and 93.", False, None
    
    # 3. Verify node not already occupied
    board_list = list(game["board"])
    if board_list[node_id - 1] != 'E':
        return False, f"Node {node_id} is already occupied.", False, None
    
    # 4. Capture node
    board_list[node_id - 1] = player_color
    new_board = "".join(board_list)
    game["board"] = new_board
    game["move_history"].append((player_color, node_id))
    game["last_move_timestamp"] = time.time()
    
    # 5. Run win detection
    is_win, win_path = check_win(new_board, node_id)
    
    if not is_win:
        # Switch turn
        game["turn"] = 'B' if player_color == 'R' else 'R'
        
        # Pie rule: swap is only available after the VERY first move.
        # If any second move is made, swap is no longer possible.
        if len(game["move_history"]) > 1:
            game["swap_available"] = False
            
        next_player_id = game["blue_player_id"] if game["turn"] == 'B' else game["red_player_id"]
        msg = f"{'Red' if player_color == 'R' else 'Blue'} played {node_id}. <@{next_player_id}> to move."
        if game["swap_available"] and len(game["move_history"]) == 1:
            msg += "\n💡 **Blue** can use `!swap` to switch roles instead of playing."
    else:
        msg = f"🏆 **{'Red' if player_color == 'R' else 'Blue'} wins by connecting all three sides!**"
        
    return True, msg, is_win, win_path

def swap_players(game):
    """
    Implements the 'pie rule' swap.
    """
    if not game["swap_available"] or len(game["move_history"]) != 1:
        return False, "Swap is only available immediately after the first move."
    
    # Swap IDs
    game["red_player_id"], game["blue_player_id"] = game["blue_player_id"], game["red_player_id"]
    
    # The first move was 'R'. Since we swapped players, the first move is now owned by the new 'Red'.
    # The turn should now be 'Blue' (the original Red player).
    game["turn"] = 'B'
    game["swap_available"] = False
    
    next_player_id = game["blue_player_id"]
    msg = f"🔄 **Roles swapped!** The first move now belongs to <@{game['red_player_id']}>. <@{next_player_id}> (Blue) to move."
    return True, msg

def get_board_image(game, last_node=None, win_path=None):
    """
    Renders the board and returns an io.BytesIO object.
    """
    img = render_board(game["board"], last_move=last_node, win_path=win_path)
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    buf.seek(0)
    return buf
