# Todo Project

A small task manager built with Django. You can view tasks, add a task, edit its title or description, mark it complete, and delete it. Django serves the pages, handles each URL, and stores tasks in a local SQLite database.

## Run the project locally

From the directory containing `manage.py`:

```bash
python -m venv .venv
source .venv/bin/activate       # macOS/Linux
# Windows: .venv\Scripts\activate
python -m pip install "Django>=5.0,<6.0"
python manage.py migrate
python manage.py runserver
```

Open <http://127.0.0.1:8000/> in your browser. `migrate` creates the local `db.sqlite3` database and its tables; the database file is intentionally excluded from Git. If you want to use a non-default Django secret key, set the `DJANGO_SECRET_KEY` environment variable before starting the server.

## What happens when a request arrives

1. `manage.py` sets `DJANGO_SETTINGS_MODULE` to `todo_project.settings` and starts Django's command-line runner.
2. `todo_project/settings.py` loads the project configuration. It names `todo_project.urls` as the root URL configuration, registers `todo_app`, configures the templates and static files, and points the database to `db.sqlite3`.
3. Django checks `todo_project/urls.py` against the requested URL. The matching route calls a view function in `todo_app/views.py`.
4. The view reads or changes records through the `todo_table` model in `todo_app/models.py`. Django translates those model operations into SQLite queries.
5. For a page response, the view renders a template from `template/`. For a completed form action, it usually redirects the browser back to the task list.

The HTML templates include the CSS files from `static/`. Django's template engine fills in task values and URL links when it renders a page.

## Task flows

### View the task list

1. The browser requests `/` (or `/home/`).
2. `todo_project/urls.py` routes the request to `views.home`.
3. `home()` in `todo_app/views.py` loads all rows with `todo_table.objects.all()`.
4. The view passes those rows as `data` to `template/home.html`.
5. `home.html` loops over `data` and displays each task, with Edit and Delete links and a completion checkbox. If there are no rows, it displays “No tasks available.”

In the current template, the `Done` column shows the Pending/Completed text, while the checkbox appears beneath the `Created` heading. The task's `created` date is stored but is not currently rendered in the table.

The page includes `template/navbar.html`, which links to the Add Task page. Its styles come from `static/home.css` and `static/navbar.css`.

### Add a task

1. The user clicks Add Task in `template/navbar.html`; the link opens `/add_task/`.
2. `todo_project/urls.py` sends that URL to `views.add_task`.
3. For the initial **GET** request, `add_task()` renders `template/add_task.html`.
4. The user enters a title and description and submits the form. The form sends a **POST** request with those values and a CSRF token.
5. `add_task()` reads `title` and `description` from `request.POST` and calls `todo_table.objects.create(...)`.
6. The model creates a task in SQLite. `done` defaults to `False`, and `created` is set to the current date by the model.
7. The view redirects to the `home` route, where the updated task list is loaded and rendered.

The form is styled with `static/add_task.css` and `static/navbar.css`.

### Edit a task

1. The user clicks Edit next to a task in `template/home.html`. The link includes that task's ID, for example `/edit_task/3/`.
2. `todo_project/urls.py` matches the integer ID and calls `views.edit_task(request, task_id)`.
3. `edit_task()` looks up the row by ID using `get_object_or_404()`. If the ID does not exist, Django returns a 404 page.
4. For a **GET** request, the view passes the task to `template/edit_task.html`. The form fields are prefilled with its current title and description.
5. When the user submits the form, the **POST** request returns to the same ID-specific URL. The view trims the submitted title and description, updates the task's `done` value from the submitted form, and calls `task.save()`.
6. The view redirects to the task list, which reads the saved row again from SQLite.

The current edit form contains title and description fields but no `done` checkbox. Therefore, submitting the edit form sets `done` to `False`; use the task-list checkbox to mark a task complete.

### Mark a task complete or pending

1. The checkbox in `template/home.html` submits its form to `/task_completed/<task_id>/` when changed.
2. The route calls `views.task_completed()`.
3. The view finds the task, reads the posted checkbox value, sets `done` to `True` when the value is `True` (otherwise `False`), and saves the row.
4. The view redirects to the task list.

### Delete a task

1. The user clicks Delete next to a task in `template/home.html`. The link opens `/delete_task/<task_id>/`.
2. `todo_project/urls.py` routes the ID to `views.delete_task()`.
3. The view finds the row with `get_object_or_404()`, deletes it from SQLite, and redirects to the task list.

In the current implementation, clicking Delete immediately deletes the task: the link uses a GET request and there is no confirmation page.

## Project structure

```text
todo_project/
├── manage.py                       # Django command-line entry point
├── README.md                       # This guide
├── db.sqlite3                      # Local database created by migrate (ignored by Git)
├── todo_project/                   # Django project configuration
│   ├── settings.py                 # Apps, middleware, templates, database, static files
│   ├── urls.py                     # URL routes mapped to views
│   ├── asgi.py                     # ASGI application entry point
│   └── wsgi.py                     # WSGI application entry point
├── todo_app/                       # Todo application code
│   ├── views.py                    # Request handlers and task operations
│   ├── models.py                   # todo_table database model
│   ├── admin.py                    # Django admin registration (currently empty)
│   ├── apps.py                     # App configuration
│   ├── tests.py                    # Test module (currently has no tests)
│   └── migrations/
│       └── 0001_initial.py         # Creates the initial todo_table schema
├── template/                       # Django HTML templates
│   ├── home.html                   # Task list and task actions
│   ├── add_task.html               # New task form
│   ├── edit_task.html              # Existing task form
│   └── navbar.html                 # Shared navigation with Add Task link
└── static/                         # Page stylesheets
    ├── home.css
    ├── add_task.css
    ├── edit_task.css
    └── navbar.css
```

## Data model

`todo_app/models.py` defines the `todo_table` model. Each database row represents one task:

| Field | Type | Purpose |
| --- | --- | --- |
| `id` | Auto-generated integer | Unique task ID used in edit, delete, and completion URLs |
| `title` | Text, up to 30 characters | Task title |
| `description` | Text, up to 30 characters | Task description |
| `done` | Boolean, defaults to `False` | Whether the task is complete |
| `created` | Date, set on creation | Date the task was added |

`todo_app/migrations/0001_initial.py` creates this model's table when you run `python manage.py migrate`.

## URL and view map

| URL | View | What it does |
| --- | --- | --- |
| `/` and `/home/` | `home` | Loads and displays all tasks |
| `/add_task/` | `add_task` | Shows the form, then creates a task on POST |
| `/edit_task/<task_id>/` | `edit_task` | Shows and saves changes for one task |
| `/delete_task/<task_id>/` | `delete_task` | Deletes one task and returns to the list |
| `/task_completed/<task_id>/` | `task_completed` | Updates completion status and returns to the list |
| `/admin/` | Django admin | Django's built-in administration route |

## Other project notes

- `todo_project/asgi.py` and `todo_project/wsgi.py` expose the application to ASGI- and WSGI-compatible servers.
- `todo_app/admin.py` currently does not register `todo_table` with the Django admin.
- `todo_app/tests.py` currently contains no automated tests.
- `.gitignore` excludes the local SQLite database, virtual environments, Python cache files, and `.env` files.
