#!/usr/bin/env python

import click
import json
import os
import subprocess


LOGISTICIAN_ROOT = os.path.dirname(os.path.abspath(__file__))

CONFIG_PATH = os.path.expanduser("~/.logistician/")



def create_config_directory():
    if not os.path.exists(CONFIG_PATH):
        os.makedirs(CONFIG_PATH)


def load_params(experiment_path):
    params_filename = os.path.join(experiment_path, "parameters.json")
    g = open(params_filename)
    params = json.load(g)
    g.close()
    return params


def echo_command_string(s):
    click.secho(s, fg='green')


def verbose_call(cmd):
    echo_command_string(subprocess.list2cmdline(cmd))
    subprocess.call(cmd)


def config():
    """
    Interactively create config file
    """
    create_config_directory()
    docker_username = click.prompt("Please enter your Docker Hub username")
    docker_repository = click.prompt("Please enter your preferred Docker repository name", "experiments")
    aws_access_key = click.prompt("Please enter your AWS access key (e.g., AKIAIOSFODNN7EXAMPLE)")
    aws_secret_key = click.prompt("Please enter your AWS secret key (e.g., wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY)")
    configuration = {
        "aws_access_key": aws_access_key,
        "aws_secret_key": aws_secret_key,
        "docker_username": docker_username,
        "docker_repository": docker_repository
    }
    f = open(os.path.join(CONFIG_PATH, "config.json"), "w")
    json.dump(configuration, f)
    f.close()


def create_ssh_key():
    """
    Create and store SSH key
    """
    create_config_directory()
    private_key_path = os.path.join(CONFIG_PATH, "ssh-key")
    if os.path.exists(private_key_path):
        click.echo("File already exists at {0}".format(private_key_path))
    else:
        verbose_call(["ssh-keygen", "-t", "rsa", "-b", "4096", "-f", private_key_path, "-P", ""])


def build(experiment_path):
    """
    Build Docker image for experiment
    """
    params = load_params(experiment_path)
    experiment_name = params["experiment_name"]
    click.echo("Building Docker image for {0}".format(experiment_name))
    verbose_call(["docker", "build", "-t", experiment_name, experiment_path])
    click.echo("Docker build done.")


def get_project_path(file_path):
    cmd = "cd '{0}' && git rev-parse --show-toplevel".format(file_path)
    echo_command_string(cmd)
    p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    p.wait()
    return p.stdout.read().strip()



@click.group()
def cli():
    pass


@click.command()
@click.pass_context
def setup(ctx):
    """
    Run initial interactive setup for Logistician
    """
    click.echo("This is the interactive setup for Logistician.")
    config()
    create_ssh_key()
    click.echo("Configuration done.")


@click.command()
@click.argument('experiment_path', type=click.Path(exists=True, dir_okay=True, writable=True, readable=True, resolve_path=True),
                default=lambda: os.getcwd())
def sync(experiment_path):
    """
    Sync all data from cloud to local machine
    """
    # Load IP addresses
    machines_filename = os.path.join(experiment_path, "machines.txt")
    if not os.path.exists(machines_filename):
        click.echo("Machine file {0} does not exist. Can't sync.".format(machines_filename))
        return
    f = open(machines_filename)
    machines = [line.strip().split(", ") for line in f.read().strip().split("\n")]
    f.close()

    # Load AWS AMI user
    params = load_params(experiment_path)
    aws_ami_user = params["aws_ami_user"]

    # Create data folder if it doesn't exist
    verbose_call(["mkdir", "-p", os.path.join(experiment_path, "data/")])

    for (ip, condition) in machines:

        remote_address = "{0}@{1}".format(aws_ami_user, ip)
        local_path = os.path.join(experiment_path, "data/", condition)

        click.echo("Syncing {0} to {1}".format(remote_address, local_path))

        # Copy latest Docker logs to remote data directory
        verbose_call(["ssh", "-o", "StrictHostKeyChecking no", "-i", "~/.logistician/ssh-key", remote_address,
                      "sudo bash -c 'docker logs `docker ps -aq | head -n 1` > /data/logs/docker.txt'"])

        # Retrieve remote data directory
        verbose_call(["rsync", "-azvv", "-e", "ssh -i ~/.logistician/ssh-key", "{0}:/data/".format(remote_address), local_path])

    click.echo("Syncing done.")


