from constants import BASE, CONTEXT_FREE_GRAMMAR

import xml.etree.ElementTree as ET

tree = ET.parse(f'{BASE}/{CONTEXT_FREE_GRAMMAR}')

Symbols = {} # Índice do símbolo: ['nome do token', tipo]. Ex= {6: [';', 1]}
Productions = {} # Índice da produção: [símbolo que dá nome à regra, contagem de símbolos]. Ex= {8: [54, 5]}
LALR_States = {} # Índice do estado: {Símbolo: [Ação, Valor]}. Ex= {0: {26: [1, 16]}}

for node in tree.findall('.//m_Symbol/Symbol'):
    Symbols[int(node.attrib['Index'])] = [node.attrib['Name'], int(node.attrib['Type'])]

for node in tree.findall('.//m_Production/Production'):
    Productions[int(node.attrib['Index'])] = [int(node.attrib['NonTerminalIndex']), int(node.attrib['SymbolCount'])]

for node in tree.findall('.//LALRTable/LALRState'):
    LALR_States[int(node.attrib['Index'])] = {}
    for child in node:
        LALR_States[int(node.attrib['Index'])][int(child.attrib['SymbolIndex'])] = [int(child.attrib['Action']), int(child.attrib['Value'])]

stack = [0] # estado inicial da pilha

# flexibiliza modificações na linguagem, podendo alterar o index final
lexer_dictionary = dict.fromkeys(['Σ','AΣ','BΣ','DΣ','FΣ','GΣ','HΣ','IΣ','KΣ','LΣ','MΣ','NΣ',
                        'OΣ','QΣ','RΣ','TΣ','UΣ','VΣ','WΣ','YΣ','ZΣ','ΩΣ','ΔΣ','ΘΣ'], 'Id')

lexer_dictionary.update({'Φ':'Inteiro','CΣ':'def', 'EΣ':'if', 'JΣ':'while', 'PΣ':'equals', 
                    'XΣ':'greater','ΛΣ':'lesser', '=':'=', '+':'+', '-':'-', '*':'*', '/':'/',
                    '{':'{','}':'}', ';':';', 'EOF':'EOF', '<ERROR>':'Error'})

def translate_token(token):
    for index in Symbols:
        if Symbols[index][0] == lexer_dictionary[token]:
            return index

def get_next_token(fita_saida):
    while True:
        token = fita_saida.pop(0)
        if token in [' ', '\n', '\t']:
            continue
        return translate_token(token)

def get_error_line(lexer):
   count = 1 # token consumido = |fita| - 1
   for token in lexer.fita_saida:
       if token not in [' ', '\n', '\t', '+', '-', '/', '*', '{', '}', '=', ';']:
           count += 1
   error = lexer.tabela_simbolos[-count]
   print(f"Erro sintático na linha {error['Line']}, símbolo '{error['Label']}'.")

def syntax_analyser(lexer):
    token, last_token = -1, 0
    while token != 0:
        get_next = False
        token = get_next_token(lexer.fita_saida) # consome FITA DE SAIDA
        while not get_next:
            try:
                transition = LALR_States[stack[-1]][token]
                match transition[0]:
                    case 1: # shift
                        stack.extend([token, transition[1]])
                        get_next = True
                        print(stack) # p/ comparar
                    case 2: # reduce
                        production = Productions[transition[1]]
                        for times in range(production[1] * 2):
                            stack.pop()
                        last_token = token
                        token = production[0]
                    case 3: # goto
                        stack.extend([token, transition[1]])
                        token = last_token
                        print(stack) # p/ comparar
                    case 4: # aceite
                        print("ACEITE")
                        return
            except:
                get_error_line(lexer)
                return