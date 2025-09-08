# Tests Documentation

This document provides an overview of all tests in the repository, grouped by file. 
It was generated automatically by scanning for files named `tests.py`, `test_*.py`, `*_test.py`, or located inside `tests/` or `test/` directories.

**Summary:** 94 test functions across 11 files.

For test to run correctly they require the static storage configuration found at `settings_test.py`.

You can run them automatically with:
```bash
python manage.py test --settings=chaptr.settings_test
```


## `accounts/Tests/tests_allauth.py`

| App / Module   | Test Class         | Test Function                                             | Docstring                                                                    |
|:---------------|:-------------------|:----------------------------------------------------------|:-----------------------------------------------------------------------------|
| accounts       | LoginLogoutTests   | test_login_empty_password_validation                      | Test login form password validation error.                                   |
| accounts       | LoginLogoutTests   | test_login_empty_username_validation                      | Test login form username validation error.                                   |
| accounts       | LoginLogoutTests   | test_login_page_excludes_search_form                      | Test that the login page does NOT include the search form.                   |
| accounts       | LoginLogoutTests   | test_login_page_renders                                   | Test that the login page renders correctly.                                  |
| accounts       | LoginLogoutTests   | test_login_with_invalid_password_fails                    | Test that login fails with an invalid password.                              |
| accounts       | LoginLogoutTests   | test_login_with_nonexistent_user_fails                    | Authentication should fail with a non-existent username.                     |
| accounts       | LoginLogoutTests   | test_logout_page_excludes_search_form                     | Test that the logout page does NOT include the search form.                  |
| accounts       | LoginLogoutTests   | test_logout_page_renders                                  | Test that the logout confirmation page renders.                              |
| accounts       | LoginLogoutTests   | test_logout_when_logged_in                                | Test successful logout when user is logged in.                               |
| accounts       | LoginLogoutTests   | test_logout_when_not_logged_in                            | Test logout behavior when user is not logged in.                             |
| accounts       | LoginLogoutTests   | test_successful_login_with_username                       | Test successful login using username.                                        |
| accounts       | PasswordResetTests | test_password_reset_page_excludes_search_form             | Test that the password reset page does NOT include the search form.          |
| accounts       | PasswordResetTests | test_password_reset_page_renders                          | Test that the password reset page renders correctly.                         |
| accounts       | PasswordResetTests | test_password_reset_sends_email                           | Test that password reset sends an email.                                     |
| accounts       | SignupBasicsTests  | test_signup_page_excludes_search_form                     | Test that the signup page does NOT include the search form.                  |
| accounts       | SignupBasicsTests  | test_signup_page_renders                                  | Test that the signup page renders correctly.                                 |
| accounts       | SignupBasicsTests  | test_signup_password_mismatch                             | Test that signup shows validation error for password mismatch.               |
| accounts       | SignupBasicsTests  | test_signup_password_too_short                            | Test that signup shows validation error for password too short.              |
| accounts       | SignupBasicsTests  | test_signup_success_shows_feedback_and_sends_confirmation | Test that a successful signup shows feedback and sends a confirmation email. |
| accounts       | SignupBasicsTests  | test_signup_username_taken                                | Test that signup shows validation error for taken username.                  |


## `activity/Tests/tests_archive_flow.py`

| App / Module   | Test Class                      | Test Function                                  | Docstring                                                               |
|:---------------|:--------------------------------|:-----------------------------------------------|:------------------------------------------------------------------------|
| activity       | ArchiveOnStatusRemovalTests     | test_status_none_archives_rating_and_review    | Setting status to NONE deletes status and archives ratings and reviews. |
| activity       | DetailHidesArchivedReviewsTests | test_archived_reviews_hidden_from_detail       | Archived reviews should not appear on book detail page.                 |
| activity       | UnarchiveOnNewRatingTests       | test_post_rating_unarchives_and_creates_status | Posting a new rating unarchives archived rating                         |


## `activity/Tests/tests_delete_action.py`

