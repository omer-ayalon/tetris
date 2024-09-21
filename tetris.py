import copy
import random
from os import environ
import sys

environ['PYGAME_HIDE_SUPPORT_PROMPT'] = '1'
import pygame

pygame.init()

# set the pygame window name
pygame.display.set_caption('Tetris - Omer Ayalon')

fps = 60
fpsClock = pygame.time.Clock()

board_height = 20
board_width = 10
block_size = 30
board_x_offset = (600 - board_width * block_size) // 2
board_y_offset = 50

count = 0
max_count_slow = 60
max_count = max_count_slow
max_count_fast = 5

lines_cleared_score = 0
score_font = pygame.font.SysFont('Verdana', 20)

game_over = False

colors = [
    (0, 0, 0),
    (255, 0, 0),
    (0, 150, 0),
    (0, 0, 255),
    (255, 120, 0),
    (255, 255, 0),
    (180, 0, 255),
    (0, 220, 220)
]

# Define the shapes of the single parts
tetris_shapes = [[[-1, 0], [-2, 0], [0, 0], [1, 0]],
                 [[0, -1], [-1, -1], [-1, 0], [0, 0]],
                 [[-1, 0], [-1, 1], [0, 0], [0, -1]],
                 [[0, 0], [-1, 0], [0, 1], [-1, -1]],
                 [[0, 0], [0, -1], [0, 1], [-1, -1]],
                 [[0, 0], [0, -1], [0, 1], [1, -1]],
                 [[0, 0], [0, -1], [0, 1], [-1, 0]]]


class Cube:
    def __init__(self, idx):
        self.idx = idx
        self.color = (255, 255, 255)
        self.occupied = False

    def draw(self):
        pygame.draw.rect(screen.screen, self.color,
                         [self.idx[1] * block_size + board_x_offset, self.idx[0] * block_size + board_y_offset,
                          block_size - 1,
                          block_size - 1])


board = [[Cube([j, i]) for i in range(board_width)] for j in range(board_height)]


class Tetris:
    def __init__(self):
        self.random_tetrominoes = []
        self.shape, self.shape_pos, self.shape_color = self.new_shape()
        self.next_shape, self.next_shape_pos, self.next_shape_color = self.new_shape()

    def new_shape(self):
        if len(self.random_tetrominoes) == 0:
            self.random_bag()

        shape = self.random_tetrominoes.pop(0)
        y_offset = abs(min([pos[0] for pos in shape]))
        shape_pos = [y_offset, 5]
        shape_color = colors[random.randrange(len(colors))]
        return shape, shape_pos, shape_color

    def random_bag(self):
        self.random_tetrominoes = copy.deepcopy(tetris_shapes)
        random.shuffle(self.random_tetrominoes)

    # @staticmethod
    # def new_shape():
    #     shape = tetris_shapes[random.randrange(len(tetris_shapes))]
    #     y_offset = abs(min([pos[0] for pos in shape]))
    #     shape_pos = [y_offset, 5]
    #     shape_color = colors[random.randrange(len(colors))]
    #     return shape, shape_pos, shape_color

    def shape_down(self):
        self.shape_pos[0] += 1

    def rotate(self):
        for i in range(4):
            x = self.shape[i][0]
            y = self.shape[i][1]
            self.shape[i][1] = -x
            self.shape[i][0] = y

    def check_staif(self, offset):
        for k in range(4):
            if self.shape[k][1] + self.shape_pos[1] + offset[1] >= board_width:  # Check For Right Screen
                return True
            elif self.shape[k][1] + self.shape_pos[1] + offset[1] < 0:  # Check For Left Screen
                return True
            elif board[self.shape[k][0] + self.shape_pos[0] +
                       offset[0]][self.shape[k][1] + self.shape_pos[1] + offset[1]].occupied:  # Check For Below
                return True
        return False

    def check_col(self, offset):
        for k in range(4):
            if self.shape[k][0] + self.shape_pos[0] == board_height - 1:  # Check For Bottom Screen
                return True
            if 0 <= self.shape[k][0] + self.shape_pos[0] + offset[0] < board_height and 0 <= self.shape[k][1] + \
                    self.shape_pos[
                        1] + offset[1] < board_width:
                if board[self.shape[k][0] + self.shape_pos[0] +
                         offset[0]][self.shape[k][1] + self.shape_pos[1] + offset[1]].occupied:  # Check For Below
                    return True
            else:
                return True
        return False

    @staticmethod
    def check_row_complete():
        for i in range(board_height):
            if all([pos.occupied for pos in board[i]]):
                return True, i
        return False, None

    @staticmethod
    def eliminate_row(i):
        for k in range(i, 0, -1):
            for j in range(board_width):
                board[k][j].color = board[k - 1][j].color
                board[k][j].occupied = board[k - 1][j].occupied

    def shape_done(self):
        self.shape, self.shape_pos, self.shape_color = copy.deepcopy(self.next_shape), copy.deepcopy(
            self.next_shape_pos), copy.deepcopy(self.next_shape_color)
        self.next_shape, self.next_shape_pos, self.next_shape_color = self.new_shape()


