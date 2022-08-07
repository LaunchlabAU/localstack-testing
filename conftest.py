from __future__ import annotations

import os
from typing import Generator

import boto3
import pytest
from botocore.client import Config

AWS_ENDPOINT_URL = "http://localhost:4566"

# https://github.com/boto/boto3/issues/1375#issuecomment-1191441249
patched_defaults = (
    "us-east-1",  # region_name
    None,  # api_version
    True,  # use_ssl
    None,  # verify
    AWS_ENDPOINT_URL,  # endpoint_url
    "testadmin",  # aws_access_key_id
    "testadmin",  # aws_secret_access_key
    None,  # aws_session_token
    Config(signature_version="s3v4"),  # config
)


@pytest.fixture(autouse=True)
def session() -> Generator[boto3.Session, None, None]:
    """
    Patch boto3 session.

    endpoint_url (for localstack) can only be set as an explicit argument to resource()
    and client(), and not via environment variable, so we need to be sure that all
    boto3 resources and clients are patched.
    """
    boto3.session.Session.resource.__defaults__ = patched_defaults
    boto3.session.Session.client.__defaults__ = patched_defaults
    yield boto3.Session()

