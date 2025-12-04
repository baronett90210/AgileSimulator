from .constants import FIELDS
from .developer import Developer

class Team:
    def __init__(self, name, current_sprint = 0):
        self.name = name
        self.bugs = 0
        self.technical_debt = 0
        self.resources = 3
        self.satisfaction = 0
        self.features_sprint = 0
        self.optimizations_sprint = 0
        self.features_round = 0
        self.optimizations_round = 0
        self.total_features = 0
        self.total_optimizations = 0
        self.allocations = {}
        self.developers = [Developer() for _ in range(3)]
        self.update_capacity(current_sprint)

    def update_capacity(self, current_sprint):

        capacity_initial = list(map(lambda x: x // 3, self.skill_per_dev))
        availability = [dev.available_from <= current_sprint for dev in self.developers]
        self.capacity = sum([cap*av for cap, av in zip(capacity_initial, availability)])

        if self.technical_debt >= 4:
            self.capacity -= 1
    
    @property
    def skill_per_dev(self):
        return [dev.skill for dev in self.developers]
    
    @property
    def n_developers(self):
        return len(self.developers)

    def allocate_points(self, allocations):
        if sum(allocations.values()) > self.capacity:
            raise ValueError("Allocation exceeds capacity!")
        self.allocations = allocations

    def handle_staffing(self, staffing, current_sprint):
        if 'Hire developers' in staffing and staffing['Hire developers'] > 0:
            self.try_hire_developer(staffing['Hire developers'], current_sprint)

    def end_sprint(self, current_sprint):
        # Update team state after a sprint: accumulation 
        self.technical_debt += self.allocations['New feature'] 
        self.technical_debt += self.allocations['Optimization']   
        new_bugs = self.allocations['New feature'] + self.allocations['Optimization'] - self.allocations['Testing']
        self.bugs += new_bugs

        # Update state: reduction
        self.bugs = max(0, self.bugs - self.allocations['Bug resolution'])
        self.technical_debt = max(0, self.technical_debt - self.allocations['Technical debt'])

        # Handle staffing
        self.update_capacity(current_sprint)

        # Update totals
        self.features_sprint += self.allocations['New feature']
        self.optimizations_sprint += self.allocations['Optimization']
        self.features_round += self.allocations['New feature']
        self.optimizations_round += self.allocations['Optimization']
        self.total_features += self.allocations['New feature']
        self.total_optimizations += self.allocations['Optimization']

    def try_hire_developer(self, count, current_sprint):
        if self.resources >= 3*count:
            for _ in range(count):
                # Create a new developer with default skill
                self.developers.append(Developer(available_from = current_sprint + 2))
                # self.resources -= 3
            print(f"{self.name} hired a new developer!")
        else:
            raise ValueError("Does not have enough resources to hire a new developer!!")

    def to_dict(self):
        return {
            "name": self.name,
            "developers": self.developers,
            "bugs": self.bugs,
            "technical_debt": self.technical_debt,
            "resources": self.resources,
            "satisfaction": self.satisfaction,
            "features_round": self.features_round,
            "optimizations_round": self.optimizations_round,
            "total_features": self.total_features,
            "total_optimizations": self.total_optimizations,
            "allocations": self.allocations,
            "developers": [dev.to_dict() for dev in self.developers]
        }
    
    
    @classmethod 
    def from_dict(cls, data, current_sprint = 0):
        
        team = cls(data["name"])
        team.developers = data["developers"]
        team.bugs = data["bugs"]
        team.technical_debt = data["technical_debt"]
        team.resources = data["resources"]
        team.satisfaction = data["satisfaction"]
        team.features_round = data["features_round"]
        team.optimizations_round = data["optimizations_round"]
        team.total_features = data["total_features"]
        team.total_optimizations = data["total_optimizations"]
        team.allocations = data["allocations"]
        team.developers = [Developer.from_dict(d) for d in data["developers"]]
        team.update_capacity(current_sprint)

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