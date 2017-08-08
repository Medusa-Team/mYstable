
class Register():
    def __init__(self):
        self.hooks = {}

    def __call__(self, evname, **kwargs):
        def register_decorator(func):
            hooks = self.hooks.setdefault(evname, [])
            hooks.append({'exec': func,
                          'evtype': kwargs.get('evtype'),
                          'object': kwargs.get('object'),
                          'subject': kwargs.get('subject')})
            return func
        return register_decorator

def exec(cmd, obj):
    if callable(cmd):
        return cmd(obj)
    return cmd == obj

class And:
    def __init__(self, *args):
        self.args = args
    def __call__(self, obj):
        for i in self.args:
            if not exec(i, obj): return False
        return True

class Or:
    def __init__(self, *args):
        self.args = args
    def __call__(self, obj):
        for i in self.args:
            if exec(i, obj): return True
        return False

class Dividable:
    def __init__(self, val):
        self.val = val
    def __call__(self, val):
        return self.val % val == 0

class Ge:
    def __init__(self, val):
        self.val = val
    def __call__(self, val):
        return self.val <= val

class Gt:
    def __init__(self, val):
        self.val = val
    def __call__(self, val):
        return self.val < val

class Le:
    def __init__(self, val):
        self.val = val
    def __call__(self, val):
        return self.val >= val

class Lt:
    def __init__(self, val):
        self.val = val
    def __call__(self, val):
        return self.val > val

