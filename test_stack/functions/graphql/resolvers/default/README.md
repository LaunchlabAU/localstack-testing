There is a bug with pip? where the poetry generated requirements.txt fails due to missing hashes.

We currently use a workaround based on:

https://github.com/aws/aws-cdk/issues/14201#issuecomment-1159733293

```
poetry export -o requirements.txt --without-hashes 
rm poetry.lock
```

If CDK finds the poetry.lock file, then it will regenerate requirements.txt which leads to the issue, so we remove it after requirement.txt has been generated.