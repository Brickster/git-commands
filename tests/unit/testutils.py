def and_exit(*args, **kwargs):
    exit_ = kwargs.get('exit_', True)
    if exit_:
        raise SystemExit('exited')

# https://stackoverflow.com/a/8389373
class PseudoTTY(object):
    def __init__(self, underlying, is_real):
        self.__underlying = underlying
        self.is_real = is_real

    def __getattr__(self, name):
        return getattr(self.__underlying, name)

    def isatty(self):
        return self.is_real