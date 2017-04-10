**This project is work-in-progress. We don't recommend that you try to use it just yet.**

----

# Logistician

Logistician makes it easy to prototype computational experiments locally and to deploy them to the cloud at scale. 

Features:

- **Fast local development loop** 

    For local development, Logistician directly uses code in a local directory in order to make it easy to test changes without committing to repositories or rebuilding docker images.
    
- **Reproducible experiments**

    Logistician uses [Docker](https://www.docker.com/community-edition) to ensure that local and remote executions run in the same environment. Remote experiments always run based on particular commits in Git repositories.
    
- **Large-scale experiments in the cloud**

    For exploring large parameter spaces, cloud deployment is parameterized by parameter sets. Logistician creates a cloud instance for each element of the set and uses [Terraform](https://www.terraform.io/) to automate setting up and shutting down large numbers of cloud machines.

- **Transparently built on standard tools**

    Logistician mostly doesn't provide its own command-line tools. By directly working with Docker and Terraform commands, you have access to all of the functionality these tools provide.

## Installation

### Setup

1. Install [Docker](https://www.docker.com/community-edition) and log in using `docker login`

    Logistician will use a Docker repository called `experiments` to store all images.

2. Install [Terraform](https://www.terraform.io/)

3. Provide [AWS Credentials for Terraform](https://www.terraform.io/docs/providers/aws/) via [environment variables](https://docs.aws.amazon.com/cli/latest/userguide/cli-chap-getting-started.html#cli-environment) or a [credentials file](https://docs.aws.amazon.com/cli/latest/userguide/cli-chap-getting-started.html#cli-config-files)

    For example, you can find your access and secret key following [these instructions](https://docs.aws.amazon.com/general/latest/gr/managing-aws-access-keys.html) and, if you're on Linux or Mac, create a file `~/.aws/credentials` that looks like this:
    
    ```ini
    [default]
    aws_access_key_id=AKIAIOSFODNN7EXAMPLE
    aws_secret_access_key=wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY
    ```

4. Clone Logistician: 

    ```sh
    git clone https://github.com/stuhlmueller/logistician.git
    ```

5. Generate SSH key by running `./scripts/generate-ssh-key` in the Logistician root directory

6. Store Docker info by running `./scripts/configure-docker` in the Logistician root directory


### Test

To make sure everything is set up correctly, try running the example experiment:

```sh
# Go to project folder
cd logistician

# Build Docker image
docker build -t addition-expt-1 example-projects/addition/experiments/1

# Run locally (directly using project directory)
docker run -v `pwd`:/project -e OPTIONS="1 2" -it addition-expt-1

# Run locally (cloned from Github)
docker run -e OPTIONS="1 2" -it addition-expt-1

# Run remotely on AWS (this will take a while)
terraform apply ../../../../terraform/aws/
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

1. Copy `logistician/example-projects/addition/experiments/1` to `my-project/experiments/1`
2. Edit `my-project/experiments/1/Dockerfile` to reflect your experimental setup

Make sure to preserve the switch in `CMD` that supports both local and remote project directories.

### Local development

```sh
# Go to project directory
cd /home/jane/my-project

# Build Docker image (once, and whenever external dependencies change)
docker build -t my-experiment-1 experiments/1

# Make changes to files in my-project

# Run the experiment script with command line args "foo bar=baz"
docker run -v `pwd`:/project -e OPTIONS="foo bar=baz" -it my-experiment-1
```

To interact with the dev environment, try this:

```sh
docker run -v `pwd`:/project -it my-first-experiment bash
cd /project
```

### Running experiments in the cloud

Once local development indicates that the experiment is ready to be run on the cloud:

```sh
# Go to project directory
cd /home/jane/my-project/

# Go to experiment folder
cd experiments/1

# Update parameters.tfvars to reflect parameters we want to run in the cloud

# Commit & push to remote Git repository
git add -A; git commit -m "Created experiment 1"; git push

# Run experiment on AWS
terraform apply /path/to/logistician/terraform/aws/
```

## FAQ

**Why is Docker `push` failing on a connection with limited upload speed?**

Add `{"max-concurrent-uploads": 1}` to your `daemon.json`. If you're on Mac, you can do this using the Docker GUI via Preferences > Daemon > Advanced.

**What should I do if something goes wrong during `terraform apply`?**

Run `terraform destroy /path/to/logistician/terraform/aws/` in the experiment directory to clean up.

**How can I log into the cloud instances manually?**

Logistician saves the instance IP addresses in `ip-addresses.txt` in the experiment directory. Using these, you can log in using SSH:
    
```sh
ssh -i /path/to/logistician/config/ssh-keys/ssh-key ubuntu@54.153.54.33
```

## Limitations

Logistician currently does not support...

- Private git repositories
- Private Docker registries
- Cloud providers other than AWS

## To discuss

- recording experimental setup (git commit id) and results (terminal log, files)
- shutting down instances
- for docker builds that clone from github, either need to point to particular commits (preferable) or rebuild with --no-cache