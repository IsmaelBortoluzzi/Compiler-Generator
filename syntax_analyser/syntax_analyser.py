from constants import BASE, CONTEXT_FREE_GRAMMAR

import xml.etree.ElementTree as ET

tree = ET.parse(f'{BASE}/{CONTEXT_FREE_GRAMMAR}')

Symbols = {} # Índice do símbolo: ['nome do token', tipo]. Ex= {6: [';', 1]}
Productions = {} # Índice da produção: [símbolo que dá nome à regra, contagem de símbolos]. Ex= {8: [54, 5]}
LALR_States = {} # Índice do estado: {Símbolo: [Ação, Valor]}. Ex= {0: {26: [1, 16]}}
stack = [0] # Pilha, iniciada com estado 0
prod_attr = [] # Lista de atributos das produções
temp = 0 # Variáveis temporárias p/ uso no código intermediário

for node in tree.findall('.//m_Symbol/Symbol'):
    Symbols[int(node.attrib['Index'])] = [node.attrib['Name'], int(node.attrib['Type'])]

for node in tree.findall('.//m_Production/Production'):
    Productions[int(node.attrib['Index'])] = [int(node.attrib['NonTerminalIndex']), int(node.attrib['SymbolCount'])]

for node in tree.findall('.//LALRTable/LALRState'):
    LALR_States[int(node.attrib['Index'])] = {}
    for child in node:
        LALR_States[int(node.attrib['Index'])][int(child.attrib['SymbolIndex'])] = [int(child.attrib['Action']), int(child.attrib['Value'])]

# flexibiliza modificações na linguagem, podendo alterar o index final
lexer_dictionary = dict.fromkeys(['Σ','AΣ','BΣ','DΣ','FΣ','GΣ','HΣ','IΣ','KΣ','LΣ','MΣ','NΣ',
                        'OΣ','QΣ','RΣ','TΣ','UΣ','VΣ','WΣ','YΣ','ZΣ','ΩΣ','ΔΣ','ΘΣ'], 'Id')

lexer_dictionary.update({'Φ':'Int', 'Ψ':'Float', 'CΣ':'def', 'EΣ':'if', 'JΣ':'while', 'PΣ':'Comp',
                    'XΣ':'Comp','ΛΣ':'Comp', '+':'+', '-':'-', '*':'*', '/':'/',
                    '=':'=', '{':'{','}':'}', ';':';', 'EOF':'EOF', '<ERROR>':'Error'})

def translate_token(token):
    for index in Symbols:
        if Symbols[index][0] == lexer_dictionary[token]:
            return index

def get_next_token(fita_saida, token_count):
    while True:
        token = fita_saida.pop(0)
        token_count += 1
        if token in [' ', '\n', '\t']:
            continue
        return translate_token(token), token_count

def print_error(ts, token_count):
    error = ts[token_count]
    print(f"Erro sintático: linha {error['Line']+1}, símbolo '{error['Label']}'.")
    print("Código da linha: ", end="")
    for symbol in ts:
        if symbol['Line'] == error['Line']:
            print(symbol['Label'], end=' ')
    print()

def print_stack():
    for i in range(len(stack)):
        if i % 2 == 0:
            print(stack[i], end=' ')
        else:
            print(Symbols[stack[i]][0], end=' ')
        i += 1
    print()

def gera_temp():
    global temp
    temp += 1
    return temp

