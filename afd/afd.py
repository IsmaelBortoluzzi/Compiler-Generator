import re
import string
from itertools import chain
from unicodedata import normalize

from tabulate import tabulate


def print_table(table, headers, title=None):
    if title:
        print(tabulate([title.upper()], tablefmt="fancy_grid"))
    print(tabulate(table, headers, tablefmt="fancy_grid"))


def formalize_data(file_name):
    words = list()
    grammar = list()
    with open(file_name, 'r') as file:
        for line in file:
            if line.strip() != '':
                if '::=' in line:
                   grammar.append(line.strip())
                else:
                   words.append(line.strip())

    return words, grammar


def prepare_alphabet_machine(all_tokens):
    formalize_data = [list(word) for word in all_tokens]
    return list(dict.fromkeys(list(chain.from_iterable(formalize_data))))


def get_all_tokens(words, grammar):
    all_tokens = list()
    pattern = "<(?:\"[^\"]*\"['\"]*|'[^']*'['\"]*|[^'\">])+>"

    for linha in words + grammar:
        valores = normalize('NFKD', linha.strip()).encode('ASCII', 'ignore').decode('ASCII').lower()
        if valores.startswith('<s>'):
            tokens = valores.replace('::=', '').split('|')
            for token in tokens:
                all_tokens.append(re.sub(pattern, '', token).strip())
            continue
        elif valores.startswith('<'):
            continue
        all_tokens.append(valores)
    return prepare_alphabet_machine(all_tokens)


