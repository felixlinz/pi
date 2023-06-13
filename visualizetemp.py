import smbus2
import bme280
import csv
import time
import plotext as plt 
from datetime import datetime
# the sample method will take a single reading and return a
# compensated_reading object


# the compensated_reading class has the following attributes

# there is a handy string representation too


def main():
    darstellung("roomconditions.csv")



def darstellung(filename):
    temps = []
    times = []
    with open(filename, "r") as file:
        reader = csv.reader(file)

        for row in reader:
            temps.append(row[1]) 

    # plt.plot(temps)
    plt.plot(temps)
    plt.show()
            
        
if __name__== "__main__":
    main()