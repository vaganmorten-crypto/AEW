from __future__ import annotations
from dataclasses import dataclass, asdict
from random import Random
from statistics import mean
from typing import Any
from aew.reproduction import ReproductionConfig, offspring_genome

def clamp(x: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, x))

@dataclass
class Genome:
    risk: float
    trade_rate: float
    reproduction_threshold: float
    reproduction_probability: float
    offspring_investment: float
    resource_consumption: float
    mutation_rate: float = 0.08

    @classmethod
    def founder(cls, rng: Random) -> "Genome":
        return cls(
            risk=rng.uniform(.05,.95),
            trade_rate=rng.uniform(.05,.95),
            reproduction_threshold=rng.uniform(130.0,230.0),
            reproduction_probability=rng.uniform(.01,.08),
            offspring_investment=rng.uniform(.12,.35),
            resource_consumption=rng.uniform(.55,1.35),
            mutation_rate=rng.uniform(.03,.12),
        )

    def mutate(self, rng: Random) -> "Genome":
        r=self.mutation_rate
        return Genome(
            risk=clamp(self.risk+rng.gauss(0,r),.01,.99),
            trade_rate=clamp(self.trade_rate+rng.gauss(0,r),.01,.99),
            reproduction_threshold=clamp(self.reproduction_threshold*(1+rng.gauss(0,r)),60.0,400.0),
            reproduction_probability=clamp(self.reproduction_probability*(1+rng.gauss(0,r)),.001,.35),
            offspring_investment=clamp(self.offspring_investment+rng.gauss(0,r*.25),.05,.60),
            resource_consumption=clamp(self.resource_consumption*(1+rng.gauss(0,r*.5)),.25,2.0),
            mutation_rate=clamp(self.mutation_rate+rng.gauss(0,.01),.005,.25),
        )

@dataclass
class Agent:
    id: int
    cash: float
    resource: float
    genome: Genome
    parent: int | None = None
    generation: int = 0
    born: int = 0
    alive: bool = True

    @property
    def risk(self) -> float:
        return self.genome.risk

class World:
    def __init__(self, agents: int = 100, seed: int = 42, group: str = 'A', resource_model: str = 'baseline'):
        if agents < 2: raise ValueError("agents must be >= 2")
        if resource_model not in ("baseline", "scaled", "abundant"):
            raise ValueError("Unknown resource model")
        self.resource_model = resource_model
        self.initial_agents = agents
        self.config=ReproductionConfig(group)
        self.rng=Random(seed); self.seed=seed; self.tick=0; self.next_id=agents; self.price=10.0
        self.population=[Agent(i,100.0,10.0,Genome.founder(self.rng)) for i in range(agents)]
        self.history: list[dict[str,Any]]=[]; self.events: list[dict[str,Any]]=[]
        self._record()

    @property
    def living(self): return [a for a in self.population if a.alive]

    def _event(self, kind: str, **data: Any) -> None:
        self.events.append({"tick":self.tick,"type":kind,**data})
        if len(self.events)>2000: self.events=self.events[-2000:]

    def step(self) -> None:
        living=self.living
        if len(living)<2:
            self.tick+=1; self._record(); return
        capacity = 1000.0 if self.resource_model == 'baseline' else float(self.initial_agents)
        scarcity=max(.2,1.0-len(living)/capacity)
        if self.resource_model == 'abundant':
            scarcity = max(.8, scarcity)
        self.price=max(.5,self.price*(1.0+self.rng.gauss(0,.015)+(1-scarcity)*.002))
        self.rng.shuffle(living)
        for buyer,seller in zip(living[::2],living[1::2]):
            propensity=(buyer.genome.trade_rate+seller.genome.trade_rate)/2
            if self.rng.random()>propensity: continue
            qty=min(seller.resource,max(0.0,buyer.risk*self.rng.random()*2.0)); cost=qty*self.price
            if qty>0 and cost<=buyer.cash:
                buyer.cash-=cost; buyer.resource+=qty; seller.cash+=cost; seller.resource-=qty
                self._event("trade",buyer=buyer.id,seller=seller.id,qty=round(qty,3),price=round(self.price,3))
        for a in living:
            consumption=a.genome.resource_consumption
            a.resource+=self.rng.random()*1.5*scarcity-(.7+.6*a.risk)*consumption
            a.cash-=.08*consumption
            if a.resource<0: a.cash+=a.resource*self.price; a.resource=0.0
            if a.cash<=0.0:
                a.alive=False; self._event("bankruptcy",agent=a.id,generation=a.generation)
        candidates=list(self.living); self.rng.shuffle(candidates)
        for p in candidates:
            g=p.genome
            threshold=g.reproduction_threshold
            resource_threshold=max(2.0,threshold/self.price*.55)
            if p.cash>=threshold and p.resource>=resource_threshold and self.rng.random()<g.reproduction_probability:
                cash_invest=p.cash*g.offspring_investment
                resource_invest=p.resource*g.offspring_investment
                if cash_invest<=0 or resource_invest<=0: continue
                p.cash-=cash_invest; p.resource-=resource_invest
                partners = [p]
                if self.config.mode in ('D', 'E'):
                    pool = [a for a in candidates if a.id != p.id and a.alive]
                    if self.config.mode == 'D' and not pool:
                        continue
                    if pool:
                        partners.append(self.rng.choice(pool))
                child_genome = offspring_genome([a.genome for a in partners], self.rng, self.config)
                child=Agent(self.next_id,cash_invest,resource_invest,child_genome,p.id,p.generation+1,self.tick)
                self.next_id+=1; self.population.append(child)
                self._event("birth",agent=child.id,parent=p.id,generation=child.generation,
                    genes=asdict(child.genome),investment={"cash":round(cash_invest,3),"resource":round(resource_invest,3)})
        self.tick+=1; self._record()

    def run(self,ticks:int)->None:
        if ticks<0: raise ValueError("ticks must be >= 0")
        for _ in range(ticks): self.step()

    def _record(self)->None:
        living=self.living
        self.history.append({"tick":self.tick,"population":len(living),"price":round(self.price,4),
          "mean_cash":round(mean([a.cash for a in living]),4) if living else 0.0,
          "mean_risk":round(mean([a.risk for a in living]),4) if living else 0.0,
          "mean_reproduction_probability":round(mean([a.genome.reproduction_probability for a in living]),5) if living else 0.0})

    def snapshot(self)->dict[str,Any]:
        return {"version":"0.5.0-experimental","group":self.config.mode,"resource_model":self.resource_model,"seed":self.seed,"tick":self.tick,"price":round(self.price,4),
          "agents":[asdict(a) for a in self.population],"history":self.history,"events":self.events}
