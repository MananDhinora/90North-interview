<div align="center">

# Backend Service implementing Google APIs and a real-time chat in Django

A set of APIs that implement the Google OAuth flow, Google Drive v3, and a real-time chat function using WebSockets.

</div>

## 🚀 Deployed

  - You can use this API, which is deployed [here](https://enfund-assignment.vercel.app/).

## 🛠️ Requirements

- Git
- Docker >= **27.4.0**
  - [Windows](https://docs.docker.com/desktop/setup/install/windows-install/)
  - [Linux](https://docs.docker.com/desktop/setup/install/linux/)
- docker-compose-plugin >= **3.8**

## ⚡️ Getting Started

### Installation using Docker 🐳

  - Clone the repository.

    ```
    git clone [https://github.com/MananDhinora/enfund-assignment.git](https://github.com/MananDhinora/enfund-assignment.git)
    ```

### Spinning up container

  - Navigate to the project directory.
    ```
    cd enfund-assignment
    ```

- *Note:* If Docker Desktop is being used, make sure it is running in the background before spinning up the container.

  - Spin up the Docker container.
    ```
    docker compose up -d
    ```
  - The container will listen on port `8000` from the **host** machine. This can be altered in `docker-compose.yaml`.

### Spin down the Docker container:

  - The container will spin down.
    ```
    docker compose down
    ```

## 🔗 API Endpoints

### Google APIs 🔍

  - #### Google OAuth2
    - **GET** /google/
    - **POST** /google/csrf_token/
    - **POST** /google/auth/login/
    - **POST** /google/auth/login/callback/
    - **POST** /google/logout/

  - #### Google Drive
    - **POST** /google/google-picker/upload/
    - **POST** /google/google-picker/download/

### Chat APIs 💬
- **WS** /chat/(str:username)/

  - #### Using GUI
    - Go to "/" endpoint.
    - Login using demo accounts:
      - 🔐 username: jeff, password: asdf
      - 🔐 username: bob, password: asdf
    - After logging in, you will be redirected to the chat dashboard. On the left, you can see all the other users that can be chatted with. Pick one and start chatting.

## 📝 Documentation
For the detailed API documentation, refer to the Postman collection [here](./enfund-assignment.postman_collection.json).