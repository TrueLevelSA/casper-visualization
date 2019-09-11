## Matlab visualization

## Python visualization

### Preqrequisites
- Python 3.7
- `pipenv` (`pip install pipenv`)
  - In case there is an error such as `module is not callable` in the install phase, downgrade pip `pip install pip==18.0` and `pipenv run pip install pip==18.0`
- Rust's cargo if you want to run simulations. 
  In this case, don't use repo as-is but use core-cbc: `git clone core-cbc`, `git submodules init`, `cd visualization`)

### Install
- `pipenv install`

### Run
- `pipenv run jupyter notebook`
- If the figure is not interactive, you may have to re-run all cells (manually?) to activate the interactive mode.

### Run (standalone)
- Install [tcl/tk](https://tcl.tk/)
  - `sudo apt-get install tk` or `sudo pacman -S tk`
- `pipenv run python visualization.py`
or
- `pipenv run python process_metrics.py`
- `pipenv run python visualization_metrics.py`

### Scripts
- `process_metrics.py`
  Process all `stats*.log` files located in the parent folder.
  Outputs two files:
  - `gen.csv` which contains data points each time a validator reaches a new consensus height.
  - `gen_averages.csv` which is the average for all values for all validators for each run.
- `aggregate.sh`
  Aggregates all the csv files located in `./generated/backup/` that start with the prefixed passed as argument.
  Output files are `./gen.csv` and `./gen_averages.csv`.
- `start_testing.sh`
  starts multiple runs of the `blockchain` integration test. saves all the log files, as well as the `gen.csv` and `gen_averages.csv`.
  parameters:
  - `prefix`: prefix of the log files
  - `nb_jobs`: number of rust testing jobs  

  example: `./start_testing.sh double_round_robin 8`
- `process.sh`
  Extracts blockchain view from a single `blockchain` integration test run. Extracted json files are saved into `./generated/processed_states*.log`
- `visualization.py`
  Shows blockchain views contained in `generated/processed_states*.log`

### Usage
#### Run simulations
If you want to run simulations:
- Go to `../tests/generative_tests.rs`
  - In the `fn blockchain()` test, in the `runner.run` function:
    Change parameters, such as height, receiver strategy, sender strategy, consensus height, number of nodes.
- In the `start_testing.sh` script: change the number of executions in the main function.
- Run `start_testing.sh prefix core` and go grab a coffee.
  You should now have a bunch of `gen*.csv` files in `generated/backup/`
- Run `aggregate.sh prefix` to aggregate all the files in `generated/backup/`
- You can now visualize the data using the next chapter

#### Use visualizations
- Launch jupyter `pipenv run jupyter-notebook`
  - This opens jupyter in your browser.
- Open the `visualization_metrics.ipynb` in jupyter
- If you want to see all the graphs with the data available on the repository:
  - Click `Kernel>Restart and Run All`
- If you want to show data that are just out of your simulations:
  - Change `if False` into `if True` in the second cell.
  - Run the two first cells of the notebook. (Shift-Enter)
