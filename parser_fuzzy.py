# -*- coding: utf-8 *-*
import fuzzy

reserved = {
    'else': 'ELSE',
    'if': 'IF',
    'then': 'THEN',
    'is': 'IS',
    'and': 'AND',
    'or': 'OR',
    'not': 'NOT',
    'universe': 'UNIVERSE',
    'implication_algotithm': 'ALGORITHM_TYPE'
}

tokens = (['ID', 'DOT', 'EQUALS', 'RPAREN', 'LPAREN', 'COMMA', 'NUMBER'] +
          list(reserved.values()))
t_DOT = r'\.'
t_EQUALS = r'='
t_RPAREN = r'\)'
t_LPAREN = r'\('
t_COMMA = r'\,'

t_ignore = " \t"


def t_COMMENT(t):
    r'\#.*'
    pass


def t_NUMBER(t):
    r'\-?\d+(\.\d+)?'
    t.value = float(t.value)
    return t


def t_ID(t):
    r'[a-zA-Z_][a-zA-Z0-9_]*'
    t.type = reserved.get(t.value.lower(), 'ID')
    t.value = t.value.lower()
    return t


def t_newline(t):
    r'\n+'
    t.lexer.lineno += t.value.count("\n")


def t_error(t):
    print("Illegal character '%s'" % t.value[0])
    t.lexer.skip(1)

# Build the lexer
from ply import lex
lex.lex()

precedence = (
    ('left', 'OR'),
    ('left', 'AND'),
    ('right', 'NOT'),
    )

implication_functions = {
    'mamdani': min,
    'larsen': lambda x, y: x * y
    }


def p_program(t):
    '''program : settings declarations statement_list'''
    pass


def p_settings(t):
    '''settings : settings setting
                | setting'''
    pass


def p_universe_declaration(t):
    '''setting : UNIVERSE EQUALS NUMBER COMMA NUMBER COMMA NUMBER'''
    my_parser.universe = fuzzy.frange(t[3], t[5], t[7])


def p_implication_type(t):
    '''setting : ALGORITHM_TYPE EQUALS ID'''
    my_parser.implication = implication_functions[t[3].lower()]


def p_declarations_list(t):
    '''declarations : declarations declaration
                    | declaration'''
    pass


def p_declaration(t):
    '''declaration : ID DOT ID EQUALS params'''
    if t[1] not in my_parser.vars:
        my_parser.vars[t[1]] = fuzzy.Variable()
    v = my_parser.vars[t[1]]
    params = t[5]
    v.sets[t[3]] = fuzzy.polygon(*params)
    my_parser.sets[t[1] + '.' + t[3]] = v.sets[t[3]]


def p_params(t):
    '''params : params LPAREN NUMBER COMMA NUMBER RPAREN
              | LPAREN NUMBER COMMA NUMBER RPAREN'''
    if len(t) == 6:
        t[0] = [(t[2], t[4])]
    else:
        t[0] = t[1] + [(t[3], t[5])]


def p_statement_list_l(t):
    '''statement_list : statement_list ELSE statement'''
    my_parser.rules.append(t[3])


def p_statement_list_s(t):
    '''statement_list : statement'''
    my_parser.rules.append(t[1])


def p_statement(t):
    '''statement : IF compose_preposition THEN preposition'''
    f = t[2]
    _set = my_parser.sets[t[4][0] + '.' + t[4][1]]
    fi = my_parser.implication

    def _if(val, cons):
        return fuzzy.FuzzySet(lambda v: fi(val, cons(v)))

    t[0] = lambda inputs: _if(f(inputs), _set)


def p_preposition_binary(t):
    '''compose_preposition : compose_preposition AND compose_preposition
                           | compose_preposition OR compose_preposition'''
    f = max if t[2] == 'AND' else min
    f1 = t[1]
    f2 = t[3]
    t[0] = lambda inputs: f(f1(inputs), f2(inputs))


def p_preposition_paren(t):
    '''compose_preposition : LPAREN compose_preposition RPAREN'''
    t[0] = t[2]


def p_preposition_not(t):
    '''compose_preposition : NOT compose_preposition'''
    f1 = t[2]
    t[0] = lambda inputs: 1 - f1(inputs)


def p_compose_preposition_preposition(t):
    '''compose_preposition : preposition'''
    var, _set = t[1]
    full = var + '.' + _set
    t[0] = lambda inputs: my_parser.sets[full](inputs[var])


def p_preposition_is(t):
    '''preposition : ID IS ID'''
    t[0] = (t[1], t[3])


def p_error(t):
    raise Exception('Error sintactico antes de %s. Linea %d' % (t.value,
                                                                  t.lineno))

from ply import yacc
my_parser = yacc.yacc()


def parse(program):
    my_parser.vars = {}
    my_parser.rules = []
    my_parser.sets = {}
    my_parser.implication = implication_functions['mamdani']
    my_parser.parse(program)
    return (my_parser.universe, my_parser.vars, my_parser.rules)

if __name__ == '__main__':
    ejemplo_corto = '''IF x IS A THEN y is B'''

    ejemplo_medio = '''IF x IS A THEN y is B ELSE
if w is A then z is B
'''

    ejemplo_largo = '''
IF distancia IS Lejos AND velocidad IS MuyRapido THEN frenado is Medio ELSE
IF distancia IS Cerca AND velocidad IS MuyRapido THEN frenado is Fuerte ELSE
IF NOT distancia IS Cerca OR velocidad IS Frenada THEN frenado is Suave
    '''
    ejemplo_completo = '''
universe = 0, 110, 0.5
implication_algotithm = MAMDANI

distancia.en_el_lugar = (0, 0)(30,1)(60, 0)
distancia.muy_cerca = (0, 10)(10, 20)
distancia.cerca = (15, 35)(35, 55)
distancia.lejos = (40, 60)(60, 80)
distancia.muy_lejos = (75, 90)(90, 105)

velocidad.frenada = (0, 0)(30,1)(60, 0)
velocidad.lento = (1, 6)(6, 11)
velocidad.rapido = (8, 15)(15, 22)
velocidad.muy_rapido = (0, 0)(30,1)(60, 0)

frenado.nada = (0, 0)(30,1)(60, 0)
frenado.suave = (0, 17)(17, 34)
frenado.medio = (30, 47)(47, 64)
frenado.fuerte = (0, 0)(30,1)(60, 0)

if distancia is cerca and velocidad is muy_rapido then frenado is fuerte else
if distancia is lejos and velocidad is muy_rapido then frenado is medio
'''
    u, var, rules = parse(ejemplo_completo)
    print u, var, rules
