"""Generic Job class."""

class Job:

    def __init__(self, job_id, client):
        self.job_id = job_id
        self.client = client
        self.status = None
    
    def get_status(self):
        self.status = self.client.status(self.job_id)
        return self.status

    def delete(self):
        """Delete the job from the scheduler"""
        self.client.delete(self.job_id)

    def hold(self):
        """Hold the job on the scheduler"""
        self.client.hold(self.job_id)
    
    def release(self):
        """Release the job from the scheduler"""
        self.client.release(self.job_id)