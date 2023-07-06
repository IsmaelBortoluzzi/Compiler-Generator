from pprint import pprint

import lexer
import syntax_analyser

from constants import BASE, SOURCE_CODE_FILE


def main():
    lexer.lexical_analyzer(f'{BASE}/{SOURCE_CODE_FILE}')
    print_all()
    syntax_analyser.syntax_analyser(lexer)
    syntax_analyser.semantic_analyser(lexer)


def print_all():
    pprint(lexer.fita_saida)
    pprint(lexer.tabela_simbolos)


if __name__ == '__main__':
    main()