class Automata:
    def __init__(self, words, grammar):
        self.initial_symbol = 'S'
        self.sigma = '\u03B4'
        self.epsilon = '\u03B5'
        self.alphabet = [
            'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M',
            'N', 'O', 'P', 'Q', 'R', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z', 'Ω',
            'Δ', 'Θ', 'Λ', 'Ξ', 'Σ', 'Φ', 'Ψ', 'Γ',
        ]
        self.words = words
        self.grammar = grammar
        self.all_tokens = get_all_tokens(self.words, self.grammar)
        self.states = [[self.initial_symbol] + [''] * len(self.all_tokens)]
        self.last_state = 0
        self.checked = set()

    def get_state(self, position=0, **kwargs):
        return kwargs.get('state_final', '') + self.alphabet[self.last_state - position]

    def create_state(self, new=True, state='', **kwargs):
        if new:
            if state:
                self.states += [
                    [kwargs.get('state_final', '') + state] + [''] * len(self.all_tokens)
                ]
            else:
                self.states += [
                    [self.get_state(state_final=kwargs.get('state_final', ''))] + [''] * len(self.all_tokens)
                ]
                self.last_state += 1

    def build_afnd(self):
        for num_word, word in enumerate(self.words):
            len_word = len(word) - 1
            for num_token, token in enumerate(word):
                if num_token == 0:
                    if num_word == 0:
                        self.states[0][self.all_tokens.index(token) + 1] += self.alphabet[self.last_state]
                        self.create_state()
                    else:
                        self.states[0][self.all_tokens.index(token) + 1] += self.alphabet[self.last_state - 1]
                else:
                    if num_token == len_word:
                        self.states[self.last_state][self.all_tokens.index(token) + 1] = self.alphabet[self.last_state]
                        self.create_state(state_final='*')
                        try:
                            self.words[num_word + 1]
                        except IndexError:
                            continue
                        self.create_state()
                    else:
                        self.states[self.last_state][self.all_tokens.index(token) + 1] = self.alphabet[self.last_state]
                        self.create_state()

        self.change_states_signature()  # troca o nome das regras da gramatica para n ter conflito

        for sentence in self.grammar:
            state = sentence.split('::=')[0].strip()[1]  # pega o nome da regra
            for x in range(len(self.states)):            # cata a posição de cada regra da gramatica na matriz
                if self.states[x][0] in (state, f'*{state}'):
                    # pega todas as transições da regra
                    tokens_with_next_state = sentence.split('::=')[1].replace(' ', '').replace('>', '').split('|')
                    self.remove_epsilon(tokens_with_next_state)
                    for token_state in tokens_with_next_state:
                        token, state = token_state.split('<')
                        # pega a posicao do token na matriz e adiciona a transição na posicao correta na regra
                        self.states[x][self.all_tokens.index(token) + 1] += state
                    break

    def change_states_signature(self):
        for x in range(1, len(self.grammar)):
            state = self.grammar[x].split('::=')[0].strip()[1]
            self.create_state()
            if self.epsilon in self.grammar[x]:
                self.states[self.last_state][0] = '*' + self.states[self.last_state][0]

            self.replace_signature(state, self.alphabet[self.last_state - 1])

    def replace_signature(self, state, new_state):
        for x in range(len(self.grammar)):
            self.grammar[x] = self.grammar[x].replace(state, new_state)

    def remove_epsilon(self, tokens_with_next_state):
        if self.epsilon in tokens_with_next_state:
            tokens_with_next_state.remove(self.epsilon)

    def build_afd(self):
        for state in self.states:
            for signature in state:
                if not any(signature in state[0] for state in self.states) and signature:
                    state_final = False
                    for token_new_state in signature:
                        if any('*' + token_new_state in state[0] for state in self.states) and \
                                not any('*' + signature in state[0] for state in self.states):
                            state_final = True
                    if state_final:
                        self.create_state(state=signature, state_final='*')
                    else:
                        self.create_state(state=signature)

                    for new_token in signature:
                        indexes_tokens = self.get_state_index_by_signature(new_token)
                        for key, valor in enumerate(self.states[indexes_tokens]):
                            if key == 0 or not valor:
                                continue
                            self.states[-1][key] += valor

        for state in self.states:
            for signature in state:
                if not any(signature in state[0] for state in self.states) and signature:
                    self.build_afd()

    def get_state_index_by_signature(self, signature):
        for i, x in enumerate(self.states):
            if x[0] in (signature, f'*{signature}'):
                return i

    def minimize(self):
        self.remove_unreachable()
        self.remove_dead()

    def remove_unreachable(self):
        self.checked.update(self.states[0])  # pega as transicoes da regra inicial
        len_checked = len(self.checked)
        newly_added_states = set()

        new_len_checked = self.annotate_states(newly_added_states)  # anota as transicoes das transicoes da regra inicia

        # checa se mais regras foram atingidas nas segundas transicoes e repete o processo
        # nas regras atingidas ate n ter mais transicoes para regras novas
        while len_checked != new_len_checked:
            len_checked = new_len_checked
            new_len_checked = self.annotate_states(newly_added_states)

        # varremos self.states e se tiver alguma regra n atingida marcaremos como UNREACHABLE para filtrar depois
        for state in self.states:
            if '*' in state[0]:
                state_signature = state[0][1:]
            else:
                state_signature = state[0]
            if state_signature not in self.checked:
                state[0] = 'UNREACHABLE'

        self.states = list(filter(lambda x: x[0] != 'UNREACHABLE', self.states))

    def annotate_states(self, newly_added_states):
        for state_signature in self.checked:
            if state_signature == '':
                continue
            state = self.get_state_by_signature(state_signature)  # pega a lista de transicoes da regra
            for signature in state:  # adiciona cada transicao da regra para unir com as existentes em self.checked
                if '*' in signature:
                    newly_added_states.add(signature[1:])
                else:
                    newly_added_states.add(signature)
        self.checked = self.checked.union(newly_added_states)
        return len(self.checked)  # para ver se foi adicionada regra nova

    def get_state_by_signature(self, signature):
        for x in self.states:
            if x[0] in (signature, f'*{signature}'):
                return x

    def remove_dead(self):
        # é mais ou menos a mesma coisa de remove_unreachable(), mas para todas as regras inves de
        # somente para a inicial, e com o detalhe de q basta acharmos uma regra final para parar
        # a busca e partir para o proximo estado
        for index, state in enumerate(self.states):
            self.checked = set(self.states[index])
            len_checked = len(self.checked)
            newly_added_states = set()
            is_dead = True

            new_len_checked, is_dead = self.check_if_is_dead(newly_added_states, is_dead)
            while len_checked != new_len_checked:
                if is_dead is False:
                    break
                len_checked = new_len_checked
                new_len_checked, is_dead = self.check_if_is_dead(newly_added_states, is_dead)

            if is_dead is True:
                self.states[index][0] = 'DEAD'

        self.states = list(filter(lambda x: x[0] != 'DEAD', self.states))

        # depois de remover estados mortos da matriz, removemos transicoes para eles tbm
        self.remove_transitions_to_dead()

    def check_if_is_dead(self, newly_added_states, is_dead):
        for state in self.checked:
            if state == '':
                continue
            s = self.get_state_by_signature(state)
            for signature in s:
                if '*' in signature:
                    newly_added_states.add(signature[1:])
                    is_dead = False
                    break
                else:
                    newly_added_states.add(signature)
            if is_dead is False:
                break

        self.checked = self.checked.union(newly_added_states)
        return len(self.checked), is_dead

    def remove_transitions_to_dead(self):
        all_states = [x[0] if '*' not in x[0] else x[0][1:] for x in self.states]
        for index_one, states in enumerate(self.states):
            for index_two, state in enumerate(states):
                if state not in all_states and index_two != 0:
                    self.states[index_one][index_two] = ''

    def create_error_state(self):
        self.create_state(state='<ERROR>', state_final='*')
        for key_state, state in enumerate(self.states):
            for key_token, token in enumerate(state):
                if not token:
                    self.states[key_state][key_token] = '<ERROR>'

    def compile(self):
        self.build_afnd()
        print_table(self.states, [self.sigma] + self.all_tokens, 'autômato não determinizado')
        self.build_afd()
        print_table(self.states, [self.sigma] + self.all_tokens, 'autômato determinizado')
        self.minimize()
        print_table(self.states, [self.sigma] + self.all_tokens, 'autômato minimizado')
        self.create_error_state()
        print_table(self.states, [self.sigma] + self.all_tokens, 'autômato com estado de erro')

