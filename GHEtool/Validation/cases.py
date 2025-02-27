"""
This document contains checks to see whether or not adaptations to the code still comply with some specific cases.
It also shows the difference between the original l_2 sizing methode (Peere et al., 2021) and a more general L3 one.

This document contains 4 different cases referring to the paper: Peere, W., Picard, D., Cupeiro Figueroa, I., Boydens, W., and Helsen, L. Validated combined first and last year borefield sizing methodology. In Proceedings of International Building Simulation Conference 2021 (2021). Brugge (Belgium), 1-3 September 2021.

"""

from GHEtool import Borefield, GroundData
import pygfunction as gt

if __name__ == "__main__":
    # relevant borefield data for the calculations
    data = GroundData(110,  # depth (m)
                      6.5,  # borehole spacing (m)
                      3.5,  # conductivity of the soil (W/mK)
                      10,   # Ground temperature at infinity (degrees C)
                      0.2,  # equivalent borehole resistance (K/W)
                      12,   # width of rectangular field (#)
                      10)   # length of rectangular field (#)

    def load_case(number):
        """This function returns the values for one of the four cases."""

        monthly_load_cooling, monthly_load_heating, peak_cooling, peak_heating = [] * 12, [] * 12, [] * 12, [] * 12

        if number == 1:
            # case 1
            # limited in the first year by cooling
            monthly_load_heating_percentage = [0.155, 0.148, 0.125, .099, .064, 0., 0., 0., 0.061, 0.087, 0.117, 0.144]
            monthly_load_cooling_percentage = [0.025, 0.05, 0.05, .05, .075, .1, .2, .2, .1, .075, .05, .025]
            monthly_load_heating = list(map(lambda x: x * 300 * 10 ** 3, monthly_load_heating_percentage))  # kWh
            monthly_load_cooling = list(map(lambda x: x * 150 * 10 ** 3, monthly_load_cooling_percentage))  # kWh
            peak_cooling = [0., 0., 22., 44., 83., 117., 134., 150., 100., 23., 0., 0.]
            peak_heating = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]

        elif number == 2:
            # case 2
            # limited in the last year by cooling
            monthly_load_heating_percentage = [0.155, 0.148, 0.125, .099, .064, 0., 0., 0., 0.061, 0.087, .117, 0.144]
            monthly_load_cooling_percentage = [0.025, 0.05, 0.05, .05, .075, .1, .2, .2, .1, .075, .05, .025]
            monthly_load_heating = list(map(lambda x: x * 160 * 10 ** 3, monthly_load_heating_percentage))  # kWh
            monthly_load_cooling = list(map(lambda x: x * 240 * 10 ** 3, monthly_load_cooling_percentage))  # kWh
            peak_cooling = [0., 0, 34., 69., 133., 187., 213., 240., 160., 37., 0., 0.]  # Peak cooling in kW
            peak_heating = [160., 142, 102., 55., 0., 0., 0., 0., 40.4, 85., 119., 136.]

        elif number == 3:
            # case 3
            # limited in the first year by heating
            monthly_load_heating_percentage = [0.155, 0.148, 0.125, .099, .064, 0., 0., 0., 0.061, 0.087, .117, 0.144]
            monthly_load_cooling_percentage = [0.025, 0.05, 0.05, .05, .075, .1, .2, .2, .1, .075, .05, .025]
            monthly_load_heating = list(map(lambda x: x * 160 * 10 ** 3, monthly_load_heating_percentage))  # kWh
            monthly_load_cooling = list(map(lambda x: x * 240 * 10 ** 3, monthly_load_cooling_percentage))  # kWh
            peak_cooling = [0] * 12
            peak_heating = [300.0, 266.25, 191.25, 103.125, 0.0, 0.0, 0.0, 0.0, 75.75, 159.375, 223.125, 255.0]

        else:
            # case 4
            # limited in the last year by heating
            monthly_load_heating_percentage = [0.155, 0.148, 0.125, .099, .064, 0., 0., 0., 0.061, 0.087, 0.117, 0.144]
            monthly_load_cooling_percentage = [0.025, 0.05, 0.05, .05, .075, .1, .2, .2, .1, .075, .05, .025]
            monthly_load_heating = list(map(lambda x: x * 300 * 10 ** 3, monthly_load_heating_percentage))  # kWh
            monthly_load_cooling = list(map(lambda x: x * 150 * 10 ** 3, monthly_load_cooling_percentage))  # kWh
            peak_cooling = [0., 0., 22., 44., 83., 117., 134., 150., 100., 23., 0., 0.]
            peak_heating = [300., 268., 191., 103., 75., 0., 0., 38., 76., 160., 224., 255.]

        return monthly_load_cooling, monthly_load_heating, peak_cooling, peak_heating

    def check_cases():

        """
        This function checks whether the borefield sizing gives the correct (i.e. validated) results for the 4 cases.
        If not, an assertion error is raised.
        NOTE: these values differ slightly from the values in the mentioned paper. This is due to the fact that GHEtool uses slightly different precalculated data.
        """

        correct_answers_L2 = (56.64, 118.7, 66.88, 92.67)
        correct_answers_L3 = (56.77, 119.23, 66.48, 91.63)

        for i in (1, 2, 3, 4):
            monthly_load_cooling, monthly_load_heating, peak_cooling, peak_heating = load_case(i)

            borefield = Borefield(simulation_period=20,
                                  peak_heating=peak_heating,
                                  peak_cooling=peak_cooling,
                                  baseload_heating=monthly_load_heating,
                                  baseload_cooling=monthly_load_cooling)

            borefield.set_ground_parameters(data)

            # set temperature boundaries
            borefield.set_max_ground_temperature(16)  # maximum temperature
            borefield.set_min_ground_temperature(0)  # minimum temperature

            borefield.size(100, L2_sizing=True)
            print(f'correct answer l_2: {correct_answers_L2[i-1]}; calculated answer l_2: {round(borefield.H,2)}; error: '
                  f'{round(abs(1 - borefield.H / correct_answers_L2[i - 1]) * 100, 4)} %')
            assert round(borefield.H, 2) == correct_answers_L2[i-1]

            borefield.size(100, L3_sizing=True)
            print(f'correct answer L3: {correct_answers_L3[i - 1]}; calculated answer L3: {round(borefield.H, 2)}; error: '
                  f'{round(abs(1 - borefield.H / correct_answers_L3[i - 1]) * 100, 4)} %')
            assert round(borefield.H, 2) == correct_answers_L3[i - 1]

    def check_custom_datafile():
        """
        This function checks whether the borefield sizing gives the correct (i.e. validated) results for the 4 cases given the custom datafile.
        If not, an assertion error is raised.
        """

        # create custom datafile

        correct_answers = (56.64, 118.7, 66.88, 92.67)
        li = [i for i in range(0, 12)]
        borefield = Borefield(simulation_period=20,
                              peak_heating=li,
                              peak_cooling=li,
                              baseload_heating=li,
                              baseload_cooling=li)

        borefield.set_ground_parameters(data)

        customField = gt.boreholes.rectangle_field(N_1=12, N_2=10, B_1=6.5, B_2=6.5, H=110., D=4, r_b=0.075)
        borefield.create_custom_dataset(customField, "custom_field")

        for i in (1, 2, 3, 4):
            monthly_load_cooling, monthly_load_heating, peak_cooling, peak_heating = load_case(i)

            borefield = Borefield(simulation_period=20,
                                  peak_heating=peak_heating,
                                  peak_cooling=peak_cooling,
                                  baseload_heating=monthly_load_heating,
                                  baseload_cooling=monthly_load_cooling)

            borefield.set_ground_parameters(data)

            # set temperature boundaries
            borefield.set_max_ground_temperature(16)  # maximum temperature
            borefield.set_min_ground_temperature(0)  # minimum temperature

            # set the custom field
            borefield.set_custom_gfunction("customfield")

            borefield.size(100)
            print(f'correct answer: {correct_answers[i-1]}; calculated '
                  f'answer: {round(borefield.H,2)}; error: '
                  f'{round(abs(1-borefield.H/correct_answers[i - 1])*100,4)} %')
            assert abs(1-borefield.H/correct_answers[i - 1]) <= 0.002

    check_cases()  # check different cases
    check_custom_datafile()  # check if the custom datafile is correct

    monthly_load_cooling, monthly_load_heating, peak_cooling, peak_heating = load_case(1)  # load case 1

    borefield = Borefield(simulation_period=20,
                          peak_heating=peak_heating,
                          peak_cooling=peak_cooling,
                          baseload_heating=monthly_load_heating,
                          baseload_cooling=monthly_load_cooling)

    borefield.set_ground_parameters(data)

    # set temperature boundaries
    borefield.set_max_ground_temperature(16)  # maximum temperature
    borefield.set_min_ground_temperature(0)  # minimum temperature

    borefield.size(100)
    print(borefield.H)
    borefield.print_temperature_profile()
