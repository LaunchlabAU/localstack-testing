from aws_cdk import CfnOutput, Duration
from aws_cdk import aws_appsync_alpha as appsync
from aws_cdk import aws_cognito as cognito
from aws_cdk import aws_iam as iam
from aws_cdk import aws_lambda as lambda_
from aws_cdk import aws_lambda_python_alpha as lambda_python
from constructs import Construct

SCHEMA_LOCATION = "test_stack/schema/schema.graphql"


class CognitoAuthGraphQL(Construct):
    def __init__(
        self,
        scope: Construct,
        id: str,
        user_pool: cognito.IUserPool,
    ) -> None:
        super().__init__(scope, id)

        # Authentication configuration

        user_pool_config = appsync.UserPoolConfig(
            user_pool=user_pool,
            default_action=appsync.UserPoolDefaultAction.ALLOW,
        )
        user_pool_auth_mode = appsync.AuthorizationMode(
            authorization_type=appsync.AuthorizationType.USER_POOL,
            user_pool_config=user_pool_config,
        )
        auth_config = appsync.AuthorizationConfig(
            default_authorization=user_pool_auth_mode,
        )

        # GraphQL Setup

        graphql_api = appsync.GraphqlApi(
            self,
            "GraphQLAPI",
            name="Api",
            authorization_config=auth_config,
            log_config=appsync.LogConfig(field_log_level=appsync.FieldLogLevel.ALL),
            schema=appsync.Schema.from_asset(SCHEMA_LOCATION),
        )

        #####
        # Resolvers
        #####

        # Use PythonFunction rather than Function so we can have module
        # dependencies built for us

        default_resolver_lambda = lambda_python.PythonFunction(
            self,
            "DefaultGraphQLResolverLambdaFunction",
            runtime=lambda_.Runtime.PYTHON_3_9,
            architecture=lambda_.Architecture.ARM_64,
            entry="test_stack/functions/graphql/resolvers/default",
            timeout=Duration.seconds(30),
            environment={
                "USER_POOL_ID": user_pool.user_pool_id,
            },
        )

        # grant full access to cognito user pools
        # No grant method yet on user pools: https://github.com/aws/aws-cdk/issues/7112
        # TODO: can we reduce the actions requred here?
        default_resolver_lambda.add_to_role_policy(
            iam.PolicyStatement(
                effect=iam.Effect.ALLOW,
                actions=["cognito-idp:*"],
                resources=[user_pool.user_pool_arn],
            )
        )

        default_datasource = graphql_api.add_lambda_data_source(
            "DefaultDataSource", default_resolver_lambda
        )

        #
        # End-user dashboard resolvers
        #

        for (type_name, field_name) in [
            ("Query", "viewer"),
            ("Mutation", "testMutation"),
        ]:
            default_datasource.create_resolver(
                type_name=type_name,
                field_name=field_name,
                request_mapping_template=appsync.MappingTemplate.lambda_request(),
                response_mapping_template=appsync.MappingTemplate.lambda_result(),
            )

        # GraphQL API Endpoint
        self.customer_graphql_endpoint = CfnOutput(
            self, "Endpoint", value=graphql_api.graphql_url
        )
