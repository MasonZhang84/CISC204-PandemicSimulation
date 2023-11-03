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

# the virtual area we are simulating
simulated_plane = []
for x in range(0, 25):
    simulated_plane.append([])


# universal constants
transmissionProb = 0.1
deadProb = 0.5
moveProb = 0.5
maxSteps = 10000


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
    def __init__(self, alive, infected, immune, plane, x, y):
        self.infected = infected
        self.alive = alive
        self.immune = immune
        self.x = x
        self.y = y
        plane[x + 4 * y].append(self)

    # get status of agent
    def getStatus(self):
        if (self.infected == True):
            if (self.alive == False):
                return '(I)'
        elif (self.alive == True):
            if (self.infected == False):
                return '(A)'
        if (self.alive == False):
            return '(D)'
    # moves the agent
    def agentMove(self, dx, dy, simulated_plane):
        simulated_plane[dx + dy * 5].append(self)
        simulated_plane[self.x + self.y * 5].remove(self)
        self.x = dx
        self.y = dy

    def __repr__(self):
        return f'[alive = {self.alive} infected = {self.infected}, immune = {self.immune}]'

# used to print the individual cel
def printCel(cel):
    print('[', end="")
    for x in range(len(cel)):
        print(cel[x].getStatus(), end="");
    print(']', end="")

# used to print the simulated plane
def printPlane(simulated_plane):
    print('----------------------------')
    for i in range(0, 25, 5):
        printCel(simulated_plane[i])
        printCel(simulated_plane[i + 1])
        printCel(simulated_plane[i + 2])
        printCel(simulated_plane[i + 3])
        printCel(simulated_plane[i + 4])
        print('\n')
    print('----------------------------')

# stores all agents
agents = []
p1 = agent_node(False, False, True, simulated_plane, 0, 0)
p2 = agent_node(False, True, False, simulated_plane, 0, 0)

# add 2 new agents to list
agents.append(p1)
agents.append(p2)

# does not work, will investigate later
# documentation is confusing!
def test_theory():
    # for every cel
    for i in simulated_plane:
        # for every agent of the cell
        for j in agents:
            # every agent must not be both immune and infected
            constraint.add_at_least_one(E, agents, agent_node(True, True, True), agent_node(False, True, True))
            # if an agent is immune, it implies they are not infected
            E.add_constraint(agents.immune >> ~agents.infected)
            # if an agent is not alive, this implies they are not immune
            E.add_constraint(agents.alive >> ~agents.immune)
    return E


if __name__ == "__main__":

    #prints vitual plane
    printPlane(simulated_plane)

    #applie restriction and compile
    T = test_theory()
    T = T.compile()

    # print results
    print("\nSatisfiable: %s" % T.satisfiable())

    print("# Solutions: %d" % count_solutions(T))

    print("   Solution: %s" % T.solve())
