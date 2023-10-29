import math
import random

from bauhaus import Encoding, proposition, constraint
from bauhaus.utils import count_solutions, likelihood

# These two lines make sure a faster SAT solver is used.
from nnf import config

config.sat_backend = "kissat"

# Encoding that will store all of your constraints
E = Encoding()

transmissionProb = 0.1
deadProb = 0.5
moveProb = 0.5
maxSteps = 10000


# To create propositions, create classes for them first, annotated with "@proposition" and the Encoding
@proposition(E)
class BasicPropositions:

    def __init__(self, data):
        self.data = data

    def __repr__(self):
        return f"A.{self.data}"


# Different classes for propositions are useful because this allows for more dynamic constraint creation
# for propositions within that class. For example, you can enforce that "at least one" of the propositions
# that are instances of this class must be true by using a @constraint decorator.
# other options include: at most one, exactly one, at most k, and implies all.
# For a complete module reference, see https://bauhaus.readthedocs.io/en/latest/bauhaus.html
@constraint.at_least_one(E)
@proposition(E)
class FancyPropositions:

    def __init__(self, data):
        self.data = data

    def __repr__(self):
        return f"A.{self.data}"


# Call your variables whatever you want
a = BasicPropositions("a")
b = BasicPropositions("b")
c = BasicPropositions("c")
d = BasicPropositions("d")
e = BasicPropositions("e")
# At least one of these will be true
x = FancyPropositions("x")
y = FancyPropositions("y")
z = FancyPropositions("z")


# Build an example full theory for your setting and return it.
#
#  There should be at least 10 variables, and a sufficiently large formula to describe it (>50 operators).
#  This restriction is fairly minimal, and if there is any concern, reach out to the teaching staff to clarify
#  what the expectations are.
def example_theory():
    # Add custom constraints by creating formulas with the variables you created. 
    E.add_constraint((a | b) & ~x)
    # Implication
    E.add_constraint(y >> z)
    # Negate a formula
    E.add_constraint(~(x & y))
    # You can also add more customized "fancy" constraints. Use case: you don't want to enforce "exactly one"
    # for every instance of BasicPropositions, but you want to enforce it for a, b, and c.:
    constraint.add_exactly_one(E, a, b, c)

    return E

class cell:

    def __init__(self):
        self.agentlist = []
        self.x = None
        self.y = None

    def addAgents(self, newAgent):
        self.agentlist.append(newAgent)

    def removeAgents(self, newAgent):
        self.agentlist.remove(newAgent)

    def countInfected(self):
        numInfected = 0
        for i in self.agentlist:
            if i.infected:
                numInfected += 1
        return numInfected

    def countAlive(self):
        for i in self.agentlist:
            numAlive = 0
            if i.alive == True:
                numAlive += 1
        return numAlive

    def countDead(self):
        numDead = 0
        for i in self.agentlist:
            if i.dead == True:
                numDead += 1
        return numDead

    def transmission(self):
        numInfected = self.countInfected()
        numAlive = self.countAlive()

        if (numInfected != 0 and numAlive != 0):
            for x in self.agentlist:
                if x.alive == True and x.Infected == False:
                    if (random.random() <= transmissionProb):
                        x.Infected = True
                        
    def dead(self):
        numInfected = self.countInfected()
        numAlive = self.countAlive()

        if (numInfected != 0 and numAlive != 0):
            for x in self.agentlist:
                if x.alive == True and x.Infected == True:
                    if (random.random() <= deadProb):
                        x.dead = True

    def __str__(self):
        return self.agentlist.__str__()

class agent:
    def __init__(self, name, infected, alive, immune):
        self.name = name
        self.infected = infected
        self.alive = alive
        self.immune = immune

    def __str__(self):
        return self.name

    def __repr__(self):
        return self.name


class plane:
    def __init__(self, cells):
        cellSquare = int(math.sqrt(len(cells)))
        tempPlaneArray = [[0] * cellSquare for _ in range(cellSquare)]

        counter = 0
        for i in range(0, len(tempPlaneArray)):
            for j in range(0, len(tempPlaneArray[0])):
                tempPlaneArray[i][j] = cells[counter]
                tempPlaneArray[i][j].x = i
                tempPlaneArray[i][j].y = j
                counter += 1
        self.planeArray = tempPlaneArray

    def __str__(self):
        arr = [[0] * len(self.planeArray[0]) for _ in range(len(self.planeArray))]
        for i in range(len(self.planeArray)):
            for j in range(len(self.planeArray[0])):
                arr[i][j] = self.planeArray[i][j].countInfected()

        return arr.__str__()

    def move(self, cell):
        moveTable = {
            0: [-1, 1],
            1: [0, 1],
            2: [1, 1],
            3: [1, 0],
            4: [1, -1],
            5: [0, -1],
            6: [-1, -1],
            7: [-1, 0]
        }

        numAlive = cell.countAlive()
        numDead = cell.countDead()

        if (numAlive > 0):
            for x in self.agentlist:
                if x.dead != True:
                    if (random.random() <= moveProb):

                        x = self.x
                        y = self.y

                        moveTable[moveTo][0] += x
                        moveTable[moveTo][1] += y

                        while (x >= 0 and x <= 2 and y >= 0 and y <= 2):
                            moveTo = random.randint(0, 7)

                            x = self.x
                            y = self.y

                            moveTable[moveTo][0] += x
                            moveTable[moveTo][1] += y

                        cell.removeAgents(x)
                        plane[x][y].addAgents(x)

if __name__ == "__main__":
    c1 = cell()
    a1 = agent("bob", True, True, False)
    a2 = agent("sally", True, True, False)
    print(a1.infected)

    c1.addAgents(a1)
    c1.addAgents(a2)


    print(c1)

    c2 = cell()
    c3 = cell()
    c4 = cell()

    cellArray = [c1, c2, c3, c4]

    p1 = plane(cellArray)
    print(p1.planeArray[1][0].x)

    print("hello world")

    # T = example_theory()
    # Don't compile until you're finished adding all your constraints!
    # T = T.compile()
    # After compilation (and only after), you can check some of the properties
    # of your model:
    # print("\nSatisfiable: %s" % T.satisfiable())
    # print("# Solutions: %d" % count_solutions(T))
    # print("   Solution: %s" % T.solve())


# print("\nVariable likelihoods:")
# for v,vn in zip([a,b,c,x,y,z], 'abcxyz'):
# Ensure that you only send these functions NNF formulas
# Literals are compiled to NNF here
# print(" %s: %.2f" % (vn, likelihood(T, v)))
# print()

