from __future__ import annotations
from dataclasses import dataclass, field, asdict
from random import Random
from typing import Dict, List
import json, math

ASSETS=("grain","energy","compute")
COGNITIVE_TRAITS=("memory","planning","exploration","learning","sociality")
def clamp(x:float,lo:float=0.0,hi:float=1.0)->float:return min(hi,max(lo,x))

@dataclass
class GenomeV2:
    risk:float; thrift:float; mutation_rate:float
    trade_bias:Dict[str,float]; cognition:Dict[str,float]
    reproduction_threshold:float; reproduction_probability:float
    offspring_investment:float; mate_preference:float; recombination:float
    @classmethod
    def random(cls,rng:Random):
        return cls(rng.random(),rng.random(),rng.uniform(.02,.14),
          {a:rng.random() for a in ASSETS},{k:rng.random() for k in COGNITIVE_TRAITS},
          rng.uniform(120,240),rng.uniform(.003,.025),rng.uniform(.15,.45),rng.random(),rng.random())
    def mutate(self,rng:Random):
        rate=self.mutation_rate
        def m(x,scale=.12):return clamp(x+(rng.gauss(0,scale) if rng.random()<rate else 0))
        return GenomeV2(m(self.risk),m(self.thrift),clamp(self.mutation_rate+rng.gauss(0,.015),.005,.35),
          {k:m(v) for k,v in self.trade_bias.items()},{k:m(v) for k,v in self.cognition.items()},
          max(60,min(400,self.reproduction_threshold+(rng.gauss(0,18) if rng.random()<rate else 0))),
          clamp(self.reproduction_probability+(rng.gauss(0,.004) if rng.random()<rate else 0),.0005,.08),
          clamp(self.offspring_investment+(rng.gauss(0,.05) if rng.random()<rate else 0),.08,.70),
          m(self.mate_preference),m(self.recombination))
    @classmethod
    def recombine(cls,parents,rng):
        def pick(attr):return getattr(rng.choice(parents),attr)
        return cls(pick("risk"),pick("thrift"),sum(p.mutation_rate for p in parents)/len(parents),
          {a:rng.choice(parents).trade_bias[a] for a in ASSETS},{k:rng.choice(parents).cognition[k] for k in COGNITIVE_TRAITS},
          pick("reproduction_threshold"),pick("reproduction_probability"),pick("offspring_investment"),
          pick("mate_preference"),pick("recombination")).mutate(rng)

@dataclass
class CognitiveAgent:
    id:int; cash:float; inventory:Dict[str,float]; genome:GenomeV2
    parent_ids:List[int]=field(default_factory=list); generation:int=0; age:int=0; alive:bool=True
    wealth_history:List[float]=field(default_factory=list); memory:List[dict]=field(default_factory=list)
    offspring_ids:List[int]=field(default_factory=list); fitness:float=0.0; last_action:str="born"
    def wealth(self,prices):return self.cash+sum(self.inventory[a]*prices[a] for a in ASSETS)
    def remember(self,event):
        cap=2+int(18*self.genome.cognition["memory"]);self.memory.append(event)
        if len(self.memory)>cap:del self.memory[:-cap]
Agent=CognitiveAgent

@dataclass
class WorldConfig:
    seed:int=7; initial_agents:int=600; initial_cash:float=100.0; resource_regen:float=.012
    carrying_capacity:float=10000.0; bankruptcy_floor:float=.01; max_agents:int=5000
    price_sensitivity:float=.025; ticks:int=500; min_reproduction_age:int=12; market_signal_strength:float=.18

