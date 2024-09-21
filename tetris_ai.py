import copy
import random
import sys
from os import environ

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
        self.best_path = []
        self.shape, self.shape_pos, self.shape_color = None, None, None
        self.next_shape, self.next_shape_pos, self.next_shape_color = self.new_shape()
        self.shape_done()
        self.decision_arr = []

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
    #     # shape = tetris_shapes[random.randrange(len(tetris_shapes))]
    #     shape = tetris_shapes[random.randint(0, len(tetris_shapes)-1)]
    #     # shape = tetris_shapes[4]
    #     y_offset = abs(min([pos[0] for pos in shape]))
    #     shape_pos = [y_offset, 5]
    #     # shape_pos = [0, 0]
    #     shape_color = colors[random.randrange(len(colors))]
    #     return shape, shape_pos, shape_color

    def shape_down(self):
        self.shape_pos[0] += 1

    @staticmethod
    def rotate(shape):
        for i in range(4):
            x = shape[i][0]
            y = shape[i][1]
            shape[i][1] = -x
            shape[i][0] = y

    @staticmethod
    def check_col(shape, shape_pos, offset):
        for k in range(4):
            if shape[k][0] + shape_pos[0] > board_height - 2:  # Check For Bottom Screen
                return True
            elif shape[k][1] + shape_pos[1] + offset[1] >= board_width:  # Check For Right Screen
                return True
            elif shape[k][1] + shape_pos[1] + offset[1] < 0:  # Check For Left Screen
                return True
            elif board[shape[k][0] + shape_pos[0] +
                       offset[0]][shape[k][1] + shape_pos[1] + offset[1]].occupied:  # Check For Below
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
        self.generate_path()
        self.next_shape, self.next_shape_pos, self.next_shape_color = self.new_shape()

    def create_decision_array(self):
        self.decision_arr = []
        dummy_shape = copy.deepcopy(self.shape)
        if dummy_shape == tetris_shapes[1]:  # If Shape Is Square Not Need To Rotate
            times_rotate = 1
        else:
            times_rotate = 4
        for k in range(times_rotate):
            # print(self.shape)
            x_border = [abs(min([pos[1] for pos in dummy_shape])),
                        board_width - max([pos[1] for pos in dummy_shape])]
            y_border = [self.shape_pos[0],
                        board_height - abs(max(pos[0] for pos in dummy_shape)) - self.shape_pos[0]]
            # print(f'x_border: {x_border}; y_border: {y_border}')
            for i in range(*x_border):  # Moving In X Axis
                max_value = 0
                for j in range(*y_border):  # Moving In Y Axis
                    # print(k, i, j)
                    # print(self.shape_pos[1]-i)
                    if not self.check_col(shape=dummy_shape, shape_pos=self.shape_pos,
                                          offset=[j, i - self.shape_pos[1]]):
                        max_value = self.shape_pos[0] + j
                    else:
                        break
                if max_value != 0:
                    self.decision_arr.append(
                        TetrisAI(copy.deepcopy(dummy_shape), copy.deepcopy([max_value, i]), copy.deepcopy(k)))
            self.rotate(dummy_shape)

    def generate_path(self):
        self.create_decision_array()

        # Put Score For Every Game Possibility
        for shape in self.decision_arr:
            shape.get_score()
        print()

        # Sort The Array To Get The Maximum Score
        self.decision_arr.sort(key=lambda x: x.score)
        # print(f'best score: {self.decision_arr[-1].score}')

        # Construct The Path To The Best Game Possibility
        self.best_path = []
        for _ in range(self.decision_arr[-1].rotation):
            self.best_path.append('rotate')
        if self.decision_arr[-1].shape_pos[1] > self.shape_pos[1]:
            for _ in range(self.decision_arr[-1].shape_pos[1] - self.shape_pos[1]):
                self.best_path.append('right')
        else:
            for _ in range(self.shape_pos[1] - self.decision_arr[-1].shape_pos[1]):
                self.best_path.append('left')
        self.best_path.append('down')
        # print('a')
        # print(self.best_path)


