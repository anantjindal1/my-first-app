## My First App

### `todo.py` CLI

This repository includes a small Python command-line to-do list app backed by `tasks.json`.

All commands are run from the project root:

```bash
python3 todo.py <command> [args...]
```

### Data storage

- **File**: `tasks.json`
- **Format**: JSON array of objects with:
  - `title`: string
  - `done`: boolean
  - `priority`: `"normal" | "high" | "low"`
  - `category`: string (default `"None"`)

### Commands

- **Show help**

```bash
python3 todo.py
```

Prints a short usage summary of all supported commands.

- **Add a task**

```bash
python3 todo.py add "task name" [--high|--low]
```

- **Behavior**:
  - Creates a new task with:
    - `title` = `"task name"`
    - `priority` = `"normal"` by default
    - `priority` = `"high"` when `--high` is provided
    - `priority` = `"low"` when `--low` is provided
    - `category` = `"None"`
  - Rejects empty titles with a clear error message.

- **Add a task with a category**

```bash
python3 todo.py add-category <category> "task name" [--high|--low]
```

- **Behavior**:
  - Same as `add`, but also sets `category` to `<category>`.
  - Priority flags work the same way (`--high` / `--low`).

- **List tasks**

```bash
python3 todo.py list
```

- **Output format**:

```text
<index>. [<status>] <priority-icon><title> :: <category>
```

- **Details**:
  - `<index>`: 1-based task number.
  - `<status>`: `✓` for completed, space for pending.
  - `<priority-icon>`:
    - `🔴 ` for high priority
    - `🔵 ` for low priority
    - empty for normal
  - `<category>`: category name, or `"None"` if unset.
  - If there are no tasks, prints: `No tasks. You're all caught up!`

- **Mark a single task done**

```bash
python3 todo.py done <number>
```

- **Behavior**:
  - Marks the task at the given 1-based index as completed.
  - Handles invalid or out-of-range numbers with clear error messages.

- **Mark an entire category done**

```bash
python3 todo.py done-category <category>
```

- **Behavior**:
  - Marks all tasks in the given category as completed.
  - If no pending tasks exist in that category, prints a message instead of changing anything.

- **Delete a task**

```bash
python3 todo.py delete <number>
```

- **Behavior**:
  - Deletes the task at the given 1-based index.
  - Handles invalid indices and empty lists gracefully.

- **Clear all completed tasks**

```bash
python3 todo.py clear
```

- **Behavior**:
  - Removes all tasks where `done` is `True`.
  - If there are no tasks, prints: `No tasks to clear.`
  - If there are tasks but none completed, prints: `There are no completed tasks to clear.`
