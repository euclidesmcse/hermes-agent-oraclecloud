import sys
import os
import json
import uuid
from datetime import datetime

# Database path
TASKS_FILE = os.path.join(os.path.dirname(__file__), "tasks.json")

def add_task(content, category="Geral", date=None, time=None):
    if not os.path.exists(TASKS_FILE):
        tasks = []
    else:
        try:
            with open(TASKS_FILE, "r", encoding="utf-8") as f:
                tasks = json.load(f)
        except Exception:
            tasks = []
            
    new_task = {
        "id": str(uuid.uuid4()),
        "content": content,
        "category": category,
        "date": date,
        "time": time,
        "status": "pending",
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    tasks.insert(0, new_task)
    with open(TASKS_FILE, "w", encoding="utf-8") as f:
        json.dump(tasks, f, ensure_ascii=False, indent=2)
    return new_task

def list_pending():
    if not os.path.exists(TASKS_FILE):
        return []
    try:
        with open(TASKS_FILE, "r", encoding="utf-8") as f:
            tasks = json.load(f)
        return [t for t in tasks if t["status"] == "pending"]
    except Exception:
        return []

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--add", action="store_true", help="Add a new task")
    parser.add_argument("--list", action="store_true", help="List all pending tasks")
    parser.add_argument("--content", type=str, help="Task content description")
    parser.add_argument("--category", type=str, default="Geral", help="Category: Anakin, Projetos, Compras, Geral")
    parser.add_argument("--date", type=str, default=None, help="Scheduled date (e.g., YYYY-MM-DD)")
    parser.add_argument("--time", type=str, default=None, help="Scheduled time (e.g., HH:MM)")
    args = parser.parse_args()
    
    if args.add:
        if not args.content:
            print("Error: --content is required when adding a task", file=sys.stderr)
            sys.exit(1)
        t = add_task(args.content, args.category, args.date, args.time)
        print(json.dumps(t, ensure_ascii=False))
    elif args.list:
        pending = list_pending()
        print(json.dumps(pending, ensure_ascii=False, indent=2))
    else:
        parser.print_help()
