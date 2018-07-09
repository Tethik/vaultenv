"""
vaultenv - cli tool to load environment variables from hashicorps vault.
"""
import os
import subprocess
import collections
import crayons
import sys
import json
import click
import hvac
import yaml
from dotenv.main import parse_dotenv, flatten_and_write
from click_default_group import DefaultGroup


def load_config():
    with open(".vaultenv", 'r') as ymlfile:
        return yaml.load(ymlfile)                


def _colour_env(env: str):
    return str(collections.defaultdict(lambda: lambda x: x,
    {
        'production': crayons.red, 
        'staging': crayons.green, 
        'develop': crayons.blue,
        'local': crayons.blue,
    })[env](env))


class NoConfigurationForEnvironmentException(Exception):
    pass

class NoVaultenvFileException(Exception):
    pass

# def launch_subshell(environment_name: str):
#     shell = os.environ['SHELL']
#     args = [shell]
#     if 'bash' in shell:
#         # Skip these because we want to reuse environment from the current process
#         # and extend the PS1 variable.
#         args += ['--noprofile', '--norc']

#     coloured_name = _colour_env(environment_name)

#     orig_ps1 = os.environ['PS1']
#     if os.environ.get('VAULTENV_CURRENT_ENV'):
#         orig_ps1 = os.environ['VAULTENV_PREVIOUS_PS1']

#     os.environ['PS1'] = f"({coloured_name}) {orig_ps1}"
#     os.environ['VAULTENV_CURRENT_ENV'] = environment_name
#     os.environ['VAULTENV_PREVIOUS_PS1'] = orig_ps1
#     subprocess.run(args, env=os.environ)


def read_dict_from_vault(vault_config, path):
    client = hvac.Client(**vault_config)        
    entry = client.read(path)
    if entry:
        return entry["data"]
    click.secho(f"No entry found in vault, the environment is empty.", sys.stderr, fg='yellow')
    return {}


def write_dict_to_vault(vault_config, path, values):
    client = hvac.Client(**vault_config)
    values = client.write(path, data=values)
    return values


@click.group(cls=DefaultGroup, default='activate', default_if_no_args=True)
@click.option('--vault-token', envvar='VAULT_TOKEN')
@click.option('--vault-cacert', envvar='VAULT_CACERT')
@click.option('--vault-addr', envvar='VAULT_ADDR')
@click.pass_context
def cli(ctx, vault_token, vault_cacert, vault_addr):
    try:
        if not ctx.obj:
            ctx.obj = {}
        ctx.obj['config'] = load_config()
    except FileNotFoundError:
        raise NoVaultenvFileException()

    ctx.obj['vault_config'] = {
        'verify': vault_cacert,
        'url': vault_addr,
        'token': vault_token
    }


@cli.command()
@click.option("--repo", prompt='Repository name')
@click.pass_context
def init(ctx, repo):
    with open(".vaultenv", 'w') as ymlfile:
        values = {
            'develop': f'services/develop/{repo}/environment',
            'staging': f'services/staging/{repo}/environment',
            'production': f'services/production/{repo}/environment'
        }
        yaml.dump(values, stream=ymlfile)


@cli.command()
@click.argument('env', envvar='VAULTENV_CURRENT_ENV')
@click.option("--env-file", default=".env")
@click.pass_context
def activate(ctx, env, env_file):    
    if not env in ctx.obj["config"]:
        click.secho(f"There is no configuration for environment {env}.", sys.stderr, fg='yellow')
        return

    values = read_dict_from_vault(ctx.obj['vault_config'], ctx.obj["config"][env])
    flatten_and_write(env_file, values.get("data", {}), quote_mode="no thanks")

    click.secho(f'Loaded "{_colour_env(env)}"-environment variables into {env_file}', fg='green')
    # launch_subshell(env)


@cli.command()
@click.argument('env', envvar='VAULTENV_CURRENT_ENV')
@click.option("--dotenv", "export_type", flag_value="dotenv", help='Export in dotenv format', default=True, is_flag=True)
@click.option("--shellscript", "export_type", flag_value="shellscript", help='Export as bash script with export statements', default=False, is_flag=True)
@click.option("--json", "export_type", flag_value="json", help='Show in prettified json format', default=False, is_flag=True)
@click.option("-O", "output", help='Output file', default=sys.stdout)
@click.pass_context
def export(ctx, env, export_type, output):        
    if not env in ctx.obj["config"]:
        click.secho(f"There is no configuration for environment {env}.", sys.stderr, fg='yellow')
        return

    values = read_dict_from_vault(ctx.obj['vault_config'], ctx.obj["config"][env])    

    if export_type == "shellscript":
        for key, value in values.items():
            print(f'export {key}={value}', file=output)
    elif export_type == "dotenv":        
        for k, v in values.items():
            str_format = '%s=%s'
            print(str_format % (k, v), file=output)
    elif export_type == "json":
        json.dump(values, output, sort_keys=True, indent=4)


@cli.command()
@click.argument('env', envvar='VAULTENV_CURRENT_ENV')
@click.argument("file", default=".env")
@click.option("--dotenv", "import_type", flag_value="dotenv", help='Import in dotenv format', default=True, is_flag=True)
@click.option("--json", "import_type", flag_value="json", help='Import in json format', default=False, is_flag=True)
@click.option("--skip-confirm", "skip_confirm", help='Skip the confirmation', default=False)
@click.option("--skip-diff", "skip_diff", help='Skip the confirmation', default=False)
@click.pass_context
def commit(ctx, env, file, import_type, skip_confirm):
    if not env in ctx.obj["config"]:
        click.secho(f"There is no configuration for environment {env}.", sys.stderr, fg='yellow')
        return

    if import_type == "dotenv":        
        values = dict(parse_dotenv(file))
    if import_type == "json":
        with open(file) as fp:
            values = json.load(fp)

    # TODO: implement a basic diff summary.
    # if not skip_diff:
    #     old_values = read_dict_from_vault(ctx.obj['vault_config'], ctx.obj["config"][env])

    if not skip_confirm and not click.confirm(f'Do you want to write the new values from {file} to vault?'):
        return
    
    write_dict_to_vault(ctx.obj['vault_config'], ctx.obj["config"][env], values)
    print(f"Saved new values into {env}")


def main():
    try:
        cli(obj={})
    except hvac.exceptions.InvalidRequest as ex:
        if "missing client token" in str(ex):
            click.secho("Please authenticate to Vault.", sys.stderr, fg='red')
        else:
            click.secho(str(ex), sys.stderr, fg='red')
        return None
    except NoVaultenvFileException:
        click.secho("This repository has not been initialized yet. Please run vaultenv init.", sys.stderr, fg='yellow')
    except NoConfigurationForEnvironmentException as ex:
        click.secho(ex, sys.stderr, fg='yellow')



if __name__ == '__main__':
    main()
