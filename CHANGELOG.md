# Changelog

This file tracks all significant changes made to the MyVidVault project during our development session.

---

### **Session Start: Initial Analysis & Documentation**

1.  **Project Analysis**:
    *   Performed an initial analysis of the project structure by listing all files.
    *   Examined `docker-compose.yml` to understand the multi-container architecture (Nginx, Django API, PostgreSQL).
    *   Examined `nginx.conf` to understand the request routing and reverse proxy setup.
    *   Examined `frontend/package.json` to identify frontend technologies (Vue 3, Vite, Pinia, Tailwind CSS v4).

2.  **Documentation Creation**:
    *   Created `PREPARATION_FOR_PUBLIC.md` to guide on sanitizing the project for public sharing.
    *   Created `DEPLOYMENT_GUIDE.md` with detailed instructions for setting up the project on a clean Debian server.
    *   Updated `DEPLOYMENT_GUIDE.md` based on user feedback to include a more comprehensive setup script.
    *   Created `ai_knowledge.md` to serve as a persistent context and knowledge base for the AI.

---

### **Phase 2: UI Modernization (Dark Theme)**

1.  **Initial Theming Attempt & Correction**:
    *   Initially created a `tailwind.config.js` file, which was incorrect for Tailwind CSS v4.
    *   Corrected the approach by moving the theme definition into `frontend/src/assets/main.css` using the `@theme` directive.
    *   Deleted the unused `tailwind.config.js` file.

2.  **Global Style Implementation**:
    *   **Font**: Added the 'Inter' Google Font to `frontend/index.html`.
    *   **Theme Definition**: Defined a new dark color palette and set the default font in `frontend/src/assets/main.css`.

3.  **Component-Level Theming**:
    *   Systematically replaced hardcoded light-theme colors and styles with the new dark-theme classes across the application.
    *   **Modified Files**:
        *   `frontend/src/App.vue`: Updated the main layout, header, and footer.
        *   `frontend/src/views/Home.vue`: Updated page-specific styles, including sort tabs.
        *   `frontend/src/components/OrientationFilter.vue`: Updated filter button styles.
        *   `frontend/src/components/BookmarkGrid.vue`: Updated the search bar, video card grid, loading skeleton, and pagination controls.

4.  **Knowledge Base Update**:
    *   Updated `ai_knowledge.md` to include a new "Theming and Modernization" section detailing the UI changes.

---

### **Phase 3: Performance Optimization**

1.  **Thumbnail Loading (Initial Fix)**:
    *   Identified slow page loads caused by broken thumbnail URLs.
    *   Implemented a graceful error handling solution in `frontend/src/components/BookmarkGrid.vue`.
    *   Added an `@error` event handler to the thumbnail `<img>` tag to show a placeholder on error.

2.  **Thumbnail Loading (Improved Lazy Loading)**:
    *   Addressed the root cause of the slowdown: browsers attempting to fetch blocked or broken URLs.
    *   Modified the `BookmarkGrid.vue` component to implement "true" lazy loading.
    *   The `<img>` `src` attribute is now initially `null`. The browser does not make a network request on page load.
    *   The `v-intersect` directive now populates the `src` with the actual URL only when the image is scrolled into view. This dramatically improves initial page load time.

3.  **Backend API Optimization (Attempted & Reverted)**:
    *   Identified the root cause of site slowness to be an inefficient database query in `api/operations/views.py`.
    *   Attempted two different refactors of the `get_queryset` method to improve performance.
    *   Both attempts introduced critical `500 Internal Server Error` bugs.
    *   **Action**: Reverted the `get_queryset` method to its original, slower, but functional state to restore site stability.

4.  **Knowledge Base Update**:
    *   Updated `ai_knowledge.md` with details on all frontend and backend performance optimizations.

---

### **Phase 4: UI/UX Features**

1.  **Search As You Type**:
    *   Modified `frontend/src/components/BookmarkGrid.vue` to provide a better search experience.
    *   Removed the search form and button.
    *   Added a `watch` effect to the search input that triggers the search automatically.
    *   Implemented a 300ms debounce to prevent excessive API calls while the user is typing.

2.  **Clickable Tags**:
    *   Implemented a new feature in `frontend/src/components/BookmarkGrid.vue`.
    *   Tags are now rendered on bookmark cards as small, clickable buttons.
    *   Clicking a tag populates the search bar with the tag's name, leveraging the "Search As You Type" feature to filter content.

3.  **Overlay Pagination**:
    *   Modified `frontend/src/components/BookmarkGrid.vue` to improve the pagination UX.
    *   The pagination controls are now in a fixed, floating overlay at the bottom of the screen, making them accessible without scrolling.

4.  **Automated Bookmark Creation**:
    *   Overhauled the bookmark creation workflow to reduce manual data entry.
    *   **Backend**: Added `requests` and `beautifulsoup4` dependencies. Created a new API endpoint (`/api/scrape-metadata/`) that scrapes a URL for Open Graph metadata.
    *   **Frontend**: Rewrote the `CreateBookmarkView` to use a two-step process. The user now enters a URL, fetches the metadata, and is then presented with a pre-filled form for review.
    *   **Enhancement (Recursive Scraping & Final Fix)**: Upgraded the backend scraper to handle sites that use a two-step embed process. The scraper now recursively fetches `/embed/` URLs and uses the most advanced JSON-parsing logic on those pages to find the final video stream link.
    *   **Enhancement (User-Controlled Player)**: Replaced the automatic "Smart Player" with a manual toggle. The `BookmarkManualPreview` component now features a button allowing the user to manually switch between the `<video>` player and the `<iframe>` player, giving them full control over the preview method.

5.  **Knowledge Base Update**:
    *   Updated `ai_knowledge.md` to document all new UI/UX features.

---

### **Phase 5: Robustness & Error Handling**

1.  **Stale Authentication Fix**:
    *   Addressed a bug where users would be in a broken, semi-logged-in state after a backend restart.
    *   Refactored `frontend/src/api/index.js` to use a centralized `axios` instance.
    *   Added a response interceptor to globally catch `401 Unauthorized` errors.
    *   If a `401` error is detected, the user's local authentication data is cleared, and they are automatically redirected to the login page.

2.  **Backend Validation Fix**:
    *   Fixed a `400 Bad Request` error when saving a new bookmark.
    *   Modified the `ManualBookmarkSerializer` to correctly allow empty `description` and `tags` fields.

3.  **Knowledge Base Update**:
    *   Updated `ai_knowledge.md` with details on all robustness fixes.

---

### **Phase 6: Feature Enhancement**

1.  **Savable Player Choice**:
    *   **Backend**: Added a `player_type` field to the `Video` model and created a database migration. Updated the serializers to save and retrieve this preference.
    *   **Frontend**: The "Add Bookmark" form now sends the selected player type to the backend. The `BookmarkDetailView` was upgraded with the same user-controlled player, which now defaults to the saved preference.

2.  **Submission Feedback**:
    *   Refactored the "Add Bookmark" page to provide clear feedback on success or failure.
    *   On success, the form collapses and shows navigation options.
    *   On error, the error message is displayed on the save button.

3.  **Automatic Tag Generation**:
    *   **Backend**: Added `nltk` for NLP. Upgraded the scraper to analyze the video title and generate a list of relevant keywords (nouns) as suggested tags.
    *   **Frontend**: The "Add Bookmark" form now pre-fills the tags input with these suggestions.

4.  **Knowledge Base Update**:
    *   Updated `ai_knowledge.md` to document all new features.
