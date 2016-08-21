def and_exit(*args, **kwargs):
    exit_ = kwargs.get('exit_', True)
    if exit_:
        raise SystemExit('exited')
