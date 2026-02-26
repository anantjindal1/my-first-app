#!/usr/bin/env python3

"""
Simple command-line to-do list app.

Design decisions:
- Store tasks in a JSON file (`tasks.json`) so it's easy to inspect and edit.
- Represent each task as a dict with `title` and `done` keys for clarity.
- Keep everything in a single file, but isolate logic in small functions to
  make it easy to extend (e.g., due dates, priorities) later.
"""

from __future__ import annotations

import json
import sys
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import List


TASKS_FILE = Path("tasks.json")


@dataclass
class Task:
    # Use a dataclass so the task shape is explicit and easy to serialize.
    title: str
    done: bool = False
    # Track a simple priority flag so we can render visual hints (e.g., 🔴/🔵).
    # Values: "normal" (default), "high", "low".
    priority: str = "normal"


def load_tasks() -> List[Task]:
    """
    Load tasks from the JSON file.

    Returns an empty list if the file does not exist or is invalid JSON.
    This makes the CLI robust to manual edits or first run.
    """
    if not TASKS_FILE.exists():
        return []

    try:
        raw = json.loads(TASKS_FILE.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        # If the file is corrupted, treat it as empty instead of crashing.
        return []

    if not isinstance(raw, list):
        return []

    tasks: List[Task] = []
    for item in raw:
        if not isinstance(item, dict):
            continue
        title = item.get("title")
        done = item.get("done", False)
        # Default priority to "normal" so older JSON files stay compatible.
        priority = item.get("priority", "normal")
        if isinstance(title, str) and isinstance(done, bool):
            tasks.append(Task(title=title, done=done, priority=priority))
    return tasks


def save_tasks(tasks: List[Task]) -> None:
    """
    Persist tasks to disk in a stable, human-readable format.
    """
    try:
        serialized = [asdict(t) for t in tasks]
        TASKS_FILE.write_text(
            json.dumps(serialized, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )
    except OSError:
        # Fail silently; for a simple CLI, we don't want to crash on IO errors.
        # In a larger app, this would be logged or surfaced to the user.
        pass


def cmd_list(tasks: List[Task]) -> None:
    """
    Print tasks in a numbered list with a checkmark for completed ones.
    """
    if not tasks:
        print("No tasks. You're all caught up!")
        return

    for idx, task in enumerate(tasks, start=1):
        status = "✓" if task.done else " "
        # Use emojis to show priority at a glance.
        if task.priority == "high":
            priority_marker = "🔴 "
        elif task.priority == "low":
            priority_marker = "🔵 "
        else:
            priority_marker = ""
        print(f"{idx}. [{status}] {priority_marker}{task.title}")


def cmd_add(tasks: List[Task], title: str, priority: str = "normal") -> None:
    """
    Add a new task with the given title.
    """
    if not title.strip():
        print("Cannot add an empty task.")
        return
    # Normalize whitespace and apply the requested priority.
    tasks.append(Task(title=title.strip(), done=False, priority=priority))
    save_tasks(tasks)
    print(f'Added: "{title.strip()}"')


def _index_from_user(tasks: List[Task], num_str: str) -> int | None:
    """
    Convert a 1-based user index into a 0-based list index with validation.
    Returns None and prints an error message if invalid.
    """
    try:
        num = int(num_str)
    except ValueError:
        print("Please provide a valid task number.")
        return None

    if num < 1 or num > len(tasks):
        if not tasks:
            print("There are no tasks yet.")
        else:
            print(f"Task number must be between 1 and {len(tasks)}.")
        return None

    return num - 1


def cmd_done(tasks: List[Task], num_str: str) -> None:
    """
    Mark the given task as completed.
    """
    if not tasks:
        print("No tasks to mark as done.")
        return

    idx = _index_from_user(tasks, num_str)
    if idx is None:
        return

    tasks[idx].done = True
    save_tasks(tasks)
    print(f'Marked as done: "{tasks[idx].title}"')


def cmd_delete(tasks: List[Task], num_str: str) -> None:
    """
    Delete the given task by number.
    """
    if not tasks:
        print("No tasks to delete.")
        return

    idx = _index_from_user(tasks, num_str)
    if idx is None:
        return

    removed = tasks.pop(idx)
    save_tasks(tasks)
    print(f'Deleted: "{removed.title}"')


def cmd_clear_completed(tasks: List[Task]) -> None:
    """
    Remove all completed tasks from the list.
    """
    if not tasks:
        print("No tasks to clear.")
        return

    # Keep tasks that are not marked as done.
    remaining = [t for t in tasks if not t.done]
    cleared_count = len(tasks) - len(remaining)

    if cleared_count == 0:
        print("There are no completed tasks to clear.")
        return

    save_tasks(remaining)
    # Reflect the new state in-memory so further operations in this process see it.
    tasks[:] = remaining
    print(f"Cleared {cleared_count} completed task(s).")


def print_usage() -> None:
    """
    Show a concise usage guide so the CLI is self-documenting.
    """
    print("Usage:")
    print('  todo.py add "task name" [--high|--low]')
    print("  todo.py list")
    print("  todo.py done <number>")
    print("  todo.py delete <number>")
    print("  todo.py clear")


def main(argv: List[str]) -> None:
    """
    Small argv router so the logic stays testable and extendable.
    """
    if len(argv) < 2:
        print_usage()
        return

    command = argv[1]
    tasks = load_tasks()

    if command == "list":
        cmd_list(tasks)
    elif command == "add":
        if len(argv) < 3:
            print('Missing task name. Example: todo.py add "Buy milk"')
            return
        # Support an optional trailing priority flag: --high or --low.
        # Everything before the flag is treated as the task title.
        *title_parts, last_part = argv[2:]
        priority = "normal"
        if last_part == "--high":
            priority = "high"
        elif last_part == "--low":
            priority = "low"
        else:
            title_parts.append(last_part)

        title = " ".join(title_parts)
        cmd_add(tasks, title, priority)
    elif command == "done":
        if len(argv) < 3:
            print("Missing task number. Example: todo.py done 1")
            return
        cmd_done(tasks, argv[2])
    elif command == "delete":
        if len(argv) < 3:
            print("Missing task number. Example: todo.py delete 1")
            return
        cmd_delete(tasks, argv[2])
    elif command == "clear":
        cmd_clear_completed(tasks)
    else:
        print(f"Unknown command: {command}")
        print_usage()


if __name__ == "__main__":
    main(sys.argv)

