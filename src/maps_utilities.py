import os
import sys
import matplotlib.pyplot as plt
import matplotlib.colors
import numpy as np
import geopandas as gpd
import seaborn as sns
from HierarchicalGeoClustering import TreeClusters, Clustering 
import shapely 
from matplotlib import cm
import pandas as pd
import warnings
import contextily as ctx



def node_translate(node, x_off, y_off, a=1, b=0, d=0,e=1):
    """
    Translate the node and ite point and there children
    """
    point_trans_x= x_off
    point_trans_y= y_off
    matrix_trans = [a, b ,d, e, point_trans_x, point_trans_y]
    new_points= [shapely.affinity.affine_transform(i,matrix_trans) for i in node.point_cluster_noise  ]
    node.point_cluster_noise = new_points           
    
    node.polygon_cluster = shapely.affinity.affine_transform(node.polygon_cluster,
                                                    matrix_trans
                                                    )
    # node.center = shapely.affinity.affine_transform(node.center,
    #                                          matrix_trans
    #                                         )
    for i in node.children:
        node_translate(i, x_off, y_off, a=a, b= b, d=d,e=e)
    
    return



def tree_translate_affine(tree_original, x_off, y_off, a=1, b=0, d=0,e=1):
    """
    Translate the tree 
    """
    node_translate(tree_original.root,  x_off, y_off, a=a, b=b, d=d,e=e)
    return



def un_normalize(tree_un,x_min, y_min, x_max, y_max ):
    """
    
    """
    ##### Si la normalización se hizo salvaje entonces 
    b=0
    d=0
    ####3
    a = (x_max - x_min)
    x_off = x_min
    e = (y_max - y_min)
    y_off = y_min
    tree_translate_affine(tree_un,x_off , y_off, a=a, b=b, d=d, e=e)    
    

    
def get_the_clusterizations(df_points, **kwargs):
    """
    Obtains the cluster for each of the posible clusterizations types
    
    """
    # levels_cluster = kwargs.get('levels', 3)
    levels_Natural = kwargs.get('levels_Natural_c', 3)
    levels_Adaptative = kwargs.get('levels_Adaptative', 3)
    levels_OPTICS = kwargs.get('levels_OPTICS', 3)
    levels_HDBSCAN = kwargs.get('levels_HDBSCAN', 3)
    
    df_points['x'] = df_points['geometry'].apply(lambda l: l.x )
    df_points['y'] = df_points['geometry'].apply(lambda l: l.y )
    orig_min_x = df_points['x'].min()
    orig_max_x = df_points['x'].max()
    orig_min_y = df_points['y'].min()
    orig_max_y = df_points['y'].max()
    df_points = df_points.drop_duplicates(subset = ['x', 'y'])
    df_points['x_trans'] = (df_points['x']- orig_min_x)/(orig_max_x- orig_min_x)
    df_points['y_trans'] = (df_points['y']- orig_min_y)/(orig_max_y- orig_min_y)
    
    data_arr = df_points[['x_trans', 'y_trans']].to_numpy()
    dic_points = {'points':[data_arr], 'parent':''}
    print('Creating trees')
    print('Calculating Natural Cities')
    tree_Natural_c = Clustering.recursive_clustering_tree(
                        dic_points,
                        levels_clustering = levels_Natural,
                        algorithm = 'natural_cities'
                )
    print('Finish Natural Cities')
    print('Calculating HDBSCAN')
    tree_HDBSCAN = Clustering.recursive_clustering_tree(
                        dic_points,
                        levels_clustering = levels_HDBSCAN,
                        algorithm = 'hdbscan'
                )
    print('Finish HDBSCAN')
    print('Calculating OPTICS')
    tree_OPTICS= Clustering.recursive_clustering_tree(
                        dic_points,
                        levels_clustering = levels_OPTICS,
                        algorithm = 'optics'
                )
    print('Finish OPTICS')
    print('Calculating Adaptative')
    tree_adaptative = Clustering.recursive_clustering_tree(
                    dic_points,
                    levels_clustering = levels_Adaptative,
                    algorithm = 'adaptative_DBSCAN'
                )
    print('Finish Adaptative')
    un_normalize(tree_Natural_c, orig_min_x, orig_min_y , orig_max_x , orig_max_y)
    un_normalize(tree_HDBSCAN, orig_min_x, orig_min_y , orig_max_x , orig_max_y)
    un_normalize(tree_adaptative, orig_min_x, orig_min_y , orig_max_x , orig_max_y)
    un_normalize(tree_OPTICS, orig_min_x, orig_min_y , orig_max_x , orig_max_y)
    
    return {'Natural_c':tree_Natural_c,
            'HDBSCAN': tree_HDBSCAN,
            'OPTICS': tree_OPTICS,
            'Adaptative': tree_adaptative
           }


def get_geopandas_tree_polygon(tree_geo):
    """
    Create a geopandas with the polygons from the tree
    """
    list_dic=[]
    for i , level_nodes in enumerate(tree_geo.levels_nodes):
        # levels_nodes= tree_geo.get_level(i)
        # print(level_nodes)
        for node in level_nodes:
            
            if node.parent == None:
                parent = ''
            else:
                parent = node.parent.name
            # print(node.name)
            list_dic.append({'Polygon': node.polygon_cluster,
                             'name': node.name,
                             'level': i,
                             'parent': parent})
    geopan_return = gpd.GeoDataFrame(list_dic)
    geopan_return.set_geometry('Polygon', inplace=True)
    geopan_return.set_crs(4326, inplace =True, allow_override=True)
    return geopan_return
