# Job Dependency

HPCpy provides an interface into the scheduler-level dependency graph architecture, allowing you to submit jobs which are dependent on the states of upstream jobs. For instance, `job2` only running on the successful completion of `job1` etc.

The `depends_on` keyword accepts a list, where each element is either:
- A single element of type `Job` or `str` (the Job ID), or
- A 2-tuple of `(status, Job or str)` where `status` is a string  defined by table below.

!!! note
    Providing a singular element to the list (rather than a 2-tuple) implies `afterok` for simply success-based dependency.

    i.e.

    ```python
    client.submit(depends_on=[job1])
    # is equivalent to
    client.submit(depends_on=[("afterok", job1)])
    ```

## Job statuses

The following is a table of the supported status for building out job dependency.

!!! warning
    Using the `before*` statuses with SLURM will raise a `ValueError` as the scheduler does not support them.

|Status|Description|PBS|SLURM|
|-|-|-|-|
|`after`|This job may be scheduled for execution at any point after all jobs in <arg_list> have started execution.|✅|✅|
|`afterok`|This job may be scheduled for execution only after all jobs in <arg_list> have terminated with no errors.|✅|✅|
|`afternotok`|This job may be scheduled for execution only after all jobs in <arg_list> have terminated with errors.|✅|✅|
|`afterany`|This job may be scheduled for execution after all jobs in <arg_list> have finished execution, with any exit status (with or without errors.) This job will not run if a job in the <arg_list> was deleted without ever having been run.|✅|✅|
|`before`|Jobs in <arg_list> may begin execution once this job has begun execution.|✅|❌|
|`beforeok`|Jobs in <arg_list> may begin execution once this job terminates without errors.|✅|❌|
|`beforenotok`|If this job terminates execution with errors, jobs in <arg_list> may begin.|✅|❌|
|`beforeany`|Jobs in <arg_list> may begin execution once this job terminates execution, with or without errors.|✅|❌|

## Example

The following examples are equivalent.

=== "HPCpy (Python)"
    ```python
    job1 = client.submit("job1.sh")
    job2 = client.submit("job2.sh")
    job3 = client.submit("job3.sh", depends_on=[job1.id, job2])
    ```
=== "PBS"
    ```shell
    JOB1=$(qsub job1.sh)
    JOB2=$(qsub job2.sh)
    JOB3=$(qsub -W depend=afterok:$JOB1:$JOB2 job3.sh)
    ```
=== "SLURM"
    ```shell
    JOB1=$(sbatch job1.sh)
    JOB2=$(sbatch job2.sh)
    JOB3=$(sbatch --dependency=afterok:$JOB1:$JOB2 job3.sh)
    ```