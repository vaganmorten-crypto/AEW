from aew.model import World
for seed in range(5):
    w=World(seed=seed); w.initialize(100); w.run(1000); s=w.snapshot()
    print(seed,s["population"],s["total_agents_ever"])
