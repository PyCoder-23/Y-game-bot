import json
import os

# Load graph structure for connectivity
GRAPH_PATH = "board_graph.json"
ADJ = {}
if os.path.exists(GRAPH_PATH):
    with open(GRAPH_PATH, "r") as f:
        graph = json.load(f)
        for u, v in graph["edges"]:
            if u not in ADJ: ADJ[u] = []
            if v not in ADJ: ADJ[v] = []
            ADJ[u].append(v)
            ADJ[v].append(u)

# Define sides for win detection
# Side A: nodes 1 through 9
# Side B: nodes 9 through 17
# Side C: nodes 17 through 24 + node 1
SIDE_A = set(range(1, 10))
SIDE_B = set(range(9, 18))
SIDE_C = set(range(17, 25)).union({1})

def check_win(board_state, last_node):
    """
    Checks if the player who just moved to last_node has won.
    A win occurs if a connected component of same-colored nodes 
    touches all three sides of the board.
    board_state: String of 93 chars ('E', 'R', 'B')
    last_node: 1-indexed node ID
    """
    color = board_state[last_node - 1]
    if color == 'E':
        return False, []

    # BFS to find the connected component of the same color
    visited = {last_node}
    queue = [last_node]
    component = [last_node]
    
    touches_a = last_node in SIDE_A
    touches_b = last_node in SIDE_B
    touches_c = last_node in SIDE_C
    
    idx = 0
    while idx < len(queue):
        u = queue[idx]
        idx += 1
        
        for v in ADJ.get(u, []):
            if v not in visited and board_state[v - 1] == color:
                visited.add(v)
                queue.append(v)
                component.append(v)
                if v in SIDE_A: touches_a = True
                if v in SIDE_B: touches_b = True
                if v in SIDE_C: touches_c = True
                
    if touches_a and touches_b and touches_c:
        # Return winning component to highlight
        # Actually, for Y, the winning edges are more important
        win_edges = []
        for u in component:
            for v in ADJ.get(u, []):
                if v in visited:
                    win_edges.append(tuple(sorted([u, v])))
        return True, list(set(win_edges))
        
    return False, []
