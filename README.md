**This project is work-in-progress. I don't recommend that you try to use it just yet.**

----

# Logistician

Logistician makes it easy to prototype computational experiments locally and to deploy them to the cloud at scale. 

## Interface

```
Usage: logistician [OPTIONS] COMMAND [ARGS]...

Options:
  --help  Show this message and exit.

Commands:
  create     Run interactive setup for a new experiment
  deploy     Run experiment in the cloud
  run        Run experiment locally
  setup      Run initial interactive setup for Logistician
  shell      Open shell in experiment environment
  status     Show deployment status
  sync       Sync all data from cloud to local machine
  terminate  Terminate cloud experiment
```


## Features

- **Fast local development loop** 

    For local development, Logistician directly uses code from your local project directory in order to make it easy to test changes without committing to repositories or constantly rebuilding docker images.
    
- **Reproducible experiments**

    Logistician uses [Docker](https://www.docker.com/community-edition) to ensure that local and remote executions run in the same environment. Remote experiments always run based on particular commits in Git repositories.
    
- **Large-scale experiments in the cloud**

    For exploring large parameter spaces, cloud deployment is parameterized by parameter sets. Logistician creates a cloud instance for each element of the set and uses [Terraform](https://www.terraform.io/) to automate setting up and shutting down large numbers of cloud machines.

- **Transparently built on standard tools**

    Logistician is a thin wrapper around Docker and Terraform and prints out all commands it issues. You can always switch to managing the containers and cloud instances using these native tools if additional functionality is needed.


## What it does

You have a project, let's say it's called `adversarial-rnn`.

```sh
# Go to project folder
cd /home/jane/adversarial-rnn

# Make sub-folder for experiments
mkdir experiments && cd experiments

# Create a new experiment
logistician create rnn-experiment-1
```

Logistician then asks you some questions about your experiment:

```
This script will interactively create a new experiment stored at:
/home/jane/adversarial-rnn/experiments/rnn-experiment-1

Globally unique experiment name [rnn-experiment-1]:
Remote Git URL [https://github.com/jane/adversarial-rnn.git]:
Experiment command (relative to project root): python src/run-rnn.py

Experiment created.
```

Now the experiments folder contains a sub-folder `rnn-experiment-1` with two files:
- `Dockerfile` describes the software environment for your experiment
- `parameters.json` describes the cloud machine setup (instance type, region, etc) and experiment conditions

These two files are sufficient to run your experiment locally and in the cloud. You can edit the `Dockerfile` to set up the environment for your experiment.

To run it locally, passing arguments to your experiment script:

```sh
logistician run ./rnn-experiment-1 -o "--learning-rate 0.01 --optimizer adam"
```

Once you're ready to run your experiment in the cloud, you edit `parameters.json` to add the arguments for all conditions:

```json
{
  "experiment_conditions": [
    "--learning-rate 0.1 --optimizer adam",
    "--learning-rate 0.01 --optimizer adam",
    "--learning-rate 0.001 --optimizer adam"
  ]
}
```

Create three AWS instances for the conditions above and run one condition on each:

```sh
logistician deploy ./rnn-experiment-1
```

Sync the logs and results from the instances to your local experiments folder:

```sh
logistician sync ./rnn-experiment-1
```

Shut down the instances:

```sh
logistician terminate ./rnn-experiment-1
```


## Installation

### Setup

1. Install [Docker](https://www.docker.com/community-edition) and log in using `docker login`

2. Install [Terraform](https://www.terraform.io/)

3. Install and configure Logistician:

    ```sh
    git clone https://github.com/stuhlmueller/logistician.git
    cd logistician
    pip install .
    logistician setup
    ```

### Test

To make sure everything is set up correctly, try running the example experiment:

```sh
# Go to experiment folder
cd logistician/examples/addition/experiments/1

# Build Docker image
logistician build

# Run locally (directly using project directory)
logistician run -o "1 2"

# Run locally (cloned from Github)
logistician run --clone -o "1 2"

# Run remotely on AWS, retrieve the data, shut down (this will take a while)
logistician deploy
logistician sync
logistician terminate
```

Note that running on AWS will incur (small) costs.

### Upgrade

To upgrade to the latest version of Logistician, run `git pull` in the cloned repository.

## Usage

### Assumptions

Your project lives in a local directory, say `/home/jane/my-project`.

This directory is a git repository that is mirrored remotely, say at `https://github.com/jane/my-project.git`.

The following assumes that there is an `experiments` folder in `my-project`, but you can use any folder under `my-project`to store your experiments and results.

### Creating a new experiment

Creating a new experiment with name `my-new-experiment`:

1. Copy `logistician/examples/addition/experiments/1` to `my-project/experiments/1`
2. Edit `my-project/experiments/1/Dockerfile` to reflect your experimental setup

Make sure to preserve the switch in `CMD` that supports both local and remote project directories.

### Local development

```sh
# Go to project directory
cd /home/jane/my-project

# Build Docker image (once, and whenever external dependencies change)
logistician build experiments/1

# Make changes to files in my-project

# Run the experiment script with command line args "foo bar=baz"
logistician run -o "foo bar=baz" experiments/1
```

To interact with the dev environment, try this:

```sh
docker shell
```

### Running experiments in the cloud

Once local development indicates that the experiment is ready to be run on the cloud:

```sh
# Go to project directory
cd /home/jane/my-project/

# Go to experiment folder
cd experiments/1

# Update parameters.json to reflect parameters we want to run in the cloud

# Commit & push to remote Git repository
git add -A; git commit -m "Created experiment 1"; git push

# Run experiment on AWS
logistician deploy

# Sync data from AWS to experiment directory
logistician sync

# Shut down AWS instances
logistician terminate
```

## FAQ

**Why is Docker `push` failing on a connection with limited upload speed?**

Add `{"max-concurrent-uploads": 1}` to your `daemon.json`. If you're on Mac, you can do this using the Docker GUI via Preferences > Daemon > Advanced.

**What should I do if something goes wrong during `terraform apply`?**

Run `logistician terminate` in the experiment directory to clean up.

**How can I log into the cloud instances manually?**

Logistician saves the instance IP addresses in `machines.txt` in the experiment directory. Using these, you can log in using SSH:
    
```sh
ssh -i ~/.logistician/ssh-key ubuntu@54.153.54.33
```

## Limitations

Logistician currently does not support...

- Private git repositories
- Docker registries other than public Docker Hub
- Cloud providers other than AWS

## To discuss

- Recording experimental setup (git commit id) and results (terminal log, files)
- For docker builds that clone from github, either need to point to particular commits (preferable) or rebuild with --no-cache
- Might want to use Docker Machine to orchestrate cloud deployments