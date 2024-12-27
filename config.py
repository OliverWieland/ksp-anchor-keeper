import argparse
from dataclasses import dataclass
from pathlib import Path

import yaml

_DEFAULT_SAVES_DIR = Path.home() / "KSP" / "saves"
_DEFAULT_DB_PATH = Path("anchors.db")


@dataclass
class ConfigData:
    saves_directory: Path = _DEFAULT_SAVES_DIR
    database_path: Path = _DEFAULT_DB_PATH


class Config:
    DEFAULT_CONFIG_PATH = Path("config.yaml")

    def __init__(self):
        self.saves_directory = _DEFAULT_SAVES_DIR
        self.database_path = _DEFAULT_DB_PATH
        self.load_config()

    def load_config(self):
        # Load from YAML if exists
        config_data = self._load_yaml()

        # Parse command line args
        args = self._parse_args()

        # Priority: CLI args > YAML > defaults
        self.saves_directory = Path(
            args.saves_dir or config_data.saves_directory
        ).expanduser()

        self.database_path = Path(config_data.database_path).expanduser()

        self._validate_paths()

    def _load_yaml(self) -> ConfigData:
        if self.DEFAULT_CONFIG_PATH.exists():
            with open(self.DEFAULT_CONFIG_PATH) as f:
                return ConfigData(**yaml.safe_load(f))
        return ConfigData()

    def _parse_args(self):
        parser = argparse.ArgumentParser(description="KSP Anchor Keeper")
        parser.add_argument("--saves-dir", type=str, help="Path to KSP saves directory")
        return parser.parse_args()

    def _validate_paths(self):
        if not self.saves_directory.exists():
            raise ValueError(f"Saves directory not found: {self.saves_directory}")
