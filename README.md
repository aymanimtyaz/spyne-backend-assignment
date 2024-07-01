Interactive docs (Swagger) can be found at /doc and /docs for this project

SAMPLE .env:
******************************************************************************
MONGO_CONNECTION_STRING=MONGO_CONNECTION_STRING_HERE
MONGO_DATABASE_NAME=DATABASE_NAME_HERE

JWT_SECRET=JWT_KEY_HERE
JWT_VALIDITY_DAYS=JWT_KEY_VALIDITY_HERE

LOCAL_STORAGE_STATIC_FILES_PATH=ABSOLUTE_PATH_TO_LOCAL_STORAGE_DIRECTORY_HERE
LOCAL_STORAGE_BASE_URL=URL_FOR_FASTAPI_STATICFILES
******************************************************************************

To run this project

1. create a virtual env
2. install the dependencies in requirements
3. create a dotenv file with settings
4. start the server with `fastapi dev main.py`
