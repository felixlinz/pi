import csv
import time
import plotext as plt 
from datetime import datetime
import sys
# the sample method will take a single reading and return a

         

def main():
    try:
        for arg in sys.argv[1:]:
            darstellung("log.csv", arg)
    except IndexError:
        darstellung("roomconditions.csv")


def darstellung(filename, dataseries = None):

    if dataseries == None:
        dataseries = "temps"
    data = []
    with open(filename, "r") as file:
        reader = csv.DictReader(file)

        for row in reader:
            data.append(float(row[dataseries])) 

    # plt.plot(temps)
    plt.plot(data)
    plt.show()
    
            
        
        
if __name__ == "__main__":
    main()