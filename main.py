import pygame, random, time, os

pygame.init()

SCREEN_WIDTH = 700
SCREEN_HEIGHT = 700
TILE_SIZE = 175
ORANGE = '#BF360C'
BUTTON_COLOR = '#D84315'
BUTTON_HOVER_COLOR = '#AF3A18'
FLIP_DELAY = 0.5
BUTTON_WIDTH = 140
BUTTON_HEIGHT = 40
WHITE = '#FFFFFF'
BLACK = '#000000'

EASY_TIMER_LIMIT = 20
MEDIUM_TIMER_LIMIT = 40
HARD_TIMER_LIMIT = 60

img_dir = 'img'
image_files = [f'{i}.png' for i in range(1, 17)]

match_sound = pygame.mixer.Sound('sounds/match.wav')

icon = pygame.image.load('img/logo-raw.png') 
pygame.display.set_icon(icon)

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Flash Memory Game")

tile_back = pygame.image.load(os.path.join(img_dir, 'back.png'))
all_tile_images = [pygame.image.load(os.path.join(img_dir, file)) for file in image_files]

logo = pygame.image.load(os.path.join(img_dir, 'logo.png'))
logo = pygame.transform.scale(logo, (300, 300))

font = pygame.font.Font(None, 36)

def play_match_sound():
    match_sound.play()

def draw_button(text, rect, color, hover_color):
    """Draws a button with hover effect."""
    if rect.collidepoint(pygame.mouse.get_pos()):
        pygame.draw.rect(screen, hover_color, rect)
    else:
        pygame.draw.rect(screen, color, rect)
    text_surface = font.render(text, True, WHITE)
    text_rect = text_surface.get_rect(center=rect.center)
    screen.blit(text_surface, text_rect)

