from __future__ import annotations
from dataclasses import dataclass, asdict
from random import Random
from statistics import mean
from typing import Any

@dataclass
class Agent:
    id: int
    cash: float
    resource: float
    risk: float
    parent: int | None = None
    generation: int = 0
    alive: bool = True

class World:
    def __init__(self, agents: int = 100, seed: int = 42):
        if agents < 2: raise ValueError("agents must be >= 2")
        self.rng=Random(seed); self.seed=seed; self.tick=0; self.next_id=agents; self.price=10.0
        self.population=[Agent(i,100.0,10.0,self.rng.uniform(.05,.95)) for i in range(agents)]
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
        scarcity=max(.2,1.0-len(living)/1000.0)
        self.price=max(.5,self.price*(1.0+self.rng.gauss(0,.015)+(1-scarcity)*.002))
        self.rng.shuffle(living)
        for buyer,seller in zip(living[::2],living[1::2]):
            qty=min(seller.resource,max(0.0,buyer.risk*self.rng.random()*2.0)); cost=qty*self.price
            if qty>0 and cost<=buyer.cash:
                buyer.cash-=cost; buyer.resource+=qty; seller.cash+=cost; seller.resource-=qty
                self._event("trade",buyer=buyer.id,seller=seller.id,qty=round(qty,3),price=round(self.price,3))
        for a in living:
            a.resource+=self.rng.random()*1.5*scarcity-(.7+.6*a.risk); a.cash-=.08
            if a.resource<0: a.cash+=a.resource*self.price; a.resource=0.0
            if a.cash<=0.0:
                a.alive=False; self._event("bankruptcy",agent=a.id,generation=a.generation)
        parents=[a for a in self.living if a.cash>180 and a.resource>12]
        for p in parents[:max(0,200-len(self.living))]:
            if self.rng.random()<.03:
                p.cash-=40; p.resource-=3
                risk=min(1,max(0,p.risk+self.rng.gauss(0,.05)))
                child=Agent(self.next_id,40.0,3.0,risk,p.id,p.generation+1)
                self.next_id+=1; self.population.append(child)
                self._event("birth",agent=child.id,parent=p.id,generation=child.generation,risk=round(risk,3))
        self.tick+=1; self._record()

    def run(self,ticks:int)->None:
        if ticks<0: raise ValueError("ticks must be >= 0")
        for _ in range(ticks): self.step()

    def _record(self)->None:
        living=self.living
        self.history.append({"tick":self.tick,"population":len(living),"price":round(self.price,4),
          "mean_cash":round(mean([a.cash for a in living]),4) if living else 0.0,
          "mean_risk":round(mean([a.risk for a in living]),4) if living else 0.0})

    def snapshot(self)->dict[str,Any]:
        return {"version":"0.3.0","seed":self.seed,"tick":self.tick,"price":round(self.price,4),
          "agents":[asdict(a) for a in self.population],"history":self.history,"events":self.events}
