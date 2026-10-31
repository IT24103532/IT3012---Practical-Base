### Theoretical Evaluation Answers

Paste these answers directly into the Practical 04 worksheet or documentation:

#### 1. What is the key difference between how Uniform-Cost Search (UCS) and $A^*$ Search prioritize which node to explore next?



* **UCS Priority Metric ($g(n)$):** Uniform-Cost Search prioritizes nodes strictly by their cumulative backward path cost $g(n)$ from the start node. It operates without knowledge of the goal's location, expanding outward uniformly in all directions like expanding contours.


* **$A^*$ Priority Metric ($f(n) = g(n) + h(n)$):** $A^*$ combines the actual backward path cost $g(n)$ with a forward heuristic estimate $h(n)$ of the cheapest path from node $n$ to the goal. By factoring in $h(n)$, $A^*$ actively biases frontier expansion toward the goal state, dramatically reducing the number of explored nodes while maintaining optimality.



#### 2. In Step 1.1, you used Manhattan Distance. Why is Manhattan Distance considered an "admissible" heuristic for this specific 4-way movement grid, and what would happen to your $A^*$ algorithm if the heuristic was NOT admissible?



* **Admissibility of Manhattan Distance:** A heuristic $h(n)$ is admissible if it never overestimates the true cost $h^*(n)$ to reach the goal ($h(n) \le h^*(n)$ for all $n$). In a 4-way orthogonal grid with uniform step cost of 1, moving from $(x_1, y_1)$ to $(x_2, y_2)$ requires at least $\vert{}x_1 - x_2\vert{} + \vert{}y_1 - y_2\vert{}$ steps in the complete absence of obstacles. Adding walls can only lengthen the path, meaning Manhattan distance represents the absolute minimum physical cost possible and is guaranteed to be admissible ($h(n) \le h^*(n)$).


* **Consequence of Non-Admissible Heuristics:** If $h(n)$ overestimates the true cost ($h(n) > h^*(n)$), $A^*$ is no longer guaranteed to return an optimal path. The search might prematurely prioritize a suboptimal path because the optimal branch was assigned an artificially inflated $f$-cost, causing $A^*$ to skip or defer expanding the true shortest path before terminating at the goal.

#### 3. If we modified visual_grid_game.py to allow the agent to move diagonally (8-way movement), would Manhattan distance still be an admissible heuristic? Why or why not? Which metric should you switch to?



* **Admissibility under 8-Way Movement:** No, Manhattan distance would **cease to be admissible**. With diagonal steps costing 1 unit, an agent can move from $(0, 0)$ to $(1, 1)$ in 1 single diagonal action ($h^*(n) = 1$). However, Manhattan distance computes $\vert{}1 - 0\vert{} + \vert{}1 - 0\vert{} = 2$. Because $h(n) = 2 > h^*(n) = 1$, it overestimates the true cost, violating admissibility.
* **Metric to Switch to:** You should switch to **Chebyshev Distance** (or Diagonal Distance), formulated as:

$$h(n) = \max(\vert{}x_1 - x_2\vert{}, \vert{}y_1 - y_2\vert{})$$



If diagonal moves cost $\sqrt{2} \approx 1.414$ while orthogonal moves cost 1, the optimal admissible heuristic would be **Octile Distance**:

$$h(n) = (\vert{}x_1 - x_2\vert{} + \vert{}y_1 - y_2\vert{}) + (\sqrt{2} - 2) \cdot \min(\vert{}x_1 - x_2\vert{}, \vert{}y_1 - y_2\vert{})$$



#### 4. When targeting multiple food items simultaneously, calculating the distance to just the single closest food item is a weak heuristic. Propose (in text) a stronger heuristic for navigating the grid to eat ALL remaining food efficiently.



* **Proposed Heuristic — Minimum Spanning Tree (MST) Relaxation:**
Treat the remaining food locations together with the agent's current position as vertices in a complete, undirected graph where edge weights equal the pairwise Manhattan distances between them. The proposed heuristic function is:

$$h(n) = \text{cost}(\text{MST of remaining food items}) + \min_{f \in \text{all\_food}} \text{dist}(n, f)$$


1. $\min_{f \in \text{all\_food}} \text{dist}(n, f)$ represents the minimum cost for the agent to reach the first food pellet.
2. $\text{cost}(\text{MST})$ computes the minimum tree connecting all remaining pellets without obstacle constraints (solvable in polynomial time using Kruskal's or Prim's algorithm).


* **Why It Is Stronger and Admissible:**
Any valid path that visits all food pellets must trace a spanning walk over all target vertices. An MST represents the minimum possible connected structure over those vertices, meaning its cost is strictly less than or equal to the shortest Traveling Salesperson tour visiting them all. Because it accounts for the spatial dispersion of all items rather than just one local point while still never overestimating the remaining travel distance, it is both admissible and significantly more informed.
