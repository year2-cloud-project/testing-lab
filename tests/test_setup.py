from pathlib import Path


def test_monitoring_configuration_is_present():
    assert Path("config/monitoring.json").is_file()
