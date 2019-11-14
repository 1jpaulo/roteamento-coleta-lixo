#coding: utf-8
import re

def modifica_valores_no_grafo(caminho, arquivo_grafo, NOME_ARQUIVO_OSM):

    dicionario = {}
    
    try:
        vertices_ordenados = open(caminho + 'vertices_ordenados.txt', 'r')
    except IOError as e:
        print (e)
    
    # Constroi um dicionário dinamicamente a partir de "Vertices_Ordenados.txt" 
    for linha in vertices_ordenados.readlines():
        s = linha.split()
        dicionario[s[0]] = int(s[1])
    
    vertices_ordenados.close()
   
    # cria arquivo graphml a partir de arquivo já gerado
    novo_grafo = open(caminho + 'grafomod(' + NOME_ARQUIVO_OSM + ').graphml', 'w', encoding='utf-8')

    achou_aresta = False
    for linha in arquivo_grafo.readlines():
        padrao = re.compile(r"(?<!(\.|\d))\d{9,10}(?!\d )|-\d{5}")
        # aqui começa os valores de edges, então há o valor de um node e de um target, por isso
        # deve-se encontrar dois valores no dicionario pra substituí-los, caso contrário ele
        # irá apenas substituir o primeiro padrão que encontrar e não os dois
        a = re.search(padrao, linha)
        # Novo código: encontra o index automaticamnte...
        if ('source' in linha and 'target' in linha and not achou_aresta):    # código mais simples...  
        #if (re.search('<edge', linha) and not achou_aresta):
            achou_aresta = True
            #print('index = %d' % (index))
        if not a:
            novo_grafo.write(linha)
        else:
            try:
                dicionario[a.group()]
            except KeyError as e:
                novo_grafo.write(linha)
                continue
            nova_linha = linha[:a.span()[0]] + str(dicionario[a.group()]) + linha[a.span()[1]:]
            #if index >= 1419:
            if achou_aresta:
                a = re.search(padrao, nova_linha)
                nova_linha = nova_linha[:a.span()[0]] + str(dicionario[a.group()]) + nova_linha[a.span()[1]:]
            novo_grafo.write(nova_linha)
    
    novo_grafo.close()

    # essa função foi usada pra imprimir o dicionario no cmd, de lá eu o copiei e o criei como dicionario em python
    # só será preciso usá-la se quisermos gerar um novo dicionário
    #print(json.dumps(dicionario, indent=2))