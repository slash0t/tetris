from copy import deepcopy
from random import Random

from game.block import Block


class Tetris:
    class GameState:
        ONGOING = 1
        LOST = 2

    class BlockPlacement:
        POSSIBLE = 1
        COLLIDES = 2
        OUT_OF_BOUNDS = 3

    POINTS_PER_LINE = 100
    POINTS_PER_TETRIS = 1000

    def __init__(self, geometry, colors, difficulty_levels, tick_time=200, width=6, height=8, difficulty_ticks=200):
        self.tick_time = tick_time
        self.width = width
        self.height = height

        false_line = [False] * width
        black_line = [(0, 0, 0)] * width
        self.filled = []
        self.colors = []
        for i in range(height):
            self.filled.append(deepcopy(false_line))
            self.colors.append(deepcopy(black_line))

        self.blocks_geometry = geometry
        self.block_colors = colors
        self.difficulty_levels = difficulty_levels
        self.difficulty_ticks = difficulty_ticks

        self._difficulty = 0
        self._score = 0
        self._state = self.GameState.ONGOING

        self.random = Random()
        self._next_block = self.generate_next_block()

        self.curr_block = None
        self.curr_block_pos = None

    def generate_next_block(self):
        index = self.random.randint(0, len(self.blocks_geometry) - 1)
        return Block(
            self.blocks_geometry[index],
            self.block_colors[self._difficulty][index]
        )

    def get_next_block(self):
        return self._next_block

    def get_score(self):
        return self._score

    def get_current_difficulty(self):
        return self._difficulty

    def get_state(self):
        return self._state

    def perform_tick(self):
        if self.curr_block is None:
            new_block = self._next_block
            self._next_block = self.generate_next_block()

            geometry = new_block.geometry
            start_pos = (self.width // 2 - geometry.width, geometry.height)

            place_res = self.can_block_place(new_block, start_pos)

            if place_res == self.BlockPlacement.POSSIBLE:
                self.place_block(new_block, start_pos)

                self.curr_block = new_block
                self.curr_block_pos = start_pos
            else:
                self._state = self.GameState.LOST
        else:
            self.destroy_block(self.curr_block, self.curr_block_pos)

            x, y = self.curr_block_pos
            new_pos = (x, y + 1)

            place_res = self.can_block_place(self.curr_block, new_pos)

            if place_res == self.BlockPlacement.POSSIBLE:
                self.place_block(self.curr_block, new_pos)
                self.curr_block_pos = new_pos
            else:
                self.place_block(self.curr_block, self.curr_block_pos)

                lines = self.lines_of_curr_block()
                lines = self.check_lines_filled(lines)

                self.destroy_lines(lines)
                self.increase_score(len(lines))

                self.curr_block = None

    def place_block(self, block, pos):
        self.set_positions(block.geometry, pos, True, block.color)

    def destroy_block(self, block, pos):
        self.set_positions(block.geometry, pos, False, (0, 0, 0))

    def set_positions(self, geometry, pos, fill, color):
        for square_pos in geometry.coords:
            x, y = [pos[i] + square_pos[i] for i in [0, 1]]

            self.filled[y][x] = fill
            self.colors[y][x] = color

    def can_block_place(self, block, pos):
        for square_pos in block.geometry.coords:
            x, y = [pos[i] + square_pos[i] for i in [0, 1]]

            if x < 0 or y < 0 or x >= self.width  or y >= self.height:
                return self.BlockPlacement.OUT_OF_BOUNDS
            if self.filled[y][x]:
                return self.BlockPlacement.COLLIDES

        return self.BlockPlacement.POSSIBLE

    def lines_of_curr_block(self):
        lines = []
        for square_pos in self.curr_block.geometry.coords:
            y = self.curr_block_pos[1] + square_pos[1]
            if y not in lines:
                lines.append(y)
        return lines

    def check_lines_filled(self, lines):
        filled = []

        for line in lines:
            if all(self.filled[line]):
                filled.append(line)

        return filled

    def destroy_lines(self, lines):
        for line in lines:
            new_line = line - len(lines)

            self.filled[line] = deepcopy(self.filled[new_line])
            self.colors[line] = deepcopy(self.colors[new_line])

        for line in range(len(lines)):
            self.filled[line] = [False] * self.width
            self.colors[line] = [(0, 0, 0)] * self.width

    def increase_score(self, lines_count):
        if lines_count > 3:
            self._score += self.POINTS_PER_TETRIS
        else:
            self._score += lines_count * self.POINTS_PER_LINE

    def rotate_curr_block(self, right):
        pass

    def move_block(self, right):
        pass

