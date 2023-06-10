import smbus2
import bme280


# the sample method will take a single reading and return a
# compensated_reading object


# the compensated_reading class has the following attributes

# there is a handy string representation too


def main():
    port = 1
    address = 0x76
    bus = smbus2.SMBus(port)

    calibration_params = bme280.load_calibration_params(bus, address)
    data = bme280.sample(bus, address, calibration_params)
    print(data)
            
        
if __name__== "__main__":
    main()