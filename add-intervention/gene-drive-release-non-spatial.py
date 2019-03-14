import itertools as it
import numpy as np
import os

from dtk.interventions.outbreakindividual import recurring_outbreak
from dtk.interventions.heg import heg_release
from dtk.utils.reports.MalariaReport import add_immunity_report, add_summary_report
from dtk.utils.core.DTKConfigBuilder import DTKConfigBuilder
from dtk.utils.builders.sweep import GenericSweepBuilder
from dtk.vector.species import set_larval_habitat
from dtk.vector.study_sites import configure_site

from simtools.ModBuilder import ModFn, ModBuilder

from simtools.SetupParser import SetupParser


# set habitat scales
def set_habs_scale(cb, value = None):
    
    temp_h = value[0]
    const_h = value[1]
 
    hab = {'gambiae': {'TEMPORARY_RAINFALL': 1.5e8 * temp_h, 'CONSTANT': 5.5e6 * const_h}}
    set_larval_habitat(cb, hab)

    return {'temp_h' : temp_h, 'const_h': const_h}
    

site = 'Kwango'
geography = 'DRC/Kwango'
demographics_filename = "DRC_Kavumba_1_node_demographics.json"

exp_name  = site + '_gene_drive_example'

nyears = 5

#####temp_h = [0.5, 1, 1.5, 2, 2.5, 3, 4, 5, 7, 10]
#####const_h = [0.5, 1, 1.5, 2, 2.5, 3, 4, 5, 7, 10]
temp_h = [3.001]
const_h = [0.94]
habitat_scales = it.product(temp_h, const_h)

'''
start_days = range(275, 560, 7)
num_released = range(1, 32, 2)
release_combs = it.product(num_released, start_days) 
'''
####start_days = [731] # release is at day 1461
start_days = [731,1096,1461] # release is at day 240,300,605,665
#start_days = range(275,560,7) # release start day between 275 and 560 with increments of 7 days
####num_released = [300] # released mosquitoes
num_released = [100,100,100] # released mosquitoes
######num_released = [100] # released mosquitoes
release_combs = it.product(num_released, start_days) 

#release_combs = it.product(num_released, start_days) 
#start_days = range(180, 181)
#num_released = range(200, 201)
#release_combs = it.product(num_released, start_days) # NOTE: this generates 656 pairs; coupled with 20 random seeds below results in 13120 sims; beware if running on a local machine...


print habitat_scales

builder = ModBuilder.from_combos(
                                    [ModFn(DTKConfigBuilder.set_param, 'HEG_Infection_Modification', im) for im in [0.05]],
                                    #[ModFn(DTKConfigBuilder.set_param, 'HEG_Fecundity_Limiting', fl) for fl in [0.9,0.3]],
                                    [ModFn(DTKConfigBuilder.set_param, 'HEG_Fecundity_Limiting', fl) for fl in [0.1]],
                                    #[ModFn(DTKConfigBuilder.set_param, 'HEG_Homing_Rate', hr) for hr in [0.95,0.4]],
                                    [ModFn(DTKConfigBuilder.set_param, 'HEG_Homing_Rate', hr) for hr in [0.95]],
                                    [ModFn(set_habs_scale, habs) for habs in habitat_scales], # set habitat scales
                                    #[ModFn(heg_release, num_released, num_repetitions = 1, node_list = [1535977513], start_day = d) for (num_released, d)  in release_combs],
                                    #[ModFn(configure_site, site)],
                                    [ModFn(heg_release, num_released, num_repetitions = 1, node_list = [1535977513], start_day = d) for (num_released, d)  in release_combs],
                                    [ModFn(configure_site, site)],
                                    
                                    #[ModFn(DTKConfigBuilder.set_param, 'Run_Number', r) for r in range(1, 21)]
                                    [ModFn(DTKConfigBuilder.set_param, 'Run_Number', r) for r in range(1, 2)]
                                )




cb = DTKConfigBuilder.from_defaults('MALARIA_SIM')

cb.update_params({
                'Geography': geography,
                'Num_Cores': 1,
                'Simulation_Duration' : nyears*365,
                #'Simulation_Duration' : 500,
                'Enable_Demographics_Reporting': 1,
                'New_Diagnostic_Sensitivity': 0.05 # 20/uL
                })


# match demographics file for constant population size (with exponential age distribution)
cb.update_params({
                'Birth_Rate_Dependence': 'FIXED_BIRTH_RATE', 
                'Enable_Nondisease_Mortality': 1
                })

cb.update_params({"Vector_Migration_Base_Rate": 0.15, # rate of migration between adjacent grid cells
                  "Default_Geography_Initial_Node_Population": 1000, 
                  "Default_Geography_Torus_Size": 10,
                  #"Enable_Vector_Migration": 1,
                  #"Enable_Vector_Migration_Human":0,
                  #"Enable_Vector_Migration_Local":1,
                  #"Enable_Vector_Migration_Wind":0,
                  "Egg_Hatch_Density_Dependence":"NO_DENSITY_DEPENDENCE",
                  "Temperature_Dependent_Feeding_Cycle": "NO_TEMPERATURE_DEPENDENCE",
                  "Enable_Drought_Egg_Hatch_Delay":0,
                  "Enable_Egg_Mortality":0,
                  "Enable_Temperature_Dependent_Egg_Hatching":0,
                  #"Vector_Migration_Modifier_Equation": "LINEAR"
                  })


#cb.update_params({'Climate_Model':'CLIMATE_CONSTANT'})

cb.set_param("Enable_Demographics_Builtin", 0)
cb.set_param("Valid_Intervention_States", [])
#cb.set_param("Enable_Memory_Logging", 1)

#cb.update_params({'Climate_Model':'CLIMATE_CONSTANT'})


# HEG parameters

cb.update_params({
                  #'HEG_Model':'DUAL_GERMLINE_HOMING',
                  'HEG_Model':'DRIVING_Y',
                  });
                  

run_sim_args =  {'config_builder': cb,
                 'exp_name': exp_name,
                 'exp_builder': builder}


if __name__ == "__main__":

    from dtk.utils.core.DTKSetupParser import DTKSetupParser
    from simtools.ExperimentManager import ExperimentManagerFactory

    sm = ExperimentManagerFactory.from_model(DTKSetupParser().get('BINARIES', 'exe_path'), 'LOCAL')
    sm.run_simulations(**run_sim_args)
