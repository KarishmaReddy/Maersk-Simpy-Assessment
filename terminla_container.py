# Simulating a container terminal using SimPy
import simpy
import random

class ContainerTerminal:
    def __init__(self, env):
        self.env = env
        self.berths = [simpy.Resource(env, capacity=1) for _ in range(2)]
        self.trucks = simpy.Resource(env, capacity=3)
        self.quay_cranes = [simpy.Resource(env, capacity=1) for _ in range(2)]

    def discharge_vessel(self, vessel):
        # Berth at the terminal
        with self.berths[vessel.berth].request() as req:
            print(f"{self.env.now}: Vessel {vessel.name} berths at berth_{vessel.berth}")

            # Unload containers
            while vessel.containers > 0:
                yield self.env.timeout(3)
                with self.quay_cranes[vessel.berth].request() as crane_req:
                    yield crane_req
                    yield self.trucks.request()
                    print(f"{self.env.now}: Quay crane {vessel.berth} moves a container from vessel {vessel.name}")

                    # Transport container to yard block
                    yield self.env.timeout(6)
                    print(f"{self.env.now}: Truck transports container from quay crane {vessel.berth} to yard block")
                    vessel.containers -= 1

            print(f"{self.env.now}: Vessel {vessel.name} leaves berth_{vessel.berth}")
            self.trucks.release()  # Release the truck

class Vessel:
    def __init__(self, name, containers, berth):
        self.name = name
        self.containers = containers
        self.berth = berth

def vessel_generator(env, terminal):
    vessel_id = 1
    while True:
        yield env.timeout(random.expovariate(1 / 5))
        berth = None
        for i in range(len(terminal.berths)):
            if terminal.berths[i].count == 0:
                berth = i
                break
        if berth is not None:
            vessel = Vessel(f"V{vessel_id}", 150, berth)
            print(f"{env.now}: Vessel {vessel.name} arrives at the terminal")
            env.process(terminal.discharge_vessel(vessel))
            vessel_id += 1

def run_simulation(simulation_time):
    env = simpy.Environment()
    terminal = ContainerTerminal(env)
    env.process(vessel_generator(env, terminal))
    env.run(until=simulation_time)

# Running simulation for one day (1440 minutes)
run_simulation(1440)
