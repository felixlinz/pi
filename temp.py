import smbus2
import bme280
import csv
import time
import plotext as plt 
import datetime

# the sample method will take a single reading and return a
# compensated_reading object


# the compensated_reading class has the following attributes

# there is a handy string representation too


def main():
    port = 1
    address = 0x76
    bus = smbus2.SMBus(port)

    calibration_params = bme280.load_calibration_params(bus, address)

    filename = "roomconditions.csv"
    open(filename, "w")
    while True:
        data = bme280.sample(bus, address, calibration_params)
        
        with open("roomconditions.csv", "a") as file:
            writer = csv.writer(file)
            writer.writerow(list((data.timestamp, data.temperature, data.pressure, data.humidity)))

        time.sleep(60)



def darstellung(filename):
    temps = []
    humids = []   
    times = []
    with open(filename, "r") as file:
        reader = csv.reader(file)
        for row in reader:
            temps.append(float(row[1]))
            humids.append(float(row[3]))
            times.append(datetime.datetime.strptime(row[0],"%Y-%m-%d %H:%M:%S.%f%z"))
            
    # plt.plot(temps)
    plt.plot(temps)
    plt.xlabel("Time")
    plt.ylabel("Temps")
    plt.show()
            
        
if __name__== "__main__":
    main()