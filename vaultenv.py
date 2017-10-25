import os
import sys
import click
import hvac


@click.command()
@click.option("--name")
def read(name):
    xargs = {
        'verify': os.getenv('VAULT_CACERT', None),
        'url': os.getenv('VAULT_ADDR', None),
        'token': os.getenv('VAULT_TOKEN', None)
    }

    try:
        client = hvac.Client(**xargs)
        print(client.read('secret/foo'))
    except hvac.exceptions.InvalidRequest as ex:
        if "missing client token" in str(ex):
            click.secho("Please authenticate.", sys.stderr, fg='red')


if __name__ == '__main__':
    read()