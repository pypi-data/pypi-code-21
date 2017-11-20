''' Este é o módulo "nester.py", e fornece uma função chamada print_lol()
que imprime listas que podem ou não incluir listas aninhadas.'''

def print_lol(the_list, level):
    '''Esta função requer um argumento posicional chamado "the_list", que é qualquer
    lista Python (de possíveis listas aninhadas). Cada item de dados na lista
    fornecida é (recursivamente) impresso na tela em sua prórpia linha.
    Um segundo argumento chamado "level" é usado para inserir tabulações quando
    uma lista é encontrada'''
    for each_item in the_list:
        if isinstance(each_item, list):
            print_lol(each_item,level+1)
        else:
            for tab_stop in range(level):
                print('\t', end='')
            print(each_item)

teste = ['Eraldo', 'Elisia', ['Adriana', 'Fernando', 'Andre', ['Pedrinho', 'Mateus']]]

print_lol(teste, 0)