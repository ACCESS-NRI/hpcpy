# Usage

The following describes the basic usage of hpcpy.

## Getting a client object

As the package aspires to be "scheduler agnostic" from the outset, the recommended way to get a client object suitable for the HPC you are on is to use the `get_client()` method as follows:

```python
from hpcpy import get_client
client = get_client()
```

This will return the most-likely client object based on the submission commands available on the system.

In the case of the factory being unable to return an appropriate client object (or if you need to be explicit), you may import the client explicitly for your system.

For example:

```python
from hpcpy import PBSClient
client = PBSClient()
```

You can now use the client object for the remaining examples.

## Submitting jobs

The simplest way to submit a pre-written job script is via the following command:

```python
job_id = client.submit("/path/to/script.sh")
```

However, oftentimes it is preferable to use a script template that is rendered with additional variables prior to submission. Depending on how this is written, a single script could be used for multiple scheduling systems.

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

## Checking job status

Checking the status of a job that has been submitted requires the `job_id` of the job on on the scheduler. Using the `submit()` command as above will return this identifier for use with the client.

```python
status = client.status(job_id)
```

The status will be a character code as listed in `constants.py`, however, certain shortcut methods are available for the most common queries.

```python
# Check if the job is queued
client.is_queued(job_id)

# Check if the job is running
client.is_running(job_id)
```

More shorthand methods will be made available as required.

Note: all status related commands will poll the underlying scheduler; please be mindful of overloading the scheduling system with repeated, frequent calls.

## Deleting jobs

Deleting a job on the system requires only the `job_id` of the job on the scheduler

```python
client.delete(job_id)
```