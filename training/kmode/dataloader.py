"""PyTorch data loading utilities for K-mode beam training."""

try:
    import torch
    from torch.utils.data import Dataset, DataLoader
except ImportError:  # optional dependency
    torch = None


class BeamDataset(Dataset if torch else object):
    def __init__(self, features, labels):
        self.features = features
        self.labels = labels

    def __len__(self):
        return len(self.labels)

    def __getitem__(self, index):
        x = self.features[index]
        y = self.labels[index]
        if torch:
            return torch.tensor(x, dtype=torch.float32), torch.tensor(y, dtype=torch.long)
        return x, y


def create_loader(features, labels, batch_size=32, shuffle=True):
    dataset = BeamDataset(features, labels)
    return DataLoader(dataset, batch_size=batch_size, shuffle=shuffle) if torch else dataset
