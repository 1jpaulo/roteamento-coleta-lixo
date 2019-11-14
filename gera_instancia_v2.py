#coding: utf-8

import pdb                  #biblioteca para Debugger
import osmnx as ox
import os                   #biblioteca com funções do sistema
import networkx as nx       #biblioteca que possui o algoritmo de Dijkstra
#import re                   #Biblioteca de Regex
import recursos.modificador_grafo
import matplotlib.pyplot as plt

# CONSTANTES
NOME_ARQUIVO_OSM = 'Centro_Campos'
#NOME_ARQUIVO_OSM = 'PqSãoMatheus_PqGuarus'
CAMINHO_ARQUIVOS = 'dados/' + NOME_ARQUIVO_OSM + '/'
ARQ_INSTANCIA = 'Instância.txt'
NMHA = 3.2
QLIHA = 0.78
V_PROD = 7.5  #Em Km/h
V_IMPROD = 20 #Em Km/h

# TOTAL: NÓS, ARESTAS E ARCOS
_QDE_NOS = 0
_QDE_ARESTAS = 0
_QDE_ARCOS = 0

# TOTAL REQUERIDOS: NÓS, ARESTAS E ARCOS
_QDE_NOS_REQ = 0
_QDE_ARESTAS_REQ = 0
_QDE_ARCOS_REQ = 0

# GUARDA VALORES DE DISTÂNCIAS DE TODOS OS LINKS
distancias_links = {}

