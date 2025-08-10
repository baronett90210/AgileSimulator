import random
from .team import Team
from .constants import FIELDS

class Game:

    def __init__(self, team, expectation = None, total_sprints = None):
        
        self.sprints_per_round = 4 
        self.team = team
        self.expectation = {
            'feature': 1,
            'optimization': 1
        } if expectation is None else expectation
        self.total_sprints = total_sprints

    def play_sprint(self, sprint_num, allocations = None, staffing = None):

        # create allocations from command prompt if not given
        if allocations is None:
            print(f"\n--- sprint {sprint_num + 1} ---")
            print(f"Customer expectation: Features: {self.expectation['feature']}, Optimizations: {self.expectation['optimization']}")
            print(f"Team capacity: {self.team.capacity}, Bugs: {self.team.bugs}, Tech Debt: {self.team.technical_debt}")

            allocations = {}
            for field in FIELDS:
                while True:
                    try:
                        val = int(input(f"Allocate points to {field}: "))
                        allocations[field] = val
                        break
                    except ValueError:
                        print("Enter a valid integer.")

        self.team.allocate_points(allocations)
        self.team.handle_staffing(staffing)
        self.team.end_sprint()

    def end_round(self):

        print("\n--- Round Over ---")
        met_expectation = (
            self.team.features_round >= self.expectation['feature'] and
            self.team.optimizations_round >= self.expectation['optimization']
        )
        too_many_bugs = self.team.bugs >= 4
        self.team.features_round = 0
        self.team.optimizations_round = 0

        if met_expectation:
            self.team.satisfaction += 1
            self.team.resources += 1
            print("✅ Expectations met! Satisfaction +1, Resources +1")
        else:
            self.team.satisfaction -= 1
            print("❌ Expectations not met! Satisfaction -1")
        
        if too_many_bugs:
            self.team.satisfaction -= 1
            print("❌ Bugs present! Satisfaction -1")

        print(f"Final Satisfaction: {self.team.satisfaction}")
        print(f"Resources: {self.team.resources}")
        print(f"Developers: {self.team.developers}")

        return met_expectation, too_many_bugs

    def end_game(self):
        print("\n--- Game Over ---")
        print(f"Final Satisfaction: {self.team.satisfaction}")
        print(f"Total Features: {self.team.total_features}")
        print(f"Total Optimizations: {self.team.total_optimizations}")
        print(f"Total Bugs: {self.team.bugs}")
        print(f"Technical Debt: {self.team.technical_debt}")    

    def to_dict(self):
        return {
            "total_sprints": self.total_sprints,
            "sprints_per_round": self.sprints_per_round,
            "expectation": self.expectation,
        }
    


if __name__ == "__main__":
    team = Team("Dev Team")
    game = Game(team)

    for sprint_num in range(1, game.sprints + 1):
        game.play_sprint(sprint_num)

    game.end_game()