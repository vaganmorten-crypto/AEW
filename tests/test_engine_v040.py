from aew.engine_v040 import GenomeV2,World,WorldConfig
def test_v040_deterministic():
    a=World(WorldConfig(seed=7,initial_agents=20,ticks=30));b=World(WorldConfig(seed=7,initial_agents=20,ticks=30));a.run();b.run();assert a.snapshot()==b.snapshot()
def test_v040_genome_and_lineage():
    w=World(WorldConfig(seed=11,initial_agents=40,ticks=120));w.run()
    assert all(isinstance(a.genome,GenomeV2) for a in w.agents)
    assert all(a.generation==0 or a.parent_ids for a in w.agents)
def test_v040_closed_world_safety():
    w=World(WorldConfig(initial_agents=2,ticks=1));w.run();s=w.snapshot()["safety"]
    assert s["closed_world"] and not s["real_money_execution"] and not s["network_execution"]
