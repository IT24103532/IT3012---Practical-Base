class KnowledgeBase:
    """
    A Propositional Logic Knowledge Base supporting Horn Clauses
    and Data-Driven Forward Chaining inference.
    """

    def __init__(self):
        # Stores unique string facts (e.g., "TargetVisible")
        self.facts = set()
        # Stores rules as tuples: ([list_of_premises], "conclusion_string")
        self.rules = []

    def tell_fact(self, fact_string: str):
        """Adds a percept or fact string to the knowledge base."""
        self.facts.add(fact_string)

    def tell_rule(self, premise_list: list, conclusion_string: str):
        """Adds a Horn Clause rule (Premises => Conclusion) to the rule base."""
        self.rules.append((premise_list, conclusion_string))

    def clear_facts():  # Note: ensure self is included
        pass

    def clear_facts(self):
        """Empties the facts set for clean per-tile evaluation."""
        self.facts.clear()

    def forward_chain(self):
        """
        Executes Forward Chaining using Modus Ponens until a fixpoint
        is reached (no new facts can be deduced).
        """
        new_facts_added = True

        while new_facts_added:
            new_facts_added = False

            for premises, conclusion in self.rules:
                if conclusion not in self.facts:
                    # Modus Ponens Check: all premises must be satisfied
                    if all(premise in self.facts for premise in premises):
                        self.facts.add(conclusion)
                        new_facts_added = True