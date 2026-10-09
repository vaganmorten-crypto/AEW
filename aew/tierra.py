"""Bounded Tierra-inspired artificial-life prototype for AEW."""
from dataclasses import dataclass
import random

HARVEST, REPRODUCE, JUMP, WAIT = range(4)

@dataclass
class Organism:
    oid: int
    genome: tuple
    energy: int = 10
    pc: int = 0
    parent: int | None = None

class TierraWorld:
    def __init__(self, seed=0, capacity=1000, mutation_rate=0.01):
        self.rng = random.Random(seed)
        self.capacity = capacity
        self.mutation_rate = mutation_rate
        self.population = {}
        self.events = []
        self.tick = 0
        self.next_id = 0

    def add(self, genome=(HARVEST, REPRODUCE, JUMP), energy=10, parent=None):
        if not genome or any(op not in range(4) for op in genome):
            raise ValueError("invalid genome")
        if len(self.population) >= self.capacity:
            return None
        oid = self.next_id
        self.next_id += 1
        self.population[oid] = Organism(oid, tuple(genome), energy, parent=parent)
        return oid

    def step(self):
        self.tick += 1
        ids = list(self.population)
        self.rng.shuffle(ids)
        for oid in ids:
            agent = self.population.get(oid)
            if agent is None:
                continue
            op = agent.genome[agent.pc]
            agent.pc = (agent.pc + 1) % len(agent.genome)
            agent.energy -= 1
            if op == HARVEST and (self.tick // 100) % 2 == 0:
                agent.energy += 4
            elif op == JUMP:
                agent.pc = 0
            elif op == REPRODUCE and agent.energy >= 6:
                genome = list(agent.genome)
                if self.rng.random() < self.mutation_rate:
                    genome[self.rng.randrange(len(genome))] = self.rng.randrange(4)
                child = self.add(genome, energy=4, parent=oid)
                if child is not None:
                    agent.energy -= 4
                    self.events.append({"tick": self.tick, "type": "birth", "parent": oid, "child": child})
            if agent.energy <= 0:
                del self.population[oid]
                self.events.append({"tick": self.tick, "type": "death", "agent": oid})
        return len(self.population)

    def run(self, ticks):
        if ticks < 0:
            raise ValueError("ticks must be nonnegative")
        return [self.step() for _ in range(ticks)]