| App / Module   | Test Class             | Test Function                                               | Docstring                          |
|:---------------|:-----------------------|:------------------------------------------------------------|:-----------------------------------|
| activity       | LibraryAndReviewsTests | test_delete_review_owner_only                               | Delete review (owner)              |
| activity       | LibraryAndReviewsTests | test_remove_from_library_from_details_deletes_and_redirects | Remove from Library (details page) |


## `activity/Tests/tests_rating.py`

| App / Module   | Test Class      | Test Function                                       | Docstring                                                                                                                                       |
|:---------------|:----------------|:----------------------------------------------------|:------------------------------------------------------------------------------------------------------------------------------------------------|
| activity       | RatingViewTests | test_authenticated_users_can_remove_a_book_rating   | Test that authenticated users can remove their book rating.                                                                                     |
| activity       | RatingViewTests | test_authenticated_users_can_update_a_book_rating   | Test that authenticated users can update their book rating.                                                                                     |
| activity       | RatingViewTests | test_can_rate_regardless_of_existing_reading_status | If the user already has any reading status (TO_READ/READING/READ), rating should still succeed and the existing status should remain unchanged. |
| activity       | RatingViewTests | test_rating_creates_record_for_authenticated_user   | Test that posting a rating creates a Rating object.                                                                                             |
| activity       | RatingViewTests | test_unauthenticated_users_redirect_to_login        | Test that unauthenticated users are redirected to login.                                                                                        |
| activity       | RatingViewTests | test_user_can_rate_book_with_no_reading_status      | Test that authenticated users can rate a book with no reading status and reading status is created as READ                                      |


## `activity/Tests/tests_reading_status.py`

| App / Module   | Test Class           | Test Function                                            | Docstring                                                                         |
|:---------------|:---------------------|:---------------------------------------------------------|:----------------------------------------------------------------------------------|
| activity       | ReadingStatusUITests | test_add_status_creates_record_for_authenticated_user    | Clicking the button when authenticated creates the record with the correct status |
| activity       | ReadingStatusUITests | test_all_valid_status_choices                            | Test all valid status choices can be set                                          |
| activity       | ReadingStatusUITests | test_anonymous_user_sees_login_button                    | Test that anonymous users see log in button.                                      |
| activity       | ReadingStatusUITests | test_remove_status_ignores_unsafe_next_and_uses_fallback | If `next` is off-site, it must be ignored and redirect to fallback (detail).      |
| activity       | ReadingStatusUITests | test_remove_status_redirects_back_when_next_is_safe      | status=NONE deletes the row and redirects to the provided `next` (same-site URL). |
| activity       | ReadingStatusUITests | test_remove_status_redirects_to_detail_when_next_missing | Without `next`, redirect should fall back to book_detail.                         |
| activity       | ReadingStatusUITests | test_unauthenticated_user_redirected_to_login            | Unauthenticated users should be redirected to login page                          |


## `activity/Tests/tests_reviews.py`

