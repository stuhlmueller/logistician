#!/usr/bin/env python

import click


@click.group()
def cli():
    pass

@click.command()
def hello():
    click.echo("Hello!")

@click.command()
def bye():
    click.echo("Bye!")


cli.add_command(hello)
cli.add_command(bye)
