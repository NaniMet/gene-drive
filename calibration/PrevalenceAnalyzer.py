import os

import numpy as np
import pandas as pd
from simtools.Analysis.BaseAnalyzers import BaseCalibrationAnalyzer


class PrevalenceAnalyzer(BaseCalibrationAnalyzer):

    def __init__(self, site):
        self.site = site
        self.name = site.name
        super().__init__(filenames=['output\\MalariaSummaryReport_AnnualAverage.json'], uid='_'.join([self.site.name, self.name]))
        self.reference = self.site.get_reference_data()

    def select_simulation_data(self, data, simulation):
        # Get the prevalence data
        prevalence_per_year = data[self.filenames[0]]["DataByTime"]["PfPR_2to10"]

        point_prevalence = np.mean(prevalence_per_year[-16:-1])

        # Returns the data needed for this simulation
        ret = {
            "sample_index": simulation.tags.get('__sample_index__'),
            "prevalence": point_prevalence
        }
        for year, data in enumerate(prevalence_per_year):
            ret["prevalence_year_{}".format(year + 1)] = data

        return ret

    def finalize(self, all_data):
        keys = list(list(all_data.values())[0].keys())

        # Create the pandas frame
        df = pd.DataFrame(list(all_data.values()), columns=keys)
        df = df.groupby('sample_index').mean().reset_index()

        # Calculate the results
        def calculate_result(calculated_prevalence):
            if calculated_prevalence == 0:
                return -1000  # We really do not want prevalence to be 0...
            return -abs(self.reference - calculated_prevalence)

        df["result"] = df["prevalence"].apply(calculate_result)

        # Make sure we are indexing by sample_index
        df.set_index("sample_index")

        # Write the results to CSV file
        print(os.path.join(self.working_dir, "results.csv"))
        df.to_csv(os.path.join(self.working_dir, "results.csv"), index=False)

        return df["result"]

