from calibtool.CalibSite import CalibSite

from PrevalenceAnalyzer import PrevalenceAnalyzer


class PointPrevalenceSite(CalibSite):

    prevalence_data = {
        "Hautlomami": 0.567717167

    }

    def __init__(self, name):
        super().__init__(name)

    def get_setup_functions(self):
        return []

    def get_reference_data(self, reference_type=None):
        return PointPrevalenceSite.prevalence_data[self.name]

    def get_analyzers(self):
        return [PrevalenceAnalyzer(self)]
