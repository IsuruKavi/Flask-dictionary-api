# Flask Dictionary API


## Features

- Fetch definitions and synonyms for a given English word.
- Translate the word and its definition to Sinhala.

## Project Structure

```plaintext
your-project/
│
├── app.py                # Main Flask application
├── requirements.txt      # Python dependencies
└── Dockerfile            # Docker configuration file

## Docker Deployment

To run the application inside a Docker container:

1. **Ensure you have Docker installed on your machine. If not, [download and install Docker](https://www.docker.com/products/docker-desktop).**

2. **Build the Docker image:**

   ```sh
   docker build -t flask-app .


3.**To run the application inside a Docker container, use the following command:**

    ```sh
    docker run -d -p 5000:5000 flask-app

The application will be accessible at [http://127.0.0.1:5000/].

### Example Request

You can test the endpoint using Postman or your browser:

- **URL:** [http://127.0.0.1:5000/word=dog]
- **Method:** GET
- **URL Params:** word=[string]

## API Endpoints

### Get Word Definition and Translation

- **URL:** `/word=<word>`
- **Method:** GET
- **URL Params:** word=[string]
