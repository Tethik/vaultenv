# vaultenv
Manage repository environment variables via vault

## Install
```bash
pip install .
```

## Usage
`vaultenv` works per repository and is configured using a `.vaultenv` file.

```bash
vaultenv init
```
Creates the file for you with default `staging` and `production` configurations. These
paths should correspond to a vault value.

```bash
vaultenv staging
```
Reads the `staging` environment variables and writes them to the project `.env` file.