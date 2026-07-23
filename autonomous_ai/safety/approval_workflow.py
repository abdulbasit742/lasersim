class ApprovalWorkflow:
    """Human approval gate for autonomous experiments."""

    def __init__(self):
        self.pending_requests = []

    def request_approval(self, experiment):
        request = {
            "experiment": experiment,
            "status": "pending"
        }
        self.pending_requests.append(request)
        return request

    def approve(self, index):
        self.pending_requests[index]["status"] = "approved"
        return self.pending_requests[index]
