import pygame
import sys

pygame.init()
WIDTH, HEIGHT = 704, 704
BOARD_SIZE = 8
SQUARE_SIZE = WIDTH // BOARD_SIZE
FPS = 60

THEMES = [
    {'light': (210, 180, 140), 'dark': (139, 69, 19)},
    {'light': (240, 240, 240), 'dark': (50, 50, 50)},
    {'light': (255, 223, 186), 'dark': (128, 0, 0)},
    {'light': (224, 255, 255), 'dark': (0, 51, 102)}
]
current_theme_index = 0

def get_theme_colors(index):
    theme = THEMES[index]
    return theme['light'], theme['dark']

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
HIGHLIGHT = (0, 255, 0, 100)
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Chess Game")
clock = pygame.time.Clock()

def load_piece_images():
    pieces = {}
    piece_types = ['pawn', 'rook', 'knight', 'bishop', 'queen', 'king']
    colors = ['white', 'black']
    for color in colors:
        for piece in piece_types:
            image = pygame.image.load(f"chess_pieces/{color}_{piece}.png").convert_alpha()
            pieces[f"{color}_{piece}"] = pygame.transform.smoothscale(image, (SQUARE_SIZE, SQUARE_SIZE))
    return pieces

class Piece:
    def __init__(self, color, piece_type, row, col):
        self.color = color
        self.type = piece_type
        self.row = row
        self.col = col
        self.has_moved = False

    def valid_moves(self, board, game_state=None):
        moves = []
        directions = []
        if self.type == 'pawn':
            direction = -1 if self.color == 'white' else 1
            start_row = 6 if self.color == 'white' else 1
            # Forward move
            if 0 <= self.row + direction < 8 and not board[self.row + direction][self.col]:
                moves.append((self.row + direction, self.col))
                if self.row == start_row and not board[self.row + 2*direction][self.col]:
                    moves.append((self.row + 2*direction, self.col))
            # Captures
            for dc in [-1, 1]:
                c = self.col + dc
                r = self.row + direction
                if 0 <= c < 8 and 0 <= r < 8:
                    target = board[r][c]
                    if target and target.color != self.color:
                        moves.append((r, c))
                    # En passant
                    if game_state and game_state.en_passant_target == (r, c):
                        moves.append((r, c))
        elif self.type == 'rook':
            directions = [(0, 1), (1, 0), (0, -1), (-1, 0)]
        elif self.type == 'knight':
            knight_moves = [
                (2, 1), (1, 2), (-1, 2), (-2, 1),
                (-2, -1), (-1, -2), (1, -2), (2, -1)
            ]
            for dr, dc in knight_moves:
                r, c = self.row + dr, self.col + dc
                if 0 <= r < 8 and 0 <= c < 8:
                    target = board[r][c]
                    if not target or target.color != self.color:
                        moves.append((r, c))
        elif self.type == 'bishop':
            directions = [(1, 1), (1, -1), (-1, -1), (-1, 1)]
        elif self.type == 'queen':
            directions = [
                (0, 1), (1, 0), (0, -1), (-1, 0),
                (1, 1), (1, -1), (-1, -1), (-1, 1)
            ]
        elif self.type == 'king':
            king_moves = [
                (0, 1), (1, 0), (0, -1), (-1, 0),
                (1, 1), (1, -1), (-1, -1), (-1, 1)
            ]
            for dr, dc in king_moves:
                r, c = self.row + dr, self.col + dc
                if 0 <= r < 8 and 0 <= c < 8:
                    target = board[r][c]
                    if not target or target.color != self.color:
                        moves.append((r, c))
        if directions:
            for dr, dc in directions:
                r, c = self.row + dr, self.col + dc
                while 0 <= r < 8 and 0 <= c < 8:
                    target = board[r][c]
                    if not target:
                        moves.append((r, c))
                    else:
                        if target.color != self.color:
                            moves.append((r, c))
                        break
                    r += dr
                    c += dc
        return moves

