"""Controlled AEW experiments; outputs raw per-seed metrics to CSV."""
import argparse
import csv
from aew.simulation import World

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--agents",type=int,default=600)
    p.add_argument("--ticks",type=int,default=10000)
    p.add_argument("--seeds",type=int,default=30)
    p.add_argument("--out",default="lifecycle_results.csv")
    args=p.parse_args()
    groups={
        "treatment":dict(deadline=1000,elite_slots=10),
        "no_deadline":dict(deadline=None,elite_slots=0),
        "no_elite":dict(deadline=1000,elite_slots=0),
        "no_mutation":dict(deadline=1000,elite_slots=10,mutation=False),
        "no_inheritance":dict(deadline=1000,elite_slots=10,inheritance=False),
    }
    fields=["group","seed","final_population","births","deadline_deaths","bankruptcies","max_generation","final_mean_cash","final_mean_reproduction_probability"]
    with open(args.out,"w",newline="",encoding="utf-8") as f:
        writer=csv.DictWriter(f,fieldnames=fields);writer.writeheader()
        for group,config in groups.items():
            for seed in range(args.seeds):
                w=World(agents=args.agents,seed=seed,**config)
                w.run(args.ticks)
                counts={kind:w.event_counts.get(kind,0) for kind in ("birth","deadline_death","bankruptcy")}
                row=dict(group=group,seed=seed,final_population=len(w.living),births=counts["birth"],deadline_deaths=counts["deadline_death"],bankruptcies=counts["bankruptcy"],max_generation=max((a.generation for a in w.population),default=0),final_mean_cash=w.history[-1]["mean_cash"],final_mean_reproduction_probability=w.history[-1]["mean_reproduction_probability"])
                writer.writerow(row)
                print(group,seed,row["final_population"],flush=True)
if __name__=="__main__": main()
