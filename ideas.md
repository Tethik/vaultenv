# Ideas for this implementation

Basic functionality:
```bash
vaultenv <env name>
```
Read <env name> into .env
e.g `vaultenv production` or `vaultenv staging`

`.vaultenvrc` for configuration.

Possible configs:
<env name> -> <vault path>


Modify bash PS1 to display active environment


pipenv integration