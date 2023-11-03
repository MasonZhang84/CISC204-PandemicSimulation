from bauhaus import Encoding, proposition, constraint
from bauhaus.utils import count_solutions, likelihood
from nnf import Var
E = Encoding()

class Hashable:
    def __hash__(self):
        return hash(str(self))

    def __eq__(self, __value: object) -> bool:
        return hash(self) == hash(__value)

    def __repr__(self):
        return str(self)

@proposition(E)
class test(Hashable):
    def __init__(self, alive, dead) -> None:
        self.alive = alive
        self.dead = dead

    def __repr__(self):
        return f'[alive = {self.alive} dead = {self.dead}]'



# build a constant object, like a set of rules
def test_theory():

    agents = []

    a = [True, True, False, False]
    d = [True, False, True, False]

    for x in range(len(a)):
        agents.append(test(a[x], d[x]))

    print(agents[0])
    print(agents[1])
    print(agents[2])
    print(agents[3])

    # obj in list cannot be dead and alive at the same time
    for i in range(len(a)):
        a,b = Var(agents[i].alive), Var(agents[i].dead)

        E.add_constraint( ((a & b) | (~a & ~b)))

    # once constants are inplace we have to return the constants
    return E


if __name__ == "__main__":
    T = test_theory()
    T = T.compile()

    print("\nSatisfiable: %s" % T.satisfiable())

    print("# Solutions: %d" % count_solutions(T))

    print("   Solution: %s" % T.solve())