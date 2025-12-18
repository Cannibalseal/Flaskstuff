import os

# Expose a config object based on FLASK_ENV (defaults to production-like defaults)
def get_config():
    env = os.environ.get('FLASK_ENV', os.environ.get('APP_ENV', 'production'))
    # load default config first
    from .default import default_config as default_cfg

    if env == 'development':
        try:
            # import the development module which may expose a few variables
            from . import development as dev_mod

            class _Cfg:
                pass

            cfg = _Cfg()
            # fill attributes from development module if present, otherwise fallback to defaults
            cfg.SECRET_KEY = getattr(dev_mod, 'SECRET_KEY', default_cfg.SECRET_KEY)
            cfg.DATABASE = getattr(dev_mod, 'DATABASE', default_cfg.DATABASE)
            cfg.SCHEMA = getattr(dev_mod, 'SCHEMA', default_cfg.SCHEMA)
            cfg.ADMIN_USER = getattr(dev_mod, 'ADMIN_USER', default_cfg.ADMIN_USER)
            cfg.ADMIN_PASS = getattr(dev_mod, 'ADMIN_PASS', default_cfg.ADMIN_PASS)
            cfg.DEBUG = getattr(dev_mod, 'DEBUG', default_cfg.DEBUG)
            return cfg
        except Exception:
            # fall back to defaults on any error
            return default_cfg

    # fallback to default
    return default_cfg


# module-level config object used by imports
cfg = get_config()
