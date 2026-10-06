from __future__ import annotations
from dataclasses import dataclass, asdict, field
from random import Random
from collections import deque
from statistics import mean
from typing import Iterable, Sequence
import math

def clamp(x, lo, hi): return max(lo, min(hi, x))

@dataclass
class GenomeV2:
    risk: float; trade_rate: float; reproduction_threshold: float
    reproduction_probability: float; offspring_investment: float
    resource_consumption: float; mutation_rate: float
    learning_rate: float; memory_span: int; planning_horizon: int
    exploration: float; information_budget: float; complexity_budget: int
    signal_weights: list[float] = field(default_factory=list)
    hidden_weights: list[float] = field(default_factory=list)

    @classmethod
    def founder(cls, rng: Random, signals: int = 8) -> "GenomeV2":
        nodes=rng.randint(4,12)
        return cls(rng.uniform(.05,.95),rng.uniform(.05,.95),rng.uniform(130,230),
          rng.uniform(.01,.08),rng.uniform(.12,.35),rng.uniform(.55,1.35),rng.uniform(.03,.12),
          rng.uniform(.01,.25),rng.randint(4,64),rng.randint(1,8),rng.uniform(.02,.35),
          rng.uniform(.05,.8),nodes,[rng.gauss(0,.5) for _ in range(signals)],
          [rng.gauss(0,.4) for _ in range(nodes)])

    def mutate(self, rng: Random) -> "GenomeV2":
        r=self.mutation_rate
        sw=[clamp(w+rng.gauss(0,r),-3,3) for w in self.signal_weights]
        hw=[clamp(w+rng.gauss(0,r),-3,3) for w in self.hidden_weights]
        # structural mutation: cognition may grow or shrink; complexity has a metabolic cost.
        if rng.random()<r and len(hw)<128: hw.insert(rng.randrange(len(hw)+1),rng.gauss(0,.4))
        if rng.random()<r*.5 and len(hw)>2: hw.pop(rng.randrange(len(hw)))
        return GenomeV2(clamp(self.risk+rng.gauss(0,r),.01,.99),
          clamp(self.trade_rate+rng.gauss(0,r),.01,.99),
          clamp(self.reproduction_threshold*(1+rng.gauss(0,r)),60,600),
          clamp(self.reproduction_probability*(1+rng.gauss(0,r)),.001,.35),
          clamp(self.offspring_investment+rng.gauss(0,r*.25),.05,.6),
          clamp(self.resource_consumption*(1+rng.gauss(0,r*.5)),.25,2),
          clamp(r+rng.gauss(0,.01),.005,.25),clamp(self.learning_rate+rng.gauss(0,r*.2),.001,.5),
          max(2,min(256,self.memory_span+rng.randint(-3,3))),
          max(1,min(32,self.planning_horizon+rng.choice([-1,0,0,1]))),
          clamp(self.exploration+rng.gauss(0,r*.2),.001,.8),
          clamp(self.information_budget+rng.gauss(0,r*.2),.01,1),
          len(hw),sw,hw)

@dataclass(frozen=True)
class MarketFrame:
    # Read-only observation. No broker credentials/order endpoint exists in this interface.
    values: tuple[float,...]
    source: str = "synthetic"

class MarketDataFeed:
    def __init__(self, frames: Iterable[Sequence[float]], source="external-read-only"):
        self._frames=tuple(MarketFrame(tuple(map(float,x)),source) for x in frames)
        if not self._frames: raise ValueError("market feed cannot be empty")
    def at(self,tick:int)->MarketFrame: return self._frames[tick % len(self._frames)]

@dataclass
class CognitiveAgent:
    id:int; cash:float; resource:float; genome:GenomeV2
    parent:int|None=None; generation:int=0; born:int=0; alive:bool=True
    memory:deque=field(default_factory=deque); prediction_error:float=0.0
    last_score:float=0.0

    def observe(self, frame:MarketFrame):
        n=max(1,int(len(frame.values)*self.genome.information_budget))
        obs=frame.values[:n]
        self.memory.append(obs)
        while len(self.memory)>self.genome.memory_span: self.memory.popleft()
        return obs

    def decide(self, frame:MarketFrame, rng:Random)->float:
        obs=self.observe(frame)
        weights=self.genome.signal_weights[:len(obs)]
        score=sum(x*w for x,w in zip(obs,weights))/max(1,len(weights))
        if self.memory:
            trend=sum(sum(x) for x in self.memory)/max(1,sum(len(x) for x in self.memory))
            score += math.tanh(trend)*mean(self.genome.hidden_weights or [0])
        score += rng.gauss(0,self.genome.exploration)
        self.last_score=math.tanh(score)
        return self.last_score

    def learn(self, reward:float, obs:Sequence[float]):
        err=reward-self.last_score; self.prediction_error=err
        lr=self.genome.learning_rate
        for i,x in enumerate(obs[:len(self.genome.signal_weights)]):
            self.genome.signal_weights[i]=clamp(self.genome.signal_weights[i]+lr*err*x*.01,-3,3)

