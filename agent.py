# agent.py
import random
from collections import deque


class GreedyGridAgent:
    """A simple agent that tries to move around systematically to clear the grid."""

    def __init__(self):
        self.actions_pool = ['Up', 'Down', 'Left', 'Right']

    def sense_and_act(self, percept: dict) -> str:
        return random.choice(self.actions_pool)


class SimpleReflexAgent:
    """Condition-Action reflex agent with no memory."""

    def sense_and_act(self, percept: dict) -> str:
        if percept['food_here']:
            return 'Suck'
        if percept['wall_ahead']:
            return 'Left'
        return 'Forward'


class ModelBasedAgent:
    """Reflex agent with internal state to escape loops."""

    def __init__(self):
        self.visited_cells = set()
        self.last_action = None
        self.position = (0, 0)
        self.facing = 'Right'
        self.wall_hits = 0

    def _turn_right(self):
        order = ['Up', 'Right', 'Down', 'Left']
        self.facing = order[(order.index(self.facing) + 1) % 4]

    def _turn_left(self):
        order = ['Up', 'Right', 'Down', 'Left']
        self.facing = order[(order.index(self.facing) - 1) % 4]

    def _next_pos(self):
        x, y = self.position
        if self.facing == 'Up':
            return (x, y + 1)
        elif self.facing == 'Down':
            return (x, y - 1)
        elif self.facing == 'Left':
            return (x - 1, y)
        else:
            return (x + 1, y)

    def _update_state(self, percept):
        self.visited_cells.add(self.position)
        if self.last_action == 'Forward' and not percept.get('wall_ahead', False):
            self.position = self._next_pos()
        elif self.last_action == 'Left':
            self._turn_left()
        elif self.last_action == 'Right':
            self._turn_right()

    def sense_and_act(self, percept: dict) -> str:
        self._update_state(percept)

        if percept.get('food_here', False):
            self.wall_hits = 0
            self.last_action = 'Suck'
            return 'Suck'

        if percept.get('wall_ahead', False):
            self.wall_hits += 1
            if self.wall_hits % 2 == 1:
                self.last_action = 'Right'
                return 'Right'
            else:
                self.last_action = 'Left'
                return 'Left'

        self.wall_hits = 0
        ahead = self._next_pos()
        if ahead in self.visited_cells:
            self.last_action = 'Right'
            return 'Right'

        self.last_action = 'Forward'
        return 'Forward'


class SearchAgent:
    """Offline planning agent using BFS to find the shortest path."""

    def bfs_search(self, start, goal, walls, grid_size):
        walls_set = set(map(tuple, walls))
        width, height = grid_size
        queue = deque()
        queue.append((start, []))
        visited = {start}

        moves = {
            'Up': (0, 1),
            'Down': (0, -1),
            'Left': (-1, 0),
            'Right': (1, 0),
        }

        while queue:
            pos, path = queue.popleft()
            if pos == goal:
                return path
            for action, (dx, dy) in moves.items():
                nx, ny = pos[0] + dx, pos[1] + dy
                npos = (nx, ny)
                if 0 <= nx < width and 0 <= ny < height and npos not in walls_set and npos not in visited:
                    visited.add(npos)
                    queue.append((npos, path + [action]))

        return None