def salva_grafo_txt(grafo, nome):

    '''
    Esta função agora gera tanto o grafo com valores originais de nós, com 10 algarismos
    como também o grafo com valores indexados, em forma de lista, que vao de 1 até
    o número máximo de nós utilizados no recorte de mapa.
    '''
    
    global _QDE_NOS, _QDE_ARESTAS, _QDE_ARCOS, _QDE_NOS_REQ, _QDE_ARESTAS_REQ, _QDE_ARCOS_REQ

    grafo_txt = ''
    
    # cria diretórios e subdiretórios para armazenar grafos e instância posteriormente
    # com o nome do arquivo osm tratado no momento, nome final será a constante CAMINHO_ARQUIVOS

    try:
        if not os.path.exists(CAMINHO_ARQUIVOS):
            os.makedirs(CAMINHO_ARQUIVOS)
    except:
        print(e)

    # gera arquivos grafo e grafo_indexado
    try:

        grafo_txt = open(CAMINHO_ARQUIVOS + 'grafo(' + nome + ').txt', 'w')
        grafo_txt.write("%4s %12s %12s %12s %12s %12s %12s %8s %10s\n" % ("id","u","v","CA","demanda","CS","length","oneway","status"))

        grafo_indexado_txt = open(CAMINHO_ARQUIVOS + 'grafo_indexado(' + nome + ').txt', 'w')
        grafo_indexado_txt.write("%4s %12s %12s %12s %12s %12s %12s %8s %10s\n" % ("id","u","v","CA","demanda","CS","length","oneway","status"))

    except IOError as e:
        print (e)

    ''' 
    Acessa nós inicial e final de cada edge, calcula seus custos de servir e 
    atravessar, estima quantidade de domicílios por edge, e todas essas 
    informações são gravadas em um grafo txt e seu respectivo grafo indexado txt
    '''

    id = 0
    id_no = 1
    way_length = float #lista de floats
    one_way = bool
    n_domicilios = 0
    custo_servir = 0
    custo_atravessar = 0
    indice = 0
    
    # contém todos os nós mapeados
    dicio_nos = {}
    links_paralelos = [0, 0]
    for nos_passagem in grafo.edges():
        
        qde_residuos = 0
        # caso nó ainda não exista no dicionário, será acrescentado
        # juntamente com um índice que será utilizado no grafo_indexado
        for nos in nos_passagem:
            if nos not in dicio_nos:
                dicio_nos[nos] = id_no
                id_no += 1

        # calcula distancia entre os nós em pares retornando um float
        way_length = ox.utils.get_route_edge_attributes(grafo, nos_passagem[:2], "length")      
        #print(nos_passagem, way_length)
        
        # descobre se o arco é unidirecional ou bidirecional
        one_way = ox.utils.get_route_edge_attributes(grafo, nos_passagem[:2], "oneway")[0]
        
        # verifica paridade do valor one_way. Se 'true', arco, caso contrário aresta
        # aqui é adicionado o valor total de arcos ou arestas
        if one_way:
            _QDE_ARCOS += 1
        else:
            _QDE_ARESTAS += 1

        if nos_passagem == links_paralelos and len(way_length) > 1:
            indice += 1
        else:
            indice = 0
            
        # verifica se é link de passagem
        try:
            status = ox.utils.get_route_edge_attributes(grafo, nos_passagem[:2], "ref")[indice]
        except:
            status = 'servico'
        #print(status)
        
		# estima quantos domicílios há em um determinado trecho de rua, multiplicado
        # por 2, já que deve-se calcular os dois lados de uma rua 
        n_domicilios = 2*(way_length[indice] / 7.5)
        
        # a lista 'way_length' pode ter duas distâncias, caso tenha links paralelos...
        #for indice in range(len(way_length)):             
        if status != 'passagem':
            qde_residuos = n_domicilios * NMHA * QLIHA

            # Aqui sabemos que o link não é de passagem, então é requerido.
            # Resta saber se este link é um arco ou aresta.
            # Neste caso, diferente do if de cima, estamos especificando se
            # ele deve entrar como requerido ou não. Mais tarde saberemos os
            # não requeridos, subtraindo os links totais dos requeridos
            if one_way:
                _QDE_ARCOS_REQ += 1
            else:
                _QDE_ARESTAS_REQ += 1
 
        links_paralelos = nos_passagem
        #print(links_paralelos)
        
        # dado em minutos
        custo_servir = (way_length[indice] / 1000) / V_PROD * 60
        custo_atravessar = (way_length[indice] / 1000) / V_IMPROD * 60   
        grafo_txt.write("%4d %12d %12d %12f %12f %12f %12f %8s %10s\n" % (id, nos_passagem[0], nos_passagem[1], custo_atravessar, qde_residuos, custo_servir, way_length[indice], one_way, status))
        grafo_indexado_txt.write("%4d %12d %12d %12f %12f %12f %12f %8s %10s\n" % (id, dicio_nos[nos_passagem[0]], dicio_nos[nos_passagem[1]], custo_atravessar, qde_residuos, custo_servir, way_length[indice], one_way, status))
        id += 1
       
    # dicionario de nós de demanda
    nos_demanda = nx.get_node_attributes(grafo, 'ref')

    # quantidade de nós que têm demanda, ou seja, são requeridos
    #print(len(nos_demanda))
    _QDE_NOS_REQ = len(nos_demanda)

    grafo_txt.write('\n%4s %12s %8s %8s\n' %('id', 'no', 'demanda', 'CS'))
    grafo_indexado_txt.write('\n%4s %12s %8s %8s\n' %('id', 'no', 'demanda', 'CS'))

    # escrita de nós com demanda 
    for indice, no in enumerate(nos_demanda):
        dados = nos_demanda[no].split()
        grafo_txt.write('%4d %12s %8s %8s\n' % (indice, no, dados[2], dados[3]))
        grafo_indexado_txt.write('%4d %12s %8s %8s\n' % (indice, dicio_nos[no], dados[2], dados[3]))

    grafo_txt.close()
    grafo_indexado_txt.close()

    # quantidade total de nós
    _QDE_NOS = len(dicio_nos)

    # escreve arquivo de vértices ordenados
    try: 
        arq_vertices = open(CAMINHO_ARQUIVOS + 'vertices_ordenados.txt', 'w')
    except:
        pass
    
    for no_padrao in dicio_nos:
        arq_vertices.write('%12d\t%12d\n' % (no_padrao, dicio_nos[no_padrao]))

    arq_vertices.close()

    _QDE_ARESTAS = int(_QDE_ARESTAS / 2)
    _QDE_ARESTAS_REQ = int(_QDE_ARESTAS_REQ / 2)


