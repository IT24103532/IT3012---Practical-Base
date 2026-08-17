# agent.py
import random
from collections import deque
import heapq


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
    """Offline planning agent using BFS, DFS, or UCS to find paths to food."""

    def __init__(self):
        self.plan = []
        self.active_algo = 'BFS'
        self.facing = 'Right'  # Track agent facing to translate absolute → relative actions

    def bfs_search(self, start, goal, walls, grid_size):
        """BFS: uses a FIFO queue (deque.popleft()) — explores shallowest nodes first."""
        walls_set = set(map(tuple, walls))
        width, height = grid_size
        queue = deque()
        queue.append((start, []))
        reached = {start}

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
                if 0 <= nx < width and 0 <= ny < height and npos not in walls_set and npos not in reached:
                    reached.add(npos)
                    queue.append((npos, path + [action]))

        return None

    def dfs_search(self, start, goal, walls, grid_size):
        """DFS: uses a LIFO stack (list.pop()) — explores deepest nodes first."""
        walls_set = set(map(tuple, walls))
        width, height = grid_size
        stack = [(start, [])]
        reached = {start}

        moves = {
            'Up': (0, 1),
            'Down': (0, -1),
            'Left': (-1, 0),
            'Right': (1, 0),
        }

        while stack:
            pos, path = stack.pop()
            if pos == goal:
                return path
            for action, (dx, dy) in moves.items():
                nx, ny = pos[0] + dx, pos[1] + dy
                npos = (nx, ny)
                if 0 <= nx < width and 0 <= ny < height and npos not in walls_set and npos not in reached:
                    reached.add(npos)
                    stack.append((npos, path + [action]))

        return None

    def ucs_search(self, start, goal, walls, grid_size):
        """UCS: uses a Priority Queue (heapq.heappop()) ordered by total path cost g(n)."""
        walls_set = set(map(tuple, walls))
        width, height = grid_size
        # heap entries: (cost, position, path)
        heap = [(0, start, [])]
        reached = {start}

        moves = {
            'Up': (0, 1),
            'Down': (0, -1),
            'Left': (-1, 0),
            'Right': (1, 0),
        }

        while heap:
            cost, pos, path = heapq.heappop(heap)
            if pos == goal:
                return path
            for action, (dx, dy) in moves.items():
                nx, ny = pos[0] + dx, pos[1] + dy
                npos = (nx, ny)
                if 0 <= nx < width and 0 <= ny < height and npos not in walls_set and npos not in reached:
                    reached.add(npos)
                    heapq.heappush(heap, (cost + 1, npos, path + [action]))

        return None

    def sense_and_act(self, percept: dict) -> str:
        # Collect food immediately if standing on it
        if percept.get('food_here', False):
            return 'Suck'

        # If there are pending relative actions in the plan, execute next one
        if self.plan:
            return self.plan.pop(0)

        # Plan is empty — search for the closest food pellet
        start = tuple(percept.get('agent_pos', (0, 0)))
        all_food = percept['all_food']
        walls = percept['walls']
        grid_size = percept['grid_size']

        # Find the closest food pellet by Manhattan distance
        best_goal = None
        best_dist = float('inf')
        for food in all_food:
            dist = abs(food[0] - start[0]) + abs(food[1] - start[1])
            if dist < best_dist:
                best_dist = dist
                best_goal = food

        if best_goal is not None:
            if self.active_algo == 'BFS':
                abs_path = self.bfs_search(start, tuple(best_goal), walls, grid_size)
            elif self.active_algo == 'DFS':
                abs_path = self.dfs_search(start, tuple(best_goal), walls, grid_size)
            elif self.active_algo == 'UCS':
                abs_path = self.ucs_search(start, tuple(best_goal), walls, grid_size)
            else:
                abs_path = None

            if abs_path:
                # Translate absolute directions → relative game actions
                # The game uses: 'Forward' (move), 'Left' (turn CCW), 'Right' (turn CW)
                turn_order = ['Up', 'Right', 'Down', 'Left']
                relative_plan = []
                facing = self.facing
                for direction in abs_path:
                    cur_idx = turn_order.index(facing)
                    tgt_idx = turn_order.index(direction)
                    diff = (tgt_idx - cur_idx) % 4
                    if diff == 1:
                        relative_plan.append('Right')
                    elif diff == 2:
                        relative_plan.extend(['Right', 'Right'])
                    elif diff == 3:
                        relative_plan.append('Left')
                    relative_plan.append('Forward')
                    facing = direction
                self.facing = facing
                self.plan = relative_plan

        if self.plan:
            return self.plan.pop(0)

        # Fallback if no plan could be found
        return 'Forward'