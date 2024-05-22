from copy import deepcopy
from random import Random

from game.block import Block
from timer import Timer


class Tetris:
    class GameState:
        ONGOING = 1
        LOST = 2
        PAUSED = 3

    class BlockPlacement:
        POSSIBLE = 1
        COLLIDES = 2
        OUT_OF_BOUNDS = 3

    POINTS_PER_LINE = 100
    POINTS_PER_TETRIS = 1000

    def __init__(self, geometry, colors, difficulty_levels, tick_time=500, width=10, height=20, difficulty_ticks=200):
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
        self._state = self.GameState.PAUSED

        self.random = Random()
        self._next_block = self.generate_next_block()

        self.curr_block = None
        self.curr_block_pos = None

        self.timer = Timer(tick_time/1000, self.perform_tick)

    async def start(self):
        if self._state != self.GameState.PAUSED:
            return

        self._state = self.GameState.ONGOING
        await self.timer.start()

    async def stop(self):
        if self._state != self.GameState.ONGOING:
            return

        self._state = self.GameState.PAUSED
        await self.timer.cancel()

    def generate_next_block(self):
        index = self.random.randint(0, len(self.blocks_geometry) - 1)
        return Block(
            deepcopy(self.blocks_geometry[index]),
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

    async def perform_tick(self):
        if self.curr_block is None:
            new_block = self._next_block
            self._next_block = self.generate_next_block()

            geometry = new_block.geometry
            start_pos = (self.width // 2 - geometry.size // 2, 0)

            place_res = self.can_block_place(new_block, start_pos)

            if place_res == self.BlockPlacement.POSSIBLE:
                self.place_block(new_block, start_pos)

                self.curr_block = new_block
                self.curr_block_pos = start_pos
            else:
                self._state = self.GameState.LOST
                await self.timer.cancel()
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

            if x < 0 or y < 0 or x >= self.width or y >= self.height:
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
        if lines is None or len(lines) == 0:
            return

        lower = min(lines)
        upper = max(lines)
        for line in range(upper, -1, -1):
            new_line = line - upper + lower - 1

            if new_line < 0:
                fill = [False] * self.width
                colors = [(0, 0, 0)] * self.width
            else:
                fill = deepcopy(self.filled[new_line])
                colors = deepcopy(self.colors[new_line])

            self.filled[line] = fill
            self.colors[line] = colors

    def increase_score(self, lines_count):
        if lines_count > 3:
            self._score += self.POINTS_PER_TETRIS
        else:
            self._score += lines_count * self.POINTS_PER_LINE

    def rotate_curr_block(self, right):
        if self.curr_block is None:
            return

        self.destroy_block(self.curr_block, self.curr_block_pos)
        self.curr_block.geometry.rotate(right)

        res = self.can_block_place(self.curr_block, self.curr_block_pos)

        if res != self.BlockPlacement.POSSIBLE:
            self.curr_block.geometry.rotate(not right)

        self.place_block(self.curr_block, self.curr_block_pos)

    def move_block(self, right):
        if self.curr_block is None:
            return

        self.destroy_block(self.curr_block, self.curr_block_pos)
        new_pos = (self.curr_block_pos[0] + (1 if right else -1), self.curr_block_pos[1])

        res = self.can_block_place(self.curr_block, new_pos)

        if res == self.BlockPlacement.POSSIBLE:
            self.curr_block_pos = new_pos

        self.place_block(self.curr_block, self.curr_block_pos)