def gera_instancia_uhga():

    '''
    Cria uma instância HGA a partir do grafo indexado, gerado em salva_grafo_txt.
    '''

    global _QDE_NOS, _QDE_ARESTAS, _QDE_ARCOS, _QDE_NOS_REQ, _QDE_ARESTAS_REQ, _QDE_ARCOS_REQ, distancias_links

    grafo_indexado_txt = ''
    instancia = ''
    
    # carrega grafo indexado
    try:
        grafo_indexado_txt = open(CAMINHO_ARQUIVOS + 'grafo_indexado(' + NOME_ARQUIVO_OSM + ').txt', 'r')
        
        # armazenar leitura de arquivo em lista, desta forma não há necessidade de 
        # voltar ao início do arquivo toda vez que for iterar sobre suas linhas com seek(0)
        grafo_indexado_linhas = grafo_indexado_txt.readlines()
    except IOError as e:
        print(e)

    # instância no formato padrão do MCGRP 
    try:
        instancia = open(CAMINHO_ARQUIVOS + ARQ_INSTANCIA, "w+")
    except IOError as e:
        print(e)        

    
    # escreve cabeçalho da instância
    instancia.write("%-14s %-12s\n" % ("Name:",          NOME_ARQUIVO_OSM))
    instancia.write("%-14s %-12s\n" % ("Optimal value:", ""))
    instancia.write("%-14s %-12d\n" % ("#Vehicles:",     -1))
    instancia.write("%-14s %-12d\n" % ("Capacity:",      10000))
    instancia.write("%-14s %-12d\n" % ("Depot Node:",    1))
    instancia.write("%-14s %-12d\n" % ("#Nodes:",        _QDE_NOS))
    instancia.write("%-14s %-12d\n" % ("#Edges:",        _QDE_ARESTAS))
    instancia.write("%-14s %-12d\n" % ("#Arcs:",         _QDE_ARCOS))
    instancia.write("%-14s %-12d\n" % ("#Required N:",   _QDE_NOS_REQ)) 
    instancia.write("%-14s %-12s\n" % ("#Required E:",   _QDE_ARESTAS_REQ))
    instancia.write("%-14s %-12s\n\n" % ("#Required A:", _QDE_ARCOS_REQ))
    
    ###################### ESCREVE OS NÓS REQUERIDOS ######################
    instancia.write("%-8s %-8s %-8s\n" % ("ReN.","DEMAND","S.COST"))
    
    lista_no = False
    for linha in grafo_indexado_linhas:
            
        if lista_no:    
            dados = linha.split()
            instancia.write("%-8s %-8d %-d\n" % ("N{}".format(dados[1]), int(dados[2]), int(dados[3])))
 
        if 'no' in linha and 'demanda' in linha:
            lista_no = True
            
    ###################### ESCREVE AS ARESTAS REQUERIDAS ######################
    instancia.write("\n%-8s %-8s %-8s %-8s %-8s %-8s\n" % ("ReE.", "From N.", "To N.", "T. COST", "DEMAND", "S.COST"))
    
    # contador para manter controle do índice das arestas requeridas incluídas na instância
    qde_aresta_count = 0
    ''' 
        Como este for irá percorrer todo grafo indexado, pode-se utilizar da variável
        (dados) pra se obter a distância dos links de serviço.
    '''
    for linha in grafo_indexado_linhas:
        
        #separa todos os valores de uma linha em uma tuple (lista)
        dados = linha.split()
       
        # se lista estiver vazia, então deve parar, pois está no fim dos arestas/arcos
        # e está entrando na lista de nós
        if len(dados) == 0:
            break

        # ignora cabeçalho
        if 'id' in dados:
            continue 
        else:
            # é o mesmo que dicionario[(u, v)] = distancia(u, v)
            distancias_links[(dados[1], dados[2])] = dados[6]
        
        # verificação de dados[1] < dados[2] se faz necessária, simplesmente para que uma way n seja repetida
        # já que (1 to 2) e (2 to 1) seria a mesma coisa, já que são arestas
        if dados[7] == 'False' and dados[8] != 'passagem' and int(dados[1]) < int(dados[2]):
            qde_aresta_count += 1
            instancia.write("%-8s %-8d %-8d %-8.2f %-8.2f %-8.2f\n" % ("E{}".format(qde_aresta_count), int(dados[1]), int(dados[2]), float(dados[3]), float(dados[4]), float(dados[5])))



    ###################### ESCREVE AS ARESTAS NÃO REQUERIDAS ######################
    instancia.write("\n%-8s %-8s %-8s %-8s\n" % ("EDGE", "From N.", "To N.", "T. COST"))
    
    # contador para manter controle do íncide das arestas não requeridas incluídas na instância
    qde_arestas_nreq_count = 0

    for linha in grafo_indexado_linhas:

        dados = linha.split()
        
        # se lista estiver vazia, então deve parar, pois está no fim dos arestas/arcos
        # e está entrando na lista de nós
        if len(dados) == 0:
            break

        # ignora cabeçalho
        if 'id' in dados:
            continue 

        # verificação de dados[1] < dados[2] se faz necessária, simplesmente para que uma way n seja repetida
        # já que 1 to 2 and 2 to 1 seria a mesma coisa, já que são arestas        
        if dados[7] == 'False' and dados[8] == 'passagem' and int(dados[1]) < int(dados[2]):
            qde_arestas_nreq_count += 1
            instancia.write("%-8s %-8d %-8d %-8.2f\n" % ("NrE{}".format(qde_arestas_nreq_count), int(dados[1]), int(dados[2]), float(dados[6])))


    ###################### ESCREVE OS ARCOS REQUERIDOS ######################
    instancia.write("\n%-8s %-8s %-8s %-8s %-8s %-8s\n" % ("ReA.", "FROM N.", "TO N.", "T. COST", "DEMAND", "S.COST"))

    nos_req_count = 0

    for linha in grafo_indexado_linhas:

        dados = linha.split()
        
        if len(dados) == 0:
            break

        # ignora cabeçalho
        if 'id' in dados:
            continue

        if len(dados) == 9:
            if  dados[7] == 'True' and dados[8] != 'passagem':
                nos_req_count += 1
                instancia.write("%-8s %-8d %-8d %-8.2f %-8.2f %-8.2f\n" % ("A{}".format(nos_req_count), int(dados[1]), int(dados[2]), float(dados[3]), float(dados[4]), float(dados[5])))
    
    ###################### ESCREVE OS ARCOS NÃO REQUERIDOS ######################
    instancia.write("\n%-8s %-8s %-8s %-8s\n" % ("ARC", "FROM N.", "TO N.", "T. COST"))

    qde_arcos_nreq = 0    

    for linha in grafo_indexado_linhas:
        
        dados = linha.split()
        
        if len(dados) == 0:
            break
        
        # ignora cabeçalho
        if 'id' in dados:
            continue
        
        if  dados[7] == 'True' and dados[8] == 'passagem':
            qde_arcos_nreq += 1
            instancia.write("%-8s %-8d %-8d %-8.2f\n" % ("NrA{}".format(qde_arcos_nreq), int(dados[1]), int(dados[2]), float(dados[6])))
 
    instancia.close()


