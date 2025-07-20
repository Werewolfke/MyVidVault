# AI Knowledge Base for MyVidVault Project

This document summarizes the architecture, technologies, and operational procedures for the MyVidVault application as understood by the AI assistant. It is intended to be used as a context primer for future sessions.

## 1. High-Level Overview

MyVidVault is a video bookmarking website. It operates as a modern, containerized web application with a decoupled frontend and backend.

## 2. System Architecture

The application uses a **three-tier architecture**, orchestrated by **Docker Compose**.

*   **Services Defined in `docker-compose.yml`**:
    1.  `nginx`: The web server and reverse proxy.
    2.  `api`: The backend application server.
    3.  `db`: The PostgreSQL database.

*   **Request Flow**:
    1.  User traffic hits the `nginx` container on ports 80/443.
    2.  `nginx` serves the static Vue.js frontend application.
    3.  The Vue.js app, running in the user's browser, makes API calls to endpoints like `/api/...`.
    4.  `nginx` reverse-proxies these requests to the `api` service.
    5.  The `api` service processes the request, communicates with the `db` service, and returns a response.
    6.  `nginx` also serves static and media files directly from shared volumes for efficiency.

---

## 3. Component Breakdown

### a. Nginx (Web Server & Proxy)
*   **Technology**: Nginx 1.25
*   **Configuration (`nginx.conf`)**:
    *   Serves the built frontend from `/usr/share/nginx/html` (which maps to `./frontend/dist`).
    *   Uses `try_files $uri $uri/ /index.html;` to enable client-side routing for the Vue SPA.
    *   Proxies requests for `/api/` and `/admin/` to the `api` service at `http://api:8000`.
    *   Serves `/static/` and `/media/` files directly from Docker volumes.
    *   Configured to mount `/etc/letsencrypt`, suggesting it's intended for production HTTPS, though this is a host dependency.

### b. Backend (`api/`)
*   **Technology**: Python with the **Django** framework.
*   **Server**: Runs on **Uvicorn** as an ASGI application, allowing for asynchronous capabilities.
*   **Structure**: A standard Django project with several apps:
    *   `authsystem`: Manages user authentication.
    *   `users`: Manages user profiles and related models.
    *   `videos`: Manages video bookmark models and logic.
    *   `operations`: Likely contains other business logic.
*   **Dependencies (`api/requirements.txt`)**: Manages Python packages.

### c. Frontend (`frontend/`)
*   **Technology**: JavaScript with the **Vue 3** framework.
*   **Build Tool**: **Vite**.
*   **Key Dependencies (`package.json`)**:
    *   `vue-router`: For client-side routing.
    *   `pinia`: For global state management.
    *   `axios`: For making HTTP requests to the backend API.
    *   `tailwindcss`: For utility-first CSS styling.
*   **Source Code Structure (`src/`)**:
    *   `main.js`: The application entry point where Vue, Pinia, and the router are initialized.
    *   `router/`: Defines URL paths and maps them to `View` components.
    *   `views/`: Components that represent full pages (e.g., Home, Login).
    *   `components/`: Smaller, reusable UI components.
    *   `stores/`: Pinia state management modules.
    *   `api/`: Centralized Axios logic for backend communication.
    *   `composables/`: Reusable stateful logic functions.

### d. Database (`db`)
*   **Technology**: **PostgreSQL 16**.
*   **Persistence**: Uses a named Docker volume (`postgres_data`) to persist data across container restarts.

---

## 4. Operational Guides

Two key documents have been created to manage the application lifecycle:

1.  **`PREPARATION_FOR_PUBLIC.md`**:
    *   Details steps to sanitize the project before sharing.
    *   Key actions: Remove the `.env` file, clean the `frontend/dist` and `frontend/node_modules` directories.

2.  **`DEPLOYMENT_GUIDE.md`**:
    *   Provides instructions for deploying on a clean Debian server.
    *   **Key Steps**:
        1.  Install prerequisites (Docker, etc.) using the provided one-line script.
        2.  Place project files on the server.
        3.  Create and populate the `.env` file.
        4.  Build the frontend: `npm install && npm run build` inside the `frontend` directory.
        5.  Start services: `docker compose up -d --build`.
        6.  Initialize the database: `docker compose exec api python manage.py migrate`.
        7.  Collect static files: `docker compose exec api python manage.py collectstatic --noinput`.

---

## 5. Theming and Modernization

A visual overhaul was performed to give the application a modern, dark-themed look.

*   **Strategy**: A new color palette and font were defined and applied globally. The theme is defined directly in the main CSS file using Tailwind v4's `@theme` directive.
*   **Font**: The 'Inter' font from Google Fonts was imported via `frontend/index.html`.
*   **Theme Definition File**: `frontend/src/assets/main.css` now contains the color and font definitions.
    *   `--color-background`: `#1a1a1a`
    *   `--color-surface`: `#2a2a2a`
    *   `--color-primary`: `#3b82f6` (accent)
    *   `--color-text-main`: `#e5e7eb`
    *   `--color-text-secondary`: `#9ca3af`