class CognitiveWorld:
    def __init__(self, agents=1000, seed=42, feed:MarketDataFeed|None=None, capacity=None):
        if agents<2: raise ValueError("agents must be >= 2")
        self.rng=Random(seed); self.seed=seed; self.tick=0; self.next_id=agents
        self.capacity=capacity or max(agents*2,2000); self.price=10.0
        if feed is None:
            frames=[]; x=0.0
            for _ in range(4096):
                x=.92*x+self.rng.gauss(0,.12); frames.append((x,abs(x),math.sin(x),math.cos(x),x*x,1.0,0.0,-x))
            feed=MarketDataFeed(frames,"synthetic")
        self.feed=feed
        self.population=[CognitiveAgent(i,100,10,GenomeV2.founder(self.rng)) for i in range(agents)]
        self.history=[]; self.events=[]; self._record()

    @property
    def living(self): return [a for a in self.population if a.alive]

    def step(self):
        living=self.living
        if not living: self.tick+=1; self._record(); return
        frame=self.feed.at(self.tick)
        market_signal=frame.values[0] if frame.values else 0.0
        self.price=max(.5,self.price*math.exp(clamp(market_signal,-.08,.08)*.02+self.rng.gauss(0,.004)))
        for a in living:
            before=a.cash+a.resource*self.price
            score=a.decide(frame,self.rng)
            # Virtual-only position adjustment; never sends an external order.
            qty=clamp(score*a.genome.risk*1.5,-a.resource,a.cash/self.price)
            a.cash-=qty*self.price; a.resource+=qty
            cognition_cost=.002*(len(a.genome.hidden_weights)+a.genome.memory_span/16+a.genome.planning_horizon)
            a.cash-=.05*a.genome.resource_consumption+cognition_cost
            after=a.cash+a.resource*self.price
            a.learn((after-before)/max(1,abs(before)),frame.values)
            if a.cash<=0: a.alive=False; self.events.append({"tick":self.tick,"type":"bankruptcy","agent":a.id})
        slots=max(0,self.capacity-len(self.living))
        candidates=list(self.living); self.rng.shuffle(candidates)
        for p in candidates[:slots]:
            g=p.genome
            if p.cash>=g.reproduction_threshold and p.resource>=2 and self.rng.random()<g.reproduction_probability:
                ci=p.cash*g.offspring_investment; ri=p.resource*g.offspring_investment
                p.cash-=ci; p.resource-=ri
                child=CognitiveAgent(self.next_id,ci,ri,g.mutate(self.rng),p.id,p.generation+1,self.tick)
                self.next_id+=1; self.population.append(child)
                self.events.append({"tick":self.tick,"type":"birth","agent":child.id,"parent":p.id,"generation":child.generation})
        self.tick+=1; self._record()

    def run(self,ticks):
        for _ in range(ticks): self.step()

    def _record(self):
        living=self.living
        self.history.append({"tick":self.tick,"population":len(living),
          "max_generation":max((a.generation for a in living),default=0),
          "mean_complexity":round(mean([len(a.genome.hidden_weights) for a in living]),3) if living else 0,
          "mean_memory":round(mean([a.genome.memory_span for a in living]),3) if living else 0,
          "mean_prediction_error":round(mean([abs(a.prediction_error) for a in living]),6) if living else 0})

    def inspect(self, agent_id:int):
        a=next(a for a in self.population if a.id==agent_id)
        return {"id":a.id,"alive":a.alive,"generation":a.generation,"parent":a.parent,
          "cash":a.cash,"resource":a.resource,"genome":asdict(a.genome),
          "cognition":{"memory_items":len(a.memory),"last_score":a.last_score,
          "prediction_error":a.prediction_error,"architecture_nodes":len(a.genome.hidden_weights)}}

    def snapshot(self):
        return {"version":"0.4.0-dev","seed":self.seed,"tick":self.tick,"market_source":self.feed.at(0).source,
          "safety":{"external_orders":False,"market_input":"read-only"},
          "history":self.history,"events":self.events,
          "agents":[self.inspect(a.id) for a in self.population]}
