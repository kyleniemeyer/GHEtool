"""
This document compares the sizing with a constant Rb*-value with sizing where the Rb*-value is being recalculated.
For the test, the l_2 sizing method is used.
The comparison is based on speed and relative accuracy in the result.
It is shown that the speed difference is significant, but so is the difference in the result. With a constant Rb* value, it is important that the initial depth is rather accurate.
"""
if __name__ == "__main__":

    import numpy as np
    import time

    from GHEtool import Borefield, GroundData, FluidData, PipeData

    number_of_iterations = 50
    max_value_cooling = 700
    max_value_heating = 800

    # initiate the arrays
    results_Rb_static = np.empty(number_of_iterations)
    results_Rb_dynamic = np.empty(number_of_iterations)
    difference_results = np.empty(number_of_iterations)

    monthly_load_cooling_array = np.empty((number_of_iterations, 12))
    monthly_load_heating_array = np.empty((number_of_iterations, 12))
    peak_load_cooling_array = np.empty((number_of_iterations, 12))
    peak_load_heating_array = np.empty((number_of_iterations, 12))

    # populate arrays with random values
    for i in range(number_of_iterations):
        for j in range(12):
            monthly_load_cooling_array[i, j] = np.random.randint(0, max_value_cooling)
            monthly_load_heating_array[i, j] = np.random.randint(0, max_value_heating)
            peak_load_cooling_array[i, j] = np.random.randint(monthly_load_cooling_array[i, j], max_value_cooling)
            peak_load_heating_array[i, j] = np.random.randint(monthly_load_heating_array[i, j], max_value_heating)

    # initiate borefield model
    data = GroundData(100, 6, 3, 10, 0.2, 10, 12)  # ground data with an inaccurate guess of 100m for the depth of the borefield
    fluid_data = FluidData(0.2, 0.568, 998, 4180, 1e-3)
    pipe_data = PipeData(1, 0.015, 0.02, 0.4, 0.05, 0.075, 2)

    # Monthly loading values
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
    borefield.set_fluid_parameters(fluid_data)
    borefield.set_pipe_parameters(pipe_data)

    # set temperature boundaries
    borefield.set_max_ground_temperature(16)   # maximum temperature
    borefield.set_min_ground_temperature(0)    # minimum temperature

    # size with constant Rb* value
    borefield.use_constant_Rb = True  # True by default, you can also give 'use_constant_Rb = True' as an argument to the size function

    # calculate the Rb* value
    borefield.Rb = borefield.calculate_Rb()

    start_Rb_constant = time.time()
    for i in range(number_of_iterations):
        borefield.set_baseload_cooling(monthly_load_cooling_array[i])
        borefield.set_baseload_heating(monthly_load_heating_array[i])
        borefield.set_peak_cooling(peak_load_cooling_array[i])
        borefield.set_peak_heating(peak_load_heating_array[i])
        results_Rb_static[i] = borefield.size(100)
    end_Rb_constant = time.time()

    # size with a dynamic Rb* value
    borefield.use_constant_Rb = False

    start_Rb_dynamic = time.time()
    for i in range(number_of_iterations):
        borefield.set_baseload_cooling(monthly_load_cooling_array[i])
        borefield.set_baseload_heating(monthly_load_heating_array[i])
        borefield.set_peak_cooling(peak_load_cooling_array[i])
        borefield.set_peak_heating(peak_load_heating_array[i])
        results_Rb_dynamic[i] = borefield.size(100)
    end_Rb_dynamic = time.time()
    print(results_Rb_dynamic[1])

    print("These are the results when an inaccurate constant Rb* value is used.")
    print("Time for sizing with a constant Rb* value:", end_Rb_constant - start_Rb_constant, "s")
    print("Time for sizing with a dynamic Rb* value:", end_Rb_dynamic - start_Rb_dynamic, "s")

    # calculate differences
    for i in range(number_of_iterations):
        difference_results[i] = results_Rb_dynamic[i] - results_Rb_static[i]

    print("The maximal difference between the sizing with a constant and a dynamic Rb* value:", np.round(np.max(difference_results), 3), "m or", np.round(np.max(difference_results) / results_Rb_static[np.argmax(difference_results)] * 100, 3), "% w.r.t. the constant Rb* approach.")
    print("The mean difference between the sizing with a constant and a dynamic Rb* value:", np.round(np.mean(difference_results), 3), "m or", np.round(np.mean(difference_results) / np.mean(results_Rb_static) * 100, 3), "% w.r.t. the constant Rb* approach.")
    print("------------------------------------------------------------------------------")

    # Do the same thing but with another constant Rb* value based on a borehole depth of 185m.

    data = GroundData(185, 6, 3, 10, 0.2, 10, 12)  # ground data with an accurate guess of 185m for the depth of the borefield
    borefield.set_ground_parameters(data)

    # size with a constant Rb* value
    borefield.use_constant_Rb = True

    # calculate the Rb* value
    borefield.Rb = borefield.calculate_Rb()

    start_Rb_constant = time.time()
    for i in range(number_of_iterations):
        borefield.set_baseload_cooling(monthly_load_cooling_array[i])
        borefield.set_baseload_heating(monthly_load_heating_array[i])
        borefield.set_peak_cooling(peak_load_cooling_array[i])
        borefield.set_peak_heating(peak_load_heating_array[i])
        results_Rb_static[i] = borefield.size(100)
    end_Rb_constant = time.time()

    # size with a dynamic Rb* value
    borefield.use_constant_Rb = False

    start_Rb_dynamic = time.time()
    for i in range(number_of_iterations):
        borefield.set_baseload_cooling(monthly_load_cooling_array[i])
        borefield.set_baseload_heating(monthly_load_heating_array[i])
        borefield.set_peak_cooling(peak_load_cooling_array[i])
        borefield.set_peak_heating(peak_load_heating_array[i])
        results_Rb_dynamic[i] = borefield.size(100)
    end_Rb_dynamic = time.time()

    print("These are the results when an accurate constant Rb* value is used.")
    print("Time for sizing with a constant Rb* value:", end_Rb_constant - start_Rb_constant, "s")
    print("Time for sizing with a dynamic Rb* value:", end_Rb_dynamic - start_Rb_dynamic, "s")

    # calculate differences
    for i in range(number_of_iterations):
        difference_results[i] = results_Rb_dynamic[i] - results_Rb_static[i]

    print("The maximal difference between the sizing with a constant and a dynamic Rb* value:",
          np.round(np.max(difference_results), 3), "m or",
          np.round(np.max(difference_results) / results_Rb_static[np.argmax(difference_results)] * 100, 3),
          "% w.r.t. the constant Rb* approach.")
    print("The mean difference between the sizing with a constant and a dynamic Rb* value:",
          np.round(np.mean(difference_results), 3), "m or",
          np.round(np.mean(difference_results) / np.mean(results_Rb_static) * 100, 3),
          "% w.r.t. the constant Rb* approach.")
