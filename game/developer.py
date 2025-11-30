class Developer:

    def __init__(self, skill = 3, available_from = 0):
        
        self.skill = skill
        self.available_from = available_from # when the developer becomes available

    def to_dict(self):
        return {
            "skill": self.skill,
            "available_from": self.available_from
        }
    
    @classmethod
    def from_dict(cls, data):
        return cls(skill_level=data["skill_level"], available_from=data["available_from"])