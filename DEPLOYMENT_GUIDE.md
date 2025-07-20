# Guide: Deploying MyVidVault on a Clean Debian System

This guide provides step-by-step instructions to deploy the MyVidVault application on a fresh Debian server, starting from system setup to a running application.

## 1. System Prerequisites

First, prepare your Debian system by installing the necessary dependencies: Docker, Docker Compose, and Node.js/NPM.

*   **Action**: Run the following command as root to prepare the system. This comprehensive script updates the system, installs Docker, enables automatic security updates, and installs other useful tools.

    ```bash
    apt-get update ; apt update ; apt upgrade -y ; apt dist-upgrade -y ; \
    apt install unattended-upgrades -y ; systemctl start unattended-upgrades ; \
    systemctl enable unattended-upgrades ; apt install ncdu -y ; apt install build-essential -y ; \
    apt install software-properties-common curl wget npm -y ; curl -fsSL get.docker.com | sh
    ```
*   **Note**: The original script included a `reboot`. You should reboot the machine after this command completes to ensure all updates are applied.
    ```bash
    reboot
    ```

## 2. Application Setup

With the prerequisites installed, you can now configure and launch the MyVidVault application.

1.  **Get the Project Files**
    *   Place the `MyVidVault` project folder on your server and navigate into it.
        ```bash
        cd /path/to/MyVidVault
        ```

2.  **Configure Environment Variables**
    *   Create a `.env` file by copying the example template.
        ```bash
        cp .env_example .env
        ```
    *   Edit the `.env` file and fill in the required values. You must provide a `SECRET_KEY`, `DB_NAME`, `DB_USER`, and `DB_PASSWORD`.
    *   **Crucially, you must also set the `ALLOWED_HOSTS` variable** to the public domain name of your website. This is required for security.
        ```bash
        nano .env
        ```
    *   **Example `.env` configuration:**
        ```
        # Generate your own unique key for production
        SECRET_KEY='r!&eqd0gu1dlc52p%t#zw5=7x=zo^=wpsk+6jj)@k$7u7z!+^g'
        DEBUG=True
        ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com

        DB_NAME=myvidvault_db
        DB_USER=myvidvault_user
        DB_PASSWORD=p@ssw0rd_d7a2b1e9c3f4
        DB_HOST=db
        DB_PORT=5432
        ```

3.  **Build the Frontend**
    *   The Nginx service requires the compiled frontend assets.
        ```bash
        cd frontend
        npm install
        npm run build
        (if there is a error here Vite:permission denied, do the following command >>> chmod +x /path/to/folder/MyVidVault/frontend/node_modules/.bin/*)
        cd ..
        ```

4.  **Launch the Application**
    *   Use Docker Compose to build and start all the services in the background.
        ```bash
        docker compose up -d --build
        ```

## 3. Database Initialization

After the containers are running, you need to initialize the database for the Django application.

1.  **Run Database Migrations**
    *   This command creates the necessary tables in the PostgreSQL database.
        ```bash
        docker compose exec api python manage.py migrate
        ```

2.  **Collect Static Files**
    *   This command gathers all static files into the shared volume for Nginx to serve.
        ```bash
        docker compose exec api python manage.py collectstatic --noinput
        ```

3.  **(Optional) Create a Superuser**
    *   To access the Django admin interface at `/admin/`, you need an admin account.
        ```bash
        docker compose exec api python manage.py createsuperuser
        ```
    *   Follow the prompts to create your admin user.

## 4. Completion

The application is now fully deployed. You should be able to access the MyVidVault website by navigating to your server's IP address (`http://<your-server-ip>`) in a web browser.