##########################################################################################################
#                Função que configura e imprime as rotas na tela                                         #
##########################################################################################################
def  mostra_rotas(Grafo):
   
    # criando referência ao objeto saidaUHGA
    saidaUHGA = ''
    rotas = [[]]          # Matriz que irá guardar as rotas
    dados = []
    ruas_visitadas = [[]]   # Guarda os Links que são apenas de 'passagem' para cada rota, como uma lista de tuplas
    edgelist = [[]]         # Guarda os Links que são apenas de 'servico'
    reqnodes = {}           # Dicionário que guarda os nós requeridos de uma rota (feito em 23/09/2019)
    allreqnodes = {}        # Dicionário que guarda todos os nós requeridos
    #Constantes
    cor = ['red', 'green', 'pink', 'yellow', 'black']
    N = 2.5
    
    try:
        # utilizando este novo trecho será interpretado como o endereço da pasta de perfil que no Windows retorna o diretório do usuário, no seu caso C:\Users\Frederico, 
        # no meu C:\Users\joao1 assim o programa vai funcionar sem que precisemos modificar pra rodar o código
        pasta_usuario = (os.environ.get('USERPROFILE') or os.environ.get('HOME')).replace('\\', '/')
        saidaUHGA = open(pasta_usuario + "/Dropbox/Projeto Pesquisa/Gerador de Instâncias MCGRP/CARP/CARP_Code_and_Instances/Solutions/CPS_CentroMCGRP.sol", "r")
        
    except IOError as e:
        print ("[Mensagem] Abertura de arquivo de leitura não deu certo.\n", e)
    
    # Constroi o dicionário 'pos' (position) com a posição (coordenadas) de todos os nós do grafo
    pos = {node: [data['x'], data['y']] for node, data in Grafo.nodes(data=True)}
    #l=0 
    n=0
    for l, linha in enumerate(saidaUHGA.readlines()):
        # A lista 'dados' agora é usada para guardar a sequência de nós de uma rota... 
        dados.clear()
        #l += 1    
        if (l > 3 and linha != ""):
            for s in linha.split():
                if s.find(",") != -1:
                    sub = s.split(",")
                    for str in sub:
                        dados.append(str.replace(")", ""))
                else:
                    if s.find("(") != -1:
                        dados.append(s.replace("(",""))
                    else: 
                        if s.find(")") != -1:
                            dados.append(s.replace(")",""))
                        else:
                            dados.append(s)
            #pdb.set_trace()
            rotas.append([])
            ruas_visitadas.append([])
            edgelist.append([])
            for i in range(len(dados)):
                if dados[i] == 'D':
                    #Caso não haja conexão entre o "penúltimo" e o "último" nó (depósito) da rota, as lacunas são preenchidas 
                    if (dados[i - 4] == 'S' and dados[i - 1] != dados[i + 2]): 
                        source = int(dados[i - 1])
                        target = int(dados[i + 2])
                        caminho = nx.dijkstra_path(Grafo, source, target, weight='weight')
                        ii = 0
                        for no in caminho[1:len(caminho)]:
                            #rotas[ll].append(no)                         
                            ruas_visitadas[n].append((caminho[ii], no))
                            ii += 1
        
                if dados[i] == 'S':
                    if dados[i + 2] != dados[i - 1]:
                        rotas[n].append(int(dados[i + 2]))
                        source = int(dados[i - 1])
                        target = int(dados[i + 2])
                        #Se a rota for descontínua, preenche as lacunas com os nós do caminho mínimo...
                        caminho = nx.dijkstra_path(Grafo, source, target, weight='weight')
                        ii = 0
                        for no in caminho[1:len(caminho)]:
                            #rotas[ll].append(no)                        
                            ruas_visitadas[n].append((caminho[ii], no))
                            ii += 1
                    # Os extremos de uma aresta serão iguais quando se tratar de um "nó requisitado" 
                    if dados[i + 2] != dados[i + 3]:
                        rotas[n].append(int(dados[i + 3])) 
                        # Lista de arestas da rota 'n'
                        edgelist[n].append((int(dados[i + 2]), int(dados[i + 3])))
                    else:
                        reqnodes[int(dados[i + 2])] = pos[int(dados[i + 2])]
                            
            allreqnodes.update( reqnodes )  # add the required nodes from route 'n' to the dictionary that will store all req. nodes
            ############### INSERI ESSE CÓDIGO NOVO AQUI ############################################
            r = input('\tMostrar rota {} no Grafo(s/n)?'.format(n + 1))
            if r == 's': 
                # Draw nodes
                nx.draw_networkx_nodes(Grafo, pos, node_size=5, alpha=0.5, node_color='gray')
                # Draw graph's edges
                nx.draw_networkx_edges(Grafo, pos, node_size=5, edgelist=Grafo.edges(), width=1.0, alpha=0.5, edge_color='gray', arrows=False)
                
                # Draw only the REQUIRED edges (links) from route n  
                nx.draw_networkx_edges(Grafo, pos, edgelist=edgelist[n], width=1.5, edge_color=cor[n], style='solid', arrowstyle='-|>', arrowsize=7, 
                                       arrows=True, node_size=5, nodelist=None, node_shape='o')
                # Draw only the NON REQUIRED edges (links) from route n
                nx.draw_networkx_edges(Grafo, pos, edgelist=ruas_visitadas[n] , width=1.0, edge_color='b', style='dashed', arrowstyle='-|>', arrowsize=7,  
                                       arrows=True, node_size=5, nodelist=None, node_shape='o')
                
                # Draw only the initial node from route n
                #nodelist = [int(dados[8])]
                #nx.draw_networkx_nodes(Grafo, pos={int(dados[8]): pos[int(dados[8])]}, nodelist=nodelist, node_size=15, node_color='black', label='1')
                reqnodes.update( {int(dados[8]): pos[int(dados[8])]} )
                
                # Draw the required nodes and the initial node from route n
                nodelist = [int(key) for key in reqnodes]
                print(nodelist)
                nx.draw_networkx_nodes(Grafo, pos=reqnodes, nodelist=nodelist, node_size=18, node_color='black', label='1')        
                
                # Draw edge labels
                edge_labels = dict([(edgelist[n][i], i + 1) for i in range(len(edgelist[n]))]) 
                #print(edge_labels)
                bbox = {'ec':[1,1,1,0], 'fc':[1,1,1,0]}  # hack to label edges over line (rather than breaking up line)
                nx.draw_networkx_edge_labels(Grafo, pos, edge_labels=edge_labels, bbox = bbox, font_size=5.5)
                
                params = plt.gcf()
                pltSize = params.get_size_inches()
                params.set_size_inches((pltSize[0]*N, pltSize[1]*N), forward=True)
                plt.axis('off')
                plt.title("Rota do caminhão {}".format(n+1))
                plt.show()
            ########################################################################################### 
            n += 1
            reqnodes.clear()
            
    r = input('\tMostrar todas as rotas no mesmo Grafo(s/n)?')
    if r == 's':
        print("\t...Gerando rotas, aguarde!....")
        # Draw nodes
        nx.draw_networkx_nodes(Grafo,pos,node_size=5, alpha=0.5, node_color='gray')
        # Draw graph's edges
        nx.draw_networkx_edges(Grafo, pos, node_size=5, edgelist=Grafo.edges(), width=1.0, alpha=0.5, edge_color='gray', arrows=False)
                    
        for r in range(n):
            # Draw only the REQUIRED edges (links) from route 1  
            nx.draw_networkx_edges(Grafo, pos, edgelist=edgelist[r], width=1.5, edge_color=cor[r], style='solid', arrowstyle='-|>', arrowsize=7, 
                                   arrows=True, node_size=10, nodelist=None, node_shape='o')                          
            # Draw edge labels
            #edge_labels.clear()
            edge_labels = dict([(edgelist[r][i], i + 1) for i in range(len(edgelist[r]))]) 
            #print(edge_labels)
            bbox = {'ec':[1,1,1,0], 'fc':[1,1,1,0]}  # hack to label edges over line (rather than breaking up line)
            nx.draw_networkx_edge_labels(Grafo, pos, edge_labels=edge_labels, bbox = bbox, font_size=5.5)
            edge_labels.clear()
            
        # Add the initial node to the required nodes
        allreqnodes.update( {int(dados[8]): pos[int(dados[8])]} )
        #print(allreqnodes)
        # Draw all the required nodes and the initial node
        nodelist = [int(key) for key in allreqnodes]
        nx.draw_networkx_nodes(Grafo, pos=allreqnodes, nodelist=nodelist, node_size=18, node_color='black', label='1')        
        
        params = plt.gcf()
        pltSize = params.get_size_inches()
        params.set_size_inches((pltSize[0]*N, pltSize[1]*N), forward=True) 
        plt.axis('off')
        plt.title("Rotas dos {} caminhões".format(n))        
        plt.show()
        
    saidaUHGA.close()
    dados.clear()
    ruas_visitadas.clear()
    edgelist.clear()  
    reqnodes.clear()
    allreqnodes.clear()
    
