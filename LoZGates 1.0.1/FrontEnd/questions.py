from BackEnd.problems_bank import Problems

class questions:
    def __init__(self):
        self.problems = Problems()
    
    def get_problem(self, index):
        return self.problems.get_problem(index)
    
    