def initialize_board():
    board = [[None for _ in range(8)] for _ in range(8)]
    for col in range(8):
        board[1][col] = Piece('black', 'pawn', 1, col)
        board[6][col] = Piece('white', 'pawn', 6, col)
    back_row = ['rook', 'knight', 'bishop', 'queen', 'king', 'bishop', 'knight', 'rook']
    for col, piece_type in enumerate(back_row):
        board[0][col] = Piece('black', piece_type, 0, col)
        board[7][col] = Piece('white', piece_type, 7, col)
    return board

def draw_board(theme_index):
    light_color, dark_color = get_theme_colors(theme_index)
    for row in range(BOARD_SIZE):
        for col in range(BOARD_SIZE):
            color = light_color if (row + col) % 2 == 0 else dark_color
            pygame.draw.rect(screen, color, (col * SQUARE_SIZE, row * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE))

def draw_pieces(board, piece_images):
    for row in range(BOARD_SIZE):
        for col in range(BOARD_SIZE):
            piece = board[row][col]
            if piece:
                screen.blit(piece_images[f"{piece.color}_{piece.type}"], 
                           (col * SQUARE_SIZE, row * SQUARE_SIZE))

def highlight_moves(moves):
    for row, col in moves:
        highlight = pygame.Surface((SQUARE_SIZE, SQUARE_SIZE), pygame.SRCALPHA)
        highlight.fill((0, 255, 0, 100))
        screen.blit(highlight, (col * SQUARE_SIZE, row * SQUARE_SIZE))

def find_king(board, color):
    for row in range(8):
        for col in range(8):
            piece = board[row][col]
            if piece and piece.type == 'king' and piece.color == color:
                return piece
    return None

def is_in_check(board, color):
    king = find_king(board, color)
    if not king:
        return False
    king_pos = (king.row, king.col)
    for row in range(8):
        for col in range(8):
            piece = board[row][col]
            if piece and piece.color != color:
                if king_pos in piece.valid_moves(board):
                    return True
    return False

def has_legal_moves(board, color):
    for row in range(8):
        for col in range(8):
            piece = board[row][col]
            if piece and piece.color == color:
                for move in piece.valid_moves(board):
                    src_row, src_col = piece.row, piece.col
                    dst_row, dst_col = move
                    captured = board[dst_row][dst_col]
                    board[src_row][src_col] = None
                    board[dst_row][dst_col] = piece
                    piece.row, piece.col = dst_row, dst_col
                    in_check = is_in_check(board, color)
                    board[src_row][src_col] = piece
                    board[dst_row][dst_col] = captured
                    piece.row, piece.col = src_row, src_col
                    if not in_check:
                        return True
    return False

def is_checkmate(board, color):
    king = find_king(board, color)
    if not king:
        return False
    king_moves = king.valid_moves(board)
    for move in king_moves:
        src_row, src_col = king.row, king.col
        dst_row, dst_col = move
        captured = board[dst_row][dst_col]
        board[src_row][src_col] = None
        board[dst_row][dst_col] = king
        king.row, king.col = dst_row, dst_col
        in_check = is_in_check(board, color)
        board[src_row][src_col] = king
        board[dst_row][dst_col] = captured
        king.row, king.col = src_row, src_col
        if not in_check:
            return False
    return is_in_check(board, color)

class GameState:
    def __init__(self):
        self.en_passant_target = None
    def reset_en_passant(self):
        self.en_passant_target = None
    def set_en_passant(self, row, col):
        self.en_passant_target = (row, col)

def can_castle_kingside(board, color):
    row = 7 if color == 'white' else 0
    king = board[row][4]
    rook = board[row][7]
    if not king or not rook:
        return False
    if king.has_moved or rook.has_moved:
        return False
    if board[row][5] or board[row][6]:
        return False
    if is_in_check(board, color):
        return False
    for col in [5, 6]:
        board[row][4] = None
        board[row][col] = king
        king.row, king.col = row, col
        if is_in_check(board, color):
            board[row][col] = None
            board[row][4] = king
            king.row, king.col = row, 4
            return False
        board[row][col] = None
        board[row][4] = king
        king.row, king.col = row, 4
    return True