def draw_menu(buttons, is_select_level_screen=False):
    """Draws the main menu or select level screen."""
    screen.fill(ORANGE)
    if is_select_level_screen:
        select_level_text = pygame.font.Font(None, 60).render("Select Level", True, WHITE)
        text_rect = select_level_text.get_rect(center=(SCREEN_WIDTH // 2, 150))
        screen.blit(select_level_text, text_rect)
    else:
        screen.blit(logo, (SCREEN_WIDTH // 2 - logo.get_width() // 2, 40))

    for button_text, button_rect, _ in buttons:
        draw_button(button_text, button_rect, BUTTON_COLOR, BUTTON_HOVER_COLOR)

def menu_loop(buttons):
    """Main menu loop."""
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                for button_text, button_rect, action in buttons:
                    if button_rect.collidepoint(pygame.mouse.get_pos()):
                        action()
        if buttons == level_buttons:
            draw_menu(buttons, is_select_level_screen=True)
        else:
            draw_menu(buttons)
        pygame.display.flip()

def draw_return_button():
    """Draws the return button."""
    return_button_rect = pygame.Rect(SCREEN_WIDTH - BUTTON_WIDTH - 15, 650, BUTTON_WIDTH, BUTTON_HEIGHT)
    draw_button("Back", return_button_rect, BUTTON_COLOR, BUTTON_HOVER_COLOR)

    if return_button_rect.collidepoint(pygame.mouse.get_pos()):
        if pygame.mouse.get_pressed()[0]:
            menu_loop(menu_buttons)

def draw_timer(remaining_time):
    """Draws the timer."""
    timer_text = font.render(f"Time: {remaining_time}s", True, BLACK)
    screen.blit(timer_text, (SCREEN_WIDTH - 150, 10))

def display_message(message):
    """Displays a message on the screen."""
    message_text = font.render(message, True, WHITE)
    text_rect = message_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
    screen.blit(message_text, text_rect)

def game_loop(num_tiles, timer_limit):
    """Main game loop."""
    global tile_state, flipped_tiles, matched_pairs, timer_start_time

    tile_state = [False] * num_tiles
    tile_images = random.sample(all_tile_images, num_tiles // 2) * 2
    random.shuffle(tile_images)
    flipped_tiles = []
    matched_pairs = 0
    timer_start_time = time.time()

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                handle_tile_click(event.pos, num_tiles, tile_images)

        screen.fill(ORANGE)
        draw_tiles(num_tiles, tile_images)
        draw_return_button()
        draw_timer(max(0, timer_limit - int(time.time() - timer_start_time)))

        if len(flipped_tiles) == 2:
            check_flipped_tiles(tile_images)

        if matched_pairs == num_tiles // 2:
            end_game("Congratulations! You found all the pairs!")
            menu_loop(menu_buttons)  
            return True

        if time.time() - timer_start_time >= timer_limit:
            end_game("Time's up! You lost the game.")
            menu_loop(menu_buttons)  
            return False

        pygame.display.flip()

def handle_tile_click(mouse_pos, num_tiles, tile_images):
    """Handles clicking on tiles for all levels."""
    return_button_rect = pygame.Rect(SCREEN_WIDTH - BUTTON_WIDTH - 20, 20, BUTTON_WIDTH, BUTTON_HEIGHT)
    if return_button_rect.collidepoint(mouse_pos):
        return
    else:
        if num_tiles == 8:  
            start_x = (SCREEN_WIDTH - 4 * TILE_SIZE) // 2
            start_y = (SCREEN_HEIGHT - 2 * TILE_SIZE) // 2

            col = (mouse_pos[0] - start_x) // TILE_SIZE
            row = (mouse_pos[1] - start_y) // TILE_SIZE
            index = row * 4 + col

            if index < 8 and not tile_state[index] and len(flipped_tiles) < 2:
                tile_state[index] = True
                flipped_tiles.append(index)
        else:
            start_x = (SCREEN_WIDTH - int(num_tiles ** 0.5) * TILE_SIZE) // 2
            start_y = (SCREEN_HEIGHT - int(num_tiles ** 0.5) * TILE_SIZE) // 2

            col = (mouse_pos[0] - start_x) // TILE_SIZE
            row = (mouse_pos[1] - start_y) // TILE_SIZE
            index = row * int(num_tiles ** 0.5) + col

            if index < num_tiles and not tile_state[index] and len(flipped_tiles) < 2:
                tile_state[index] = True
                flipped_tiles.append(index)

def reset_game(num_tiles, tile_images):
    """Resets the game."""
    global tile_state, flipped_tiles, matched_pairs, timer_start_time
    random.shuffle(tile_images)
    tile_state = [False] * num_tiles
    flipped_tiles = []
    matched_pairs = 0
    timer_start_time = time.time()

def draw_tiles(num_tiles, tile_images):
    """Draws the tiles on the screen for all levels."""
    if num_tiles == 8:  
        draw_tiles_medium(tile_images)
    else:
        tile_area_width = int(num_tiles ** 0.5) * TILE_SIZE
        tile_area_height = int(num_tiles ** 0.5) * TILE_SIZE
        start_x = (SCREEN_WIDTH - tile_area_width) // 2
        start_y = (SCREEN_HEIGHT - tile_area_height) // 2

        for i in range(int(num_tiles ** 0.5)):
            for j in range(int(num_tiles ** 0.5)):
                index = i * int(num_tiles ** 0.5) + j
                tile_x = start_x + j * TILE_SIZE
                tile_y = start_y + i * TILE_SIZE

                pygame.draw.rect(screen, ORANGE, (tile_x, tile_y, TILE_SIZE, TILE_SIZE))
                if tile_state[index] or index in flipped_tiles:
                    tile = tile_images[index]
                else:
                    tile = tile_back
                tile = pygame.transform.scale(tile, (TILE_SIZE - 8, TILE_SIZE - 8))
                screen.blit(tile, (tile_x + 4, tile_y + 4))

def draw_tiles_medium(tile_images):
    """Draws the tiles on the screen with 4 columns and 2 rows for the Medium level."""
    tile_area_width = 4 * TILE_SIZE
    tile_area_height = 2 * TILE_SIZE
    start_x = (SCREEN_WIDTH - tile_area_width) // 2
    start_y = (SCREEN_HEIGHT - tile_area_height) // 2

    for i in range(2):
        for j in range(4):
            index = i * 4 + j
            tile_x = start_x + j * TILE_SIZE
            tile_y = start_y + i * TILE_SIZE

            pygame.draw.rect(screen, ORANGE, (tile_x, tile_y, TILE_SIZE, TILE_SIZE))
            if tile_state[index] or index in flipped_tiles:
                tile = tile_images[index]
            else:
                tile = tile_back
            tile = pygame.transform.scale(tile, (TILE_SIZE - 8, TILE_SIZE - 8))
            screen.blit(tile, (tile_x + 4, tile_y + 4))

def check_flipped_tiles(tile_images):
    """Checks the flipped tiles for a match."""
    global flipped_tiles, matched_pairs
    if tile_images[flipped_tiles[0]] == tile_images[flipped_tiles[1]]:
        matched_pairs += 1
        flipped_tiles = []
        play_match_sound()
    else:
        time.sleep(FLIP_DELAY)
        tile_state[flipped_tiles[0]] = False
        tile_state[flipped_tiles[1]] = False
        flipped_tiles = []

def end_game(message):
    """Ends the game with a message."""
    display_message(message)
    pygame.display.flip()
    time.sleep(2)

def start_game(num_tiles, timer_limit):
    """Starts the game with specified number of tiles and timer limit."""
    game_loop(num_tiles, timer_limit)

def quit_game():
    """Quits the game."""
    pygame.quit()
    quit()

level_buttons = [
    ("Easy", pygame.Rect(SCREEN_WIDTH // 2 - BUTTON_WIDTH // 2, 240, BUTTON_WIDTH, BUTTON_HEIGHT), lambda: start_game(4, EASY_TIMER_LIMIT)),
    ("Medium", pygame.Rect(SCREEN_WIDTH // 2 - BUTTON_WIDTH // 2, 320, BUTTON_WIDTH, BUTTON_HEIGHT), lambda: start_game(8, MEDIUM_TIMER_LIMIT)),
    ("Hard", pygame.Rect(SCREEN_WIDTH // 2 - BUTTON_WIDTH // 2, 400, BUTTON_WIDTH, BUTTON_HEIGHT), lambda: start_game(16, HARD_TIMER_LIMIT)),
    ("Back", pygame.Rect(SCREEN_WIDTH // 2 - BUTTON_WIDTH // 2, 480, BUTTON_WIDTH, BUTTON_HEIGHT), lambda: menu_loop(menu_buttons))
]

menu_buttons = [
    ("Start", pygame.Rect(SCREEN_WIDTH // 2 - BUTTON_WIDTH // 2, 340, BUTTON_WIDTH, BUTTON_HEIGHT), lambda: menu_loop(level_buttons)),
    ("Quit", pygame.Rect(SCREEN_WIDTH // 2 - BUTTON_WIDTH // 2, 420, BUTTON_WIDTH, BUTTON_HEIGHT), quit_game)
]

menu_loop(menu_buttons)