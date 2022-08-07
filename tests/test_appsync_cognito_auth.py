
import uuid

import requests


def test_appsync_cognito_auth(session):
    # Use boto3 session patched to point to localstack
    cognito_client = session.client("cognito-idp")
    appsync_client = session.client("appsync")

    # Get user pool id

    response = cognito_client.list_user_pools(MaxResults=1)
    user_pool_id = response["UserPools"][0]["Id"]
    print(f"user_pool_id: {user_pool_id}")

    # get client id
    response = cognito_client.list_user_pool_clients(UserPoolId=user_pool_id)
    user_pool_client_id = response["UserPoolClients"][0]["ClientId"]
    print(f"user_pool_client_id: {user_pool_client_id}")

    # get graphql endpoint
    response = appsync_client.list_graphql_apis()
    api_id = response["graphqlApis"][0]["apiId"]
    print(f"api_id: {api_id}")
    api_endpoint = f"http://localhost:4566/graphql/{api_id}"

    email = f"{uuid.uuid4().hex[:6]}@example.org"
    pw = "8c01d1A%"
    cognito_client.sign_up(
        ClientId=user_pool_client_id,
        Username=email,
        Password=pw,
        UserAttributes=[
            {"Name": "email", "Value": email},
        ],
    )
    cognito_client.admin_confirm_sign_up(UserPoolId=user_pool_id, Username=email)

    response = cognito_client.admin_initiate_auth(
        UserPoolId=user_pool_id,
        ClientId=user_pool_client_id,
        AuthFlow="USER_PASSWORD_AUTH",
        AuthParameters={"USERNAME": email, "PASSWORD": pw},
    )

    token = response["AuthenticationResult"]["IdToken"]
    auth_header = f"Bearer {token}"

    headers = {"Authorization": auth_header, 'Content-type': 'application/json'}

    print("request headers")
    print(headers)

    # Test GraphQL endpoint
    query = """query {
        viewer { email }
    }
    """
    response = requests.post(
        url=api_endpoint, json={"query": query}, headers={"Authorization": auth_header, 'Content-type': 'application/json'}
    )

    assert response.status_code == 200
