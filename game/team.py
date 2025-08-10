from .constants import FIELDS

class Team:
    def __init__(self, name):
        self.name = name
        self.developers = 3
        self.skill_per_dev = [3]*3  # Each developer has a skill level of 3
        self.bugs = 0
        self.technical_debt = 0
        self.resources = 0
        self.satisfaction = 0
        self.features_round = 0
        self.optimizations_round = 0
        self.total_features = 0
        self.total_optimizations = 0
        self.allocations = {}

    @property
    def capacity(self):
        capacity = sum(list(map(lambda x: x // 3, self.skill_per_dev))) 
        if self.technical_debt >= 4:
            capacity -= 1
        return max(capacity, 0)

    def allocate_points(self, allocations):
        if sum(allocations.values()) > self.capacity:
            raise ValueError("Allocation exceeds capacity!")
        self.allocations = allocations

    def end_sprint(self):
        # Update team state after a sprint: accumulation 
        self.technical_debt += self.allocations['New feature'] 
        self.technical_debt += self.allocations['Optimization']
        if self.allocations['Testing'] < self.allocations['New feature']:
            new_bugs = self.allocations['New feature'] + self.allocations['Optimization'] - self.allocations['Testing']
        else:
            new_bugs = 0
        self.bugs += new_bugs

        # Update state: reduction
        self.bugs = max(0, self.bugs - self.allocations['Bug resolution'])
        self.technical_debt = max(0, self.technical_debt - self.allocations['Technical debt'])

        # Update totals
        self.features_round += self.allocations['New feature']
        self.optimizations_round += self.allocations['Optimization']
        self.total_features += self.allocations['New feature']
        self.total_optimizations += self.allocations['Optimization']

    def try_hire_developer(self):
        if self.resources >= 3:
            self.developers += 1
            self.resources -= 3
            print(f"{self.name} hired a new developer!")

    def to_dict(self):
        return {
            "name": self.name,
            "developers": self.developers,
            "skill_per_dev": self.skill_per_dev,
            "bugs": self.bugs,
            "technical_debt": self.technical_debt,
            "resources": self.resources,
            "satisfaction": self.satisfaction,
            "features_round": self.features_round,
            "optimizations_round": self.optimizations_round,
            "total_features": self.total_features,
            "total_optimizations": self.total_optimizations,
            "allocations": self.allocations,
        }
    
    @classmethod 
    def from_dict(cls, data):
        
        team = cls(data["name"])
        team.developers = data["developers"]
        team.skill_per_dev = data["skill_per_dev"]
        team.bugs = data["bugs"]
        team.technical_debt = data["technical_debt"]
        team.resources = data["resources"]
        team.satisfaction = data["satisfaction"]
        team.features_round = data["features_round"]
        team.optimizations_round = data["optimizations_round"]
        team.total_features = data["total_features"]
        team.total_optimizations = data["total_optimizations"]
        team.allocations = data["allocations"]

        return team
    
if __name__ == "__main__":
    team = Team("Dev Team")
    print(f"Team {team.name} initialized with {team.developers} developers.")
    print(f"Initial capacity: {team.capacity}")
    # Example usage
    try:
        team.allocate_points({'New feature': 1, 'Optimization': 0, 'Testing': 2, 'Bug_resolution': 0, 'Technical_debt': 0})
        print("Points allocated successfully.")
    except ValueError as e:
        print(e)