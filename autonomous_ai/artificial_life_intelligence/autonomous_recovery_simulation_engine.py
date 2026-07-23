class AutonomousRecoverySimulationEngine:
    def __init__(self):
        self.simulations = []

    def run_simulation(self, failure_type, recovery_strategy, result):
        simulation = {
            "failure_type": failure_type,
            "recovery_strategy": recovery_strategy,
            "result": result
        }
        self.simulations.append(simulation)
        return simulation

    def get_results(self):
        return self.simulations