def can_castle_queenside(board, color):
    row = 7 if color == 'white' else 0
    king = board[row][4]
    rook = board[row][0]
    if not king or not rook:
        return False
    if king.has_moved or rook.has_moved:
        return False
    if board[row][1] or board[row][2] or board[row][3]:
        return False
    if is_in_check(board, color):
        return False
    for col in [3, 2]:
        board[row][4] = None
        board[row][col] = king
        king.row, king.col = row, col
        if is_in_check(board, color):
            board[row][col] = None
            board[row][4] = king
            king.row, king.col = row, 4
            return False
        board[row][col] = None
        board[row][4] = king
        king.row, king.col = row, 4
    return True

def perform_castle(board, color, side):
    row = 7 if color == 'white' else 0
    if side == 'kingside':
        king = board[row][4]
        rook = board[row][7]
        board[row][4] = None
        board[row][7] = None
        board[row][6] = king
        board[row][5] = rook
        king.row, king.col = row, 6
        rook.row, rook.col = row, 5
    else:
        king = board[row][4]
        rook = board[row][0]
        board[row][4] = None
        board[row][0] = None
        board[row][2] = king
        board[row][3] = rook
        king.row, king.col = row, 2
        rook.row, rook.col = row, 3
    king.has_moved = True
    rook.has_moved = True

