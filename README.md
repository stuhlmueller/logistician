**This project is work-in-progress. I don't recommend that you try to use it just yet.**

----

# Logistician

Logistician makes it easy to prototype computational experiments locally and to deploy them to the cloud at scale. 

Features:

- **Fast local development loop** 

    For local development, Logistician directly uses code from your local project directory in order to make it easy to test changes without committing to repositories or constantly rebuilding docker images.
    
- **Reproducible experiments**

    Logistician uses [Docker](https://www.docker.com/community-edition) to ensure that local and remote executions run in the same environment. Remote experiments always run based on particular commits in Git repositories.
    
- **Large-scale experiments in the cloud**

    For exploring large parameter spaces, cloud deployment is parameterized by parameter sets. Logistician creates a cloud instance for each element of the set and uses [Terraform](https://www.terraform.io/) to automate setting up and shutting down large numbers of cloud machines.

- **Transparently built on standard tools**

    Logistician is a thin wrapper around Docker and Terraform and prints out all commands it issues. You can always switch to managing the containers and cloud instances using these native tools if additional functionality is needed.

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
logistician run --no-volume -o "1 2"

# Run locally (cloned from Github)
logistician run -o "1 2"

# Run remotely on AWS, retrieve the data, shut down (this will take a while)
cd examples/addition/experiments/1
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
cd /project
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
terraform deploy

# Sync data from AWS to experiment directory
logistician sync

# Shut down AWS instances
logistician terminate
```

## FAQ

**Why is Docker `push` failing on a connection with limited upload speed?**

Add `{"max-concurrent-uploads": 1}` to your `daemon.json`. If you're on Mac, you can do this using the Docker GUI via Preferences > Daemon > Advanced.

**What should I do if something goes wrong during `terraform apply`?**

Run `terraform destroy -var-file="./parameters.json" -var-file="~/.logistician/config.json" /path/to/logistician/terraform/aws/` in the experiment directory to clean up.

**How can I log into the cloud instances manually?**

Logistician saves the instance IP addresses in `ip-addresses.txt` in the experiment directory. Using these, you can log in using SSH:
    
```sh
ssh -i ~/.logistician/ssh-key ubuntu@54.153.54.33
```

## Limitations

Logistician currently does not support...

- Private git repositories
- Docker registries other than public Docker Hub
- Cloud providers other than AWS

## To discuss

- recording experimental setup (git commit id) and results (terminal log, files)
- for docker builds that clone from github, either need to point to particular commits (preferable) or rebuild with --no-cache