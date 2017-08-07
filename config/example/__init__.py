from constants import MED_OK, MED_NO
import random
conf = {}

def register(evname):
    def register_decorator(func):
        hooks = conf.setdefault(evname, [])
        hooks.append({'exec': func})
        return func
    return register_decorator

@register('getprocess')
def aka(evtype, subj, obj):
    print(evtype)
    print(subj)
    print(obj)
    return MED_OK

@register('kill')
def kill(etype, subj, obj):
    return MED_NO

@register('fork')
def fork(evtype, subj, obj):
    if random.random() < 0.2:
        return MED_NO
    return MED_YES
