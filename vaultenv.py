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

def exportfile(file, values):
    with open(file, 'w') as _file:
        for key, value in values.items():
            _file.write('export {key}={value}\n'.format(key=key,value=value))


def read_dict_from_vault(name):
    xargs = {
        'verify': os.getenv('VAULT_CACERT', None),
        'url': os.getenv('VAULT_ADDR', 'http://127.0.0.1:8200'),
        'token': os.getenv('VAULT_TOKEN', None)
    }
    config = loadconfig()

    try:
        client = hvac.Client(**xargs)
        values = client.read(config[name])["data"]
        return values
    except hvac.exceptions.InvalidRequest as ex:
        if "missing client token" in str(ex):
            click.secho("Please authenticate to Vault.", sys.stderr, fg='red')
        else:
            click.secho(str(ex), sys.stderr, fg='red')
        return None

@click.group()
def cli():
    pass


@cli.command()
@click.option("--repo", prompt='Repository name')
def init(repo):
    with open(".vaultenv", 'w') as ymlfile:
        values = {
            'staging': 'services/staging/{}/environment'.format(repo),
            'production': 'services/production/{}/environment'.format(repo)
        }
        yaml.dump(values, stream=ymlfile)


@cli.command()
@click.option("--name", prompt='Environment name')
def read(name):
    values = read_dict_from_vault(name)
    if not values:
        sys.exit(1)
        return
    print(values)


@cli.command()
@click.option("--name", prompt='Environment name')
@click.option("--env-file", prompt='Env file name', default=".env")
@click.option("--dot-env", help='Export in dotenv format', default=False)
@click.option("--exportable", help='Export as bash script with export statements', default=False)
def activate(name, env_file, dot_env, exportable):
    xargs = {
        'verify': os.getenv('VAULT_CACERT', None),
        'url': os.getenv('VAULT_ADDR', 'http://127.0.0.1:8200'),
        'token': os.getenv('VAULT_TOKEN', None)
    }

    config = loadconfig()

    # modify environment
    values = read_dict_from_vault(name)
    if not values:
        sys.exit(1)
        return

    if exportable:
        exportfile(env_file, values)
    else:
        flatten_and_write(env_file, values, quote_mode="no thanks")
        click.secho('Loaded "{name}"-environment variables into {env_file}'\
                    .format(name=name, env_file=env_file), fg='green')



def main():
    cli()

if __name__ == '__main__':
    main()