def syntax_directed_translation(ts, token_count, production):
    if production == 7: ## C + D -> C
        token_D = prod_attr.pop()
        token_C = prod_attr.pop()
        name = f'T{gera_temp()}'
        cod = name + ' = ' + token_C['Name'] + ' + ' + token_D['Name'] + ';'
        prod_attr.append({'Token':Symbols[Productions[production][0]][0], 'Name':name, 'Type':'Float', 'Code':token_C['Code'] + '' + token_D['Code'] + cod})
    if production == 8: ## C - D -> C
        token_D = prod_attr.pop()
        token_C = prod_attr.pop()
        name = f'T{gera_temp()}'
        cod = name + ' = ' + token_C['Name'] + ' - ' + token_D['Name'] + ';'
        prod_attr.append({'Token':Symbols[Productions[production][0]][0], 'Name':name, 'Type':'Float', 'Code':token_C['Code'] + '' + token_D['Code'] + cod})
    if production == 9: ## D -> C
        token_D = prod_attr.pop()
        prod_attr.append({'Token':Symbols[Productions[production][0]][0], 'Name':token_D['Name'], 'Type':token_D['Type'], 'Code':token_D['Code']})
    if production == 10: ## D * E -> D
        token_E = prod_attr.pop()
        token_D = prod_attr.pop()
        name = f'T{gera_temp()}'
        cod = name + ' = ' + token_D['Name'] + ' * ' + token_E['Name'] + ';'
        prod_attr.append({'Token':Symbols[Productions[production][0]][0], 'Name':name, 'Type':'Float', 'Code':token_D['Code'] + '' + token_E['Code'] + cod})
    if production == 11: ## D / E -> D
        token_E = prod_attr.pop()
        token_D = prod_attr.pop()
        name = f'T{gera_temp()}'
        cod = name + ' = ' + token_D['Name'] + ' / ' + token_E['Name'] + ';'
        prod_attr.append({'Token':Symbols[Productions[production][0]][0], 'Name':name, 'Type':'Float', 'Code':token_D['Code'] + '' + token_E['Code'] + cod})
    if production == 12: ## E -> D
        token_E = prod_attr.pop()
        prod_attr.append({'Token':Symbols[Productions[production][0]][0], 'Name':token_E['Name'], 'Type':token_E['Type'], 'Code':token_E['Code']})
    if production == 13: ## { C } -> E
        token_C = prod_attr.pop()
        prod_attr.append({'Token':Symbols[Productions[production][0]][0], 'Name':token_C['Name'], 'Type':token_C['Type'], 'Code':token_C['Code']})
    if production == 14: # F -> E
        token_E = prod_attr.pop()
        prod_attr.append({'Token':Symbols[Productions[production][0]][0], 'Name':token_E['Name'], 'Type':token_E['Type'], 'Code':''})
    if production == 15: ## int -> F
        prod_attr.append({'Token':Symbols[Productions[production][0]][0], 'Name':ts[token_count-1]['Label'], 'Type':'Int'})
    if production == 16: ## float -> F
        prod_attr.append({'Token':Symbols[Productions[production][0]][0], 'Name':ts[token_count-1]['Label'], 'Type':'Float'})
    if production == 17: ## Id -> F
        prod_attr.append({'Token':Symbols[Productions[production][0]][0], 'Name':ts[token_count-1]['Label'], 'Type':'Id'})        
    if production == 18: ## def Id H -> G
        token_H = prod_attr.pop()
        name = ts[token_count-2]['Label'] if token_H['Type'] == "" else ts[token_count-4]['Label']
        prod_attr.append({'Token':Symbols[Productions[production][0]][0], 'Name':name, 'Type':token_H['Type'], 'Value':token_H['Name'], 'Code':''})
    if production == 19: ## I = C ; -> G
        token_C = prod_attr.pop()
        token_I = prod_attr.pop()
        cod = token_C['Code'] + '' + token_I['Name'] + ' = ' + token_C['Name'] + ';'
        prod_attr.append({'Token':Symbols[Productions[production][0]][0], 'Name':token_I['Name'], 'Type':token_C['Type'], 'Value':'', 'Code':cod})
    if production == 20: ## ; -> H
        prod_attr.append({'Token':Symbols[Productions[production][0]][0], 'Name':'', 'Type':''})
    if production == 21: ## = F ; -> H
        token_F = prod_attr.pop()
        prod_attr.append({'Token':Symbols[Productions[production][0]][0], 'Name':token_F['Name'], 'Type':token_F['Type']})
    if production == 22: ## Id -> I
        prod_attr.append({'Token':Symbols[Productions[production][0]][0], 'Name':ts[token_count-1]['Label'], 'Type':'Id'})
    return

def syntax_analyser(lexer):
    token, last_token, token_count = -1, 0, -1
    while token != 0:
        get_next = False
        token, token_count = get_next_token(lexer.fita_saida, token_count) # consome FITA DE SAIDA
        while not get_next:
            try:
                transition = LALR_States[stack[-1]][token]
                match transition[0]:
                    case 1: # shift
                        stack.extend([token, transition[1]])
                        get_next = True
                        print_stack() ## DEBUG
                    case 2: # reduce
                        syntax_directed_translation(lexer.tabela_simbolos, token_count, transition[1])
                        production = Productions[transition[1]]
                        for times in range(production[1] * 2):
                            stack.pop()
                        last_token = token
                        token = production[0]
                    case 3: # goto
                        stack.extend([token, transition[1]])
                        token = last_token
                        print_stack() ## DEBUG
                    case 4: # aceite
                        print("ACEITE")
                        return
            except:
                print_error(lexer.tabela_simbolos, token_count)
                exit()

def semantic_analyser(lexer):
    for x in prod_attr: ## DEBUG, imprime atributos das produções reduzidas
        print(x.values())
    definition = []
    for num, entry in enumerate(lexer.tabela_simbolos):
        if translate_token(entry['State']) == 12: ## se def, salva sua definição
            definition.append(lexer.tabela_simbolos[num + 1]['Label'])
        if translate_token(entry['State']) == 14: ## se Id, verifica se já foi definido
            if entry['Label'] in definition:
                continue
            else:
                print(f'Erro semântico na linha {entry["Line"]+1}, variável "{entry["Label"]}" ainda não foi definida.')
                exit()