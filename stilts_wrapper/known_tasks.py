import yaml
from pathlib import Path

def _load_known_tasks():
    config_dir = Path(__file__).absolute().parent / "configuration"
    known_tasks_path = config_dir / "known_tasks.yaml"
    with open(known_tasks_path, "r") as f:
        known_tasks= yaml.load(f, Loader=yaml.FullLoader)
        known_tasks["all_tasks"] = [
            task for task_type in known_tasks.values() for task in task_type
        ]
    return known_tasks

KNOWN_TASKS = _load_known_tasks()
