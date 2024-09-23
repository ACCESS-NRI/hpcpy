# Advanced Usage

The following documentation describes what we'll consider "Advanced Usage", that is, whatever might require more than a few lines of code.

## Task dependence

HPCpy implements a simple task-dependence strategy at the scheduler level, whereby, we can use scheduler directives to make a job dependent on another.

Consider the following snippet:

```python
from hpcpy import get_client
client = get_client()

# Submit the first job
first_id = client.submit("job.sh")

# Submit some interim jobs all requiring the first to finish
job_ids = list()
for x in range(3):
    jobx_id = client.submit("job.sh", depends_on=first_id)
    job_ids.append(jobx_id)

# Submit a final job that requires everything to have finished.
job_last = client.submit("job.sh", depends_on=job_ids)
```

This will create 5 jobs:
- 1 x starting job
- 3 x middle jobs (which depend on the first)
- 1 x finishing job (which depends on the middle jobs to complete)

Essentially demonstrating a "fork and join" example.

More advanced graphs can be assembled as needed, the complexity of which is determined by your scheduler.