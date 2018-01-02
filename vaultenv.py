"""
vaultenv - cli tool to load environment variables from hashicorps vault.
"""
import os
import sys
import json
import click
import hvac
import yaml
from dotenv.main import parse_dotenv, flatten_and_write
from click_default_group import DefaultGroup

def loadconfig():
    with open(".vaultenv", 'r') as ymlfile:
        cfg = yaml.load(ymlfile)
        # print(cfg)
        return cfg


def read_dict_from_vault(name):
    xargs = {
        'verify': os.getenv('VAULT_CACERT', None),
        'url': os.getenv('VAULT_ADDR', 'http://127.0.0.1:8200'),
        'token': os.getenv('VAULT_TOKEN', None)
    }

    try:
        config = loadconfig()
    except FileNotFoundError as ex:
        click.secho("This repository has not been initialized yet. Please run vaultenv init.", sys.stderr, fg='yellow')
        return None

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


@click.group(cls=DefaultGroup, default='activate', default_if_no_args=True)
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
@click.argument("name")
@click.option("--env-file", default=".env")
def activate(name, env_file):
    # modify environment
    values = read_dict_from_vault(name)
    if not values:
        sys.exit(1)
        return

    flatten_and_write(env_file, values, quote_mode="no thanks")
    click.secho('Loaded "{name}"-environment variables into {env_file}'\
                .format(name=name, env_file=env_file), fg='green')


@cli.command()
@click.argument("name")
@click.option("--dotenv", "export_type", flag_value="dotenv", help='Export in dotenv format', default=True, is_flag=True)
@click.option("--shellscript", "export_type", flag_value="shellscript", help='Export as bash script with export statements', default=False, is_flag=True)
@click.option("--json", "export_type", flag_value="json", help='Show in prettified json format', default=False, is_flag=True)
def export(name, export_type):
    # modify environment
    values = read_dict_from_vault(name)
    if not values:
        sys.exit(1)
        return

    if export_type == "shellscript":
        for key, value in values.items():
            print('export {key}={value}'.format(key=key,value=value))
    elif export_type == "dotenv":
        # copied from dotenv flatten_and_write
        for k, v in values.items():
            str_format = '%s=%s'
            print(str_format % (k, v))
    elif export_type == "json":
        json.dump(values, sys.stdout, sort_keys=True, indent=4)
        print() # add newline



@cli.command()
@click.argument("name")
def write(name):
    # TODO Functionality to write current .env into vault
    pass


def main():
    cli()


if __name__ == '__main__':
    main()
