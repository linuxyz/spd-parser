#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Excel Expression parser with SLY."""

import re
import sys

from sly import Lexer, Parser

from .Formula import XFormula

# set encoding='utf-8' for consoole
sys.stdout.reconfigure(encoding='utf-8')


class FormulaLexer(Lexer):
    """Lexer with SLY."""
    tokens = {SHEET, STRING, CELL, NUMBER, AS, OP_CMP, OP_MULDIV, IF, NAME}
    ignore = ' \t'
    ignore_comment = r'\#.*$'
    literals = {':', '!', '&', '%', ',', '^',
                '+', '-', '*', '/',
                '(', ')', '[', ']', '{', '}'}

    # ignore case is nice
    reflags = re.IGNORECASE

    # Tokens

    SHEET = r"'[^']+'"

    def SHEET(self, t):
        """Extract the Sheet name by strip the single quote."""
        t.value = t.value[1:-1]
        return t

    STRING = r'"([^"]|"")*"'

    def STRING(self, t):
        """Extract the string value by remove the double quote."""
        t.value = t.value[1:-1].replace('""', '"')
        return t

    CELL = r'\$?(XF[A-D]|X[A-E][A-Z]|[A-W][A-Z]{2}|[A-Z]{1,2})\$?\d+'

    NUMBER = r'\d+(\.\d*)?(E-?\d+)?'

    AS = r'@='

    OP_CMP = r'<>|<=|>=|>|<|='
    OP_MULDIV = r'\*|/'

    IF = r'IF\>'

    NAME = r'[\w_]+'

    def error(self, t):
        print(
            f'Illegal character {t.value[0]!r} at index {self.index}', t.value, self.index)
        self.index += 1


