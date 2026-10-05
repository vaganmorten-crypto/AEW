"""Controlled multi-seed reproduction-discovery experiment."""
from statistics import mean
from aew.simulation import World

SEEDS = range(1, 101)
TICKS = 3000
FOUNDERS = 60

def run():
    rows=[]
    for seed in SEEDS:
        w=World(FOUNDERS, seed)
        w.run(TICKS)
        born=[a for a in w.population if a.parent is not None]
        max_gen=max((a.generation for a in w.population), default=0)
        rows.append({
            "seed":seed, "births":len(born), "max_generation":max_gen,
            "living":len(w.living),
            "extinct":len(w.living)==0,
            "mean_founder_repro_p":mean(a.genome.reproduction_probability for a in w.population[:FOUNDERS]),
            "mean_survivor_repro_p":mean(a.genome.reproduction_probability for a in w.living) if w.living else 0.0,
        })
    print("seeds",len(rows),"ticks",TICKS)
    print("with_births",sum(r["births"]>0 for r in rows))
    print("reached_gen3",sum(r["max_generation"]>=3 for r in rows))
    print("extinct",sum(r["extinct"] for r in rows))
    print("mean_births",round(mean(r["births"] for r in rows),2))
    print("mean_delta_repro_p",round(mean(r["mean_survivor_repro_p"]-r["mean_founder_repro_p"] for r in rows),5))
    for r in rows: print(r)

if __name__=="__main__": run()
