import numpy as np
import itertools

def gen_combinations(d):
    keys, values = d.keys(), d.values()
    if not isinstance(list(values)[0], list):
        values = [values]
    combinations = itertools.product(*values)

    for c in combinations:
        yield dict(zip(keys, c))

def get_exp_range(min, max, steps, percent=0.825):
    span = max - min
    def get_exp():
        e = 1 / np.sort(np.random.exponential(1, steps))
        e = 1 - ((e - np.min(e))/np.ptp(e))
        return (e*span) + min
    exps = [get_exp() for _ in range(1000)]
    i = np.argmin([np.abs(e.mean() - (span*percent)) for e in exps])
    return exps[i]

def rm_glob(glob_str):
    [os.remove(msh) for msh in glob.glob(glob_str)]

def normalizar_conf(conf):
    for k, v in conf.items():
        if isinstance(v, list):
            mode = v[0]
            if isinstance(mode, str):
                if len(v) > 3:
                    min, max, steps = v[1:]
                if mode == 'lin':
                    conf[k] = np.linspace(min, max, steps)
                elif mode == 'exp':
                    conf[k] = get_exp_range(min, max, steps)
                elif mode == 'vals':
                    conf[k] = v[1:]
                elif mode == 'tile':
                    conf[k] = np.tile(*v[1:])
            else:
                conf[k] = np.linspace(*v)
        else:
            conf[k] = [v]