################################################################################ 
#                           EXECUÇÃO DO PROGRAMA                               #
################################################################################
def main():
    
    grafo = object
    
    try:
        # grafo - MultiDiGraph
        print('>>\tCarregando grafo de arquivo .OSM')
        grafo = ox.graph_from_file(simplify=True, retain_all=False, filename=NOME_ARQUIVO_OSM + ".osm", name=NOME_ARQUIVO_OSM)
    except IOError as e:
        print('!!\tO grafo não pôde ser carregado.\n\nErro:\n', e)
    
    print('OK\tGrafo OSM carregado.\n')
    
    
    r = input(">>\tGerar arquivo graphml e grafos em formato de texto? (s/n)")
    if r == 's':
        #grafo = ox.graph_from_file(network_type='all', simplify=True, retain_all=False, filename=NOME_ARQUIVO_OSM + ".osm", name=NOME_ARQUIVO_OSM)
        #Salvando grafo gerado como arquivo .graphml em disco local
        ox.save_load.save_graphml(grafo, filename="grafo("+NOME_ARQUIVO_OSM+").graphml", folder=CAMINHO_ARQUIVOS )
    
        print('OK\tGrafo graphml gerado.\n')

        print('>>\tGerando grafo com nós padrão e grafo indexado no formato de arquivo texto.')
        # como é preciso que os grafos txt sejam gerados e que o número de nós seja
        # conhecido, a opção de gerar grafo agora é obrigatória ao usuário. O grafo
        # é carregado a partir de arquivo .graphml
        grafo = ox.save_load.load_graphml("grafo(" + NOME_ARQUIVO_OSM + ").graphml", folder=CAMINHO_ARQUIVOS)
        salva_grafo_txt(grafo, NOME_ARQUIVO_OSM)
        
        print('OK\tGrafos de texto gerados.\n')


    r = input('>>\tGerar instância (s/n)?')
    if r == 's': 
        gera_instancia_uhga()
        
        print('OK\tInstância gerada.\n')


    r = input(">>\tGerar arquivo '.graphml' modificado? (s/n)")
    if r == 's':
        # recebe o grafo com valores de nós padronizados
        # e retorna um grafo modificado com valores de nós menores (indexados) para ser desenhado
        try:
            arquivo_grafo = open(CAMINHO_ARQUIVOS + 'grafo('+NOME_ARQUIVO_OSM+').graphml', 'r', encoding='utf-8')
            recursos.modificador_grafo.modifica_valores_no_grafo(CAMINHO_ARQUIVOS, arquivo_grafo, NOME_ARQUIVO_OSM)        
        except IOError as e:
            print (e)

        print('OK\tGrafo modificado gerado.\n')

    grafoml = ox.save_load.load_graphml("grafomod(" + NOME_ARQUIVO_OSM + ").graphml", CAMINHO_ARQUIVOS)

    r = input('>>\tMostrar rotas no Grafo? (s/n)')
    if r == 's': 
        mostra_rotas(grafoml)    
    


if __name__ == "__main__":
    main()