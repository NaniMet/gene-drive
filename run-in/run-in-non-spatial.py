import itertools as it
import os
from dtk.utils.core.DTKConfigBuilder import DTKConfigBuilder
from dtk.vector.species import set_larval_habitat
from simtools.ExperimentManager.ExperimentManagerFactory import ExperimentManagerFactory
from simtools.ModBuilder import ModFn, ModBuilder
from simtools.SetupParser import SetupParser


# set habitat scales
def set_habs_scale(cb, value=None):
    temp_h = value[0]
    const_h = value[1]

    hab = {'gambiae': {'TEMPORARY_RAINFALL': 1.5e8 * temp_h, 'CONSTANT': 5.5e6 * const_h}}
    set_larval_habitat(cb, hab)

    return {'temp_h': temp_h, 'const_h': const_h}


const_h = [5.6217885208653975]
temp_h = [12.424280532176581]
habitat_scales = it.product(temp_h, const_h)

site = 'Hautkatanga'
demographics_filename = "Hautkatanga_node13.json"
air_temp_filename = "DemocraticRepublicOfTheCongo_30arcsec_air_temperature_daily.bin"
land_temp_filename = "DemocraticRepublicOfTheCongo_30arcsec_air_temperature_daily.bin"
rainfall_filename = "DemocraticRepublicOfTheCongo_30arcsec_rainfall_daily.bin"
relative_humidity_filename = "DemocraticRepublicOfTheCongo_30arcsec_relative_humidity_daily.bin"

exp_name = site + '_baseline_single'

nyears = 50

builder = ModBuilder.from_combos(
    [ModFn(set_habs_scale, habs) for habs in habitat_scales],  # set habitat scales
    [ModFn(DTKConfigBuilder.set_param, 'Run_Number', r) for r in range(1)]
)

cb = DTKConfigBuilder.from_defaults('MALARIA_SIM')

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
    'Birth_Rate_Dependence': 'FIXED_BIRTH_RATE',
    'Enable_Nondisease_Mortality': 1
})

cb.update_params({"Vector_Migration_Base_Rate": 0.15,  # rate of migration between adjacent grid cells
                  "Default_Geography_Initial_Node_Population": 1000,
                  "Default_Geography_Torus_Size": 10,
                  "Migration_Model": "NO_MIGRATION",  ### changed from "FIXED_RATE_MIGRATION"
                  "Enable_Vector_Migration": 0,  ### changed to off
                  "Enable_Vector_Migration_Human": 0,
                  "Enable_Vector_Migration_Local": 0,  ### changed to off
                  "x_Vector_Migration_Local": 100,
                  "Enable_Vector_Migration_Wind": 0,
                  "Vector_Migration_Filename_Local": "",
                  "Egg_Hatch_Density_Dependence": "NO_DENSITY_DEPENDENCE",
                  "Temperature_Dependent_Feeding_Cycle": "NO_TEMPERATURE_DEPENDENCE",
                  "Enable_Drought_Egg_Hatch_Delay": 0,
                  "Enable_Egg_Mortality": 0,
                  "Enable_Temperature_Dependent_Egg_Hatching": 0,
                  "Vector_Migration_Modifier_Equation": "EXPONENTIAL"
                  })

cb.update_params({
    "Demographics_Filenames": [os.path.join("DRC", site, demographics_filename)],
    "Air_Temperature_Filename": os.path.join("DRC", site, air_temp_filename),
    "Land_Temperature_Filename": os.path.join("DRC", site, land_temp_filename),
    "Rainfall_Filename": os.path.join("DRC", site, rainfall_filename),
    "Relative_Humidity_Filename": os.path.join("DRC", site, relative_humidity_filename)
     })

# Enable one mosq species
cb.update_params({'Vector_Species_Names': ['gambiae']})

cb.set_param("Enable_Demographics_Builtin", 0)
cb.set_param("Valid_Intervention_States", [])
cb.set_param("Enable_Demographics_Builtin", 0)
cb.set_param("Valid_Intervention_States", [])

# Save
cb.update_params({'Serialization_Time_Steps': [50 * 365]})

run_sim_args = {'config_builder': cb,
                'exp_name': exp_name,
                'exp_builder': builder}

if __name__ == "__main__":
    SetupParser.init('HPC')
    sm = ExperimentManagerFactory.from_cb(cb)
    sm.run_simulations(**run_sim_args)
