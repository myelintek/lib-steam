__version__ = "0.4.0"
try:
    from .sha import __sha__
except Exception:
    __sha__ = '0'
