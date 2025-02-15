from dataclasses import dataclass

from pydantic_core.core_schema import dataclass_args_schema

from .base import get_config
import configparser
from typing import List


@dataclass
class Reminder:
    time: str | List[int]

    def __post_init__(self):
        self.time = [int(i) for i in self.time.split(",")]


@dataclass
class Scrap:
    period: str | int

    def __post_init__(self):
        self.period = int(self.period)


@dataclass
class Goat:
    bots_addition: int | str

    def __post_init__(self):
        self.bots_addition = int(self.bots_addition)


@dataclass
class Config:
    reminder: Reminder
    scrap: Scrap
    goat: Goat


def load_config():
    configuration_file = configparser.ConfigParser()
    configuration_file.read("config.ini")

    local_config = Config(
        reminder=Reminder(
            time=get_config(configuration_file, "time", "REMINDER", default="30,60,120,180,240")
        ),
        scrap=Scrap(
            period=get_config(configuration_file, "period", "SCRAP", default="5")
        ),
        goat=Goat(
            bots_addition=get_config(configuration_file, "goat_addition", "GOAT", default="6")
        )
    )
    return local_config


configuration: Config = load_config()
