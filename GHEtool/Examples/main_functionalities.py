"""
This file contains all the main functionalities of GHEtool being:
    * sizing of the borefield
    * sizing of the borefield for a specific quadrant
    * plotting the temperature evolution
    * plotting the temperature evolution for a specific depth
    * printing the array of the temperature

"""

# import all the relevant functions
from GHEtool import Borefield, GroundData, FluidData, PipeData

if __name__ == "__main__":
    # relevant borefield data for the calculations
    data = GroundData(110,           # depth (m)
                      6,             # borehole spacing (m)
                      3,             # conductivity of the soil (W/mK)
                      10,            # Ground temperature at infinity (degrees C)
                      0.2,           # equivalent borehole resistance (K/W)
                      12,            # width of rectangular field (#)
                      10)            # length of rectangular field (#)}

    # monthly loading values
    peak_cooling = [0., 0, 34., 69., 133., 187., 213., 240., 160., 37., 0., 0.]              # Peak cooling in kW
    peak_heating = [160., 142, 102., 55., 0., 0., 0., 0., 40.4, 85., 119., 136.]             # Peak heating in kW

    # annual heating and cooling load
    annual_heating_load = 300 * 10 ** 3  # kWh
    annual_cooling_load = 160 * 10 ** 3  # kWh

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
    print("The borehole depth is: ", depth, "m")

    # print imbalance
    print("The borefield imbalance is: ", borefield.imbalance, "kWh/y. (A negative imbalance means the the field is heat extraction dominated so it cools down year after year.)") # print imbalance

    # plot temperature profile for the calculated depth
    borefield.print_temperature_profile(legend=True)

    # plot temperature profile for a fixed depth
    borefield.print_temperature_profile_fixed_depth(depth=75, legend=False)

    # print gives the array of monthly temperatures for peak cooling without showing the plot
    borefield.calculate_temperatures(depth=90)
    print("Result array for cooling peaks")
    print(borefield.results_peak_cooling)
    print("---------------------------------------------")

    # size the borefield for quadrant 3
    # for more information about borefield quadrants, see (Peere et al., 2021)
    depth = borefield.size(100, quadrant_sizing=3)
    print("The borehole depth is: ", str(round(depth, 2)), "m for a sizing in quadrant 3")
    # plot temperature profile for the calculated depth
    borefield.print_temperature_profile(legend=True)

    # size with a dynamic Rb* value
    # note that the original Rb* value will be overwritten!

    # this requires pipe and fluid data
    fluid_data = FluidData(0.2, 0.568, 998, 4180, 1e-3)
    pipe_data = PipeData(1, 0.015, 0.02, 0.4, 0.05, 0.075, 2)
    borefield.set_fluid_parameters(fluid_data)
    borefield.set_pipe_parameters(pipe_data)

    depth = borefield.size(100, use_constant_Rb=False)
    print("The borehole depth is: ", str(round(depth, 2)), "m for a sizing with dynamic Rb*.")
    borefield.print_temperature_profile(legend=True)
