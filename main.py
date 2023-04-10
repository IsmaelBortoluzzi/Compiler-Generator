from afd import formalize_data, Automata

words, grammar = formalize_data('tokens_grammar2.txt')

aut = Automata(words=words, grammar=grammar)
aut.compile()
