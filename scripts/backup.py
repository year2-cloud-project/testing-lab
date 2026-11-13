from pathlib import Path
import shutil


def backup_files(source_dir, destination_dir):
    source = Path(source_dir)
    destination = Path(destination_dir)

    if not source.is_dir():
        raise FileNotFoundError(f"Backup source does not exist: {source}")

    destination.mkdir(parents=True, exist_ok=True)

    copied = []
    for source_file in sorted(source.glob("*.json")):
        target_file = destination / source_file.name
        shutil.copy2(source_file, target_file)
        copied.append(target_file)

    return copied
