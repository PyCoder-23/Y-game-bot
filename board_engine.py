import PIL.Image as Image
import PIL.ImageDraw as ImageDraw
import PIL.ImageFont as ImageFont
import io
import os
from coords import COORDS

def get_adjacencies():
    """
    Returns the adjacency list for the 93-node Y board based on the spiral topology.
    """
    rings_def = [
        (1,  24, 9),   # Ring 0
        (25, 45, 8),   # Ring 1
        (46, 63, 7),   # Ring 2
        (64, 78, 6),   # Ring 3
        (79, 90, 5),   # Ring 4
        (91, 93, 2),   # Ring 5
    ]
    
    edges = set()
    
    def add_edge(u, v):
        edges.add(tuple(sorted([u, v])))

    # Within-ring connections
    for r_idx in range(6):
        start, end, _ = rings_def[r_idx]
        count = end - start + 1
        for i in range(count):
            u = start + i
            v = start + (i + 1) % count
            add_edge(u, v)
            
    # Inter-ring connections (Zipper)
    for r_idx in range(5):
        s1, e1, _ = rings_def[r_idx]
        s2, e2, _ = rings_def[r_idx + 1]
        
        outer = list(range(s1, e1 + 1))
        inner = list(range(s2, e2 + 1))
        
        o_ptr, i_ptr = 0, 0
        while o_ptr < len(outer) or i_ptr < len(inner):
            add_edge(outer[o_ptr % len(outer)], inner[i_ptr % len(inner)])
            if (o_ptr + 1) / len(outer) < (i_ptr + 1) / len(inner):
                o_ptr += 1
            else:
                i_ptr += 1
                
    # --- Specific User Overrides ---
    # Remove requested edges
    to_remove = [
        (90, 93), (79, 91), (91, 82), (92, 86), (92, 83), (93, 87)
    ]
    for u, v in to_remove:
        edge = tuple(sorted([u, v]))
        if edge in edges:
            edges.remove(edge)
            
    # Add requested edges
    to_add = [
        (90, 80), (89, 91), (81, 92), (93, 85), (88, 86), (82, 84)
    ]
    for u, v in to_add:
        add_edge(u, v)
                
    return sorted(list(edges))

def render_board(board_state=None, last_move=None, win_path=None):
    """
    Renders the Y board using the provided manual coordinates.
    High resolution for tournament quality.
    """
    if board_state is None:
        board_state = 'E' * 93
        
    # --- Configuration ---
    # Double resolution for crisp quality
    WIDTH, HEIGHT = 2000, 2000
    # Original coordinates are 800x800. We scale them up to fit 2000x2000.
    SCALE_FACTOR = 2.2
    OFFSET_X = 120
    OFFSET_Y = 120
    
    # Colors (Modern Light Theme)
    BG_COLOR = "#ffffff"      # Pure white
    LINE_COLOR = "#000000"    # Sharp Black
    NODE_BORDER = "#000000"   # Sharp Black
    NODE_EMPTY = "#ffffff"    # Pure white
    NODE_RED = "#ef4444"      # Red
    NODE_BLUE = "#3b82f6"     # Blue
    TEXT_COLOR = "#000000"    # Sharp Black
    HIGHLIGHT_COLOR = "#fbbf24" # Amber
    WIN_COLOR = "#10b981"     # Emerald
    
    img = Image.new("RGB", (WIDTH, HEIGHT), BG_COLOR)
    draw = ImageDraw.Draw(img)
    
    def to_screen(x, y):
        return (x * SCALE_FACTOR + OFFSET_X, y * SCALE_FACTOR + OFFSET_Y)

    # --- Draw Edges ---
    edges = get_adjacencies()
    for u, v in edges:
        p1 = to_screen(*COORDS[u])
        p2 = to_screen(*COORDS[v])
        
        # Determine color based on node states
        s1 = board_state[u-1]
        s2 = board_state[v-1]
        
        color = LINE_COLOR # Default Black
        width = 3
        
        if s1 == 'R' and s2 == 'R':
            color = NODE_RED
        elif s1 == 'B' and s2 == 'B':
            color = NODE_BLUE
            
        # Draw win path highlight if provided
        if win_path and ((u, v) in win_path or (v, u) in win_path):
            width = 12
            color = WIN_COLOR
            
        draw.line([p1, p2], fill=color, width=width)

    # --- Load Font ---
    try:
        # Use bold font for better legibility
        font_path = "/System/Library/Fonts/Supplemental/Arial Bold.ttf"
        if not os.path.exists(font_path):
            font_path = "/System/Library/Fonts/Supplemental/Arial.ttf"
        font = ImageFont.truetype(font_path, 32) # Larger font for 2000px scale
    except:
        font = ImageFont.load_default()

    # --- Draw Nodes ---
    radius = 38 # Larger nodes for 2000px scale
    for nid in range(1, 94):
        x, y = to_screen(*COORDS[nid])
        state = board_state[nid-1]
        
        color = NODE_EMPTY
        if state == 'R': color = NODE_RED
        elif state == 'B': color = NODE_BLUE
        
        # Border
        draw.ellipse([x - radius, y - radius, x + radius, y + radius], 
                     fill=color, outline=NODE_BORDER, width=3)
        
        # Highlight last move
        if nid == last_move:
            draw.ellipse([x - radius - 8, y - radius - 8, x + radius + 8, y + radius + 8], 
                         outline=HIGHLIGHT_COLOR, width=8)
            
        # Number (Bold and Centered)
        txt_color = TEXT_COLOR if state == 'E' else "#ffffff"
        draw.text((x, y), str(nid), fill=txt_color, font=font, anchor="mm")

    return img

def export_graph_json():
    """
    Exports the manual coordinates and adjacency list to board_graph.json.
    """
    import json
    nodes = []
    for nid, (x, y) in COORDS.items():
        nodes.append({"id": nid, "x": x, "y": y})
    
    edges = get_adjacencies()
    
    with open("board_graph.json", "w") as f:
        json.dump({"nodes": nodes, "edges": edges}, f, indent=2)
    print("board_graph.json exported successfully.")

if __name__ == "__main__":
    # Generate board_base.png
    board_img = render_board()
    board_img.save("board_base.png")
    print("board_base.png generated successfully.")
    
    # Export graph to JSON for game logic
    export_graph_json()
