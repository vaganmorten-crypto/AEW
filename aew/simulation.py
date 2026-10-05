from __future__ import annotations
from dataclasses import dataclass, asdict, fields
from random import Random
from statistics import mean
from typing import Any

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
    partner_count: int = 1
    offspring_count: int = 1
    partner_selectivity: float = 0.5
    gene_mix_bias: float = 0.5

    @classmethod
    def founder(cls, rng: Random) -> "Genome":
        return cls(rng.uniform(.05,.95), rng.uniform(.05,.95), rng.uniform(105,175),
                   rng.uniform(.015,.09), rng.uniform(.12,.32), rng.uniform(.45,1.05),
                   rng.uniform(.03,.12), rng.randint(1,4), rng.randint(1,3),
                   rng.uniform(0,1), rng.uniform(.15,.85))

    def mutate(self, rng: Random) -> "Genome":
        r=self.mutation_rate
        return Genome(
            clamp(self.risk+rng.gauss(0,r),.01,.99),
            clamp(self.trade_rate+rng.gauss(0,r),.01,.99),
            clamp(self.reproduction_threshold*(1+rng.gauss(0,r)),55,350),
            clamp(self.reproduction_probability*(1+rng.gauss(0,r)),.001,.40),
            clamp(self.offspring_investment+rng.gauss(0,r*.25),.05,.55),
            clamp(self.resource_consumption*(1+rng.gauss(0,r*.5)),.20,1.8),
            clamp(self.mutation_rate+rng.gauss(0,.01),.005,.25),
            max(1,min(6,self.partner_count+(rng.choice([-1,0,1]) if rng.random()<r else 0))),
            max(1,min(5,self.offspring_count+(rng.choice([-1,0,1]) if rng.random()<r else 0))),
            clamp(self.partner_selectivity+rng.gauss(0,r*.4),0,1),
            clamp(self.gene_mix_bias+rng.gauss(0,r*.4),.05,.95))

@dataclass
class Agent:
    id:int; cash:float; resource:float; genome:Genome
    parent:int|None=None; generation:int=0; born:int=0; alive:bool=True
    children:int=0; trades:int=0; volume:float=0.0; death_tick:int|None=None
    @property
    def risk(self)->float: return self.genome.risk

