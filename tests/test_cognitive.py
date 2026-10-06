from aew.cognitive import GenomeV2,CognitiveWorld,MarketDataFeed
from random import Random

def test_genome_v2_has_cognitive_and_structural_genes():
    g=GenomeV2.founder(Random(1))
    assert g.memory_span>=2 and g.planning_horizon>=1 and len(g.hidden_weights)==g.complexity_budget

def test_default_population_is_ten_x_old_default():
    assert len(CognitiveWorld(seed=1).population)==1000

def test_external_market_feed_is_read_only_input():
    f=MarketDataFeed([(0.1,0.2),(0.2,0.3)],"fixture")
    w=CognitiveWorld(10,1,f); w.run(2)
    assert w.snapshot()["safety"]=={"external_orders":False,"market_input":"read-only"}
    assert f.at(0).values==(0.1,0.2)

def test_agent_inspector_exposes_cognition_lineage_and_genome():
    w=CognitiveWorld(10,2); w.step(); x=w.inspect(0)
    assert {"genome","cognition","generation","parent"} <= x.keys()
    assert "architecture_nodes" in x["cognition"]

def test_deterministic():
    a=CognitiveWorld(20,9); b=CognitiveWorld(20,9); a.run(5); b.run(5)
    assert a.snapshot()==b.snapshot()
