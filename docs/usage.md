# Usage

The following describes the basic usage of HPCpy.

## Getting a client object

As the package aspires to be "scheduler agnostic" from the outset, the recommended way to get a client object suitable for the HPC you are on is to use the `get_client()` method as follows:

```python
from hpcpy import get_client
client = get_client()
```

This will return the most-likely client object based on the submission commands available on the system, raising a `NoClientException` if no host scheduler is detected. In the case of the factory being unable to return an appropriate client object (or if you need to be explicit), you may import the client explicitly for your system:

```python
from hpcpy import PBSClient, SLURMClient
client_pbs = PBSClient()
client_slurm = SLURMClient()
```

!!! note

    When using this approach you are bypassing any auto-detection of the host scheduler.

## Submit

The simplest way to submit a pre-written job script is via the `submit()` command, which executes the appropriate command for the scheduler:

=== "HPCpy (Python)"
    ```python
    job_id = client.submit("/path/to/script.sh")
    ```

=== "PBS"
    ```shell
    JOB_ID=$(qsub /path/to/script.sh)
    ```

=== "SLURM"
    ```shell
    JOB_ID=$(sbatch /path/to/script.sh)
    ```

### Environment Variables

=== "HPCpy (Python)"
    ```python
    job_id = client.submit(
        "/path/to/script.sh",
        variables=dict(a=1, b="test")
    )
    ```

=== "PBS"
    ```shell
    qsub -v a=1,b=test /path/to/script.sh
    ```

!!! note
    
    All environment variables are passed to the job as strings WITHOUT treatment of commas.

### Script templates

Script templates can be used to generalise a single template script for use in multiple scenarios (i.e. different scheduling systems).

*template.sh*
```shell
#!/bin/bash
echo "{{message}}"
```
*submit.py*
```python

job_id = client.submit(
    "/path/to/template.sh",
    render=True, # Note, this is False by default
    
    # Additional key/value pairs are added to rendering context
    message="Hello World."
)
```

This will do two things:

1. The template will be loaded into memory, rendered, and written to a temporary file at `$HOME/.hpcpy/job_scripts` (these are periodically cleared by hpcpy).
2. The rendered jobscript will be submitted to the scheduler.

Job script rendering has full access to the [Jinja2](https://jinja.palletsprojects.com/en/3.1.x/) template rendering system and may be as simple or as complex as needed.

If you want to check the output of a rendered template prior to actually submitting the job, you may access the private method to write the rendered job script without submitting it.

For example:

```python
job_script_filepath = client._render_job_script(
    "template.sh",
    message="Hello World!"
)
```

## Status

Checking the status of a job that has been submitted requires the `job_id` of the job on on the scheduler. Using the `submit()` command as above will return this identifier for use with the client.

=== "HPCpy (Python)"
    ```python
    status = client.status(job_id)
    ```
=== "PBS"
    ```shell
    STATUS=$(qstat -f -F json $JOB_ID)
    # ... then grepping through to find the job_state attribute
    ```

The status will be a character code as listed in `constants.py`, however, certain shortcut methods are available for the most common queries.

```python
# Check if the job is queued
client.is_queued(job_id)

# Check if the job is running
client.is_running(job_id)
```

More shorthand methods will be made available as required.

!!! note
    All status related commands will poll the underlying scheduler; please be mindful of overloading the scheduling system with repeated, frequent calls.

## Delete

Deleting a job on the system requires only the `job_id` of the job on the scheduler

=== "HPCpy (Python)"
    ```python
    client.delete(job_id)
    ```
=== "PBS"
    ```shell
    qdel $JOB_ID
    ```

## Task dependence

HPCpy implements a simple task-dependence strategy at the scheduler level, whereby, we can use scheduler directives to make one job dependent on another.

=== "HPCpy (Python)"
    ```python
    job1 = client.submit("job1.sh")
    job2 = client.submit("job2.sh", depends_on=job1)
    ```
=== "PBS"
    ```shell
    JOB1=$(qsub job1.sh)
    JOB2=$(qsub -W depend=afterok:$JOB1 job2.sh)
    ```

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