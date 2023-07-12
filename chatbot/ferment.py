from fermentationbox import Fermenter
import time

fermenter = Fermenter()
fermenter.turn_on()
print(fermenter.targets)
print(fermenter.conditions)
time.sleep(2)
fermenter.turn_off()
time.sleep(3)
fermenter.adjust_targets(temperature=20)
print(fermenter.targets)
fermenter.turn_on()

