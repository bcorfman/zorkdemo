# Extending The Game

This guide explains where to add new content and commands in the current Python engine.

## Quick Contributor Flow

1. Add or update content objects in the `adventure/` package.
2. Add tests for new behavior under `tests/` (engine) and `backend/tests/` (API behavior if needed).
3. Run quality checks:
   - `make lint`
   - `make test`

## Add A New Location

1. Create a new location class in `adventure/` similar to `NorthOfHouse` and `WestOfHouse`.
2. Add a matching text file under `data/` named after the class (for example, `DeepForest.txt`).
3. Register the location in `Adventure.__init__` in `adventure/app.py` by adding it to `self.locations`.
4. Add directional access by updating `accessible` mappings on related location classes.

## Add A New Item

1. Define the item in the relevant location module (or a shared item module).
2. Add item features via `Item(...)` keyword arguments (`full_name`, `description`, `can_be_taken`, etc.).
3. Include the item in the location's `contains` list so it appears in world state.
4. Add tests for examine/take/drop/open/close behavior as needed.

## Add A New Command

1. Implement a new method on `Adventure` in `adventure/app.py`.
2. Wire command tokens to that method in `self.commands` inside `Adventure.__init__`.
3. Keep output in markdown/plain text so backend and frontend rendering remain consistent.
4. Add command-level tests in `tests/test_app.py` and API-level tests in `backend/tests/` if behavior affects endpoints.

## API Notes

The backend wraps this engine and exposes:

- `POST /api/v1/session`
- `POST /api/v1/command`
- `POST /api/v1/session/reset`

If command behavior changes response semantics, update and run `backend/tests/test_smoke_e2e.py`.
