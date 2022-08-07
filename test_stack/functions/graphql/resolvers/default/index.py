from aws_lambda_powertools.event_handler import AppSyncResolver

app = AppSyncResolver()


@app.resolver(type_name="Query", field_name="viewer")
def get_viewer():
    return {"id": "1", "email": "user@example.org"}


@app.resolver(type_name="Mutation", field_name="testMutation")
def test_mutation():
    return True

def handler(event, context):
    return app.resolve(event, context)