def promote_pawn_ui(screen, color):
    font = pygame.font.SysFont(None, 48)
    choices = ['queen', 'rook', 'bishop', 'knight']
    rects = []
    for i, piece in enumerate(choices):
        text = font.render(piece.capitalize(), True, (0,0,0))
        rect = pygame.Rect(100 + i*170, HEIGHT//2 - 40, 160, 80)
        pygame.draw.rect(screen, (200,200,200), rect)
        text_rect = text.get_rect(center=rect.center)
        screen.blit(text, text_rect)
        rects.append((rect, piece))
    pygame.display.flip()
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                mx, my = event.pos
                for rect, piece in rects:
                    if rect.collidepoint(mx, my):
                        return piece

def promote_pawn(board, pawn, screen):
    promotion_row = 0 if pawn.color == 'white' else 7
    if pawn.row == promotion_row:
        choice = promote_pawn_ui(screen, pawn.color)
        pawn.type = choice
        pawn.has_moved = True

def main():
    global current_theme_index
    piece_images = load_piece_images()
    board = initialize_board()
    selected_piece = None
    valid_moves = []
    current_player = 'white'
    game_over = False
    winner = None
    game_state = GameState()
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_h:
                    font = pygame.font.SysFont(None, 70)
                    text = font.render(f"HELP MENU", True, (255,255,0))
                    rect = text.get_rect(center=(WIDTH//2 , HEIGHT//2 - 110))
                    screen.blit(text, rect)
                    pygame.display.flip()
                    font = pygame.font.SysFont(None, 50)
                    text = font.render(f"Press R to reset the board", True, (255,255,0))
                    rect = text.get_rect(center=(WIDTH//2 , HEIGHT//2 - 50))
                    screen.blit(text, rect)
                    pygame.display.flip()
                    font = pygame.font.SysFont(None, 50)
                    text = font.render(f"Press T to change the theme", True, (255,255,0))
                    rect = text.get_rect(center=(WIDTH//2 , HEIGHT//2 ))
                    screen.blit(text, rect)
                    pygame.display.flip()
                    font = pygame.font.SysFont(None, 50)
                    text = font.render(f"Press Q to quit the game", True, (255,255,0))
                    rect = text.get_rect(center=(WIDTH//2 , HEIGHT//2 + 50))
                    screen.blit(text, rect)
                    pygame.display.flip()
                    pygame.time.wait(2000)
                elif event.key == pygame.K_q:
                    pygame.quit()
                    sys.exit()
                elif event.key == pygame.K_r:
                    board = initialize_board()
                    selected_piece = None
                    valid_moves = []
                    current_player = 'white'
                    game_over = False
                    winner = None
                    game_state = GameState()
                elif event.key == pygame.K_t:
                    current_theme_index = (current_theme_index + 1) % len(THEMES)
            elif not game_over and event.type == pygame.MOUSEBUTTONDOWN:
                col = event.pos[0] // SQUARE_SIZE
                row = event.pos[1] // SQUARE_SIZE
                if not selected_piece:
                    piece = board[row][col]
                    if piece and piece.color == current_player:
                        selected_piece = piece
                        valid_moves = []
                        for move in piece.valid_moves(board, game_state):
                            src_row, src_col = piece.row, piece.col
                            dst_row, dst_col = move
                            captured = board[dst_row][dst_col]
                            board[src_row][src_col] = None
                            board[dst_row][dst_col] = piece
                            piece.row, piece.col = dst_row, dst_col
                            in_check = is_in_check(board, current_player)
                            board[src_row][src_col] = piece
                            board[dst_row][dst_col] = captured
                            piece.row, piece.col = src_row, src_col
                            if not in_check:
                                valid_moves.append(move)
                        if piece.type == 'king':
                            if can_castle_kingside(board, current_player):
                                valid_moves.append((row, 6))
                            if can_castle_queenside(board, current_player):
                                valid_moves.append((row, 2))
                elif selected_piece:
                    if (row, col) in valid_moves:
                        if selected_piece.type == 'king' and abs(col - selected_piece.col) == 2:
                            side = 'kingside' if col == 6 else 'queenside'
                            perform_castle(board, current_player, side)
                        else:
                            # En passant capture
                            if selected_piece.type == 'pawn' and (row, col) == game_state.en_passant_target:
                                capture_row = selected_piece.row
                                capture_col = col
                                board[capture_row][capture_col] = None
                            prev_row = selected_piece.row
                            board[selected_piece.row][selected_piece.col] = None
                            selected_piece.row, selected_piece.col = row, col
                            selected_piece.has_moved = True
                            board[row][col] = selected_piece
                            # En passant set
                            if selected_piece.type == 'pawn' and abs(row - prev_row) == 2:
                                ep_row = (row + prev_row) // 2
                                game_state.set_en_passant(ep_row, col)
                            else:
                                game_state.reset_en_passant()
                            promotion_row = 0 if selected_piece.color == 'white' else 7
                            if selected_piece.type == 'pawn' and row == promotion_row:
                                promote_pawn(board, selected_piece, screen)
                        current_player = 'black' if current_player == 'white' else 'white'
                        selected_piece = None
                        valid_moves = []
                        if is_checkmate(board, current_player):
                            game_over = True
                            winner = 'White' if current_player == 'black' else 'Black'
                    else:
                        selected_piece = None
                        valid_moves = []
        draw_board(current_theme_index)
        if selected_piece:
            highlight_moves(valid_moves)
        draw_pieces(board, piece_images)
        
        if game_over:
            font = pygame.font.SysFont(None, 72)
            text = font.render(f"Checkmate! {winner} wins!", True, (255,255,0))
            rect = text.get_rect(center=(WIDTH//2, HEIGHT//2))
            screen.blit(text, rect)
            pygame.display.flip()
            font = pygame.font.SysFont(None, 50)
            text = font.render(f"Choose R to reset or Q to quit", True, (255,255,0))
            rect = text.get_rect(center=((WIDTH)//2, (HEIGHT)//2 + 50))
            screen.blit(text, rect)
            pygame.display.flip()
            pygame.time.wait(5000)
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_q:
                    pygame.quit()
                    sys.exit()
                elif event.key == pygame.K_r:
                    board = initialize_board()
                    selected_piece = None
                    valid_moves = []
                    current_player = 'white'
                    game_over = False
                    winner = None
                    game_state = GameState()
            else:
                board = initialize_board()
                selected_piece = None
                valid_moves = []
                current_player = 'white'
                game_over = False
                winner = None
                game_state = GameState()
        pygame.display.flip()
        clock.tick(FPS)
        
    pygame.quit()

if __name__ == "__main__":
    main()