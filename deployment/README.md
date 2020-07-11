# Deployment scripts

Prep
```
set AWS_DEFAULT_REGION=us-west-2
set AWS_ACCESS_KEY_ID=AKIAQNBKYE4KO2HRZXM2
set AWS_SECRET_ACCESS_KEY=...
```

Create instances
```
py -3 deploy.py -n 4
```

List instances
```
py -3 list_stacks.py
py -3 list_stacks.py -h
```
