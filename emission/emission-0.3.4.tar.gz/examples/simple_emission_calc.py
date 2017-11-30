import sys
import os

cwd = os.path.dirname(os.path.abspath(__file__))
cwd_parent = os.path.abspath(os.path.join(cwd, os.pardir))
sys.path.append(cwd)
sys.path.append(cwd_parent)

import emission


if __name__ == '__main__':
    
    fuel_petrol = emission.vehicles.FuelTypes.PETROL
    car = emission.vehicles.Car(fuel_petrol)

    pollutants = [emission.PollutantTypes.NOx, emission.PollutantTypes.CO]
    emissionDb = emission.EmissionsJsonParser(car, pollutants)
    #planner.add_pollutant(emission.PollutantTypes.NOx)
    #planner.add_pollutant(emission.PollutantTypes.CO)
    #planner.run()
