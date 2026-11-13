from pathlib import Path
import shutil


def deploy_configs(source_dir, target_dir):
    source = Path(source_dir)
    target = Path(target_dir)

    if not source.is_dir():
        raise FileNotFoundError(f"Deployment source does not exist: {source}")

    target.mkdir(parents=True, exist_ok=True)

    deployed = []
    for source_file in sorted(path for path in source.iterdir() if path.is_file()):
        target_file = target / source_file.name
        shutil.copy2(source_file, target_file)
        deployed.append(target_file)

    return deployed
