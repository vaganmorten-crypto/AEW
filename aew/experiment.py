from __future__ import annotations
import argparse,json
from pathlib import Path
from .cognitive import CognitiveWorld

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--agents",type=int,default=1000)
    p.add_argument("--ticks",type=int,default=500)
    p.add_argument("--seed",type=int,default=42)
    p.add_argument("--out",default="dashboard/data/latest.json",
                   help="Genome v2/CognitiveAgent snapshot consumed by the Experimental Observatory")
    a=p.parse_args()
    w=CognitiveWorld(a.agents,a.seed); w.run(a.ticks)
    result=w.snapshot()
    result["experiment"]={"from_generation":0,
      "to_generation":max((x["generation"] for x in result["agents"]),default=0)}
    out=Path(a.out); out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(result,indent=2),encoding="utf-8")
    print(json.dumps({"tick":w.tick,"living":len(w.living),
      "max_generation":result["experiment"]["to_generation"],
      "mean_complexity":w.history[-1]["mean_complexity"],"out":str(out)}))

if __name__=="__main__":
    main()