@click.command()
@click.option('--options', '-o', help='Options to pass to experiment script', default='')
@click.option('--clone/--no-clone', help='Clone from remote repo, don\'t use project folder', default=False)
@click.argument('experiment_path', type=click.Path(exists=True, dir_okay=True, writable=True, readable=True, resolve_path=True),
                default=lambda: os.getcwd())
def run(experiment_path, clone=False, options=""):
    """
    Run experiment locally
    """
    build(experiment_path)
    params = load_params(experiment_path)
    experiment_name = params["experiment_name"]
    click.echo("Running {0} with options '{1}'".format(experiment_name, options))
    if clone:
        verbose_call(["docker", "run", "-e", 'OPTIONS={0}'.format(options), "-it", experiment_name])
    else:
        project_path = get_project_path(experiment_path)
        verbose_call(["docker", "run", "-v", "{0}:/project".format(project_path), "-e",
                      'OPTIONS={0}'.format(options), "-it", experiment_name])
    click.echo("Experiment done.")


@click.command()
@click.option('--volume/--no-volume', help='Mount project folder as /project volume in Docker', default=True)
@click.argument('experiment_path', type=click.Path(exists=True, dir_okay=True, writable=True, readable=True, resolve_path=True),
                default=lambda: os.getcwd())
def shell(experiment_path, volume=True):
    """
    Open shell in experiment environment
    """
    build(experiment_path)
    params = load_params(experiment_path)
    experiment_name = params["experiment_name"]
    click.echo("Opening shell for {0}".format(experiment_name))
    if volume:
        project_path = get_project_path(experiment_path)
        verbose_call(["docker", "run", "-v", "{0}:/project".format(project_path), "-it", experiment_name, "bash",  "-c", "cd /project && bash"])
    else:
        verbose_call(["docker", "run", "-it", experiment_name, "bash"])
    click.echo("Shell exited.")


@click.command()
@click.argument('experiment_path', type=click.Path(exists=True, dir_okay=True, writable=True, readable=True, resolve_path=True),
                default=lambda: os.getcwd())
def deploy(experiment_path):
    """
    Run experiment in the cloud
    """
    build(experiment_path)
    click.echo("Deploying {0} to cloud".format(experiment_path))
    params_file = os.path.join(experiment_path, "parameters.json")
    config_file = os.path.join(CONFIG_PATH, "config.json")
    terraform_aws_path = os.path.join(LOGISTICIAN_ROOT, "terraform/aws")
    verbose_call(["terraform", "apply", '-var-file={0}'.format(params_file), '-var-file={0}'.format(config_file), terraform_aws_path])
    click.echo("Deployment done.")


@click.command()
@click.argument('experiment_path', type=click.Path(exists=True, dir_okay=True, writable=True, readable=True, resolve_path=True),
                default=lambda: os.getcwd())
def status(experiment_path):
    """
    Show deployment status
    """
    verbose_call(["terraform", "show", os.path.join(experiment_path, "terraform.tfstate")])


@click.command()
@click.argument('experiment_path', type=click.Path(exists=True, dir_okay=True, writable=True, readable=True, resolve_path=True),
                default=lambda: os.getcwd())
def terminate(experiment_path):
    """
    Terminate cloud experiment
    """
    click.echo("Terminating {0} in cloud".format(experiment_path))
    params_file = os.path.join(experiment_path, "parameters.json")
    config_file = os.path.join(CONFIG_PATH, "config.json")
    terraform_aws_path = os.path.join(LOGISTICIAN_ROOT, "terraform/aws")
    verbose_call(["terraform", "destroy", '-var-file={0}'.format(params_file), '-var-file={0}'.format(config_file), terraform_aws_path])
    click.echo("Experiment terminated.")


cli.add_command(setup)
cli.add_command(config)
cli.add_command(create_ssh_key)
cli.add_command(sync)
cli.add_command(build)
cli.add_command(run)
cli.add_command(shell)
cli.add_command(deploy)
cli.add_command(status)
cli.add_command(terminate)