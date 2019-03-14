import os

import pandas as pd
from dtk.utils.analyzers.BaseAnalyzer import BaseAnalyzer
from simtools.AnalyzeManager.AnalyzeHelper import AnalyzeManager
from simtools.SetupParser import SetupParser


class InsetAnalyzer(BaseAnalyzer):

    def __init__(self, sweep_name, dir_name):
        super(InsetAnalyzer, self).__init__()

        self.dir_name = dir_name
        self.sweep_name = sweep_name
        self.filenames = ["output/InsetChart.json"]
        self.channels = ['Statistical Population', 'Parasite Prevalence', 'Adult Vectors', 'Wildtype Vector Fraction',
                         'New Diagnostic Prevalence', 'New Clinical Cases']
        self.data = pd.DataFrame()

    def apply(self, parser):

        simdata = pd.DataFrame()
        for channel in self.channels :
            channeldata = parser.raw_data[self.filenames[0]]['Channels'][channel]['Data']
            data = pd.DataFrame({channel: channeldata,
                                 'time': list(range(len(channeldata)))})
            if simdata.empty :
                simdata = data
            else :
                simdata = pd.merge(left=simdata, right=data, on='time')

        return simdata

    def combine(self, parsers):

        selected = [p.selected_data[id(self)] for p in parsers.values() if id(self) in p.selected_data]
        for i in range(len(selected)):
            selected[i]['Run_Number'] = i

        if len(selected) == 0:
            print("No data have been returned from apply... Exiting...")
            exit()

        self.data = pd.concat(selected).reset_index(drop=True)
        self.data['expt_name'] = self.dir_name

    def finalize(self):
        output_path = os.path.join(self.sweep_name, "%s.csv" % self.dir_name)
        self.data.to_csv(os.path.join(output_path), index=False)


if __name__ == "__main__":

    SetupParser.init("HPC")

    sweep_name = "NoDrive"
    sweep = {

        "Kwango_null": [
            "d488e16f-2f15-e911-a2bd-c4346bcb1555"
        ],
        "Nordubangui_null": [
            "ca9de450-2f15-e911-a2bd-c4346bcb1555"
        ],
        "Kinshasa_null": [
            "bd6dc3c9-2e15-e911-a2bd-c4346bcb1555"
        ],
        "Kasaicentral_null": [
            "f0c2ed93-2e15-e911-a2bd-c4346bcb1555"
        ],
        "Hautkatanga_null": [
            "5e8f0a53-2e15-e911-a2bd-c4346bcb1555"
        ],
        "Equateur_null": [
            "bc37ef04-2e15-e911-a2bd-c4346bcb1555"
        ],
        "Basuele_null": [
            "f36e2793-2d15-e911-a2bd-c4346bcb1555"
        ]

    }

    if not os.path.exists(sweep_name):
        os.mkdir(sweep_name)

    for dirname, exp_id in sweep.items():
        am = AnalyzeManager(exp_list=exp_id, analyzers=[InsetAnalyzer(sweep_name=sweep_name,
                                                                     dir_name=dirname,
                                                                     )],
                            force_analyze=True)

        print(am.experiments)
        am.analyze()
