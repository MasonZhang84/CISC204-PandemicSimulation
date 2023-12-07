import math
import random

from bauhaus import Encoding, proposition, constraint
from bauhaus.utils import count_solutions, likelihood



# These two lines make sure a faster SAT solver is used.
from nnf import config

config.sat_backend = "kissat"

# Encoding that will store all of your constraints
E = Encoding()

"""
The agents list and the universal constants act as ways for the user to change certain properties that the code runs on.
The agents is a list of all the agents in the given simulation. (agents = (Alive,Infected,x-coord,y-coord))
The maxTime controls, how many time steps the problem runs for (# of loops ran).
The planeMaxX controls how many x tiles are in the plane. 
The planeMaxY controls how many y tiles are in the plane. 
The Lethality controls how likely the infection is to kill on the next turn.
"""

agents = [(True, False, 0,0),
          (True, False, 0,0),
          (False, False, 2,2),
          (True, True, 2,2),
          (True, True, 0,1),
          (False, True, 2, 2),
          (True, True, 2, 2)]

# universal constants
maxTime = 10
planeMaxX = 3
planeMaxY = 3
lethality = 2


class Hashable:
    """
    This class is inherited from the prof's example and is used to help print out the code.

    """
    def __hash__(self):
        return hash(str(self))

    def __eq__(self, __value: object) -> bool:
        return hash(self) == hash(__value)

    def __repr__(self):
        return str(self)


#repersents an individal in our simulation
@proposition(E)
class agent_node:
    """
    This class controls each individual character node which has if the agent is alive or infected. This also helps
    with printouts.
    """
    def __init__(self, alive, infected):
        self.infected = infected
        self.alive = alive

    def __repr__(self):
        return f'[alive = {self.alive}, infected = {self.infected}]'


#repersents an individal's time and space
@proposition(E)
class timeAndLocation:
    """
    This class controls each agent with their individual time and space, this class helps with the time steps and move
    ment of agents. This also helps with printouts.
    """
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
    """
    This is currently unused as the infection does not seem to work properly, this was meant to tell the user if the
    population succumbed to the disease or not. This also helps with printouts.
    """
    def __init__(self):
        pass

    def __repr__(self):
        return f'[The population will die]'

#(self, agent, time, x, y) #this works!
def move_agent(agent):
    """
    This function controls the movement of each agent in the given simulation, using the timeAndLocation class defined
    above. This fucntion works assinging a possible x and y value that an agent can move to and moves the agent to that
    x or y as long as it is still inside the plane as defined by the user. (We use math.random to pick which space
    to move next)
    :param agent: An agent in timeAndSpace that has not been moved yet.
    :return: An agent in timeAndSpace that has been moved.
    """

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

def infect(curState):
    """
    This is currently bugged and does not work. (See bug exploration in final write-up for details)

    This function is supposed to go through the currentState and then check if healthy nodes are in the same tile
    as infected ones and then make both be infected.

    :param curState: The current Game state with all nodes inside of it.
    :return: GameState with infected healthy nodes that are supposed to be infected.
    """

    infectZone = []

    for i in curState:
        if i.agent.infected == True:
            if (i.x, i.y) not in infectZone:
                infectZone.append((i.x, i.y))

    if infect:
        for zone in infectZone:
            for i in curState:
                if i.agent.alive == True:
                    if i.x == zone[0] and i.y == zone[1]:
                        i.agent.infected = True



def death(population, t):
    """
    This checks if the final game state is fully dead (or full of infected agents) and prints out if it is. This
    currently does not work as infection does not, but it should work if infection fully worked.
    :param population: Takes in the final game state.
    :param t: a time step in time and space.
    :return:
    """
    for i in range(len(population[-1])):
        if population[-1][i].agent.infected == True:
            if t >= lethality and population[t-lethality][i].agent.infected == True:
                population[-1][i].alive = False
                print("Population is fully dead.")


"""
This next bit of code, puts all the agent nodes into the time and spaces and creates the current game state.
"""
agentsProposition = []
simulationStates = []

currentState = []

for i in agents:
    agentsProposition.append(agent_node(i[0], i[1]))
    currentState.append(timeAndLocation(agent_node(i[0], i[1]), 0, i[2], i[3]))
    

simulationStates.append(currentState)

demise = populationDeath()

# constraints
def test_theory():
    """
    This is our propositions for the problem.
    :return: E which adds constraints on agents.
    """
    #agent cannot be infected and immune
    for agent in agentsProposition:
        # agent cannot be infected and immune at the same time
        # agent_node(alive, infected, immune)
        E.add_constraint(~((agent_node(True, False, True) | agent_node(False, False, True)) &
                           (agent_node(True, True, False) | agent_node(False, True, False))))

    return E

if __name__ == "__main__":
    """
    This is where are main bit of code is located. This code runs until the user specified time and just keeps 
    doing moving all the agents, infecting them and checking if the population has died.
    """
    t = 1

    while t <= maxTime:
        currentState = []

        #move agent and if they share cell, infect everyone in the cell
        for agent in simulationStates[t - 1]:
            currentState.append(move_agent(agent))

        infect(currentState)

        death(simulationStates, t)

        simulationStates.append(currentState)
        # increase time
        t = t + 1

    print("There are", len(simulationStates), "Simulation States!")

    #correct way to print out our final game state
    for i in simulationStates:
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

