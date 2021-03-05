import sys
from pathlib import Path

from environs import Env


env = Env()
env.read_env()


class Config:
    DEBUG = env.bool("HUG_DEBUG", default=False)
    SECRET_KEY = env.str("SECRET_KEY")
    DATABASE_URL = env.str("DATABASE", default="sqlite:///sessions.db")
    TESTING = False


class TestConfig(Config):
    DEBUG = False
    SECRET_KEY = "testing key"
    DATABASE_URL = "sqlite:///:memory:"
    TESTING = True


STAGE = env.str("HUG_SETTINGS", default="config").lower()
print(STAGE)


CONFIG_STAGES = {
    "config": Config,
    "test": TestConfig,
}


settings = CONFIG_STAGES[STAGE]
