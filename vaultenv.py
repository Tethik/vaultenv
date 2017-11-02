import os
import sys
import click
import hvac
import shlex, subprocess
from collections import OrderedDict
import yaml
from dotenv.main import parse_dotenv, flatten_and_write

def loadconfig():
    with open(".vaultenv", 'r') as ymlfile:
        cfg = yaml.load(ymlfile)
        print(cfg)
        return cfg

def init():
    """
    Command to initialize a .vaultenv config file.
    """
    pass

@click.command()
@click.option("--name", prompt='Environment name')
@click.option("--env-file", prompt='Env file name', default=".env")
def activate(name, env_file):
    xargs = {
        'verify': os.getenv('VAULT_CACERT', None),
        'url': os.getenv('VAULT_ADDR', 'http://127.0.0.1:8200'),
        'token': os.getenv('VAULT_TOKEN', None)
    }

    config = loadconfig()

    # modify environment
    try:
        client = hvac.Client(**xargs)
        values = client.read(config[name])["data"]
    except hvac.exceptions.InvalidRequest as ex:
        if "missing client token" in str(ex):
            click.secho("Please authenticate to Vault.", sys.stderr, fg='red')
        else:
            click.secho(str(ex), sys.stderr, fg='red')
        sys.exit(1)

    flatten_and_write(env_file, values)
    click.secho('Loaded "{name}"-environment variables into {env_file}'.format(name=name, env_file=env_file), fg='green')


def main():
    activate()

if __name__ == '__main__':
    main()
