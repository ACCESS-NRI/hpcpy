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

The simplest way to submit a pre-written job script is via the `submit()` command, which executes the appropriate command for the scheduler. Submitting a job will return a `Job` object from which you can interact with the scheduler.

=== "HPCpy (Python)"
    ```python
    job = client.submit("/path/to/script.sh")
    ```

=== "PBS"
    ```shell
    qsub /path/to/script.sh
    ```

=== "SLURM"
    ```shell
    sbatch /path/to/script.sh
    ```

### Environment Variables

=== "HPCpy (Python)"
    ```python
    job = client.submit(
        "/path/to/script.sh",
        variables=dict(a=1, b="test")
    )
    ```

=== "PBS"
    ```shell
    qsub -v a=1,b=test /path/to/script.sh
    ```

=== "SLURM"
    ```shell
    # Environment variables are exported to the job
    export a=1
    export b="test"
    sbatch /path/to/script.sh
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

job = client.submit(
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

To access the status of a job on the scheduler, simply call the `status()` method on the `Job` object:

=== "HPCpy (Python)"
    ```python
    status = job.status()
    ```
=== "PBS"
    ```shell
    qstat -f -F json $JOB_ID
    ```
=== "SLURM"
    ```shell
    squeue -j $JOB_ID
    ```

You may also access the status directly through the client, if you have the `job_id` readily at hand via the following command:

=== "HPCpy (Python)"
    ```python
    status = client.status(job_id)
    ```

The status will be a character code as listed in `constants/__init__.py`, however, certain shortcut methods are available for the most common queries.

```python
# Check if the job is queued, using the client
client.is_queued(job_id)

# Check if the job is running, using the client
client.is_running(job_id)
```

More shorthand methods will be made available as required.

!!! note
    All status related commands will poll the underlying scheduler; please be mindful of overloading the scheduling system with repeated, frequent calls.

## Delete

Deleting a job is accomplished by calling the delete method on either the client or the job object:

=== "HPCpy (Python)"
    ```python
    # For when you have the ID
    client.delete(job_id)

    # For when you are using the job object
    job.delete()
    ```

=== "PBS"
    ```shell
    qdel $JOB_ID
    ```

=== "SLURM"
    ```shell
    scancel $JOB_ID
    ```

## Job dependency

You can create dependency between jobs using the underlying scheduler. See [Job Dependency](dependency.md)