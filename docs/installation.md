# Installation

## Stable release

`hpcpy` is installed via conda.

```shell
conda install -c accessnri hpcpy
```

## Development code

```shell
# Clone the repository
git clone git@github.com:ACCESS-NRI/hpcpy.git

# Create the environment, activate it
cd hpcpy
conda env create -f .conda/hpcpy-dev.yml
conda activate hpcpy_dev

# Install the package in editable mode inside the dev environment
pip install -e .

# Do you development work as normal.
```