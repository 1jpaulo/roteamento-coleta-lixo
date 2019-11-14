import folium
import numpy as np
import pandas as pd
from collections import namedtuple


def get_bearing(p1, p2):
    
    '''
    Returns compass bearing from p1 to p2
    
    Parameters
    p1 : namedtuple with lat lon
    p2 : namedtuple with lat lon
    
    Return
    compass bearing of type float
    
    Notes
    Based on https://gist.github.com/jeromer/2005586
    '''
    
    long_diff = np.radians(p2.lon - p1.lon)
    
    lat1 = np.radians(p1.lat)
    lat2 = np.radians(p2.lat)
    
    x = np.sin(long_diff) * np.cos(lat2)
    y = (np.cos(lat1) * np.sin(lat2) 
        - (np.sin(lat1) * np.cos(lat2) 
        * np.cos(long_diff)))
    bearing = np.degrees(np.arctan2(x, y))
    
    # adjusting for compass bearing
    if bearing < 0:
        return bearing + 360
    return bearing

def get_arrows(locations, color='blue', size=6, n_arrows=3):
    
    '''
    Get a list of correctly placed and rotated 
    arrows/markers to be plotted
    
    Parameters
    locations : list of lists of lat lons that represent the 
                start and end of the line. 
                eg [[41.1132, -96.1993],[41.3810, -95.8021]]
    arrow_color : default is 'blue'
    size : default is 6
    n_arrows : number of arrows to create.  default is 3
    Return
    list of arrows/markers
    '''
    
    Point = namedtuple('Point', field_names=['lat', 'lon'])
    
    # creating point from our Point named tuple
    p1 = Point(locations[0][0], locations[0][1])
    p2 = Point(locations[1][0], locations[1][1])
    
    # getting the rotation needed for our marker.  
    # Subtracting 90 to account for the marker's orientation
    # of due East(get_bearing returns North)
    rotation = get_bearing(p1, p2) - 90
    
    # get an evenly space list of lats and lons for our arrows
    # note that I'm discarding the first and last for aesthetics
    # as I'm using markers to denote the start and end
    arrow_lats = np.linspace(p1.lat, p2.lat, n_arrows + 2)[1:n_arrows+1]
    arrow_lons = np.linspace(p1.lon, p2.lon, n_arrows + 2)[1:n_arrows+1]
    
    arrows = []
    
    #creating each "arrow" and appending them to our arrows list
    for points in zip(arrow_lats, arrow_lons):
        arrows.append(folium.RegularPolygonMarker(location=points, 
                      fill_color=color, number_of_sides=3, 
                      radius=size, rotation=rotation).add_to(some_map))
    return arrows
    
def plot_arrows(nb_nodes, rotas, NOME_ARQUIVO_OSM, some_map):

    # Dicionário que guarda as listas contendo as 'latitudes'(coord x) e 'longitudes'(coord y) de todos os vértices
    coord_vertices = {}
    
    # O objeto está sendo passado como 'some_map'
    #try:
    #    graphml = open("data/grafomod(" + NOME_ARQUIVO_OSM + ").graphml", "r")
    #except IOError as e:
    #    print ("[Mensagem] Erro ao tentar abrir o arquivo para leitura!", e)
    
    l = 1
    for linha in some_map.readlines():
    
        if (linha.find("node id")):
            pass
    
    
    """
    Exemplo de como adicionar uma lista a um dicionário
    >>> dic = {}
    >>> lista = []
    >>> dic['a'] = lista
    >>> lista.append('a')
    >>> print dic
    {'a': ['a']}"""
    
    # Será necessário criar uma matriz com as 'lats' (y) e 'lons' (x) de todos os nós do grafo. 
    # Essas coordenadas são encontradas no arquivo .graphml como 'x' e 'y'
    '''    
    # using omaha coordinates 
    center_lat = 41.257160
    center_lon = -95.995102
    # generating a couple of random latlongs in the omaha area
    lats = np.random.uniform(low=center_lat - .25, high=center_lat +    .25, size=(2,))
    lons = np.random.uniform(low=center_lon - .25, high=center_lon + .25, size=(2,))
    p1 = [lats[0], lons[0]]  # [lats[0], lons[0]] = [y, x]
    p2 = [lats[1], lons[1]] = [y, x]

    some_map = folium.Map(location=[center_lat, center_lon], zoom_start=10)

    folium.Marker(location=p1,     icon=folium.Icon(color='green')).add_to(some_map)
    folium.Marker(location=p2, icon=folium.Icon(color='red')).add_to(some_map)
    folium.PolyLine(locations=[p1, p2], color='blue').add_to(some_map)
    '''

    # para cada link da rota, devemos identificar as coordenadas de seus nós e passar para a função 'get_arrow'
    arrows = get_arrows(locations=[p1, p2], n_arrows=3)
    for arrow in arrows:
        arrow.add_to(some_map)
    some_map