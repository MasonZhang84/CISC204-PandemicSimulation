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

agents = [(True, False,0,0),
          (True, False, 0,0),
          (False, False, 2,2),
          (True, True, 3,3),
          (True, True, 0,1),
          (False, True, 2, 2),
          (True, True, 3, 3)]


ToF = (True, False)

# universal constants
maxTime = 200
planeMaxX = 3
planeMaxY = 3
lethality = 2

class Hashable:
    def __hash__(self):
        return hash(str(self))

    def __eq__(self, __value: object) -> bool:
        return hash(self) == hash(__value)

    def __repr__(self):
        return str(self)


#repersents a individal in our simulation
@proposition(E)
class agent_node:
    def __init__(self, alive, infected):
        self.infected = infected
        self.alive = alive

    def __repr__(self):
        return f'[alive = {self.alive}, infected = {self.infected}]'


#repersents an individal's time and space
@proposition(E)
class timeAndLocation:
    def __init__(self, agent, time, x, y):
        self.x = x
        self.y = y
        self.time = time
        self.agent = agent

    def __repr__(self):
        return f'[node = {self.agent}, time: {self.time}, location: ({self.x},{self.y})]'


# this will be true if the population is guaranteed to die
@proposition(E)
class populationDeath:
    def __init__(self):
        pass

    def __repr__(self):
        return f'[The population will die]'

#(self, agent, time, x, y)
def move_agent(agent):

    temp = timeAndLocation(agent.agent, agent.time, agent.x, agent.y)

    # If person is dead, they cannot move
    if agent.agent.alive == False:
        temp.time = temp.time + 1
        return temp

    # Define possible movements: up, down, left, right
    movements = [(0, 1), (0, -1), (-1, 0), (1, 0)]

    while True:
        # Randomly choose a movement
        dx, dy = random.choice(movements)

        # Calculate new position
        new_x = temp.x + dx
        new_y = temp.y + dy

        # If new position is out of bounds, choose another movement
        if new_x < 0 or new_x > planeMaxX or new_y < 0 or new_y > planeMaxY:
            continue

        # Update agent's position
        temp.x = new_x
        temp.y = new_y
        temp.time = temp.time + 1

        return temp

def infect(agents):
    infect = False

    infectZone = []

    for i in agents:
        if i.agent.infected == True:
            infect = True
            if (i.x, i.y) not in infectZone:
                infectZone.append((i.x, i.y))

    if infect:
        for zone in infectZone:
            for i in agents:
                if i.agent.alive == True:
                    if i.x == zone[0] and i.y == zone[1]:
                        i.agent.infected = True

def death(population, t):
    for i in range(len(population[-1])):
        if population[-1][i].agent.infected == True:
            if t >= lethality and population[t-lethality][i].agent.infected == True:
                population[-1][i].alive = False


print("tyest")

#Initalize Proposition
agentsProposition = []
simulatuionStates = []

currentState = []

for i in agents:
    agentsProposition.append(agent_node(i[0],i[1]))
    currentState.append(timeAndLocation(agent_node(i[0],i[1]),0,i[2], i[3]))

simulatuionStates.append(currentState)

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

    t = 1

    while t <= maxTime:
        currentState = []

        infect(currentState)

        #move agent
        for agent in simulatuionStates[t-1]:
            currentState.append(move_agent(agent))

        # if they share cell, infect everyone in the cell

        death(simulatuionStates, t)

        simulatuionStates.append(currentState)
        # increase time
        t = t + 1



    print(len(simulatuionStates))
    for i in simulatuionStates:
        print("--------------------------------------")
        for j in i:
            print(j)

    #applie restriction and compile
    #T = test_theory()
    #T = T.compile()

    #print("\nSatisfiable: %s" % T.satisfiable())

    #print("# Solutions: %d" % count_solutions(T))

    #print("   Solution: %s" % T.solve())

    # Call the function with your simulation states

