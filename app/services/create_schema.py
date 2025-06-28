from weaviate.classes.config import Property, DataType, Configure
from app.services.weaviate_client import client as weaviate_client

def setup_schema():
    try:
        if "Product" not in weaviate_client.collections.list_all():
            weaviate_client.collections.create(
                name="Product",
                properties=[
                    Property(name="product_id", data_type=DataType.TEXT, is_primary_key=True),
                    Property(name="title", data_type=DataType.TEXT),
                    Property(name="color", data_type=DataType.TEXT),
                    Property(name="gender", data_type=DataType.TEXT),
                    Property(name="price", data_type=DataType.TEXT),
                    Property(name="link", data_type=DataType.TEXT),
                    Property(name="image_link", data_type=DataType.TEXT),
                ],
                vectorizer_config=Configure.Vectorizer.none()
            )
            print("Created Product schema.")
        else:
            print("Product schema already exists.")
    except Exception as e:
        print(f"Error creating Product schema: {e}")

    try:
        if "ContentItem" not in weaviate_client.collections.list_all():
            weaviate_client.collections.create(
                name="ContentItem",
                properties=[
                    Property(name="content_id", data_type=DataType.TEXT, is_primary_key=True),
                    Property(name="title", data_type=DataType.TEXT),
                    Property(name="category", data_type=DataType.TEXT),
                    Property(name="genre_list", data_type=DataType.TEXT_ARRAY),
                    Property(name="image", data_type=DataType.TEXT),
                    Property(name="description", data_type=DataType.TEXT),
                    Property(name="language", data_type=DataType.TEXT),
                    Property(name="creator", data_type=DataType.TEXT),
                    Property(name="actors", data_type=DataType.TEXT_ARRAY),
                    Property(name="publisher", data_type=DataType.TEXT),
                    Property(name="releaseYear", data_type=DataType.INT),
                    Property(name="tags", data_type=DataType.TEXT_ARRAY),
                    Property(name="rating", data_type=DataType.NUMBER),
                    Property(name="duration", data_type=DataType.TEXT),
                    Property(name="link", data_type=DataType.TEXT),
                ],
                vectorizer_config=Configure.Vectorizer.text2vec_transformers()
            )
            print("Created ContentItem schema.")
        else:
            print("ContentItem schema already exists.")
        weaviate_client.close()

    except Exception as e:
        print(f"Error creating ContentItem schema: {e}")
setup_schema()