class FormulaParser(Parser):
    """Parser with SLY."""

    tokens = FormulaLexer.tokens

    # Lower priority go first
    precedence = (
        ('nonassoc', OP_CMP),
        ('left', '&'),
        ('left', '+', '-'),
        ('left', OP_MULDIV),
        ('left', '^'),
        ('left', '%'),
        ('right', 'SIGN'),
    )

    def __init__(self):
        # `refer` and `href` is for alias
        self.refer = None
        self.target = None
        # this is for normal case
        # line number in the text file
        self.lineno: int = 0
        self.txt: str = None
        # str: target sheet name
        self.sheet: str = ''
        self.syntax = []
        self.params = []
        self.values = []

    # Assignment is the entry point

    @_('reference AS expr')
    def assignment(self, p):
        print(f"=={self.lineno:06d}==",  p.reference, ":=", p.expr)

    @_('NAME AS reference')
    def assignment(self, p):
        self.refer = p.NAME
        self.target = p.reference
        print(f"=={self.lineno:06d}==", self.refer, "@=", self.target)

    # Reference

    @_('SHEET "!" CELL [ ":" CELL ]')
    def reference(self, p):
        # return ('R', p.SHEET, p.CELL0, p.CELL1)
        if len(self.sheet) == 0:
            self.sheet = p.SHEET
            if p.CELL1:
                self.target = (p.CELL0, p.CELL1)
            else:
                self.target = p.CELL0
            return (p.SHEET, p.CELL0, p.CELL1)
        else:
            self.params.append((p.SHEET, p.CELL0, p.CELL1))
            return f"${len(self.params)-1}"

    @_('NAME "!" CELL [ ":" CELL ]')
    def reference(self, p):
        # return ('R', p.NAME, p.CELL0, p.CELL1)
        self.params.append((p.NAME, p.CELL0, p.CELL1))
        return f"${len(self.params)-1}"

    @_('CELL [ ":" CELL ]')
    def reference(self, p):
        # return ('R', None, p.CELL0, p.CELL1)
        if p.CELL1:
            self.params.append((None, p.CELL0, p.CELL1))
        else:
            self.params.append(p.CELL0)
        return f"${len(self.params)-1}"

    # IF Function

    # @_(',')
    # def _iftest(self, p):
    #    # this is the right place for if
    #    idx = len(self.syntax)
    #    self.syntax.append(None)    # BR
    #    self.syntax.append(None)    # Label%true
    #    return idx

    # @_('')
    # def _ifelse(self, p):
    #    idx = len(self.syntax)
    #    self.syntax.append(None)    # BR end
    #    self.syntax.append(None)    # Label%false
    #    return idx

    # @_('')
    # def _ifend(self, p):
    #    idx = len(self.syntax)
    #    self.syntax.append(None)    # Label%end
    #    self.syntax.append(None)    # phi
    #    return idx

    @_('IF "(" expr "," expr "," expr ")"')
    def factor(eelf, p):
        # if p.expr1[0] != '@' and p.expr2[0] != '@':   # two values
        #    self.syntax[p._iftest] = (idx, 'IF', p.expr0, p.expr1, p.expr2)
        #    return f"@{idx}"
        # IF and ELSE
        #self.syntax[p._iftest]   = ('BR', idx, p.expr0)
        #self.syntax[p._iftest+1] = ('LB', idx, 'true')
        #self.syntax[p._ifelse]   = ('JP', idx)
        #self.syntax[p._ifelse+1] = ('LB', idx, 'false')
        #self.syntax[p._ifend]    = ('LB', idx, 'end')
        #self.syntax[p._ifend+1]  = ('PHI', idx, p.expr1, p.expr2)
        return f"@{idx} {p.expr0}?{p.expr1}:{p.expr2}"

    @_('IF "(" expr "," expr ")"')
    def factor(self, p):
        ''' A group of pseudo instruments are define to help the branch
        BR - llvm IR `br` of *idx* by testing p.expr0
        LB - Label of *idx* for `true|false|end`
        JP - Jump to the end label of *idx* 
        PHI - llvm IR `phi` of *idx*
        '''
        #print("IF/ELSE: ", p.expr0, p.expr1, p.expr2)
        # return ('?', p.expr0, p.expr1, p.expr2)
        # only has TRUE expression
        # if p.expr1[0] != '@':   # value
        #    idx = p._iftest
        #    del self.syntax[p._ifend]
        #    del self.syntax[p._ifend]
        #    del self.syntax[p._iftest]
        #    self.syntax[p._iftest] = (idx, 'IF', p.expr0, p.expr1, False)
        #    return f"@{idx}"
        # expression of True
        #idx = p._ifend
        #self.syntax[p._iftest]   = ('BR', idx, p.expr0)
        #self.syntax[p._iftest+1] = ('LB', idx, 'true')
        #self.syntax[p._ifend]    = ('JP', idx)
        #self.syntax[p._ifend+1]  = ('LB', idx, 'false')
        #self.syntax.append( ('LB', idx, 'end') )
        #self.syntax.append( ('PHI', idx, p.expr1, False) )
        return f"@{idx} {p.expr0}?{p.expr1}:False"

    # Factors

    @_('reference')
    def factor(self, p):
        return p.reference

    @_('factor "%"')
    def factor(self, p):
        #print("PCT: ", p.factor)
        # return ('%', p.factor)
        idx = len(self.syntax)
        self.syntax.append((idx, '%', p.factor))
        return f"@{idx}"

    @_('"-" factor %prec SIGN')
    def factor(self, p):
        #print("MINUS: ", p.factor)
        # return ('-', p.factor)
        idx = len(self.syntax)
        self.syntax.append((idx, '-', p.factor))
        return f"@{idx}"

    @_('"+" factor %prec SIGN')
    def factor(self, p):
        #print("POS ", p.factor)
        return p.factor

    @_('"(" expr ")"')
    def factor(self, p):
        #print("PARAM: ", p.expr)
        return p.expr

    @_('STRING')
    def factor(self, p):
        #print("STR: ", p.STRING)
        # return p.STRING
        self.values.append(p.STRING)
        return f"#{len(self.values)-1}"

    @_('NUMBER')
    def factor(self, p):
        #print("NUM: ", p.NUMBER)
        # return p.NUMBER
        self.values.append(p.NUMBER)
        return f"#{len(self.values)-1}"

