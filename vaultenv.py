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

def load_env_into_current_shell(name):
    """
    loads and activates environment variables.
    """
    with open("tmp", "w") as f:
        for key,val in parse_dotenv(".env"):
            f.write(f'export {key}={val}\n')
        f.write(f'export PS1="({name}) {os.environ["PS1"]}"\n')
    subprocess.Popen(['pwd'], shell=True)
    subprocess.Popen(['source', './tmp'], shell=True)


def init():
    """
    Command to initialize a .vaultenv config file.
    """
    pass

@click.command()
@click.option("--name", prompt='Environment name')
def activate(name):
    xargs = {
        'verify': os.getenv('VAULT_CACERT', None),
        'url': os.getenv('VAULT_ADDR', 'http://127.0.0.1:8200'),
        'token': os.getenv('VAULT_TOKEN', None)
    }

    config = loadconfig()

    # modify environment:
    # os.environ["PS1"] = f'({name}) {os.environ["PS1"]}'
    shellprogram = os.environ["SHELL"]

    try:
        client = hvac.Client(**xargs)
        values = client.read(config[name])["data"]
        flatten_and_write(".env", values)
        # load_env_into_current_shell(name)
    except hvac.exceptions.InvalidRequest as ex:
        if "missing client token" in str(ex):
            click.secho("Please authenticate to Vault.", sys.stderr, fg='red')


if __name__ == '__main__':
    activate()
