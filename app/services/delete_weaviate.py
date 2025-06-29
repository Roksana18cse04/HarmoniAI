import weaviate
from weaviate.auth import AuthApiKey

client = weaviate.connect_to_custom(
    http_host='vektor.harmoniai.net',
    http_secure=True,
    http_port=443,
    grpc_host='grpc.harmoniai.net',
    grpc_secure=True,
    grpc_port=8443,
    auth_credentials=AuthApiKey('vek-sJgVNyn1DgzPXUmsYZz9y5WeRUEqdSeBmneWnIXXI8Z5ylbB1aSwtPCrBTzt'),
    skip_init_checks=True
)

classes_to_delete = ['Product']

for class_name in classes_to_delete:
    try:
        client.collections.delete(class_name)
        print(f"Deleted class: {class_name}")
    except Exception as e:
        print(f"Error deleting class {class_name}: {e}")
