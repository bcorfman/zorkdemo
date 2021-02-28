from environs import Env

env = Env()
env.read_env()

# Override in .env for local development
DEBUG = env.bool("FLASK_DEBUG", default=False)

# SECRET_KEY is required
SECRET_KEY = env.str("SECRET_KEY")

DATABASE = env.str("DATABASE", default="sqlite:///sessions.db")
