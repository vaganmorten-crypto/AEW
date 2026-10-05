from __future__ import annotations
import argparse, json
from pathlib import Path
from .simulation import World

def run_cmd(args):
    w=World(args.agents,args.seed); w.run(args.ticks)
    Path(args.out).write_text(json.dumps(w.snapshot(),indent=2),encoding="utf-8")
    print(f"AEW 0.3.0: tick={w.tick} living={len(w.living)} events={len(w.events)} snapshot={args.out}")

def dashboard_cmd(args):
    import matplotlib.pyplot as plt
    data=json.loads(Path(args.snapshot).read_text(encoding="utf-8")); h=data["history"]; ticks=[x["tick"] for x in h]
    fig,ax=plt.subplots(); ax.plot(ticks,[x["population"] for x in h],label="population"); ax.set_xlabel("tick"); ax.set_ylabel("living agents")
    ax2=ax.twinx(); ax2.plot(ticks,[x["price"] for x in h],linestyle="--"); ax2.set_ylabel("virtual price")
    fig.suptitle("AEW 0.3.0 — simulation dashboard"); fig.tight_layout(); fig.savefig(args.out,dpi=150); plt.close(fig)

def main():
    p=argparse.ArgumentParser(prog="python -m aew"); s=p.add_subparsers(dest="command",required=True)
    r=s.add_parser("run"); r.add_argument("--ticks",type=int,default=1000); r.add_argument("--agents",type=int,default=100); r.add_argument("--seed",type=int,default=42); r.add_argument("--out",default="aew_snapshot.json"); r.set_defaults(func=run_cmd)
    d=s.add_parser("dashboard"); d.add_argument("snapshot"); d.add_argument("--out",default="aew_dashboard.png"); d.set_defaults(func=dashboard_cmd)
    a=p.parse_args(); a.func(a)
if __name__=="__main__": main()
