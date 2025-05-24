# Deployment Guide

After cloning the repository,  open `/src/backend`, build and run the Docker container:

```
docker build -t swen90017-backend .
```
For Linux/MacOS:
```
docker run -d -p 8081:8081 `
  -v ${PWD}/src:/app/src `
  --name swen90017-backend `
  swen90017-backend
```

For Windows:
```
docker run -d -p 8081:8081 ^
  -v %cd%\src:/app/src ^
  --name swen90017-backend ^
  swen90017-backend
```

<!--
```
docker build -t swen90017-backend .
docker run -d -p 8081:8081 --name swen90017-backend swen90017-backend
```
-->
To apply the modified code, run 
```
docker restart swen90017-backend
```
To enable hot-reloading when modifying code, add reload parameter to dockerfile:
```
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8081", "--reload"]
```

Once the container is running, you can access the API documentation at:

- Swagger UI: http://localhost:8081/docs
- ReDoc: http://localhost:8081/redoc

![](https://github.com/user-attachments/assets/a227d2b0-6245-42fa-9f2c-8dec7e6f2e5e)

![](https://private-user-images.githubusercontent.com/159036687/430286477-9ca516fa-5285-44ca-b7c8-e4e3fab7eb19.png?jwt=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJnaXRodWIuY29tIiwiYXVkIjoicmF3LmdpdGh1YnVzZXJjb250ZW50LmNvbSIsImtleSI6ImtleTUiLCJleHAiOjE3NDM3NTQ4MzcsIm5iZiI6MTc0Mzc1NDUzNywicGF0aCI6Ii8xNTkwMzY2ODcvNDMwMjg2NDc3LTljYTUxNmZhLTUyODUtNDRjYS1iN2M4LWU0ZTNmYWI3ZWIxOS5wbmc_WC1BbXotQWxnb3JpdGhtPUFXUzQtSE1BQy1TSEEyNTYmWC1BbXotQ3JlZGVudGlhbD1BS0lBVkNPRFlMU0E1M1BRSzRaQSUyRjIwMjUwNDA0JTJGdXMtZWFzdC0xJTJGczMlMkZhd3M0X3JlcXVlc3QmWC1BbXotRGF0ZT0yMDI1MDQwNFQwODE1MzdaJlgtQW16LUV4cGlyZXM9MzAwJlgtQW16LVNpZ25hdHVyZT1mOTc5ZmY0MGY1OTExMTAyNjA2ZjUyZjk0NTNkZTY5YjJjNWViNTcxMzU3MTZhNWY5ZDRkN2U2N2Y4N2IyYmYwJlgtQW16LVNpZ25lZEhlYWRlcnM9aG9zdCJ9.R5UgzVXAmk8GDdYB2JUrUoB40sgHk_enRmdI4w0D610)

# Development Guide

## Tech Stack

- **Language**: Python 3.12
- **Database**: MySQL 8.0
- **ORM**: SQLModel
- **Web Framework**: FastAPI
- **File Storage**: Azure
- **Containerization**: Docker

## Project Structure

To help our team transition from Java to Python with FastAPI, here's a detailed explanation of the project structure.

```
src/
├── app/                 
│   ├── core/            # Core configurations and constants
│   ├── crud/            # CRUD operations
│   ├── database/        # Database connection setup
│   ├── dependencies/    # Dependency injection functions
│   ├── models/          # Database models using SQLModel
│   ├── routers/         # API route definitions
│   ├── schemas/         # Pydantic models for request and response data validation
│   ├── services/        # Business logic layer
│   ├── tests/           # Test cases
│   ├── utils/           # Utility functions
│   └── main.py          # Application entry point
├── .env                 # Environment configuration file
└── requirements.txt     # Python dependencies
```

#### Extra Explanation on Some Directories

#### `models/`

- Defines database table models using **SQLModel**.

#### `schemas/`

- Defines **Pydantic models** used for validating request and response bodies in APIs.
- Equivalent to Java's **DTO (Data Transfer Object)** or request/response classes.

#### `routers/`

- Responsible for setting up API **routes/endpoints**.
- Similar to the **Controller layer** in a Java Spring application.

#### `crud/`

- Contains functions that perform **Create, Read, Update, and Delete** operations on the database.
- Think of it like the **DAO (Data Access Object)** layer in Java.

#### `dependencies/`

- Defines reusable **dependency functions**, leveraging FastAPI's **Dependency Injection** system, can be used for tasks like access control.
- Different from Java's dependency injection.
- For more on this, check the official docs: [FastAPI - Dependencies](https://fastapi.tiangolo.com/tutorial/dependencies/)

## Getting Started

1. Clone the repository.

2. Make sure Python 3.12 has been installed.

3. Open the `src/backend/src` directory using PyCharm or any preferred IDE.

4. Install the required dependencies listed in the `requirements.txt` file.

   ```cmd
   pip install -r requirements.txt
   ```

5. Open `app` directory, Run `main.py`.

Once the program is running, you can access the API documentation at:

- Swagger UI: http://localhost:8081/docs
- ReDoc: http://localhost:8081/redoc

![](https://github.com/user-attachments/assets/a227d2b0-6245-42fa-9f2c-8dec7e6f2e5e)

![](https://private-user-images.githubusercontent.com/159036687/430286477-9ca516fa-5285-44ca-b7c8-e4e3fab7eb19.png?jwt=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJnaXRodWIuY29tIiwiYXVkIjoicmF3LmdpdGh1YnVzZXJjb250ZW50LmNvbSIsImtleSI6ImtleTUiLCJleHAiOjE3NDM3NTQ4MzcsIm5iZiI6MTc0Mzc1NDUzNywicGF0aCI6Ii8xNTkwMzY2ODcvNDMwMjg2NDc3LTljYTUxNmZhLTUyODUtNDRjYS1iN2M4LWU0ZTNmYWI3ZWIxOS5wbmc_WC1BbXotQWxnb3JpdGhtPUFXUzQtSE1BQy1TSEEyNTYmWC1BbXotQ3JlZGVudGlhbD1BS0lBVkNPRFlMU0E1M1BRSzRaQSUyRjIwMjUwNDA0JTJGdXMtZWFzdC0xJTJGczMlMkZhd3M0X3JlcXVlc3QmWC1BbXotRGF0ZT0yMDI1MDQwNFQwODE1MzdaJlgtQW16LUV4cGlyZXM9MzAwJlgtQW16LVNpZ25hdHVyZT1mOTc5ZmY0MGY1OTExMTAyNjA2ZjUyZjk0NTNkZTY5YjJjNWViNTcxMzU3MTZhNWY5ZDRkN2U2N2Y4N2IyYmYwJlgtQW16LVNpZ25lZEhlYWRlcnM9aG9zdCJ9.R5UgzVXAmk8GDdYB2JUrUoB40sgHk_enRmdI4w0D610)

## Docker Note

To ensure Docker can build the image correctly, the `requirements.txt` file must be up to date.

#### Instructions:

1. Open PyCharm.

2. Navigate to **Tools** > **Sync Python Requirements**.

   ![](https://private-user-images.githubusercontent.com/159036687/430284655-035f1e99-4a2e-460a-af98-6bbb6d560d9b.jpg?jwt=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJnaXRodWIuY29tIiwiYXVkIjoicmF3LmdpdGh1YnVzZXJjb250ZW50LmNvbSIsImtleSI6ImtleTUiLCJleHAiOjE3NDM3NTQ1OTQsIm5iZiI6MTc0Mzc1NDI5NCwicGF0aCI6Ii8xNTkwMzY2ODcvNDMwMjg0NjU1LTAzNWYxZTk5LTRhMmUtNDYwYS1hZjk4LTZiYmI2ZDU2MGQ5Yi5qcGc_WC1BbXotQWxnb3JpdGhtPUFXUzQtSE1BQy1TSEEyNTYmWC1BbXotQ3JlZGVudGlhbD1BS0lBVkNPRFlMU0E1M1BRSzRaQSUyRjIwMjUwNDA0JTJGdXMtZWFzdC0xJTJGczMlMkZhd3M0X3JlcXVlc3QmWC1BbXotRGF0ZT0yMDI1MDQwNFQwODExMzRaJlgtQW16LUV4cGlyZXM9MzAwJlgtQW16LVNpZ25hdHVyZT1iOTc3NDc1OGIwY2NmNmFjMjlkOTJhMDRjNGU4YzA3NmFiODdiNzRiZGNjNTU2ZjJkNTllNGFhNDM1YjA0OWVlJlgtQW16LVNpZ25lZEhlYWRlcnM9aG9zdCJ9.qz3YuSDELddzwelItPp-kp90s9XsFMfHJDoT-LOGfRA)

Alternatively, you can manually add any dependencies to `requirements.txt`.

