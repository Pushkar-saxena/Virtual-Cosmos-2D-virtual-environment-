import pygame, asyncio, websockets, json, threading, uuid
from queue import Queue

# Configuration
WIDTH, HEIGHT = 1250, 750
GAME_W = 900
SIDEBAR_W = 350
FPS = 60

# Colors
C_FLOOR = (210, 180, 140)
C_WALL = (100, 70, 40)
C_SIDEBAR = (255, 255, 255)
C_DARK = (23, 22, 34)
C_CHAIR = (150, 75, 0)
C_TABLE = (120, 60, 30)

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Virtual Cosmos - Multiplayer")
font = pygame.font.SysFont("Arial", 16)
bold_font = pygame.font.SysFont("Arial", 19, bold=True)

# Queues for Thread Communication
send_q = Queue()
recv_q = Queue()
my_id = str(uuid.uuid4())
players = {}
chat_log = []
input_text = ""
near_user = None

# --- MAP DESIGN WITH DOORWAYS ---
GAP = 100
mid_x = GAME_W // 2
mid_y = (HEIGHT - 110) // 2 + 50

walls = [
    pygame.Rect(0, 50, GAME_W, 10), # Top
    pygame.Rect(0, HEIGHT-60, GAME_W, 10), # Bottom
    pygame.Rect(mid_x, 50, 10, mid_y - 50 - GAP//2), # Vertical Top
    pygame.Rect(mid_x, mid_y + GAP//2, 10, (HEIGHT-60) - (mid_y + GAP//2)), # Vertical Bottom
    pygame.Rect(0, mid_y, mid_x - GAP//2, 10), # Horizontal Left
    pygame.Rect(mid_x + GAP//2, mid_y, GAME_W - (mid_x + GAP//2), 10) # Horizontal Right
]

furniture = [
    {"type": "table", "rect": pygame.Rect(100, 150, 150, 80)},
    {"type": "chair", "rect": pygame.Rect(160, 120, 30, 30)},
    {"type": "chair", "rect": pygame.Rect(160, 235, 30, 30)},
    {"type": "chair", "rect": pygame.Rect(600, 150, 40, 40)},
    {"type": "chair", "rect": pygame.Rect(700, 150, 40, 40)},
    {"type": "table", "rect": pygame.Rect(550, 500, 80, 50)},
    {"type": "table", "rect": pygame.Rect(750, 500, 80, 50)},
]

def draw_avatar(surf, x, y, name, color=(50, 120, 200)):
    pygame.draw.rect(surf, color, (x-15, y, 30, 25), border_radius=5) # Body
    pygame.draw.circle(surf, (255, 220, 180), (x, y-10), 15) # Head
    pygame.draw.circle(surf, (0, 0, 0), (x-5, y-12), 2) # Eye
    pygame.draw.circle(surf, (0, 0, 0), (x+5, y-12), 2) # Eye
    txt = font.render(name, True, (0,0,0))
    surf.blit(txt, (x - txt.get_width()//2, y - 45))

async def network():
    try:
        async with websockets.connect(f"ws://localhost:8000/ws/{my_id}") as ws:
            async def send_task():
                while True:
                    if not send_q.empty(): await ws.send(json.dumps(send_q.get()))
                    await asyncio.sleep(0.01)
            async def recv_task():
                while True:
                    data = await ws.recv()
                    recv_q.put(json.loads(data))
            await asyncio.gather(send_task(), recv_task())
    except: print("Server not found. Run server.py first!")

threading.Thread(target=lambda: asyncio.run(network()), daemon=True).start()

# --- MAIN LOOP ---
px, py = 100, 100
clock = pygame.time.Clock()
running = True

while running:
    # 1. Events
    for event in pygame.event.get():
        if event.type == pygame.QUIT: running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN and near_user:
                if input_text:
                    send_q.put({"type": "chat", "msg": input_text})
                    input_text = ""
            elif event.key == pygame.K_BACKSPACE: input_text = input_text[:-1]
            else: 
                if event.unicode.isprintable():
                    input_text += event.unicode

    # 2. Movement & Collision
    keys = pygame.key.get_pressed()
    dx, dy = 0, 0
    if keys[pygame.K_LEFT]: dx = -4
    if keys[pygame.K_RIGHT]: dx = 4
    if keys[pygame.K_UP]: dy = -4
    if keys[pygame.K_DOWN]: dy = 4

    # Create a small hitbox at the player's feet for smoother movement
    # This prevents the head/name tag from triggering wall collisions
    new_rect_x = pygame.Rect(px + dx - 10, py + 5, 20, 15)
    new_rect_y = pygame.Rect(px - 10, py + dy + 5, 20, 15)

    # Check X movement collision
    if new_rect_x.collidelist(walls) == -1:
        px += dx
    
    # Check Y movement collision
    if new_rect_y.collidelist(walls) == -1:
        py += dy

    # Stay within game boundaries (Adjusted to avoid spawning inside walls)
    px = max(30, min(px, GAME_W - 30))
    py = max(100, min(py, HEIGHT - 100)) # Changed from 70/80 to 100 to clear walls

    send_q.put({"type": "move", "x": px, "y": py})

    # 3. Room Detection
    current_room = "Hallway"
    if px < mid_x and py < mid_y: current_room = "Meeting Room A"
    elif px > mid_x and py < mid_y: current_room = "Lounge Area"
    elif px < mid_x and py > mid_y: current_room = "Breakout Room"
    elif px > mid_x and py > mid_y: current_room = "Office Space"

    # 4. Process Network
    while not recv_q.empty():
        data = recv_q.get()
        if data["type"] == "sync": players = data["users"]
        if data["type"] == "chat": chat_log.append(f"{data['user']}: {data['msg']}")

    # 5. Proximity Check
    near_user = None
    for id, p in players.items():
        if id != my_id:
            dist = ((px - p['x'])**2 + (py - p['y'])**2)**0.5
            if dist < 120: near_user = p['name']

    # 6. Rendering
    screen.fill((240, 240, 240))
    pygame.draw.rect(screen, C_FLOOR, (0, 50, GAME_W, HEIGHT-110))
    
    for w in walls: pygame.draw.rect(screen, C_WALL, w)
    for f in furniture:
        color = C_TABLE if f["type"] == "table" else C_CHAIR
        pygame.draw.rect(screen, color, f["rect"], border_radius=3)

    # Labels
    screen.blit(bold_font.render("Meeting Room A", True, (80,80,80)), (50, 70))
    screen.blit(bold_font.render("Lounge Area", True, (80,80,80)), (500, 70))
    screen.blit(bold_font.render("Breakout Room", True, (80,80,80)), (50, 370))
    screen.blit(bold_font.render("Office Space", True, (80,80,80)), (500, 370))
    screen.blit(bold_font.render(f"Location: {current_room}", True, (200, 50, 50)), (20, HEIGHT - 90))

    # Players
    for id, p in players.items():
        color = (50, 120, 200) if id == my_id else (200, 80, 80)
        draw_avatar(screen, p['x'], p['y'], p['name'], color)

    # UI Overlay
    pygame.draw.rect(screen, C_DARK, (0, 0, WIDTH, 50))
    screen.blit(bold_font.render("🌌 Virtual Cosmos", True, (255,255,255)), (20, 12))
    
    # Sidebar Chat
    pygame.draw.rect(screen, C_SIDEBAR, (GAME_W, 50, SIDEBAR_W, HEIGHT-110))
    screen.blit(bold_font.render("Chat History", True, (0,0,0)), (GAME_W + 20, 70))
    
    if near_user:
        for i, msg in enumerate(chat_log[-12:]):
            screen.blit(font.render(msg, True, (40,40,40)), (GAME_W + 20, 110 + i*25))
        pygame.draw.rect(screen, (230,230,230), (GAME_W+15, HEIGHT-120, 320, 40), border_radius=5)
        screen.blit(font.render(input_text + "|", True, (0,0,0)), (GAME_W+25, HEIGHT-110))
    else:
        screen.blit(font.render("Walk near a user to chat", True, (150,150,150)), (GAME_W + 20, 110))

    # Bottom Bar
    pygame.draw.rect(screen, C_DARK, (0, HEIGHT-60, WIDTH, 60))
    btns = ["Share", "Invite", "Record", "Move", "React"]
    for i, b in enumerate(btns):
        screen.blit(font.render(b, True, (180,180,180)), (40 + i*120, HEIGHT-35))

    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()