class World:
    """Closed ALife economy. External market data may only be supplied as read-only numeric signals."""
    def __init__(self,cfg:WorldConfig,market_signals:List[dict]|None=None):
        self.cfg,self.rng,self.tick=cfg,Random(cfg.seed),0
        self.prices={"grain":1.0,"energy":1.3,"compute":2.0}
        self.resources={a:cfg.carrying_capacity/3 for a in ASSETS}
        self.agents=[];self.next_id=1;self.history=[];self.birth_events=[];self.market_signals=market_signals or []
        for _ in range(cfg.initial_agents):self.agents.append(self._new_agent())
    def _new_agent(self,parents=None,investment=None):
        parents=parents or []
        genome=GenomeV2.recombine([p.genome for p in parents],self.rng) if parents else GenomeV2.random(self.rng)
        inv={a:self.rng.uniform(2,8) for a in ASSETS};cash=self.cfg.initial_cash if not parents else max(5.0,investment or 5.0)
        a=CognitiveAgent(self.next_id,cash,inv,genome,[p.id for p in parents],0 if not parents else max(p.generation for p in parents)+1)
        self.next_id+=1
        for p in parents:p.offspring_ids.append(a.id)
        if parents:self.birth_events.append({"tick":self.tick,"child":a.id,"parents":a.parent_ids,"generation":a.generation})
        return a
    def _external_signal(self,asset):
        if not self.market_signals:return 0.0
        row=self.market_signals[min(self.tick-1,len(self.market_signals)-1)]
        return clamp(float(row.get(asset,0.0)),-1,1)
    def _fundamental(self,asset):
        scarcity=self.cfg.carrying_capacity/max(1,self.resources[asset]*3)
        return max(.05,(1+{"grain":0,"energy":.3,"compute":1}[asset])*scarcity)
    def _trade_round(self):
        alive=[a for a in self.agents if a.alive];self.rng.shuffle(alive);pressure={x:0.0 for x in ASSETS}
        for a in alive:
            foresight=a.genome.cognition["planning"];learning=a.genome.cognition["learning"]
            for asset in ASSETS:
                signal=self._external_signal(asset)*self.cfg.market_signal_strength;recent=0.0
                if len(a.memory)>1:recent=a.memory[-1].get("returns",{}).get(asset,0.0)
                adaptive=learning*recent+foresight*signal;target=4+18*clamp(a.genome.trade_bias[asset]+adaptive)
                qty=max(-3,min(3,(target-a.inventory[asset])*(.15+.85*a.genome.risk)));price=self.prices[asset]
                if qty>0:
                    qty=min(qty,a.cash/max(price,.01),self.resources[asset]);a.cash-=qty*price;a.inventory[asset]+=qty;self.resources[asset]-=qty
                else:
                    sell=min(-qty,a.inventory[asset]);a.cash+=sell*price;a.inventory[asset]-=sell;self.resources[asset]+=sell
                pressure[asset]+=qty
            a.last_action="trade"
        old=dict(self.prices)
        for asset in ASSETS:
            pull=.02*math.log(self._fundamental(asset)/self.prices[asset]);noise=self.rng.gauss(0,.006)
            self.prices[asset]*=math.exp(self.cfg.price_sensitivity*pressure[asset]/max(1,len(alive))+pull+noise)
            self.prices[asset]=max(.05,min(50,self.prices[asset]))
        returns={x:math.log(self.prices[x]/old[x]) for x in ASSETS}
        for a in alive:a.remember({"tick":self.tick,"returns":returns,"wealth":a.wealth(self.prices)})
    def _select_partners(self,focal,alive):
        candidates=[x for x in alive if x.id!=focal.id and x.age>=self.cfg.min_reproduction_age and x.wealth(self.prices)>=x.genome.reproduction_threshold]
        if not candidates:return [focal]
        n=2 if focal.genome.recombination>.72 and len(candidates)>=2 else 1
        ranked=sorted(candidates,key=lambda x:abs(x.genome.risk-focal.genome.mate_preference))
        return [focal]+ranked[:n]
    def _ecology(self):
        cap=self.cfg.carrying_capacity/3
        for asset in ASSETS:
            r=self.resources[asset];self.resources[asset]=min(cap,r+self.cfg.resource_regen*r*(1-r/cap))
        alive=[x for x in self.agents if x.alive];newborns=[]
        for a in alive:
            a.age+=1;a.cash-=.08+.28*(1-a.genome.thrift)+.04*a.genome.cognition["planning"]
            w=a.wealth(self.prices);a.wealth_history.append(w);a.fitness=max(0,w)*(1+len(a.offspring_ids)*.05)
            if a.cash<=self.cfg.bankruptcy_floor and sum(a.inventory.values())<.05:
                a.alive=False;a.last_action="bankrupt";continue
            if a.age<self.cfg.min_reproduction_age or w<a.genome.reproduction_threshold:continue
            if len(alive)+len(newborns)>=self.cfg.max_agents:break
            if self.rng.random()<a.genome.reproduction_probability:
                parents=self._select_partners(a,alive)
                invest=sum(max(0,p.cash)*p.genome.offspring_investment for p in parents)/len(parents)
                if invest>=5:
                    share=invest/len(parents)
                    if all(p.cash>=share for p in parents):
                        for p in parents:p.cash-=share;p.last_action="reproduce"
                        newborns.append(self._new_agent(parents,invest))
        self.agents.extend(newborns)
    def step(self):
        self.tick+=1;self._trade_round();self._ecology();alive=[a for a in self.agents if a.alive]
        self.history.append({"tick":self.tick,"population":len(alive),
          "births":sum(1 for b in self.birth_events if b["tick"]==self.tick),
          "mean_wealth":sum((a.wealth(self.prices) for a in alive),0)/max(1,len(alive)),
          "prices":dict(self.prices),"resources":dict(self.resources),
          "max_generation":max((a.generation for a in alive),default=0),
          "mean_fitness":sum((a.fitness for a in alive),0)/max(1,len(alive))})
    def run(self,ticks=None):
        for _ in range(ticks or self.cfg.ticks):self.step()
        return self.history
    def snapshot(self):
        return {"version":"0.4.0","tick":self.tick,"config":asdict(self.cfg),"prices":self.prices,"resources":self.resources,
          "agents":[asdict(a) for a in self.agents],"birth_events":self.birth_events,"history":self.history,
          "safety":{"closed_world":True,"real_money_execution":False,"network_execution":False,"external_data":"read-only numeric input only"}}
    def save(self,path):
        with open(path,"w",encoding="utf-8") as f:json.dump(self.snapshot(),f,indent=2)
