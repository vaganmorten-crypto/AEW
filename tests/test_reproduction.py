from random import Random
import pytest
from aew.simulation import Genome
from aew.reproduction import ReproductionConfig, offspring_genome, FIELDS


def test_modes_are_deterministic_and_do_not_mutate_parents():
    for mode in "ABCDE":
        p = Genome.founder(Random(1))
        q = Genome.founder(Random(2))
        before = (repr(p), repr(q))
        parents = [p, q] if mode in "DE" else [p]
        a = offspring_genome(parents, Random(17), ReproductionConfig(mode))
        b = offspring_genome(parents, Random(17), ReproductionConfig(mode))
        assert a == b
        assert (repr(p), repr(q)) == before


def test_full_repair_restores_base_genome():
    p = Genome.founder(Random(4))
    child = offspring_genome([p], Random(5),
                             ReproductionConfig("C", repair_probability=1))
    assert child == p and child is not p


def test_recombination_requires_multiple_parents():
    with pytest.raises(ValueError):
        offspring_genome([Genome.founder(Random(1))], Random(2),
                         ReproductionConfig("D"))


def test_all_genes_remain_bounded():
    for mode in "ABCDE":
        parents = [Genome.founder(Random(4)), Genome.founder(Random(5))]
        for seed in range(100):
            child = offspring_genome(parents if mode in "DE" else parents[:1],
                                     Random(seed), ReproductionConfig(mode))
            assert all(getattr(child, f) is not None for f in FIELDS)
            assert 0.005 <= child.mutation_rate <= 0.25
            assert 0.01 <= child.risk <= 0.99
