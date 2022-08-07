
```
export AWS_REGION=us-east-1
npm install -g aws-cdk-local aws-cdk
python3 -m venv .venv
. .venv/bin/activate
pip install -r requirements-dev.txt
cdklocal bootstrap
cdklocal synth
cdklocal deploy
pytest tests
```