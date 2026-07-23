"""Dataset utilities for 2D laser intensity maps."""

import torch
from torch.utils.data import Dataset


class BeamImageDataset(Dataset):
    def __init__(self, images, labels):
        self.images = images
        self.labels = labels

    def __len__(self):
        return len(self.labels)

    def __getitem__(self, index):
        image = torch.tensor(self.images[index], dtype=torch.float32)
        label = torch.tensor(self.labels[index], dtype=torch.long)
        if image.ndim == 2:
            image = image.unsqueeze(0)
        return image, label
