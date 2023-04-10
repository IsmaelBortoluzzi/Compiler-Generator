from itertools import chain
from afd import Automata, formalize_data


def generate_table():
    words, grammar = formalize_data('/home/ballke/Documents/compiladores/Lexer/tokens_grammar2.txt')
    aut = Automata(words=words, grammar=grammar)
    aut.compile()
    table = dict()
    tokens = [aut.sigma] + aut.all_tokens

    for state in aut.states:
        symbol = state[0][1:] if '*' in state[0] else state[0]
        table[symbol] = dict()

        for index, transition in enumerate(state):
            table[symbol][tokens[index]] = transition

        if '*' in state[0]:
            table[symbol]['final'] = True
        else:
            table[symbol]['final'] = False

    return table


def get_source_code(file_name):
    with open(file_name, 'r') as file:
        return [line for line in file]


tabela = generate_table()
fita_saida, simbolos, tabela_simbolos = list(), list(), list()


def lexical_analyzer(code):
    separadores = [' ', '\n', '\t', '+', '-', '{', '}', '=', ';']
    espacadores = [' ', '\n', '\t']
    operadores = ['+', '-', '=', ';']
    cdg = get_source_code('tokens_grammar2.txt')

    id, idx = 0, 0
    for idx, linha in enumerate(cdg):  # pega numero da linha e código de cada linha
        E = 'S'
        string = ''
        for char in linha:
            if char in operadores and string:  # caso lemos um operador e a string não está vazia
                if string[-1] not in operadores:  # se o ultimo caracter não é um operador
                    if tabela[E]['final'] is True:  # a regra do caracter lido é um dos regras_finais
                        tabela_simbolos.append({'Line': idx, 'State': E, 'Label': string})
                        fita_saida.append(E)  # adicionamos a regra na fita de saida
                    else:
                        tabela_simbolos.append({'Line': idx, 'State': 'Error', 'Label': string})
                        fita_saida.append('Error')
                    E = tabela['S'][char]  # mapeamento para a próxima estrutura de operadores
                    string = char
                    id += 1
                else:  # se o último caractere é um operador
                    string += char  # adiciona na string o caracter e continua normalmente
                    if char not in simbolos:
                        E = '€'
                    else:
                        E = tabela[E][char]
            elif char in separadores and string:
                if tabela[E]['final'] is True:
                    tabela_simbolos.append({'Line': idx, 'State': E, 'Label': string})  # adiciona em tabela_simbolos linha, estado e descricao
                    fita_saida.append(E)  # caso seja um final, adiciona na fita de saida
                else:
                    tabela_simbolos.append({'Line': idx, 'State': '<ERROR>', 'Label': string})
                    fita_saida.append('<ERROR>')
                E = 'S'
                string = ''
                id += 1
            else:
                if char in espacadores:  # se for um espaçador, continua
                    continue
                if char not in separadores and char not in operadores and string:  # caso n seja um separador, operador e já exista algo na string
                    if string[-1] in operadores:  # caso não seja um separador ele somente incrementa na string
                        if tabela[E]['final'] is True:  # operado é um final
                            tabela_simbolos.append({'Line': idx, 'State': E, 'Label': string})
                            fita_saida.append(E)
                        else:
                            tabela_simbolos.append({'Line': idx, 'State': '<ERROR>', 'Label': string})
                            fita_saida.append('<ERROR>')
                        E = 'S'
                        string = ''
                        id += 1
                string += char
                if char not in simbolos:  # caso o caracter não esteja na tabela de simbolos
                    E = '€'
                else:
                    E = tabela[E][char]  # o E recebe a regra do caracter

    tabela_simbolos.append({'Line': idx, 'State': 'EOF', 'Label': ''})
    fita_saida.append('EOF')
    erro = False
    for linha in tabela_simbolos:
        if linha['State'] == 'Error':  # caso exita erro léxico, imprime
            erro = True
            print('Erro léxico: linha {}, sentença "{}" não reconhecida!'.format(linha['Line'] + 1, linha['Label']))
    if erro:
        exit()  # finaliza caso exista erro


def start_analysis():
    source_code = get_source_code('/home/ballke/Documents/compiladores/Lexer/tokens_grammar2.txt')
    # lexical_analyzer(source_code)


if __name__ == '__main__':
    tabela = generate_table()
    start_analysis()