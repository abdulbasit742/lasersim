"""AI cloud resource auto provisioning foundation."""

class AICloudResourceAutoProvisioning:
    def __init__(self):
        self.resources = []

    def provision(self, resource_type, amount):
        item = {"resource_type": resource_type, "amount": amount}
        self.resources.append(item)
        return item
