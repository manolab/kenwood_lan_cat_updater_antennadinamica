## cat_updater_lan890.py

### Install dependencies
`pip install -r requirements.txt`

### Run

```
usage: cat_updater_lan890.py [-h] [-u USER] [-p] host [port] outpath

Connect to Kenwood receiver and save frequency to file

positional arguments:
  host                  Hostname or IP of receiver
  port                  Port to connect to
  outpath               Path of file to save to. CAUTION: File will be overwritten

options:
  -h, --help            show this help message and exit
  -u USER, --user USER  Username, or env var USER
  -p, --password        Password (interactive) or env var PASSWORD
```

```shell
## E.g.
python cat_updater_lan890.py "192.168.1.16" 60000 "/usr/local/share/ad/frequency.txt" --user "admin" --password
```

You could also pass user and password via environment variables, like so
```shell
export USER=username
export PASSWORD=password

python cat_updater_lan890.py "192.168.1.16" 60000 "/usr/local/share/ad/frequency.txt"
```