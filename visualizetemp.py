import csv
import time
import plotext as plt 
from datetime import datetime
import sys
# the sample method will take a single reading and return a


def main():
    try:
        for arg in sys.argv[1:]:
            darstellung("roomconditions.csv", arg)
    except IndexError:
        darstellung("roomconditions.csv")


def darstellung(filename, dataseries = None):

    datatypes = {"temps":1,"humids":2,"presures":3}
    if dataseries == None:
        dataseries = "temps"
    data = []
    with open(filename, "r") as file:
        reader = csv.reader(file)

        for row in reader:
            data.append(float(row[datatypes[dataseries]])) 

    # plt.plot(temps)
    plt.plot(data)
    plt.show()
            
        
if __name__ == "__main__":
    main()