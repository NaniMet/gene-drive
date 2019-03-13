import itertools as it
import os
from dtk.utils.core.DTKConfigBuilder import DTKConfigBuilder
from dtk.vector.species import set_larval_habitat
from simtools.ExperimentManager.ExperimentManagerFactory import ExperimentManagerFactory
from simtools.ModBuilder import ModFn, ModBuilder
from simtools.SetupParser import SetupParser
from interventions.heg import heg_release
from dtk.interventions.irs import add_IRS
from dtk.interventions.itn_age_season import add_ITN_age_season
from dtk.interventions.health_seeking import add_health_seeking


# set habitat scales
def set_habs_scale(cb, value=None):
    temp_h = value[0]
    const_h = value[1]

    hab = {'gambiae': {'TEMPORARY_RAINFALL': 1.5e8 * temp_h, 'CONSTANT': 5.5e6 * const_h}}
    set_larval_habitat(cb, hab)

    return {'temp_h': temp_h, 'const_h': const_h}


const_h = [2.40385E-05]
temp_h = [14.17386863]
habitat_scales = it.product(temp_h, const_h)

site = 'Basuele'
demographics_filename = "Basuele-25nodes.json"
air_temp_filename = "DemocraticRepublicOfTheCongo_30arcsec_air_temperature_daily.bin"
land_temp_filename = "DemocraticRepublicOfTheCongo_30arcsec_air_temperature_daily.bin"
rainfall_filename = "DemocraticRepublicOfTheCongo_30arcsec_rainfall_daily.bin"
relative_humidity_filename = "DemocraticRepublicOfTheCongo_30arcsec_relative_humidity_daily.bin"


exp_name = site + '_95%ITN-test'

nyears = 15

baseline_year = 0
'''
start_days = [(365 * baseline_year) + 1]
num_released = [200]  # released mosquitoes
release_combs = it.product(num_released, start_days)  # NOTE: this generates 656 pairs; coupled with 20 random seeds below results in 13120 sims; beware if running on a local machine...
'''

builder = ModBuilder.from_combos(
    #[ModFn(DTKConfigBuilder.set_param, 'HEG_Infection_Modification', im) for im in [1.0]],
    #[ModFn(DTKConfigBuilder.set_param, 'HEG_Fecundity_Limiting', fl) for fl in [0.05, 0.1, 0.15]],
    #[ModFn(DTKConfigBuilder.set_param, 'HEG_Homing_Rate', hr) for hr in [0.9, 0.95, 1.0]],
    #[ModFn(heg_release, num_released, d) for (num_released, d) in release_combs],

    [ModFn(set_habs_scale, habs) for habs in habitat_scales],  # set habitat scales
    [ModFn(DTKConfigBuilder.set_param, 'Run_Number', r) for r in range(1)]
)

cb = DTKConfigBuilder.from_defaults('MALARIA_SIM')

for year in range(0, nyears, 3):
    add_ITN_age_season(cb, start=(365 * (baseline_year+year)) + 1, coverage_all=0.95, seasonal_dep={'times': [0, 365], 'values': [0.65, 0.65]})
'''
for year in range(nyears):
    add_IRS(cb, start=(365 * (baseline_year + year)) + 1,
            coverage_by_ages=[{'min': 0, 'max': 100, 'coverage': 0.95}])

add_health_seeking(cb, start_day=(365 * baseline_year) + 1, targets=[{'trigger': 'NewClinicalCase', 'coverage': 0.95, 'agemin': 0, 'agemax': 100, 'seek': 1, 'rate': 0.3}])
'''
cb.update_params({
    'Num_Cores': 1,
    'Simulation_Duration': (nyears + baseline_year) * 365,
    # 'Simulation_Duration' : 500,
    'Enable_Demographics_Reporting': 1,
    'New_Diagnostic_Sensitivity': 0.05,  # 20/uL
    #'Listed_Events': ['Bednet_Using', 'Bednet_Got_New_One', 'Bednet_Discarded', 'Received_Treatment', 'Received_IRS']
})

# match demographics file for constant population size (with exponential age distribution)
cb.update_params({
    'Birth_Rate_Dependence': 'FIXED_BIRTH_RATE',
    'Enable_Nondisease_Mortality': 1
})

cb.update_params({"Vector_Migration_Base_Rate": 0.15,  # rate of migration between adjacent grid cells
                  "Default_Geography_Initial_Node_Population": 1000,
                  "Default_Geography_Torus_Size": 10,
                  "Migration_Model": "FIXED_RATE_MIGRATION",  ### changed from "NO_MIGRATION"
                  "Enable_Vector_Migration": 1,  ### changed to on
                  "Enable_Vector_Migration_Human": 0,
                  "Enable_Vector_Migration_Local": 1,  ### changed to on
                  "x_Vector_Migration_Local": 1, #### changed from 100
                  "Enable_Vector_Migration_Wind": 0,
                  "Vector_Migration_Filename_Local": "Basuele_local_Migration.bin",
                  "Egg_Hatch_Density_Dependence": "NO_DENSITY_DEPENDENCE",
                  "Temperature_Dependent_Feeding_Cycle": "NO_TEMPERATURE_DEPENDENCE",
                  "Enable_Drought_Egg_Hatch_Delay": 0,
                  "Enable_Egg_Mortality": 0,
                  "Enable_Temperature_Dependent_Egg_Hatching": 0,
                  "Vector_Migration_Modifier_Equation": "EXPONENTIAL",
                  "x_Temporary_Larval_Habitat": 1,
                  "Vector_Migration_Habitat_Modifier": 0, #### added
                  "Vector_Migration_Stay_Put_Modifier": 0 #### added
                  })
cb.update_params({
    "Demographics_Filenames": [os.path.join("DRC", site, demographics_filename)],
    "Air_Temperature_Filename": os.path.join("DRC", site, air_temp_filename),
    "Land_Temperature_Filename": os.path.join("DRC", site, land_temp_filename),
    "Rainfall_Filename": os.path.join("DRC", site, rainfall_filename),
    "Relative_Humidity_Filename": os.path.join("DRC", site, relative_humidity_filename)
     })

#Enable one mosq species
cb.update_params({'Vector_Species_Names': ['gambiae']})

cb.set_param("Enable_Demographics_Builtin", 0)
cb.set_param("Valid_Intervention_States", [])
cb.set_param("Enable_Demographics_Builtin", 0)
cb.set_param("Valid_Intervention_States", [])

# Enable spatial output
cb.update_params({
    "Enable_Spatial_Output": 1,
    "Spatial_Output_Channels": ["Adult_Vectors"]
})

'''
# HEG parameters
cb.update_params({
    'HEG_Model': 'DRIVING_Y'
})
'''

# When you run your scenarios, you will have to comment out the Serialization_Timesteps parameter and add two new parameters

cb.update_params({
    'Serialized_Population_Path': '//IAZCVFIL01.IDMHPC.AZR/IDM/Home/nmetchanun/output/Basuele_runin_20190205_105139/b0a/6f5/123/b0a6f512-3429-e911-a2bf-c4346bcb1554/output/',
    'Serialized_Population_Filenames': ['state-%05d.dtk' % (50 * 365)]})

run_sim_args = {'config_builder': cb,
                'exp_name': exp_name,
                'exp_builder': builder}

if __name__ == "__main__":
    SetupParser.init('HPC')
    sm = ExperimentManagerFactory.from_cb(cb)
    sm.run_simulations(**run_sim_args)
