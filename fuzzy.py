# -*- coding: utf-8 *-*
from collections import defaultdict
import parser_fuzzy

norm = min
conorm = max


class FuzzySet(object):

    def __init__(self, membership_function, label=''):
        self.label = label
        if type(membership_function) == str:
            self.mf = self.parse(membership_function)
        elif hasattr(membership_function, '__call__'):
            self.mf = membership_function

    def __call__(self, value):
        return self.mf(value)

    def parse(self, s):
        res = defaultdict(lambda: 0)
        s = s.replace(' ', '')
        for value in s.split('+'):
            mf, v = value.split('/')
            res[int(v)] = float(mf)
        return lambda x: res(x)

    def union(self, other):
        return FuzzySet(lambda v: max(self(v), other(v)))


def show_sets(universe, *sets, **kwargs):
    import pylab
    import numpy
    t = numpy.array(universe)
    for i, _set in enumerate(sets):
        s = numpy.array([_set(x) for x in universe])
        if (_set.label is not None and _set.label != ''):
            pylab.plot(t, s, label=_set.label)
        else:
            pylab.plot(t, s, label='Set NN')
    if ('title' in kwargs):
        pylab.title(kwargs['title'])
    pylab.ylim((-0.1, 1.1))
    pylab.xlim((-10, 70))
    pylab.legend()
    pylab.grid(True)
    pylab.show()


def polygon(*args):
    def f(v):
        if len(args) == 1:
            return args[0][1]
        x1, y1 = args[0]
        for x2, y2 in args[1:]:
            if (x1 <= v < x2):
                m = (y1 - y2) / (x1 - x2)
                return v * m + y1 - m * x1
            x1, y1 = x2, y2
        return 0
    return f


def frange(start, stop, step=1.0):
    res = []
    while start < stop:
        res.append(start)
        start += step
    return res

larsen = lambda x, y: x * y
mamdani = lambda x, y: norm(x, y)


class Variable(object):

    def __init__(self):
        self.sets = {}

    def __str__(self):
        return str(self.sets)

    def __repr__(self):
        return str(self)


class FuzzyAlgorithm(object):

    def __init__(self):
        self.implication = mamdani
        self._else = max
        self.program = self.set_program()
        self.universe, self.vars, self.rules = parser_fuzzy.parse(self.program)

    def set_program(self):
        return ''

    def compute(self, **inputs):
        results = [rule(inputs) for rule in self.rules]
        results = []
        for rule in self.rules:
            r = rule(inputs)
            if (r is not None):
                results.append(r)
        if len(results) == 0:
            return 0
        res = self.ELSE(results)
        return self.defuzzification(res)

    def ELSE(self, rules):
        res = rules[0]
        for s in rules[1:]:
            res = res.union(s)
        return res

    def defuzzification(self, _set):
        sum_u = 0
        sum_v = 0
        for k in self.universe:
            v = _set(k)
            if v > 0:
                sum_u += v
                sum_v += v * k
        if sum_u > 0:
            return float(sum_v) / sum_u
        return 0

    def show_vars(self, variables=None):
        import pylab
        import numpy
        if (variables is None):
            variables = self.vars.keys()
        for i, var_name in enumerate(variables):
            pylab.subplot(len(variables), 1, i)
            pylab.title(var_name)
            pylab.grid(True)
            x_axis = numpy.array(self.universe)
            pylab.ylim((-0.1, 1.1))
            for _name, _set in self.vars[var_name].sets.iteritems():
                y_axis = numpy.array([_set(x) for x in x_axis])
                pylab.plot(x_axis, y_axis, label=var_name + '.' + _name)
            pylab.legend()
        pylab.show()

if __name__ == '__main__':

    class Temperaturas(FuzzyAlgorithm):

        def set_program(self):
            return '''
universe = -4, 40, 0.5
implication_algotithm = MAMDANI

temperatura.muy_frio = (-4, 1)(0, 1)(6, 0)
temperatura.frio = (0, 0)(5, 1)(10, 1)(15, 0)
temperatura.agradable = (10, 0)(15, 1)(20, 1)(25, 0)
temperatura.caluroso = (20, 0)(25, 1)(30, 1)(35, 0)
temperatura.muy_caluroso = (30, 0)(35, 1)(40, 1)

if temperatura is muy_frio then temperatura is muy_frio
           '''

    t = Temperaturas()
    t.show_vars()