class Screen:
    def __init__(self, width=640, height=480):
        self.width = width
        self.height = height
        self.screen = pygame.display.set_mode((width, height))

    def draw_next_shape(self):
        score_render = score_font.render(f'Next Shape:', True, (0, 0, 0))
        self.screen.blit(score_render, score_render.get_rect(center=[self.screen.get_width() // 8, 100]))

        pygame.draw.rect(self.screen, (200, 200, 200),
                         [-1.3 * block_size + 50, -2.1 * block_size + 175, block_size * 4, block_size * 4.5])
        pygame.draw.rect(self.screen, (0, 0, 0),
                         [-1.3 * block_size + 50, -2.1 * block_size + 175, block_size * 4, block_size * 4.5], 4)
        for i in range(4):
            pygame.draw.rect(self.screen, game.next_shape_color,
                             [game.next_shape[i][1] * block_size + 50, game.next_shape[i][0] * block_size + 180,
                              block_size - 1,
                              block_size - 1])

    def draw(self):
        screen.screen.fill((100, 100, 100))

        max_value = 0
        for i in range(0, board_height - game.shape_pos[0]):
            if not any((pos[0] + game.shape_pos[0] + i) >= board_height for pos in game.shape):
                if not game.check_col(offset=[i, 0]):
                    max_value = game.shape_pos[0] + i
                else:
                    break

        self.draw_next_shape()

        score_render = score_font.render(f'Score: {str(lines_cleared_score)}', True, (0, 0, 0))
        self.screen.blit(score_render, score_render.get_rect(center=[self.screen.get_width() // 2, 25]))

        # Draw Board
        for i in range(board_height):
            for j in range(board_width):
                board[i][j].draw()

        # Draw Shape
        for k in range(4):
            pygame.draw.rect(self.screen, game.shape_color,
                             [(game.shape[k][1] + game.shape_pos[1]) * block_size + board_x_offset,
                              (game.shape[k][0] + game.shape_pos[0]) * block_size + board_y_offset,
                              block_size - 1, block_size - 1])

        # Draw Shadow Where Block Suppose To Land
        if max([pos[0] for pos in game.shape]) + game.shape_pos[0] < board_height - 1:
            for k in range(4):
                pygame.draw.rect(self.screen, game.shape_color,
                                 [(game.shape[k][1] + game.shape_pos[1]) * block_size + board_x_offset,
                                  (game.shape[k][0] + max_value) * block_size + board_y_offset,
                                  block_size - 1, block_size - 1], 3)

        if game_over:
            score_render = score_font.render(f'Game Over', True, (255, 0, 0), (0, 0, 0))
            self.screen.blit(score_render, score_render.get_rect(center=self.screen.get_rect().center))

        pygame.display.flip()
        fpsClock.tick(fps)


screen = Screen(width=600, height=block_size * board_height + board_y_offset + 10)
game = Tetris()

while True:
    # Keyboard Handler
    for event in pygame.event.get():
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                pygame.quit()
                sys.exit()
            if not game_over:
                if event.key == pygame.K_LEFT:
                    if not game.check_staif(offset=[0, -1]):
                        game.shape_pos[1] -= 1
                if event.key == pygame.K_RIGHT:
                    if not game.check_staif(offset=[0, 1]):
                        game.shape_pos[1] += 1
                if event.key == pygame.K_r:
                    game.rotate()
                    rem = False
                    if game.check_col(offset=[0, 0]):
                        for i in [-1, 1, -2, 2]:
                            if not game.check_col(offset=[0, i]):
                                game.shape_pos[1] += i
                                rem = True
                                break
                        if not rem:
                            for _ in range(3):
                                game.rotate()

                if event.key == pygame.K_DOWN:
                    max_count = max_count_fast
                if event.key == pygame.K_UP:
                    max_count = max_count_slow

    if not game_over:
        # Counter Handling
        count += 1
        if count >= max_count:
            count = 0

            # If Collision Occurred, Pass Info To Board And Draw New Shape
            if game.check_col(offset=[1, 0]):
                for i in range(4):
                    board[game.shape[i][0] + game.shape_pos[0]][game.shape[i][1] + game.shape_pos[1]].occupied = True
                    board[game.shape[i][0] + game.shape_pos[0]][
                        game.shape[i][1] + game.shape_pos[1]].color = game.shape_color
                max_count = max_count_slow
                game.shape_done()
                if game.check_col(offset=[0, 0]):
                    game_over = True
            else:
                game.shape_down()

            # Check Row Compilation
            while game.check_row_complete()[0]:
                row_complete, index = game.check_row_complete()
                if row_complete:
                    game.eliminate_row(index)
                    lines_cleared_score += 1

    screen.draw()
