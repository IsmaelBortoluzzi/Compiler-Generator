from pprint import pprint

from afd import formalize_data, Automata
import lexer

from constants import BASE, SOURCE_CODE_FILE


def main():
    lexer.lexical_analyzer(f'{BASE}/{SOURCE_CODE_FILE}')


def print_all():
    pprint(lexer.fita_saida)
    pprint(lexer.tabela_simbolos)


if __name__ == '__main__':
    main()
    print_all()
