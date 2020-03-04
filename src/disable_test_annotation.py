def disabled(reason):
    def _func(f):
        def _arg():
            print(f.__name__ + ' has been disabled. ' + reason)
        return _arg
    return _func

