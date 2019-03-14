import os
from calibtool.CalibManager import CalibManager
from calibtool.algorithms.OptimTool import OptimTool
from calibtool.plotters.OptimToolPlotter import OptimToolPlotter
from dtk.utils.core.DTKConfigBuilder import DTKConfigBuilder
from dtk.vector.species import set_larval_habitat
from simtools.SetupParser import SetupParser
import itertools as it
from PointPrevalenceSite import PointPrevalenceSite
from dtk.interventions.heg import heg_release
from malaria.reports.MalariaReport import add_summary_report

# Set some general defaults
SetupParser.default_block = 'HPC'                                   # We want to run on COMPS
site = 'Hautlomami'                                                    # Which site do we want to run?
demographics_filename = "Hautlomami_node13.json"                       # Name of the demographics file
exp_name = site + '_calib'                                          # Name of the calibration
nyears = 50                                                         # Length of the simulations
release = False                                                     # Do we want to release mosquitoes?

# Define the parameters we want to change during the calibration
params = [
    {
        'Name': 'Temporary_Habitat',
        'Dynamic': True,
        'Guess': 1,
        'Min': 0.000001, ##changed from 0.00001
        'Max': 200 ##changed from 60, 600
    },
    {
        'Name': 'Constant_Habitat',
        'Dynamic': True,
        'Guess': 1,
        'Min': 0.0000001,
        'Max': 200
    }
]

cb = DTKConfigBuilder.from_defaults('MALARIA_SIM')

if release:
    # Set the releases
    start_days = [731, 1096, 1461]
    num_released = [100, 100, 100]
    # Add the releases to the CB
    for (num_released, release_day) in it.product(num_released, start_days):
        heg_release(cb, released_number=num_released, num_repetitions=1, node_list=[1535977513], start_day=release_day)

# Set the HEG parameters
cb.update_params({
    "HEG_Infection_Modification": .05,
    "HEG_Fecundity_Limiting": .1,
    "HEG_Homing_Rate": .95,
    "HEG_Model": "DRIVING_Y"
})

# Set general simulation parameters
cb.update_params({
    "Num_Cores": 1,
    "Age_Initialization_Distribution_Type": 'DISTRIBUTION_COMPLEX',
    "Simulation_Duration": nyears*365,
    "Enable_Demographics_Reporting": 1,
    "Enable_Demographics_Builtin": 0,
    "Valid_Intervention_States": [],
    "New_Diagnostic_Sensitivity": 0.05  # 20/uL
})

# match demographics file for constant population size (with exponential age distribution)
cb.update_params({
    "Birth_Rate_Dependence": "FIXED_BIRTH_RATE",
    "Enable_Nondisease_Mortality": 1
})

# Update Vector parameters
cb.update_params({
    "Vector_Migration_Base_Rate": 0.15,     # rate of migration between adjacent grid cells
    "Default_Geography_Initial_Node_Population": 1000,
    "Default_Geography_Torus_Size": 10,
    "Enable_Vector_Migration": 0,           ## this was on, but commented out
    "Enable_Vector_Migration_Human": 0,     ## this was commented out
    "Enable_Vector_Migration_Local": 0,     ## this was on, but commented out
    "Enable_Vector_Migration_Wind": 0,      ## this was commented out
    "Egg_Hatch_Density_Dependence": "NO_DENSITY_DEPENDENCE",
    "Temperature_Dependent_Feeding_Cycle": "NO_TEMPERATURE_DEPENDENCE",
    "Enable_Drought_Egg_Hatch_Delay": 0,
    "Enable_Egg_Mortality": 0,
    "Enable_Temperature_Dependent_Egg_Hatching": 0,
    "Vector_Species_Names": ["gambiae"],  # TODO: We are only selecting Gambiae for now
    "Vector_Migration_Modifier_Equation": "EXPONENTIAL"  # this was off in previous single node setting and was linear
})

# Update the file paths to match the selected site
cb.update_params({
    "Demographics_Filenames": [os.path.join("DRC", site, demographics_filename)],
    "Air_Temperature_Filename": os.path.join("DRC", site, "DemocraticRepublicOfTheCongo_30arcsec_air_temperature_daily.bin"),
    "Land_Temperature_Filename": os.path.join("DRC", site, "DemocraticRepublicOfTheCongo_30arcsec_air_temperature_daily.bin"),
    "Rainfall_Filename": os.path.join("DRC", site, "DemocraticRepublicOfTheCongo_30arcsec_rainfall_daily.bin"),
    "Relative_Humidity_Filename": os.path.join("DRC", site, "DemocraticRepublicOfTheCongo_30arcsec_relative_humidity_daily.bin")
})


def map_sample_to_model_input(cb, sample):
    hab = {'gambiae':{
        'TEMPORARY_RAINFALL': 1.5e8 * sample["Temporary_Habitat"],
        'CONSTANT': 5.5e6 * sample["Constant_Habitat"]
    }}
    set_larval_habitat(cb, hab)

    return sample


optimtool = OptimTool(params, center_repeats=1, samples_per_iteration=25)
calib_manager = CalibManager(name=exp_name,
                             config_builder=cb,
                             map_sample_to_model_input_fn=map_sample_to_model_input,
                             sites=[PointPrevalenceSite(site)],
                             next_point=optimtool,
                             sim_runs_per_param_set=1,
                             max_iterations=3,
                             plotters=[OptimToolPlotter()])

add_summary_report(cb, description='AnnualAverage')  ## add summary report of annual prevalence
run_calib_args = {
    "calib_manager": calib_manager
}

if __name__ == "__main__":
    SetupParser.init()
    cm = run_calib_args["calib_manager"]
    cm.run_calibration()
