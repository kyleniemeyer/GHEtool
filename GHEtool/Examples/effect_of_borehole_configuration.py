"""
This document is an example of how the borefield configuration can influence the total borehole length and hence the cost of the borefield.
"""

# import all the relevant functions
from GHEtool import *

if __name__ == "__main__":
    # GroundData for an initial field of 11 x 11
    data = GroundData(110, 6, 3, 10, 0.2, 11, 11)

    # Monthly loading values
    peak_cooling = [0., 0, 34., 69., 133., 187., 213., 240., 160., 37., 0., 0.]              # Peak cooling in kW
    peak_heating = [160., 142, 102., 55., 0., 0., 0., 0., 40.4, 85., 119., 136.]             # Peak heating in kW

    # annual heating and cooling load
    annual_heating_load = 150 * 10 ** 3  # kWh
    annual_cooling_load = 400 * 10 ** 3  # kWh

    # percentage of annual load per month (15.5% for January ...)
    monthly_load_heating_percentage = [0.155, 0.148, 0.125, .099, .064, 0., 0., 0., 0.061, 0.087, 0.117, 0.144]
    monthly_load_cooling_percentage = [0.025, 0.05, 0.05, .05, .075, .1, .2, .2, .1, .075, .05, .025]

    # resulting load per month
    monthly_load_heating = list(map(lambda x: x * annual_heating_load, monthly_load_heating_percentage))   # kWh
    monthly_load_cooling = list(map(lambda x: x * annual_cooling_load, monthly_load_cooling_percentage))   # kWh

    # create the borefield object

    borefield = Borefield(simulation_period=20,
                          peak_heating=peak_heating,
                          peak_cooling=peak_cooling,
                          baseload_heating=monthly_load_heating,
                          baseload_cooling=monthly_load_cooling)

    borefield.set_ground_parameters(data)

    # set temperature boundaries
    borefield.set_max_ground_temperature(16)   # maximum temperature
    borefield.set_min_ground_temperature(0)    # minimum temperature

    # size borefield
    depth = borefield.size(100)
    print("The borehole depth is:", depth, "m for a 11x11 field")
    print("The total length is:", int(depth * 11 * 11), "m")
    print("------------------------")

    # borefield of 6x20
    data = GroundData(110, 6, 3, 10, 0.2, 6, 20)

    # set ground parameters to borefield
    borefield.set_ground_parameters(data)

    # size borefield
    depth6_20 = borefield.size(100)
    print("The borehole depth is:", depth6_20, "m for a 6x20 field")
    print("The total length is:", int(depth6_20 * 6 * 20), "m")
    print("The second field is hence", -int(depth6_20 * 6 * 20) + int(depth * 11 * 11), "m shorter")
    borefield.print_temperature_profile()