class World:
    def __init__(self, agents:int=100, seed:int=42, max_population:int=300):
        if agents<2: raise ValueError("agents must be >= 2")
        self.rng=Random(seed); self.seed=seed; self.tick=0; self.next_id=agents
        self.price=10.; self.max_population=max_population
        self.population=[Agent(i,125.,14.,Genome.founder(self.rng)) for i in range(agents)]
        self.history=[]; self.events=[]; self.births=0; self.deaths=0; self._record()

    @property
    def living(self): return [a for a in self.population if a.alive]
    @property
    def max_generation(self): return max((a.generation for a in self.population),default=0)

    def _event(self,kind:str,**data:Any):
        self.events.append({"tick":self.tick,"type":kind,**data})
        if len(self.events)>5000:self.events=self.events[-5000:]

    def _die(self,a:Agent):
        if a.alive:
            a.alive=False;a.death_tick=self.tick;self.deaths+=1
            self._event("bankruptcy",agent=a.id,generation=a.generation)

    def step(self):
        living=self.living
        if not living:
            self.tick+=1;self._record();return
        scarcity=max(.30,1-len(living)/1200)
        self.price=max(.5,self.price*(1+self.rng.gauss(0,.012)+(1-scarcity)*.0015))
        self.rng.shuffle(living)
        for buyer,seller in zip(living[::2],living[1::2]):
            if self.rng.random()>(buyer.genome.trade_rate+seller.genome.trade_rate)/2:continue
            qty=min(seller.resource,max(0,buyer.risk*self.rng.random()*1.6));cost=qty*self.price
            if qty>0 and cost<=buyer.cash:
                buyer.cash-=cost;buyer.resource+=qty;seller.cash+=cost;seller.resource-=qty
                buyer.trades+=1;seller.trades+=1;buyer.volume+=cost;seller.volume+=cost
                self._event("trade",buyer=buyer.id,seller=seller.id,qty=round(qty,3),price=round(self.price,3))
        for a in list(self.living):
            c=a.genome.resource_consumption
            # renewable resource inflow keeps reproduction possible but remains genetically costly
            a.resource+=self.rng.random()*2.25*scarcity-(.45+.45*a.risk)*c
            a.cash-=.035*c
            if a.resource<0:a.cash+=a.resource*self.price;a.resource=0.
            if a.cash<=0:self._die(a)
        capacity=max(0,self.max_population-len(self.living))
        candidates=list(self.living);self.rng.shuffle(candidates)
        for initiator in candidates:
            if capacity<=0:break
            g=initiator.genome
            if self.rng.random()>=g.reproduction_probability:continue
            wanted=max(1,min(g.partner_count,len(self.living)))
            pool=[x for x in self.living if x.id!=initiator.id]
            self.rng.shuffle(pool)
            # Selectivity is genetic: high values favor resource-rich partners; low values retain randomness.
            pool.sort(key=lambda x:g.partner_selectivity*(x.cash+x.resource*self.price)+
                      (1-g.partner_selectivity)*self.rng.random()*200,reverse=True)
            parents=[initiator]+pool[:wanted-1]
            if len(parents)<wanted:continue
            if any(x.cash<g.reproduction_threshold/wanted for x in parents):continue
            n=min(g.offspring_count,capacity)
            cash_parts=[x.cash*g.offspring_investment for x in parents]
            res_parts=[x.resource*g.offspring_investment for x in parents]
            cash_pool=sum(cash_parts);res_pool=sum(res_parts)
            if cash_pool/n<5 or res_pool/n<1:continue
            for x,ci,ri in zip(parents,cash_parts,res_parts):
                x.cash-=ci;x.resource-=ri
            for _ in range(n):
                child_genome=Genome.recombine([x.genome for x in parents],self.rng,g.gene_mix_bias)
                child=Agent(self.next_id,cash_pool/n,res_pool/n,child_genome,initiator.id,
                            max(x.generation for x in parents)+1,self.tick)
                for x in parents:x.children+=1
                self.next_id+=1;self.population.append(child);self.births+=1;capacity-=1
                self._event("birth",agent=child.id,parent=initiator.id,
                    parents=[x.id for x in parents],generation=child.generation,
                    mode=("clone" if wanted==1 else f"{wanted}-parent"),
                    genes=asdict(child.genome),
                    investment={"cash":round(cash_pool/n,3),"resource":round(res_pool/n,3)})
        self.tick+=1;self._record()

    def run(self,ticks:int):
        if ticks<0:raise ValueError("ticks must be >= 0")
        for _ in range(ticks):self.step()

    def _record(self):
        L=self.living
        self.history.append({"tick":self.tick,"population":len(L),"price":round(self.price,4),
          "births":self.births,"deaths":self.deaths,"max_generation":self.max_generation,
          "mean_cash":round(mean([a.cash for a in L]),4) if L else 0.,
          "mean_risk":round(mean([a.risk for a in L]),4) if L else 0.,
          "mean_reproduction_probability":round(mean([a.genome.reproduction_probability for a in L]),5) if L else 0.})

    def inspect_agent(self,agent_id:int)->dict[str,Any]:
        a=next((x for x in self.population if x.id==agent_id),None)
        if a is None:raise KeyError(agent_id)
        lineage=[];cur=a
        while cur is not None:
            lineage.append(cur.id)
            cur=next((x for x in self.population if x.id==cur.parent),None) if cur.parent is not None else None
        return {"agent":asdict(a),"age":(self.tick if a.death_tick is None else a.death_tick)-a.born,
                "lineage":lineage,"child_ids":[x.id for x in self.population if x.parent==a.id]}

    def snapshot(self)->dict[str,Any]:
        return {"version":"0.3.0","seed":self.seed,"tick":self.tick,"price":round(self.price,4),
          "births":self.births,"deaths":self.deaths,"max_generation":self.max_generation,
          "agents":[asdict(a) for a in self.population],"history":self.history,"events":self.events}
