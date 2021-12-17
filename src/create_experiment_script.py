import sys
import os 
import argparse
import pandas as pd
from HierarchicalGeoClustering import TreeClusters, Clustering

def create_and_clusterize_save(number_exp , levels_=3, points_per_cluster= 200 , path='../output/Data_experiments' , name_prefix= ''):
    """
    Creates the trees and return only the dataframes
    """
    lis_DF_res = []
    for i in range(number_exp):
        print('Experimento: ',i)
        all_dataframes_i = Clustering.generate_tree_clusterize_form(tree_level= levels_,
                                         per_cluster = points_per_cluster,
                                         levels_cluster =  levels_,
                                         verbose = True)
    #######Añadir columnad X, Y  y ordenar
    
        for data in all_dataframes_i['Point_dataframes'].items():
            data[1]['X'] = data[1]['Points'].apply(lambda l: l.x)
            data[1]['Y'] = data[1]['Points'].apply(lambda l: l.y)
            data[1].sort_values(by =['X','Y'], inplace= True)
            data[1].reset_index(inplace=True)
            save_name= path +'/'+name_prefix +'Exp_'+str(i)+'_'+str(data[0])+'.csv'
            print('to save:', save_name )
            data[1].to_csv(save_name)
    #######Añadir columnad X, Y  y ordenar
    
        for data in all_dataframes_i['Noise_signal'].items():
            data[1]['X'] = data[1]['Points'].apply(lambda l: l.x)
            data[1]['Y'] = data[1]['Points'].apply(lambda l: l.y)
            data[1].sort_values(by =['X','Y'], inplace= True)
            data[1].reset_index(inplace=True)
            save_name= path +'/'+name_prefix +'Exp_'+str(i)+'_'+str(data[0])+'_Noise_signal.csv'
            print('to save:', save_name )
            data[1].to_csv(save_name)
            
        df_metric_form = pd.DataFrame(all_dataframes_i['metric_form'])
        file_simi=path +'/'+name_prefix +'Exp_'+str(i)+'_'+'Similarity'+'.csv'
        print('to save:',file_simi)
        
        df_metric_form.to_csv(file_simi)

    return 

def main(**kwargs):
    num_exp = kwargs.get('experiments', 3)
    levels = kwargs.get('levels', 3)
    points = kwargs.get('levels', 100)
    path = kwargs.get('path', '../output/Data_experiments')
    name_prefix = kwargs.get('name_prefix', '')
    #print(num_exp)
    #print(levels)
    #print(points)
    #print(path)
    if num_exp is None:
        num_exp = 3
    if levels is None:
        levels = 3
    if points is None:
        points = 100
    if path is None:
        path = '../output/Data_experiments'
    if name_prefix is None:
        name_prefix = ''
    create_and_clusterize_save(num_exp,
                               levels_= levels,
                               points_per_cluster= points,
                               path = path,
                               name_prefix = name_prefix)
    
    
    
if __name__== '__main__':
    
    parser = argparse.ArgumentParser()
    parser.add_argument('--exp', type=int, help= 'Number of experiment to create')
    parser.add_argument('--levels', type=int, help= 'Number of levels in each experiment')
    parser.add_argument('--points', type=int, help= 'Number of points per cluster')
    parser.add_argument('--path', type=str , help= 'path to store the resulting csv of dataframes')
    parser.add_argument('--prefix', type=str , help= 'Prefix in the name')
    
    args = parser.parse_args()
    #print(args)
    
    main(experiments = args.exp,
         levels = args.levels,
         points= args.points,
         path= args.path,
         name_prefix= args.prefix,
        )
    