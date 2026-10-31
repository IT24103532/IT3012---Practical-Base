import random
import math
from collections import deque
import heapq
from logic_engine import KnowledgeBase


class GreedyGridAgent:
    def __init__(self):
        self.actions_pool = ['Up', 'Down', 'Left', 'Right']

    def sense_and_act(self, percept: dict) -> str:
        pos = percept['agent_pos']
        return random.choice(self.actions_pool)


class SimpleReflexAgent:
    def sense_and_act(self, percept: dict) -> str:
        if percept.get('food_here') or percept.get('smells_food'):
            return 'suck'
        elif percept.get('wall_here') or percept.get('hit_wall') or percept.get('wall_ahead'):
            return random.choice(['Up', 'Down', 'Left', 'Right'])
        elif percept.get('trap_here') or percept.get('smells_toxin'):
            return random.choice(['Up', 'Down', 'Left', 'Right'])
        else:
            return 'Up'


class ModelBasedAgent:
    def __init__(self):
        self.x = 0
        self.y = 0
        self.last_action = None
        self.visited_cells = set()

    def sense_and_act(self, percept: dict) -> str:
        if self.last_action == 'Up':
            self.y += 1
        elif self.last_action == 'Down':
            self.y -= 1
        elif self.last_action == 'Left':
            self.x -= 1
        elif self.last_action == 'Right':
            self.x += 1

        self.visited_cells.add((self.x, self.y))

        if percept.get('food_here') or percept.get('smells_food'):
            action = 'Stay'
        else:
            candidates = {
                'Up': (self.x, self.y + 1),
                'Down': (self.x, self.y - 1),
                'Left': (self.x - 1, self.y),
                'Right': (self.x + 1, self.y)
            }
            if percept.get('wall_here') or percept.get('hit_wall') or percept.get('wall_ahead'):
                if self.last_action in candidates:
                    del candidates[self.last_action]

            unvisited_actions = [a for a, pos in candidates.items() if pos not in self.visited_cells]
            if unvisited_actions:
                action = random.choice(unvisited_actions)
            elif candidates:
                action = random.choice(list(candidates.keys()))
            else:
                action = random.choice(['Up', 'Down', 'Left', 'Right'])
        self.last_action = action
        return action


