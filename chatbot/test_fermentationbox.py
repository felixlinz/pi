import pytest
from fermentationbox import Fermenter, ChatBox

# fermenter 

def test_init():
    fermenter = Fermenter()
    assert fermenter._on == False 
    assert fermenter.logfile == "__conditionslog.csv"
    fermenter.turn_on()
    assert fermenter._on == True
    
def test_adjust_targets():
    fermenter2 = Fermenter()
    fermenter2.adjust_targets(temperature=45)
    assert fermenter2.targets.temperature == 45
    fermenter2.adjust_targets(humidity=90)
    assert fermenter2.targets.humidity == 90
    fermenter2.turn_off()
    assert fermenter2._on == False
    assert fermenter2.targets.temperature == 0