| App / Module   | Test Class      | Test Function                                            | Docstring                                                                                                  |
|:---------------|:----------------|:---------------------------------------------------------|:-----------------------------------------------------------------------------------------------------------|
| activity       | ReviewFlowTests | test_anonymous_sees_login_message_no_form                | Test that an anonymous user sees a login prompt without a form.                                            |
| activity       | ReviewFlowTests | test_authenticated_user_with_review_sees_buttons         | Test that an authenticated user without a review sees edit and delete buttons.                             |
| activity       | ReviewFlowTests | test_authenticated_user_without_review_sees_correct_form | Test that an authenticated user without a review sees the review form.                                     |
| activity       | ReviewFlowTests | test_book_detail_displays_reviews                        | Test that the book detail view displays reviews.                                                           |
| activity       | ReviewFlowTests | test_delete_button_visible_only_for_owner                | The delete control should be visible for the current user's own review only.                               |
| activity       | ReviewFlowTests | test_delete_confirmation_modal_markup_present            | The book detail page should render a modal for delete confirmation, and delete buttons should point to it. |
| activity       | ReviewFlowTests | test_delete_removes_record_from_db                       | A successful POST to delete removes the Review row.                                                        |
| activity       | ReviewFlowTests | test_delete_shows_success_message                        | After a successful delete POST, a success message is flashed.                                              |
| activity       | ReviewFlowTests | test_review_creates_read_status_when_none_exists         | Posting a review creates READ status if none exists                                                        |
| activity       | ReviewFlowTests | test_review_respects_existing_read_status                | If a status already exists, posting a review should NOT override it to READ.                               |
| activity       | ReviewFlowTests | test_user_can_create_review                              | Test that a logged-in user can create a review.                                                            |
| activity       | ReviewFlowTests | test_user_can_delete_own_review                          | Test that a user can delete their own review.                                                              |
| activity       | ReviewFlowTests | test_user_can_edit_review_without_creating_duplicate     | Test that a user can edit their review without creating a duplicate.                                       |


## `books/Tests/tests_book_detail.py`

| App / Module   | Test Class          | Test Function                            | Docstring                                                 |
|:---------------|:--------------------|:-----------------------------------------|:----------------------------------------------------------|
| books          | BookDetailViewTests | test_book_detail_caches_volume           | Test that the book detail view caches the fetched volume. |
| books          | BookDetailViewTests | test_book_detail_renders_200_and_context | Test that the book detail view renders correctly.         |
| books          | BookDetailViewTests | test_book_detail_search_form_inclusion   | Test that the book detail page includes the search form.  |


## `books/Tests/tests_home.py`

| App / Module   | Test Class    | Test Function                                 | Docstring                                                       |
|:---------------|:--------------|:----------------------------------------------|:----------------------------------------------------------------|
| books          | HomeViewTests | test_about_section_content                    | Test that the about section renders correctly.                  |
| books          | HomeViewTests | test_anonymous_user_sees_auth_links           | Test that anonymous users see sign up and log in links.         |
| books          | HomeViewTests | test_authenticated_user_sees_welcome_and_menu | Test that logged-in users see welcome message and account menu. |
| books          | HomeViewTests | test_genre_section_content                    | Test that genre browsing section renders correctly.             |
| books          | HomeViewTests | test_hero_section_content                     | Test that hero section contains expected content.               |
| books          | HomeViewTests | test_home_page_extends_base_template          | Test that essential base template elements are present.         |
| books          | HomeViewTests | test_home_page_uses_correct_template          | Test that home view uses the correct template.                  |
| books          | HomeViewTests | test_home_view_renders                        | Test that the home page loads without errors.                   |
| books          | HomeViewTests | test_search_form_inclusion                    | Test that the search form is included in the header.            |


## `books/Tests/tests_search_books.py`

| App / Module   | Test Class             | Test Function                                                  | Docstring                                                       |
|:---------------|:-----------------------|:---------------------------------------------------------------|:----------------------------------------------------------------|
| books          | BookSearchViewTests    | test_book_search_no_query_renders                              | Test that the search view renders with no query.                |
| books          | BookSearchViewTests    | test_book_search_uses_built_query                              | Test that the search view uses the built query.                 |
| books          | BuildQTests            | test_build_q_all_keeps_plain_text                              | Leaves query unchanged when field is 'all'.                     |
| books          | BuildQTests            | test_build_q_empty_returns_empty                               | Returns empty string for empty input.                           |
| books          | BuildQTests            | test_build_q_preserves_existing_operator_even_if_field_differs | Passes through when user already supplied an operator.          |
| books          | BuildQTests            | test_build_q_subject_applies_operator                          | Applies `subject:` when field is 'subject'.                     |
| books          | BuildQTests            | test_build_q_with_field_author                                 | Applies `inauthor:` when field is 'author'.                     |
| books          | FetchBookByIdTests     | test_fetch_book_by_id_404_on_non_200                           | Test that fetch_book_by_id raises Http404 on non-200.           |
| books          | FetchBookByIdTests     | test_fetch_book_by_id_success_maps_fields                      | Test that fetch_book_by_id maps fields correctly.               |
| books          | SearchGoogleBooksTests | test_non_200_or_exception_returns_empty                        | Test that non-200 responses or exceptions return an empty list. |
| books          | SearchGoogleBooksTests | test_returns_parsed_list_on_200                                | Test that a successful API call returns a parsed list.          |


