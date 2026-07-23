class ModelQualityGate:
    def __init__(self, threshold=0.90):
        self.threshold = threshold

    def validate(self, accuracy):
        return accuracy >= self.threshold


if __name__ == '__main__':
    gate = ModelQualityGate()
    print(gate.validate(0.95))