*   **Key Modified Components**: To apply the theme, hardcoded colors were replaced with the new theme colors in the following files:
    *   `frontend/src/App.vue` (main layout, header, footer)
    *   `frontend/src/views/Home.vue` (page-specific layout, sort tabs)
    *   `frontend/src/components/OrientationFilter.vue` (filter buttons)
    *   `frontend/src/components/BookmarkGrid.vue` (search, video cards, pagination)

---

## 6. Performance Optimizations

To address slow page loads caused by broken or slow-loading thumbnails, the following optimizations are in place:

*   **Frontend: True Lazy Loading**: The `BookmarkGrid.vue` component implements a robust lazy loading strategy. The `<img>` `src` attribute is initially null and is only populated by the `v-intersect` directive when the image enters the viewport. This prevents the initial page load from being blocked by image requests.
*   **Frontend: Image Error Handling**: An `@error` event handler on the thumbnail `<img>` tag in `BookmarkGrid.vue` replaces any broken images with a default placeholder, improving UI resilience.
*   **Backend: API Query Optimization**: The main bookmark listing API endpoint in `api/operations/views.py` was identified as a performance bottleneck. An attempt was made to refactor the `get_queryset` method for efficiency. **(Note: This optimization introduced critical bugs and was reverted. The code is now back to its original, slower, but functional state.)**

---

## 7. UI/UX Features

*   **Search As You Type**: Implemented in `frontend/src/components/BookmarkGrid.vue`. The search functionality no longer requires a button click. A Vue `watch` effect monitors the search input, and a debounce function (300ms timeout) is used to trigger the search API call automatically after the user stops typing, providing a smoother user experience.
*   **Clickable Tags**: Implemented in `frontend/src/components/BookmarkGrid.vue`. Tags are now rendered as clickable buttons on each bookmark card. Clicking a tag populates the search bar with the tag's name, leveraging the "Search As You Type" feature to instantly filter the content.
*   **Overlay Pagination**: Implemented in `frontend/src/components/BookmarkGrid.vue`. The pagination controls are now in a fixed overlay at the bottom of the screen, preventing users from having to scroll down to change pages. The controls are only visible if there is more than one page of content.
*   **Automated Bookmark Creation**: The bookmark creation process has been completely overhauled to reduce manual entry.
    *   **Backend**: A new API endpoint (`/api/scrape-metadata/`) was created in `api/videos/views.py`. It uses `requests` and `BeautifulSoup` to scrape a given URL. The scraper was upgraded multiple times, with the final version using a **recursive** approach that also intelligently parses JSON from `<script>` tags on both the initial and embed pages. This is the most robust version for finding the true video stream URL.
    *   **Frontend**: The `CreateBookmarkView.vue` page was rewritten into a two-step process. The user first enters a URL and fetches the metadata. If the scraper returns multiple potential embed URLs, a dropdown menu appears, allowing the user to select the correct one. The form in `BookmarkManual.vue` then appears, pre-filled with the scraped data for the user to review, edit, and save. The preview component, `BookmarkManualPreview.vue`, was upgraded to use a **User-Controlled Player**. It now features a toggle button that allows the user to manually switch between the direct media (`<video>`) player and the `<iframe>` player, providing full control over the preview method.
*   **Savable Player Choice**:
    *   **Backend**: The `Video` model in `api/operations/models.py` was updated with a `player_type` field. A database migration was created and applied. The bookmark creation serializer was updated to save this choice, and the detail serializers were updated to return it.
    *   **Frontend**: The "Add Bookmark" form now sends the selected player type to the backend. The `BookmarkDetailView.vue` page was upgraded with the same "User-Controlled Player" toggle, which now defaults to the saved preference for each bookmark.
*   **Submission Feedback**: The bookmark creation page (`CreateBookmarkView.vue`) was refactored to provide clear user feedback. On successful submission, the form is hidden and replaced with a success message and navigation buttons. On error, the error message is displayed on the save button itself, and is cleared when the user edits the form.
*   **Automatic Tag Generation**:
    *   **Backend**: The `nltk` library was added for Natural Language Processing. The metadata scraper in `api/videos/views.py` was upgraded to include a `generate_tags_from_title` function. This function tokenizes the scraped video title, removes common stop words, and uses Part-of-Speech tagging to extract the most relevant nouns as suggested tags.
    *   **Frontend**: The "Add Bookmark" page now automatically populates the "Tags" input field with the keywords generated by the backend, which the user can then edit before saving.

---

## 8. Robustness & Error Handling

*   **Centralized API Client**: The frontend API calls in `frontend/src/api/index.js` have been refactored to use a central `axios` instance (`apiClient`).
*   **Automatic Token Injection**: This `apiClient` uses a request interceptor to automatically attach the JWT authentication token to the headers of protected requests, reducing code repetition.
*   **Global Auth Error Handling**: A response interceptor has been added to the `apiClient`. If any API call returns a `401 Unauthorized` error, this interceptor will automatically clear the user's invalid login data from `localStorage` and redirect them to the login page. This fixes a bug where users would get stuck in a broken state after a backend restart.
*   **Backend Validation Fix**: Corrected a bug in the `ManualBookmarkSerializer` (`api/videos/serializers.py`) that was too strict. The validation logic was updated to correctly allow empty strings for the `description` field and empty lists for the `tags` field, preventing `400 Bad Request` errors on valid submissions.
