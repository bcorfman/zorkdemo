"""
template loading helper
"""
from jinja2 import FileSystemLoader, Environment


template_engine = Environment(loader=FileSystemLoader("web/templates"))


def get_template(name):
    """get and return a template"""
    return template_engine.get_template(name)
