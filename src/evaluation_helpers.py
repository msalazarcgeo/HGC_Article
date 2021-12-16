import sys
import os 
import argparse
import geopandas as gpd
module_path = os.path.abspath(os.path.join('..'))
#if module_path not in sys.path:
#    sys.path.append(module_path)
#from src.data_syntetic_structure import *
from sklearn import metrics

def visualize_experiment(experiment, level_to_vis, axs, noise=False, legend=True,  **kwargs):
    """
    Reads from the all_data_cal values the experiment and 
    """
    path = kwargs.get('path', '../output/500_p/' )
    alpha_original = kwargs.get('alpha_original',.05 )
    alpha_clusterizations = kwargs.get('alpha_clusterizations',.03 )
    print(path + experiment +'_original_retag.csv')
    read_experim = path + experiment 
    all_data_Exp_i ={
        'original_retag': pd.read_csv( read_experim +'_original_retag.csv'),
        'Natural_C': pd.read_csv( read_experim +'_Natural_C.csv'),
        'DBSCAN': pd.read_csv( read_experim +'_DBSCAN.csv'),
        'OPTICS': pd.read_csv( read_experim +'_OPTICS.csv'),
        'HDBSCAN': pd.read_csv( read_experim +'_HDBSCAN.csv'),
        'Adap_DBSCAN': pd.read_csv( read_experim +'Adap_DBSCAN.csv'),
        'similarity_metric': pd.read_csv( read_experim +'_Similarity.csv'),
    }
    get_noise_signal_tag( all_data_Exp_i)
    
    Level_vis =level_to_vis
    

    for num_key, df_name in enumerate(all_data_Exp_i.keys()):
        if df_name == 'original_retag':
            df_geo_max =  gpd.geodataframe.DataFrame( all_data_Exp_i[df_name])            
            if Level_vis == 0:
                geo_lev_vis_previus = df_geo_max
            else:
                geo_lev_vis_previus = df_geo_max[df_geo_max['concat_tags_signal'].apply(lambda l: l.split('_')[Level_vis-1]!='noise')]
            geo_lev_vis =  df_geo_max[df_geo_max['concat_tags_signal'].apply(lambda l: l.split('_')[Level_vis]!='noise')]
            if noise:
                axs.scatter(geo_lev_vis_previus['X'], geo_lev_vis_previus['Y'] , alpha=alpha_original, label='original_no' )
            print(geo_lev_vis.shape)
            axs.scatter(geo_lev_vis['X'], geo_lev_vis['Y'], alpha=alpha_original, label='original')
            
            
        elif df_name != 'similarity_metric':
            df_geo_max =  gpd.geodataframe.DataFrame( all_data_Exp_i[df_name])
            #df_geo_max['Points_geo'] = df_geo_max.apply( lambda l: shapely.geometry.Point(l.X, l.Y), axis=1)
            geo_lev_vis =  df_geo_max[df_geo_max['concat_tags_signal'].apply(lambda l: l.split('_')[Level_vis]!='noise')]
            axs.scatter(geo_lev_vis['X'],geo_lev_vis['Y'],
                        alpha=alpha_clusterizations, label= df_name
                       )
            axs.set_title('Clusters in level '+ str(level_to_vis))
            #xs.title.set_text(df_name)    
        
    return axs


def Eval_level_metric(dic_dataframes_Exp_i, **kwargs):
                      
    """
    For each clustering we get the evaluation using the corresponding metric
    """
    metric_eval = kwargs.get('metric_eval' , metrics.normalized_mutual_info_score) 
    level = kwargs.get('level' ,0)
    verbose = kwargs.get('verbose', False)
    clus_df = kwargs.get( 'dataframes', ['Natural_C','DBSCAN','OPTICS','HDBSCAN','Adap_DBSCAN'])
    
    ### get the points that shoul be on the level using the original data 
    if verbose:
        print('Nivel a considerar: ', level)
        
    if level !=0:
        to_get = dic_dataframes_Exp_i['original_retag']['concat_tags_signal'].apply(lambda l: l.split('_')[level-1] != 'noise')
        should_be = dic_dataframes_Exp_i['original_retag']['concat_tags_signal'][to_get]
    #The ones that actually are in the clusterization 
        dic_point_level_index={}
        for df_name in clus_df:
            point_clus_level_index = dic_dataframes_Exp_i[df_name]['concat_tags_signal'][
                                        dic_dataframes_Exp_i[df_name]['concat_tags_signal'].apply(
                                                        lambda l: l.split('_')[level-1]!='noise')
                            ]
            get_eval_ = should_be.index.union(point_clus_level_index.index)
            dataframe_eval =dic_dataframes_Exp_i[df_name].iloc[get_eval_]['concat_tags_signal'].apply(lambda l: l.split('_')[level])
                
            original_ev_ = dic_dataframes_Exp_i['original_retag'].iloc[get_eval_]['concat_tags_signal'].apply(lambda l: l.split('_')[level])
            if verbose:
                print('Elementos original: ', original_ev_.shape)
                print('Etiquetas en original: ', original_ev_.unique())
                print('Elementos clusterizado: ', dataframe_eval.shape) 
                print('Etiquetas en clusterizado: ', dataframe_eval.unique())
            
            res_metric = metric_eval(original_ev_, dataframe_eval)
            dic_point_level_index[df_name] = res_metric
    
    elif level ==0:
        dic_point_level_index={}
        for df_name in clus_df:
            dataframe_eval =dic_dataframes_Exp_i[df_name]['concat_tags_signal'].apply(lambda l: l.split('_')[level])
            original_ev_ = dic_dataframes_Exp_i['original_retag']['concat_tags_signal'].apply(lambda l: l.split('_')[level])
            res_metric = metric_eval(original_ev_, dataframe_eval)
            dic_point_level_index[df_name] = res_metric

    
    dic_point_level_index['Level'] = level
    
    return  dic_point_level_index
