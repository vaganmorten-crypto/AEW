from __future__ import annotations

from dataclasses import dataclass, field, asdict
import random
from typing import Dict, List, Optional

ASSETS = ("food", "energy", "ore", "data", "credits")


@dataclass
class Strategy:
    risk: float
    trade_rate: float
    mutation_rate: float = 0.08

    def mutate(self, rng: random.Random) -> "Strategy":
        def m(x: float) -> float:
            return max(0.01, min(0.99, x + rng.gauss(0, self.mutation_rate)))
        return Strategy(m(self.risk), m(self.trade_rate), self.mutation_rate)


@dataclass
class Agent:
    id: int
    parent_id: Optional[int]
    generation: int
    inventory: Dict[str, float]
    strategy: Strategy
    age: int = 0
    alive: bool = True

    @property
    def wealth(self) -> float:
        return sum(max(0.0, v) for v in self.inventory.values())


@dataclass
class World:
    seed: int = 42
    agents: List[Agent] = field(default_factory=list)
    tick: int = 0
    next_id: int = 0

    def __post_init__(self):
        self.rng = random.Random(self.seed)

    def spawn(self, parent: Optional[Agent] = None) -> Agent:
        if parent is None:
            inv = {a: self.rng.uniform(5, 15) for a in ASSETS}
            strat = Strategy(self.rng.random(), self.rng.random())
            generation, parent_id = 0, None
        else:
            inv = {a: max(0.0, parent.inventory[a] * 0.35) for a in ASSETS}
            for a in ASSETS:
                parent.inventory[a] *= 0.65
            strat = parent.strategy.mutate(self.rng)
            generation, parent_id = parent.generation + 1, parent.id
        agent = Agent(self.next_id, parent_id, generation, inv, strat)
        self.next_id += 1
        self.agents.append(agent)
        return agent

    def initialize(self, n: int):
        for _ in range(n):
            self.spawn()

    def step(self):
        living = [a for a in self.agents if a.alive]
        self.rng.shuffle(living)

        # Metabolic scarcity: all agents consume food and energy.
        for a in living:
            a.age += 1
            a.inventory["food"] -= 0.08
            a.inventory["energy"] -= 0.05

        # Closed-world bilateral exchange. No external prices or accounts.
        for a, b in zip(living[::2], living[1::2]):
            if self.rng.random() < (a.strategy.trade_rate + b.strategy.trade_rate) / 2:
                give, take = self.rng.sample(ASSETS[:-1], 2)
                qty = min(0.25 + self.rng.random(), max(0.0, a.inventory[give]))
                if qty > 0 and b.inventory[take] > 0:
                    counter = min(qty, b.inventory[take])
                    a.inventory[give] -= qty
                    b.inventory[give] += qty
                    b.inventory[take] -= counter
                    a.inventory[take] += counter

        # Virtual production with finite stochastic opportunities.
        for a in living:
            if self.rng.random() < 0.35:
                asset = self.rng.choice(ASSETS[:-1])
                a.inventory[asset] += self.rng.uniform(0.0, 0.5)

        # Bankruptcy/death and reproduction.
        newborns = []
        for a in living:
            if a.inventory["food"] <= 0 or a.inventory["energy"] <= 0 or a.wealth <= 0:
                a.alive = False
            elif a.wealth > 45 and a.age > 20 and self.rng.random() < 0.03:
                newborns.append(a)
        for parent in newborns:
            self.spawn(parent)

        self.tick += 1

    def run(self, ticks: int):
        for _ in range(ticks):
            self.step()

    def snapshot(self) -> dict:
        living = [a for a in self.agents if a.alive]
        return {
            "version": "0.2.1",
            "seed": self.seed,
            "tick": self.tick,
            "population": len(living),
            "total_agents_ever": len(self.agents),
            "agents": [asdict(a) for a in self.agents],
        }
