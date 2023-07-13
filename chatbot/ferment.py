from fermentationbox import Fermenter
import time

fermenter = Fermenter()
fermenter.turn_on()
time.sleep(1)
print(fermenter.targets)
fermenter.adjust_targets(temperature=22)
print(fermenter.targets)
time.sleep(10)


