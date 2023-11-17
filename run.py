import math
import random

from bauhaus import Encoding, proposition, constraint
from bauhaus.utils import count_solutions, likelihood
from nnf import Var

# These two lines make sure a faster SAT solver is used.
from nnf import config

config.sat_backend = "kissat"

# Encoding that will store all of your constraints
E = Encoding()

agents = [(True, False, False, 0, 0, 0), # alive, not infected, not immune
          (True, True, False, 0, 0, 0), # alive, infected, not dead
          (False, True, False, 0, 0, 0),# not alive, infected, not immune
          (True, False, True, 0, 0, 0)]# alive, not infected, immune

ToF = (True, False)

# universal constants
maxTime = 3
planeMaxX = 2
planeMaxY = 2

class Hashable:
    def __hash__(self):
        return hash(str(self))

    def __eq__(self, __value: object) -> bool:
        return hash(self) == hash(__value)

    def __repr__(self):
        return str(self)


#repersents a individal in our simulation
@proposition(E)
class agent_node(Hashable):
    def __init__(self, alive, infected, immune):
        self.infected = infected
        self.alive = alive
        self.immune = immune

    def __repr__(self):
        return f'[alive = {self.alive}, infected = {self.infected}, immune = {self.immune}\n]'


#repersents an individal's time and space
@proposition(E)
class timeAndLocation(Hashable):
    def __init__(self, agent, time, x, y):
        self.x = x
        self.y = y
        self.time = time
        self.agent = agent

        def __repr__(self):
            return f'[node: {self.agent}\n time: {self.time}, location: ({self.x},{self.y})]'


# this will be true if the population is guaranteed to die
@proposition(E)
class populationDeath(Hashable):
    def __init__(self):
        pass

    def __repr__(self):
        return f'[The population will die]'



#Initalize Proposition
agentsProposition = []

for i in range(len(agents)):
                for alive in ToF:
                    for infected in ToF:
                        for immune in ToF:
                            agentsProposition.append(agent_node(alive, infected, immune))

agentTimeAndSpace = []
for agent in agentsProposition:
    for t in maxTime:
        for x in planeMaxX:
            for y in planeMaxY:
                agentTimeAndSpace.append(timeAndLocation(agent, t, x, y))

demise = populationDeath()

# constraints
def test_theory():
    #agent cannot be infected and immune

    for agent in agentsProposition:
        # agent cannot be infected and immune at the same time
        # agent_node(alive, infected, immune)
        E.add_constraint(~((agent_node(True, False, True)|agent_node(False, False, True))&
                           (agent_node(True, True, False)|agent_node(False, True, False))))

    return E
if __name__ == "__main__":

    #applie restriction and compile
    T = test_theory()
    T = T.compile()

    print("\nSatisfiable: %s" % T.satisfiable())

    print("# Solutions: %d" % count_solutions(T))

    print("   Solution: %s" % T.solve())