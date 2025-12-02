#!/usr/bin/env python3

import click

@click.command()
def cli():
    """ Prints a greeting. """

    click.echo("Hello, World!")