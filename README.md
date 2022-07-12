## How to start
**REQUIRED** python3.8+, pip, virtualenv

### Create virtual environment

```
python3 -m venv /path/to/virtual/environment
```

### Install requirements
```
pip install -r requirements.txt
```

### Run crawler 
```
python crawler/crawler.py -d '{"keywords": ["openstack", "nova", "css"], "proxies": ["80.48.119.28:8080"],"type": "Repositories"}'
```
`-d/--details` is argument for crawler input.

### Run tests
```
python -m unittest crawler.tests
```