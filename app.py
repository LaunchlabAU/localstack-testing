#!/usr/bin/env python3

import aws_cdk as cdk
from test_stack.stack import TestStack


app = cdk.App()
TestStack(app, "TestStack")
app.synth()
