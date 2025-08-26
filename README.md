# NextChaptr

**NextChaptr** is a minimalist book-tracking web app built to help readers organize and reflect on their reading journey. Developed as a full-stack project, it highlights key features such as book categorization, rating, and commenting using modern web technologies.

Unlike feature-heavy platforms, NextChaptr focuses on simplicity, allowing users to manage their reading lists (To Read, Reading, Read), rate completed books, and engage through comments in a clean, distraction-free interface.

---

## Target Audience

Chaptr is built for individual readers who want a focused, user-friendly space to log their reading habits without social clutter or complex features.

---

## Site Goal

To create a fully functional, database-backed full-stack application that:
- Demonstrates CRUD operations across multiple models
- Integrates external APIs (Google Books)
- Implements authentication, permissions, and user-specific data
- Prioritizes UX, accessibility, and responsive design

---

## Requirements Overview

Below is a summary of the planned development scope using Agile epics, user stories, and tasks.

---

### Epic 1: [Book Discovery and Browsing](#1)

**Goal**: Enable users to explore the book catalog using a search interface powered by the Google Books API.

#### [Search for books by title, author](#6)

**Technical Tasks**
- [Implement search form and view](#19)
- [Integrate Google Books API](#20)
- [Display search results](#21)

#### [View book details](#7)

**Technical Tasks**
- [Create book detail view](#22)
- [Style Book Detail Page](#23)
- [Populate data from API or local cache](#24)

#### [View review on books](#8)

**Technical Tasks**
- [Create review model and form](#43)
- [Display reviews in template](#44)

#### [Prompt login when guests try to interact](#9)

**Technical Tasks**
- [Add Login Checks to Views](#25)
- [Add Login Prompt Messaging](#26)

---

### Epic 2: [User Authentication and Permissions](#2)

**Goal**: Set up account registration, login/logout, and protect user actions.

#### [Register an account](#10)

**Technical Tasks:**
- [Create Registration Form and View](#29)
- [Handle Form Validation and Feedback](#30)
- [Link Registration in Navbar](#31)

#### [Log in and log out securely](#11)

**Technical Tasks:**
- [Create login and logout views](#32)
- [Update navbar based on auth status](#33)
- [Handle redirection after login/logout](#34)

#### [Restrict book interactions to authenticated users](#12)

**Technical Tasks:**
- [Add `@login_required` to protected views](#36)
- [Update templates to show/hide based on login messages](#35)

---

### Epic 3: [Book Interaction and Reading Progress](#3)

**Goal**: Allow users to track their reading activity, rate books, and comment.

#### [Mark books as To Read, Reading, or Read](#13)

**Technical Tasks:**
- [Create reading status and comment models](#37)
- [Add forms for status, rating, and commenting](#38)
- [Display and update user content](#39)

#### [Rate books](#14)

**Technical Tasks:**
- [Add rating field to reading model or separate model](#40)
- [Create form and view logic for adding/updating rating](#41)
- [Show rating summary on book detail](#42)

#### [Leave a review](#15)

**Technical Tasks:**
- [Create review model and form](#43)
- [Display reviews in template](#44)

#### [Edit, and delete reviews](#16)

**Technical Tasks:**
- [Validate review ownership](#45)
- [Implement update and delete views for reviews](#46)
- [Add conditional logic in template for ownership](#47)
- [Add messaging or UI confirmation for deletion](#48)

---

### Epic 4: [User Library](#4)

**Goal**: Provide users with a personalized library to manage their reading activity.

#### [View books grouped by reading status](#17)

**Technical Tasks:**
- [Create library view with user authentication](#49)
- [Build style library template](#50)
- [Query and display grouped book data](#51)

#### [Update reading status directly from library](#18)

**Technical Tasks:**
- [Add inline status update controls](#52)
- [Implement Status Update Logic in View](#53)
- [Show success messages after updates](#54)

---

## Project Board

All issues are tracked on the GitHub project board:  
https://github.com/larevolucia/chaptr/projects/12

## Sprint Planning

Sprints are organized to deliver features incrementally, with each sprint focusing on specific epics and user stories. The sprint timebox is set to 1 week.

### Sprint 0: Project Setup
- [x] Create Epics, User Stories, and Tasks in GitHub
- [x] Set up Django project and apps
- [x] Configure Google Books API integration
- [x] Deploy initial version to Heroku
- [x] Set up Postgres database
- [x] Set up basic templates and static files

### Sprint Breakdown
Sprint 1:
- Epic 1: Book Discovery and Browsing
   - [x] [Search for books by title, author, genre](#6)
   - [x] [View book details](#7)
   - [x] [Homepage - MVP](#56)

- Epic 2: User Authentication and Permissions
   - [x] [Register an account](#10)
   - [x] [Log in and log out securely](#11)

Sprint 2:
- Epic 1: Book Discovery and Browsing
   - [x] [Prompt login when guests try to interact](#9)
   - [x] [Homepage - Stretch](#56)
- Epic 2: User Authentication and Permissions
   - [x] [Restrict book interactions to authenticated users](#12)
- Epic 3: Book Interaction and Reading Progress
   - [x] [Mark books as To Read, Reading, or Read](#13)
   - [x] [Rate books](#14)
   - [x] [Leave a review](#15)

Sprint 3:
- Epic 1: Book Discovery and Browsing
   - [x] [View reviews on books](#8)
- Epic 3: Book Interaction and Reading Progress
   - [x] [Edit, and delete reviews](#16)
- Epic 4: User Dashboard
   - [ ] [View books grouped by reading status](#17)
   - [ ] [Update reading status directly from dashboard](#18)
- Testing and Bug Fixes

---


## Features

### Homepage (Banner, Intro & Quick Browse)

A welcoming, responsive landing experience that introduces CHAPTR and funnels visitors into core actions.

* **Responsive Hero Banner**: A full‑width banner at the top establishes brand tone and provides instant visual context.
* **Clear Purpose Blurb**: A short, centered description directly beneath the banner explains what NextChaptr does and who it’s for.
* **Primary Actions Up Front**: Prominent entry points to start searching books or sign up/log in, keeping the first‑run path obvious.
* **Browse by Genre**: Category tiles allow users to jump straight to a filtered browse view for a given genre.

### Search & Browse (API First)

Book discovery is powered by the Google Books API, allowing users to explore a vast catalog with flexible search options.

- **Keyword or Field-Specific Search**: Search by general keywords or refine by title, author, or genre.
- **Smart Query Handling**: The system applies the correct Google Books operators automatically.
- **Clean Results**: Results display thumbnails, titles, and authors in a browsable layout.
- **Resilient Design**: Handles API or network errors gracefully without breaking the user experience.
* **Caching:** details are cached for \~1h to reduce API calls.

### Book Detail View
Each book has a dedicated detail page with enriched information for readers.

- **Comprehensive Metadata**: Includes title, subtitle, authors, publisher, publication date, page count, categories, description, and cover image.
- **Performance Boost**: Uses Django caching to store details for one hour, reducing API calls while keeping data fresh.
- **Seamless Access**: Directly linked from search results for a smooth browsing experience

### Reading Status

Lets users track their progress with any book, directly from search results or detail pages.

* **Simple Progress Tracking**: Mark books as *To Read*, *Reading*, or *Read*.
* **Integrated Placement**: Status buttons are shown beneath the cover art on both search results and book detail views, by implementing a template partial.
* **Lightweight Persistence**: Saving a status automatically creates/updates a minimal `Book` record, ensuring it appears in Admin and future *My Library* views without extra API calls.

### Rating System

Provides a quick way for readers to rate books and share feedback with the community.

* **Star-Based Ratings**: Authenticated users can assign a rating from 0–5 stars.
* **Automatic Sync**: Rating a book without a status sets it to *Read* by default, achieved by using `post_save` signals.
* **User Feedback**: Notifications confirm when a rating is saved or updated.
* **Flexible Control**: Ratings can be removed at any time.

### Review System

Lets readers share longer-form thoughts on a book, with a clear, edit-friendly flow on the detail page.

* **Single, Text-Based Review**: Authenticated users can post one review per book.
* **Inline Compose, Edit & Delete**: If you haven’t reviewed, a form appears. If you have, your review shows with an *Edit* and *Delete* buttons.
* **One-Per-Book Guarantee**: A unique `(user, book)` constraint updates on re-submit (no duplicates).
* **Clean Presentation**: Reviews appear under the book details. Your own review isn’t duplicated in the list.
* **Lightweight Persistence**: Posting a review auto-ensures a minimal `Book` record for Admin and future library views.

### Library

A user’s personal library displays all books they are interested in, along with their reading status.

* **Grouped by Status**: Books are organized into sections for *To Read*, *Reading*, and *Read*.
* **Dynamic Updates**: The library view updates in real-time as users change book statuses.
* **Link to Book Details**: Each book links to its detail page for more information.

### Authentication (Login, Logout & Sign-Up)

User authentication is powered by **Django Allauth**, providing a secure and reliable way to manage accounts.

- **Sign-Up**: New users can easily create an account. The sign-up template has been customized to match the site’s brand style.
- **Login / Logout**: Users can log in to access their personal features and log out securely when finished.
- **Consistent UI**: Allauth templates have been adapted to the project’s design system, ensuring a seamless experience across authentication pages.

- Track reading progress with status updates
- Rate and review books
- Leave comments on books
- User dashboard for managing reading activity

### Admin Panel

- **Books** admin shows minimal cached metadata (id, title, authors, thumb, language, published date, fetch markers).
- **Reading statuses** admin shows `(user, book_id, title, status)` with a link to the Google Books page.


## Design

### Wireframes

![Mobile Logged-In Wireframes](documentation/Mobile_Logged-In.png)

![Mobile Vistor Wireframes](documentation/Mobile_Visitor.png)

---

## Models

The data model balances **external metadata** (from Google Books) with **internal user interactions**.
Books are only stored locally if a user explicitly saves or interacts with them, keeping the database lightweight.

### User 
Uses Django’s built-in `User` model for authentication and ownership of records.

### Book
Represents a book saved in the system (created only when a user adds it to a shelf or sets a reading status).
Primary key is the Google Books `volumeId`.

**Fields:**

* `id`: `CharField`, `PK` (Google volumeId)
* `title`: `CharField`
* `authors`: `TextField` (list of author names)
* `thumbnail_url`: `URLField`
* `language`: `CharField`
* `published_date_raw`: `CharField`
* `etag`: `CharField`
* `last_modified`: `DateTimeField` (HTTP cache header)
* `last_fetched_at`: `DateTimeField` (defaults to now)
* `created_at`: `DateTimeField` (record creation timestamp)
* `updated_at`: `DateTimeField` (auto-updated timestamp)

**Meta:**
* Index on `title` for faster search.

**Methods:**
* `needs_refresh(ttl_minutes=1440)`: checks if book metadata is stale.


### ReadingStatus
Tracks a user's reading status for a specific book.

**Fields:**

* `user`: `ForeignKey` → `User`
* `book`: `ForeignKey` → `Book`
* `status`: `CharField` with choices:
  * `"TO_READ"` → "To read"
  * `"READING"` → "Reading"
  * `"READ"` → "Read"
* `created_at`: `DateTimeField`
* `updated_at`: `DateTimeField`

**Meta:**
* Unique constraint on `(user, book)` → one status per book per user.
* Indexes on `(user, status)`, `(user, book)`, and `status`.

### Rating
Stores a user's rating for a book.

**Fields:**
* `user`: `ForeignKey` → `User`
* `book`: `ForeignKey` → `Book`
* `rating`: `PositiveSmallIntegerField` (0-5)
* `created_at`: `DateTimeField`
* `updated_at`: `DateTimeField` (auto_now=True)

**Meta:**
* Unique constraint on `(user, book)` → one rating per book per user.

### Review
 Represents a user's written review of a book.

 **Fields:**
 * `user` (FK): `User`
 * `book` (FK): `Book`
 * `content`: `TextField`
 * `created_at`: `DateTimeField`
 * `updated_at`: `DateTimeField` (auto_now=True)

 **Meta:** 
* Unique constraint on `(user, book)` → one review per book per user.

---

## Django Project Structure

The *NextChaptr* project is divided into focused Django applications to ensure clear separation of concerns and maintainable code architecture.

### apps/

| App Name         | Responsibility                                                                |
|------------------|-------------------------------------------------------------------------------|
| `books`          | Google Books search/detail, minimal cached `Book`, admin, service             |
| `activity`       | Per-user `ReadingStatus`, `Rating`, `Review` persistence + admin              |
| `dashboard`      | Displays user-specific reading activity grouped by status.                    |


### Design Rationale

- **Modular design**: Each app reflects a distinct domain of the system and aligns with a major feature group (search, authentication, interaction, UI).
- **Separation of concerns**: Each app encapsulates its own models, views, and templates, making it easier to manage and extend.
- **Maintainability**: Clear boundaries between apps reduce complexity and improve code readability.
- **Scalability**: Allows future extension, such as adding a social/friendship app, without disrupting the core architecture.
---

## Testing

***NextChaptr** includes a comprehensive suite of automated tests to ensure reliability and maintainability across core features. Tests are written using **Django’s TestCase** framework with mocking for external dependenciess, such as Google Books API.

### Coverage

* **Authentication Tests (Allauth)**

  * __Sign-up flow__: page rendering, successful account creation, and validation errors (duplicate username, short passwords, mismatches).
  * __Login flow__: correct credentials, invalid credentials, and required validation checks.
  * __Logout flow__: proper behavior when logged in or out.
  * __Password reset__: form rendering and email delivery.


* **Books App Tests**

  * __Query building__: correct application of search operators (`intitle`, `inauthor`, `subject`).
  * __Search view__: integration with `search_google_books`, correct rendering of results.
  * __Google Books API integration__: parsing of valid responses, handling of failed requests.
  * __Book detail view__: correct mapping of metadata fields, 404 behavior for missing books, and caching to reduce API calls.
  * __Home page__: correct rendering of template, hero, about area, featured genres and search functionality.

* **ReadingStatus Tests**

  * __Anonymous users see login CTA__: detail view renders a “Log in to add” prompt and links to the login page when not authenticated.
  * __Valid choices can be set__: authenticated users can set any of `"TO_READ"`, `"READING"`, or `"READ"` and the value is persisted.
  * __Creating a status__: posting a valid status while authenticated creates a `ReadingStatus` row for the `(user, book)` pair.
  * __Unauthenticated redirects__: posting without authentication redirects to the login page and does **not** create a status.
  * __Removing a status with safe `next`__: sending `status=NONE` deletes the row and safely redirects to a same‑site `next` URL (book remains).
  * __Removing a status without `next`__: falls back to redirecting to the book detail page (book remains).
  * __Unsafe `next` is ignored__: off‑site `next` URLs are rejected; redirect falls back to the detail page.

* **Rating Tests**

  * __Unauthenticated redirects__: posting a rating without logging in redirects to the login page and does **not** create a record.
  * __Creating a rating__: authenticated users can post a rating, which creates a `Rating` row and redirects to the book detail view.
  * __Updating a rating__: posting a new value overwrites the existing `Rating` (no duplicates).
  * __Removing a rating__: posting `rating=0` deletes the existing row and redirects back to the book detail page.
  * __Auto-create status__: if a user rates a book without an existing `ReadingStatus`, the `post_save` signal ensures a new `READ` status is created.
  * __Respect existing status__: if the user already has a `ReadingStatus` (`TO_READ`, `READING`, `READ`), rating succeeds without changing it.


* **Review Tests**

  * __Creating a review__: POST to `/books/<book_id>/review/` saves and redirects; assert redirect and one new `Review` for `(user, book)`.
  * __Book detail displays reviews__: detail view lists reviews; assert content and author appear in “User Reviews”.
  * __Anonymous users see login CTA__: shows “Log in to leave a review”; assert CTA present and no `<form>`.
  * __Authenticated users see add review form__: no existing review → textarea rendered; assert form action targets `add_review`.
  * __Editing a review (no duplicates)__: second POST updates existing row; assert updated content and still exactly one `Review`.
  * __Creates READ status when missing__: Posting a review with no existing `ReadingStatus` auto-creates one with status **READ**, then redirects back to the book detail.
  * __Respects existing status__: If a `ReadingStatus` already exists (e.g. **READING**), saving/posting a review **does not** override it to READ; the original status remains unchanged.
  * __Delete ownership check__: Only the user who created a review can delete it. Delete button is not visible to others.
  * __Delete confirmation__: The book detail page renders a modal for delete confirmation, allowing the user to confirm or cancel the deletion.
  * __Delete success__: The review is removed from the database after confirmation, displaying a success message to user.


### Approach

* **Isolation**: External API calls are mocked to ensure tests run quickly and deterministically.
* **Resilience**: Cache is cleared between tests to avoid cross-test interference.
* **Realism**: Sample JSON payloads (e.g.`REALISTIC_DETAIL_JSON`) simulate real Google Books responses for reliable field mapping tests.

These tests run automatically with:

```bash
python manage.py test
```

and provide confidence that both authentication flows and book-related features behave as expected under different conditions.

---


## Credits & References

- Homepage banner image: [Unsplash](https://unsplash.com/photos/iyKVGRu79G4) Photo by [Lilly Rum](https://unsplash.com/@rumandraisin?utm_content=creditCopyText&utm_medium=referral&utm_source=unsplash)
- Google Books API: [Google Developers](https://developers.google.com/books/docs/v1/getting_started)
- Color palette: [Material Palette](https://www.materialpalette.com/teal/deep-orange)
- Favicon: [Favicon.io](https://favicon.io/favicon-converter/)
- Favicon art by [Good Ware](https://www.flaticon.com/authors/good-ware)
- ChatGPT: [OpenAI](https://openai.com/chatgpt) for documentation improvement
- Copilot: [GitHub Copilot](https://github.com/features/copilot) for code completion and docstring generation
- Django Allauth: [Django Allauth](https://django-allauth.readthedocs.io/en/latest/)
- Conditional Requests: [MDN Web Docs](https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Conditional_requests)
- Session Objects: [Requests Documentation](https://requests.readthedocs.io/en/latest/user/advanced/#conditional-requests)