## `books/Tests/tests_search_pagination.py`

| App / Module   | Test Class                | Test Function                                       | Docstring                                                                                              |
|:---------------|:--------------------------|:----------------------------------------------------|:-------------------------------------------------------------------------------------------------------|
| books          | BookSearchPaginationTests | test_book_search_pagination_context_variables       | Tests that all pagination template variables are set correctly.                                        |
| books          | BookSearchPaginationTests | test_book_search_pagination_first_page              | Verifies that page 1 uses start_index=0.                                                               |
| books          | BookSearchPaginationTests | test_book_search_pagination_second_page             | Verifies that page 2 uses start_index=12.                                                              |
| books          | GenreBrowsingTests        | test_genre_tile_redirects_to_search_with_pagination | Tests that clicking a genre tile (subject) hits book_search and paginates.                             |
| books          | GenreBrowsingTests        | test_genre_tile_second_page_maintains_genre_filter  | Verifies that pagination preserves the genre filter (field & q) on subsequent pages.                   |
| books          | GenreBrowsingTests        | test_home_page_genre_links_format                   | Confirms genre links have the correct URL structure: /book_search?field=subject&q=<urlencoded-subject> |


## `library/Tests/tests.py`

| App / Module | Test Class              | Test Function                                              | Docstring                                                                                                                               |
| ------------ | ----------------------- | ---------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------- |
| library      | LibraryViewTests        | test_navbar_links_visible_only_when_authenticated          | Navbar (in base.html) shows user dropdown items only for logged-in users.                                                               |
| library      | LibraryViewTests        | test_unauthenticated_user_is_redirected_to_login           | Unauthenticated users should not see the library page. The @login_required decorator redirects to LOGIN_URL with ?next=...              |
| library      | LibraryViewTests        | test_authenticated_user_can_access_library                  | Authenticated users should be able to access the library page.                                                                          |
| library      | LibraryViewTests        | test_library_page_no_books                                  | If the user has no books in their library, they should see a message.                                                                   |
| library      | LibraryViewTests        | test_library_page_with_books                                | If the user has books in their library, they should see the book table and not the empty library message.                               |
| library      | LibraryViewTests        | test_library_page_with_only_to_read_book                    | If the user has only books on their to-read list, they shouldn't see empty library message.                                             |
| library      | LibraryViewTests        | test_library_page_with_only_reading_book                    | If the user has only books on their reading list, they shouldn't see empty library message.                                             |
| library      | LibraryViewTests        | test_library_page_with_only_read_book                       | If the user has only books on their reading list, they shouldn't see empty library message.                                             |
| library      | LibraryViewTests        | test_each_book_links_to_its_detail_page                     | Each book card links to the detail route 'book_detail' with the book pk.                                                                |
| library      | LibraryPageActionsTests | test_remove_from_library_deletes_and_redirects              | Remove from Library (library page).                                                                                                     |
| library      | LibraryPageActionsTests | test_change_status_to_to_read_from_library                  | Change status to TO_READ from library.                                                                                                   |
| library      | LibraryPageActionsTests | test_change_status_to_reading_from_library                  | Change status to READING from library.                                                                                                   |
| library      | LibraryPageActionsTests | test_change_status_to_read_from_library                     | Change status to READ from library.                                                                                                      |
| library      | LibraryPageActionsTests | test_library_actions_render_review_and_rating_links         | Verify the Library HTML contains the correct hrefs for the rows actions: - Write a review -> book detail #reviews - Rate -> book detail |
