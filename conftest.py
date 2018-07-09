# contents of conftest.py
import pytest
import os
import sys
from click.testing import CliRunner
import vaultenv

vault_args = ['--vault-addr', 'http://127.0.0.1:1234', '--vault-token', "myroot"]

@pytest.fixture #(scope="session")
def tmprepodir(tmpdir_factory):    
    fn = tmpdir_factory.mktemp("test-project")
    currdir = os.curdir
    os.chdir(fn)
    yield fn
    os.chdir(currdir)


@pytest.fixture
def initeddir(tmprepodir):
    runner = CliRunner()
    result = runner.invoke(vaultenv.cli, vault_args + ['init', '--repo', 'test-project'])
    print(result.output)
    print(result.exception)
    assert result.exit_code == 0