#    @_('NAME "(" ")"')
#    def factor(self, p):
#        print("FUNC: ", p.NAME)
#        return ('FUNC', p.NAME)

    @_('expr')
    def param(self, p):
        return p.expr

    @_('')
    def param(self, p):
        return None

    @_('param { "," param }')
    def args(self, p):
        return [p.param0] + p.param1

    @_('NAME "(" args ")"')
    def factor(self, p):
        #print("FUNC: ", p.NAME, p.args)
        # return ('FUNC', p.NAME, p.args)
        idx = len(self.syntax)
        self.syntax.append((idx, p.NAME, p.args))
        return f"@{idx}"

    @_('NAME')
    def factor(self, p):
        #print("NAME: ", p.NAME)
        # return ('VAR', p.NAME)
        self.params.append(('', p.NAME))
        return f"${len(self.params)-1}"

    @_('factor')
    def expr(self, p):
        #print("FACTOR: ", p.factor)
        return p.factor

    # Expressions
    # Math Expression

    @_('expr "^" expr')
    def expr(self, p):
        #print("OP_CARET: ", p.expr0, p.expr1)
        # return ('^', p.expr0, p.expr1)
        idx = len(self.syntax)
        self.syntax.append((idx, '^', p.expr0, p.expr1))
        return f"@{idx}"

    @_('expr OP_MULDIV expr')
    def expr(self, p):
        #print("OP_MULDIV: ", p[1], p.expr0, p.expr1)
        # return (p[1], p.expr0, p.expr1)
        idx = len(self.syntax)
        self.syntax.append((idx, p[1], p.expr0, p.expr1))
        return f"@{idx}"

    @_('expr "+" expr',
       'expr "-" expr')
    def expr(self, p):
        #print("OP_ADDSUB: ", p[1], p.expr0, p.expr1)
        # return (p[1], p.expr0, p.expr1)
        idx = len(self.syntax)
        self.syntax.append((idx, p[1], p.expr0, p.expr1))
        return f"@{idx}"

    # String concat

    @_('expr "&" expr')
    def expr(self, p):
        #print("OP_CONCAT: ", p.expr0, p.expr1)
        # return (p[1], p.expr0, p.expr1)
        idx = len(self.syntax)
        self.syntax.append((idx, p[1], p.expr0, p.expr1))
        return f"@{idx}"

    # Boolean Expression

    @_('expr OP_CMP expr')
    def expr(self, p):
        #print("OP_CMP: ", p[1], p.expr0, p.expr1)
        # return (p[1], p.expr0, p.expr1)
        idx = len(self.syntax)
        self.syntax.append((idx, p[1], p.expr0, p.expr1))
        return f"@{idx}"

    # Error Handling

    def error(self, token):
        '''
        Default error handling function.  This may be subclassed.
        '''
        sys.stderr.write(
            f'sly: Syntax error at line {self.lineno:06d}, token={token.type}\n')
        # Read ahead looking for a terminating ";"
        # return token

    def as_formula(self) -> XFormula:
        '''
        return current state as the XFormula
        '''
        fma = XFormula(self.sheet, self.syntax, self.params,
                         self.values, self.lineno, self.txt)
        fma.targets.append(self.target)
        self.__init__()
        return fma


if __name__ == '__main__':
    lexer = FormulaLexer()
    parser = FormulaParser()

    parser.lineno = 1

    while len(sys.argv) == 1:
        try:
            text = input('formula > ')
        except EOFError:
            break
        if text:
            parser.parse(lexer.tokenize(text))
            print(parser.as_formula())
            parser.__init__()

    try:
        ln = 0
        with open(sys.argv[1], 'r', encoding='utf-8') as f:
            for line in f:
                ln += 1
                line = line.strip()
                if len(line) == 0 or line.startswith('//'):
                    continue
                print(f"[{ln:06d}] {line}")
                parser.lineno = ln
                parser.txt = line
                # Parse
                parser.parse(lexer.tokenize(line))
                fma = parser.as_formula()
                print(fma)
    except OSError:
        # 'File not found' error message.
        print("File not found!")
        pass

# vim: noai:ts=4:sw=4:expandtab
