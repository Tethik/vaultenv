# Ideas for this implementation

Basic functionality:
```bash
vaultenv <env name>
```
Read <env name> into .env
e.g `vaultenv production` or `vaultenv staging`

`.vaultenv` for configuration.

Possible configs:
`<env name> -> <vault path>`

```
staging='secrets/staging/environment'
production='secrets/production/environment'
```


Modify bash PS1 to display active environment
```bash
tethik@tethik-N350DW:~/playground$ vaultenv staging
(staging) tethik@tethik-N350DW:~$
```


pipenv integration
```bash
tethik@tethik-N350DW:~/playground$ pipenv shell
(vaultenv-jkCJv85B) (staging) tethik@tethik-N350DW:~$
```

switching between environments
```bash
(local) tethik@tethik-N350DW:~$ vaultenv staging
* .env was updated!
* Environment varibles loaded into this shell!
(staging) tethik@tethik-N350DW:~$
```