class TetrisAI:
    def __init__(self, shape, pos, rotation):
        self.shape = shape
        self.shape_pos = pos
        self.rotation = rotation
        self.score = 0
        self.path_to_place = []

    def get_score(self):
        # print(self.shape, self.rotation)
        shape_x_unique = list(set([pos[1] for pos in self.shape]))
        empty_spaces = 0
        for i in shape_x_unique:
            split_list_x = []
            for j in range(4):
                if self.shape[j][1] == i:
                    split_list_x.append(self.shape[j])

            low_x = sorted(split_list_x, key=lambda x: x[0])[-1]  # This Is The Lowest Position At Given X
            low_x = [low_x[0] + self.shape_pos[0], low_x[1] + self.shape_pos[1]]
            # print(f'low_x: {low_x}, rotation: {self.rotation}')
            # try:
            #     print('for ', low_x[1], board[low_x[0]+1][low_x[1]].occupied)
            #     if not board[low_x[0]+1][low_x[1]].occupied:
            #         empty_spaces += 1
            # except IndexError:
            #     pass
            for k in range(low_x[0]+1, board_height):
                # print('for ', k, low_x[1], board[k][low_x[1]].occupied)
                if not board[k][low_x[1]].occupied:
                    empty_spaces += 1
        # print(f'score: {-empty_spaces}')

        # Punish Empty Space Below Shape
        self.score -= empty_spaces
        # Encourage Lower Shape Placement
        # self.score += self.shape_pos[0] / 20
        # for pos in self.shape:
        #     self.score += pos[0] + self.shape_pos[0]

        # print(self.score)
        # print(empty_spaces, 'a')
        # print()


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
            try:
                if not game.check_col(shape=game.shape, shape_pos=game.shape_pos, offset=[i, 0]):
                    max_value = game.shape_pos[0] + i
                else:
                    break
            except IndexError:
                pass

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
                    if not game.check_col(shape=game.shape, shape_pos=game.shape_pos, offset=[0, -1]):
                        game.shape_pos[1] -= 1
                if event.key == pygame.K_RIGHT:
                    if not game.check_col(shape=game.shape, shape_pos=game.shape_pos, offset=[0, 1]):
                        game.shape_pos[1] += 1
                if event.key == pygame.K_r:
                    game.rotate(game.shape)
                    rem = False
                    if game.check_col(shape=game.shape, shape_pos=game.shape_pos, offset=[0, 0]):
                        for i in [-1, 1, -2, 2]:
                            if not game.check_col(shape=game.shape, shape_pos=game.shape_pos, offset=[1, i]):
                                game.shape_pos[1] += i
                                rem = True
                                break
                        if not rem:
                            for _ in range(3):
                                game.rotate(game.shape)

                if event.key == pygame.K_DOWN:
                    max_count = max_count_fast

    # print(game.best_path)
    next_move = None
    if len(game.best_path) > 0:
        next_move = game.best_path.pop(0)

    if next_move == 'down':
        max_count = max_count_fast
    elif next_move == 'rotate':
        game.rotate(game.shape)
    elif next_move == 'right':
        if not game.check_col(shape=game.shape, shape_pos=game.shape_pos, offset=[0, 1]):
            game.shape_pos[1] += 1
    elif next_move == 'left':
        if not game.check_col(shape=game.shape, shape_pos=game.shape_pos, offset=[0, -1]):
            game.shape_pos[1] -= 1

    if not game_over:
        # Counter Handling
        count += 1
        if count >= max_count:
            count = 0
            game.shape_down()

            # If Collision Occurred, Pass Info To Board And Draw New Shape
            if game.check_col(shape=game.shape, shape_pos=game.shape_pos, offset=[1, 0]):
                for i in range(4):
                    board[game.shape[i][0] + game.shape_pos[0]][game.shape[i][1] + game.shape_pos[1]].occupied = True
                    board[game.shape[i][0] + game.shape_pos[0]][
                        game.shape[i][1] + game.shape_pos[1]].color = game.shape_color
                max_count = max_count_slow
                game.shape_done()
                if game.check_col(shape=game.shape, shape_pos=game.shape_pos, offset=[0, 0]):
                    game_over = True

        # Check Row Compilation
        row_complete, index = game.check_row_complete()
        if row_complete:
            game.eliminate_row(index)
            lines_cleared_score += 1

    screen.draw()
