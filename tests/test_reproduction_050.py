from dataclasses import asdict
from random import Random
import pytest
from aew.simulation import Genome
from aew.reproduction import reproduce, GROUPS

def example():
    return Genome(.2,.3,150,.04,.2,.9,.08)

@pytest.mark.parametrize("group", GROUPS)
def test_parent_unchanged(group):
    parent=example()
    original=asdict(parent)
    child=reproduce(parent, Random(12), group, (example(),))
    assert asdict(parent)==original
    assert child is not parent

@pytest.mark.parametrize("group", GROUPS)
def test_reproducible(group):
    p=example()
    assert asdict(reproduce(p,Random(123),group,(p,))) == asdict(reproduce(p,Random(123),group,(p,)))

def test_unknown_group():
    with pytest.raises(ValueError):
        reproduce(example(),Random(1),"X")
