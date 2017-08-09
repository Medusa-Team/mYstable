
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
    # execute function
    if callable(cmd):
        return cmd(obj)
    #conpare dictionaries
    if isinstance(cmd, dict):
        #print('compare dictionaries')
        for k, v in cmd.items():
            if not exec(v, obj[k]):
                False
        return True
    if isinstance(cmd, list):
        # compare lists
        if isinstance(obj, list):
            if len(cmd) != len(obj):
               return False
            for i in range(len(cmd)):
               if not exec(cmd[i], obj[i]):
                  return False
            return True
        # this is OR
        for i in cmd:
            if exec(i, obj):
                return True
        return False
    # and compare
    return cmd == obj

class Xor:
    def __init__(self, a, b):
        self.a = a
        self.b = b
    def __call__(self, obj):
        return exec(self.a, obj) ^ exec(self.b, obj)

class Not:
    def __init__(self, arg):
        self.arg = arg
    def __call__(self, val):
        return not exec(self.arg, val)

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

class Between:
    def __init__(self, a, b):
        self.a = a
        self.b = b
    def __call__(self, val):
        return self.a <= val and val <= self.b
