# test_heuristics.py
from agent import SearchAgent

def test_heuristics():
    agent = SearchAgent()
    start = (0, 0)
    goal = (3, 4)

    m_dist = agent.manhattan_distance(start, goal)
    e_dist = agent.euclidean_distance(start, goal)

    print(f"Manhattan Distance between {start} and {goal}: {m_dist}")
    print(f"Euclidean Distance between {start} and {goal}: {e_dist}")

    assert m_dist == 7, f"Expected 7, got {m_dist}"
    assert e_dist == 5.0, f"Expected 5.0, got {e_dist}"
    print("Heuristic checkpoint passed successfully!")

if __name__ == "__main__":
    test_heuristics()