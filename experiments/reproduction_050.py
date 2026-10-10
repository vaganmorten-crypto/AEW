"""Run 150 paired-seed AEW experiments; writes measured results only."""
import argparse
import csv
import json
from pathlib import Path
from statistics import mean
from aew.experimental_world import World

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--agents",type=int,default=600)
    p.add_argument("--ticks",type=int,default=10000)
    p.add_argument("--seeds",type=int,default=30)
    p.add_argument("--out",default="results/reproduction_050.csv")
    a=p.parse_args()
    rows=[]
    for group in "ABCDE":
        for seed in range(a.seeds):
            w=World(a.agents,seed,group)
            w.run(a.ticks)
            births=sum(x.generation>0 for x in w.population)
            max_generation=max((x.generation for x in w.population),default=0)
            row=dict(group=group,seed=seed,ticks=w.tick,founders=a.agents,
                     final_population=len(w.living),births=births,
                     max_generation=max_generation,
                     final_mean_cash=w.history[-1]["mean_cash"])
            rows.append(row)
            print(json.dumps(row),flush=True)
    out=Path(a.out);out.parent.mkdir(parents=True,exist_ok=True)
    with out.open("w",newline="",encoding="utf-8") as f:
        writer=csv.DictWriter(f,fieldnames=list(rows[0]))
        writer.writeheader();writer.writerows(rows)
    print("Saved",out,len(rows),"measured runs")

if __name__=="__main__":
    main()
