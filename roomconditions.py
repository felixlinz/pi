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
    while True:
        data = bme280.sample(bus, address, calibration_params)
        
        with open("roomconditions.csv", "a") as file:
            writer = csv.writer(file)
            writer.writerow(list((data.timestamp, data.temperature, data.pressure, data.humidity)))

        time.sleep(60)



def darstellung(filename):
    data = pd.read_csv(filename)

    data[0] = pd.to_datetime(data[0]) 

    data[0] = data[0].dt.strftime('%Y-%m-%d %H:%M:%S')  
    temperature = data[1].tolist()
    time = data[0].tolist()

    # plt.plot(temps)
    plt.plot(time, temperature)
    plt.show()
            
        
if __name__== "__main__":
    main()