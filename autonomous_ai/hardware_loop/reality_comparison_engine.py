"""Simulation versus real hardware comparison foundation."""


class RealityComparisonEngine:
    def compare(self, simulated_result, hardware_result):
        return {
            "simulation": simulated_result,
            "hardware": hardware_result,
            "matched": simulated_result == hardware_result,
        }
