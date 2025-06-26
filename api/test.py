import os
import boto3

session = boto3.session.Session()
client = session.client(
    "s3",
    aws_access_key_id=os.environ["DO_SPACES_KEY"],
    aws_secret_access_key=os.environ["DO_SPACES_SECRET"],
    region_name="nyc3",
    endpoint_url="https://nyc3.digitaloceanspaces.com",
)

# Replace this key with a real path to a file you know exists in your bucket:
key = "media/profile_pics/your_test_image.jpg"

try:
    response = client.head_object(Bucket="myvidvault-storage", Key=key)
    print("SUCCESS! Object metadata:", response)
except client.exceptions.ClientError as e:
    print("ERROR:", e.response['Error']['Code'], e.response['Error']['Message'])
