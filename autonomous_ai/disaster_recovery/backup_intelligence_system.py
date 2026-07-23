"""Backup intelligence foundation for LaserSim recovery workflows."""


class BackupIntelligenceSystem:
    def __init__(self):
        self.backups = []

    def register_backup(self, backup):
        self.backups.append(backup)

    def latest_backup(self):
        return self.backups[-1] if self.backups else None
