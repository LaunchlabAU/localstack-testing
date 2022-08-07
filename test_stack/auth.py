from aws_cdk import CfnOutput
from aws_cdk import aws_cognito as cognito
from constructs import Construct


class CognitoClient(Construct):
    def __init__(
        self,
        scope: Construct,
        id: str,
        cognito_domain_prefix: str,
    ) -> None:
        super().__init__(scope, id)

        self.user_pool = cognito.UserPool(
            self,
            "UserPool",
            self_sign_up_enabled=True,
            sign_in_case_sensitive=False,
            sign_in_aliases=cognito.SignInAliases(email=True),
            standard_attributes=cognito.StandardAttributes(
                email=cognito.StandardAttribute(required=True)
            ),
        )

        client = cognito.UserPoolClient(
            self,
            "OAuth2Client",
            user_pool=self.user_pool,
            user_pool_client_name="Oauth2Client",
            prevent_user_existence_errors=True,
            o_auth=cognito.OAuthSettings(
                flows=cognito.OAuthFlows(authorization_code_grant=True),
                scopes=[
                    cognito.OAuthScope.OPENID,
                    cognito.OAuthScope.PROFILE,
                    cognito.OAuthScope.EMAIL,
                ],
                callback_urls=["http://localhost:8090/callback"],
            ),
        )

        auth_domain = self.user_pool.add_domain(
            "TestOauthDomain",
            # TODO: get environment name from scope or env var
            cognito_domain=cognito.CognitoDomainOptions(
                domain_prefix=cognito_domain_prefix
            ),
        )
        self.user_pool_id = CfnOutput(
            self, "OAuthId", value=self.user_pool.user_pool_id
        )
        self.user_pool_client_id = CfnOutput(
            self, "OAuthClientId", value=client.user_pool_client_id
        )
        CfnOutput(self, "OAuthClientBaseURL", value=auth_domain.base_url())