class SearchAgent:
    """
    SearchAgent equipped with Uninformed Search (BFS, DFS, UCS),
    Informed A* Search, and a Declarative Knowledge Base for Feasibility verification.
    """

    def __init__(self):
        self.plan = []
        self.active_algo = 'AStar'

        # Part 3.1: Setup Knowledge Base and Domain Rules
        self.kb = KnowledgeBase()
        self.kb.tell_rule(['TargetVisible', 'HasDust'], 'SafeToEngage')
        self.kb.tell_rule(['SafeToEngage', 'BloodseekerMissing'], 'Retreat')

    def manhattan_distance(self, pos, goal) -> int:
        return abs(pos[0] - goal[0]) + abs(pos[1] - goal[1])

    def euclidean_distance(self, pos, goal) -> float:
        return math.sqrt((pos[0] - goal[0]) ** 2 + (pos[1] - goal[1]) ** 2)

    def bfs_search(self, start_pos, goal_pos, walls, grid_size) -> list:
        start = tuple(start_pos)
        goal = tuple(goal_pos)
        walls_set = set(tuple(w) for w in walls)
        width, height = grid_size

        queue = deque([(start, [])])
        visited = {start}

        while queue:
            current, path = queue.popleft()

            if current == goal:
                return path

            x, y = current
            moves = [
                ('Up', (x, y + 1)),
                ('Down', (x, y - 1)),
                ('Left', (x - 1, y)),
                ('Right', (x + 1, y))
            ]

            for action, next_pos in moves:
                nx, ny = next_pos
                # Chained boundary and obstacle comparison corrected
                if 0 <= nx < width and 0 <= ny < height and next_pos not in walls_set:
                    if next_pos not in visited:
                        visited.add(next_pos)
                        queue.append((next_pos, path + [action]))

        return []

    def dfs_search(self, start_pos, goal_pos, walls, grid_size) -> list:
        start = tuple(start_pos)
        goal = tuple(goal_pos)
        walls_set = set(tuple(w) for w in walls)
        width, height = grid_size

        stack = [(start, [])]
        visited = {start}

        while stack:
            current, path = stack.pop()

            if current == goal:
                return path

            x, y = current
            moves = [
                ('Up', (x, y + 1)),
                ('Down', (x, y - 1)),
                ('Left', (x - 1, y)),
                ('Right', (x + 1, y))
            ]

            for action, next_pos in moves:
                nx, ny = next_pos
                if 0 <= nx < width and 0 <= ny < height and next_pos not in walls_set:
                    if next_pos not in visited:
                        visited.add(next_pos)
                        stack.append((next_pos, path + [action]))

        return []

    def ucs_search(self, start_pos, goal_pos, walls, grid_size) -> list:
        start = tuple(start_pos)
        goal = tuple(goal_pos)
        walls_set = set(tuple(w) for w in walls)
        width, height = grid_size

        counter = 0
        pq = [(0, counter, start, [])]
        visited = set()

        while pq:
            cost, _, current, path = heapq.heappop(pq)
            if current == goal:
                return path

            if current not in visited:
                visited.add(current)
                x, y = current
                moves = [
                    ('Up', (x, y + 1)),
                    ('Down', (x, y - 1)),
                    ('Left', (x - 1, y)),
                    ('Right', (x + 1, y))
                ]
                for action, next_pos in moves:
                    nx, ny = next_pos
                    if 0 <= nx < width and 0 <= ny < height and next_pos not in walls_set:
                        if next_pos not in visited:
                            counter += 1
                            heapq.heappush(pq, (cost + 1, counter, next_pos, path + [action]))
        return []

    def astar_search(self, start_pos, goal_pos, walls, grid_size, heuristic_type='manhattan', tile_facts=None) -> list:
        start = tuple(start_pos)
        goal = tuple(goal_pos)
        walls_set = set(tuple(w) for w in walls)
        width, height = grid_size

        if tile_facts is None:
            tile_facts = {}

        h = self.manhattan_distance if heuristic_type == 'manhattan' else self.euclidean_distance

        reached_states = set()
        g_start = 0
        h_start = h(start, goal)
        f_start = g_start + h_start

        pq = [(f_start, g_start, start, [])]

        while pq:
            f_cost, g_cost, current_pos, path_taken = heapq.heappop(pq)

            if current_pos == goal:
                return path_taken

            if current_pos in reached_states:
                continue

            reached_states.add(current_pos)

            x, y = current_pos
            moves = [
                ('Up', (x, y + 1)),
                ('Down', (x, y - 1)),
                ('Left', (x - 1, y)),
                ('Right', (x + 1, y))
            ]

            for action, next_pos in moves:
                nx, ny = next_pos

                # Check 1: Physical Reachability (Boundaries & Static Walls)
                if not (0 <= nx < width and 0 <= ny < height) or next_pos in walls_set:
                    continue

                if next_pos in reached_states:
                    continue

                # Check 2: Logical Feasibility via Knowledge Base
                self.kb.clear_facts()
                for fact in tile_facts.get(next_pos, []):
                    self.kb.tell_fact(fact)

                self.kb.forward_chain()

                # Prune node if Retreat is logically deduced
                if 'Retreat' in self.kb.facts:
                    continue

                g_new = g_cost + 1
                h_new = h(next_pos, goal)
                f_new = g_new + h_new
                heapq.heappush(pq, (f_new, g_new, next_pos, path_taken + [action]))

        return []

    def sense_and_act(self, percept: dict) -> str:
        if not self.plan:
            agent_pos = tuple(percept.get('agent_pos', [0, 0]))
            all_food = percept.get('all_food', [])
            walls = percept.get('walls', [])
            grid_size = percept.get('grid_size', (10, 10))

            if not all_food:
                return 'Stay'

            closest_food = min(
                all_food,
                key=lambda f: self.manhattan_distance(agent_pos, f)
            )

            # Step 3.3: Supply per-tile domain facts
            tile_facts = {
                (1, 0): ['TargetVisible', 'HasDust', 'BloodseekerMissing'],  # deduces Retreat: blocked
                (0, 1): ['TargetVisible', 'HasDust'],                        # SafeToEngage only: allowed
            }

            if self.active_algo == 'BFS':
                self.plan = self.bfs_search(agent_pos, closest_food, walls, grid_size)
            elif self.active_algo == 'DFS':
                self.plan = self.dfs_search(agent_pos, closest_food, walls, grid_size)
            elif self.active_algo == 'UCS':
                self.plan = self.ucs_search(agent_pos, closest_food, walls, grid_size)
            elif self.active_algo == 'AStar':
                self.plan = self.astar_search(
                    agent_pos, closest_food, walls, grid_size,
                    heuristic_type='manhattan', tile_facts=tile_facts
                )

        if self.plan:
            return self.plan.pop(0)
        return 'Stay'