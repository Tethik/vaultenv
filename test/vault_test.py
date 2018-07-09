import pytest
import hvac
import vaultenv
from click.testing import CliRunner

vault_args = ['--vault-addr', 'http://127.0.0.1:1234', '--vault-token', "myroot"]

runner = CliRunner()

def test_init(tmprepodir):    
    result = runner.invoke(vaultenv.cli, vault_args + ['init', '--repo', 'test-project'])
    print(result.output)
    print(result.exception)
    assert result.exit_code == 0


def test_activate(initeddir):    
    result = runner.invoke(vaultenv.cli, vault_args + ['activate', 'staging'])
    print(result.output)
    print(result.exception)
    assert result.exit_code == 0


def test_commit(initeddir):
    result = runner.invoke(vaultenv.cli, vault_args + ['commit', 'staging'])
    print(result.output)
    print(result.exception)
    assert result.exit_code == 0    


def test_export(initeddir):
    result = runner.invoke(vaultenv.cli, vault_args + ['export', 'staging'])
    print(result.output)
    print(result.exception)
    assert result.exit_code == 0    


def test_bad_token(tmprepodir):        
    result = runner.invoke(vaultenv.cli, ['--vault-addr', 'http://127.0.0.1:1234', '--vault-token', "bad"] + ['activate', 'production'])
    print(result.output)
    print(result.exception)
    assert result.exit_code != 0
    assert result.output == ""


def test_bad_addr(tmprepodir):        
    result = runner.invoke(vaultenv.cli, ['--vault-addr', 'http://127.0.0.1:1337', '--vault-token', "myroot"] + ['activate', 'production'])
    print(result.output)
    print(result.exception)
    assert result.exit_code != 0
    assert result.output == ""
