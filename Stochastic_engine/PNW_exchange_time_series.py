# -*- coding: utf-8 -*-
"""
Created on Mon May 14 17:29:16 2018
@author: jdkern
"""
from __future__ import division
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

def exchange(year,scenario,job_id):

    filename = 'Synthetic_demand_pathflows/Load_Path_Sim_' + scenario + '_{}.csv' 
    df_data = pd.read_csv(filename.format(job_id),header=0)
    c = ['Path3_sim','Path8_sim','Path14_sim','Path65_sim','Path66_sim']
    df_data = df_data[c]
    paths = ['Path3','Path8','Path14','Path65','Path66']
    df_data.columns = paths
    df_data = df_data.loc[year*365:year*365+364,:]
    
    # select dispatchable imports 
    imports = df_data
    imports = imports.reset_index()
    
    for p in paths:
        for i in range(0,len(imports)):     
            
            if p=='Path3' or p=='Path65' or p=='Path66':   #SCRIPT ASSUMPTION: NEGATIVE = EXPORT. revert sign when needed
                if imports.loc[i,p] >= 0:
                    imports.loc[i,p] = 0
                else:
                    imports.loc[i,p] = -imports.loc[i,p]
            
            else:
                if imports.loc[i,p] < 0:
                    imports.loc[i,p] = 0
    
    filename = 'Path_setup/PNW_imports_' + scenario + '_{}.csv'
    imports.to_csv(filename.format(job_id))
    
    # convert to minimum flow time series and dispatchable (daily)
    df_mins = pd.read_excel('Path_setup/PNW_imports_minflow_profiles.xlsx',header=0)
    lines = ['Path3','Path8','Path14','Path65','Path66']
    
    for i in range(0,len(df_data)):
        for L in lines:
            
            if df_mins.loc[i,L] >= imports.loc[i,L]:
                df_mins.loc[i,L] = imports.loc[i,L]
                imports.loc[i,L] = 0
            
            else:
                imports.loc[i,L] = np.max((0,imports.loc[i,L]-df_mins.loc[i,L]))
    
    dispatchable_imports = imports*24
    filename = 'Path_setup/PNW_dispatchable_imports_' + scenario + '_{}.csv'
    dispatchable_imports.to_csv(filename.format(job_id))
    
    df_data = imports.copy(deep=True)
    
    # hourly minimum flow for paths
    hourly = np.zeros((8760,len(lines)))
    
    for i in range(0,365):
        for L in lines:
            index = lines.index(L)
            
            hourly[i*24:i*24+24,index] = np.min((df_mins.loc[i,L], df_data.loc[i,L]))
            
    H = pd.DataFrame(hourly)
    H.columns = ['Path3','Path8','Path14','Path65','Path66']
    filename = 'Path_setup/PNW_path_mins_' + scenario + '_{}.csv'
    H.to_csv(filename.format(job_id))
    
    # hourly exports
    filename = 'Synthetic_demand_pathflows/Load_Path_Sim_' + scenario + '_{}.csv'
    df_data = pd.read_csv(filename.format(job_id),header=0)
    c = ['Path3_sim','Path8_sim','Path14_sim','Path65_sim','Path66_sim']
    df_data = df_data[c]
    df_data.columns = [paths]
    df_data = df_data.loc[year*365:year*365+364,:]
    df_data = df_data.reset_index(drop=True)
    
    e = np.zeros((8760,5))
    
    for p in paths:
        
        path_profiles = pd.read_excel('Path_setup/PNW_path_export_profiles.xlsx',sheet_name=p,header=None)
        
        p_index = paths.index(p)
        pp = path_profiles.values
        
        if p=='Path3' or p=='Path65' or p=='Path66':   #SCRIPT ASSUMPTION: NEGATIVE = EXPORT. revert sign when needed
                for j in range(0,len(df_data)):
                    df_data.loc[j,p]=df_data.loc[j,p]*-1
                    
        for i in range(0,len(df_data)):
            if df_data.loc[i,p].values < 0:
                e[i*24:i*24+24,p_index] = pp[i,:]*-df_data.loc[i,p].values
    
    e = e*24
    for i in range(0,len(e)):
        if e[i,3] > 3800:
            e[i,3] = 3800
    exports = pd.DataFrame(e) 
    exports.columns = ['Path3','Path8','Path14','Path65','Path66']
    filename = 'Path_setup/PNW_exports_' + scenario + '_{}.csv'
    exports.to_csv(filename.format(job_id))
    
    
    ##########################
    ##########################
    
    # HYDRO
    
    # convert to minimum flow time series and dispatchable (daily)
    
    df_data = pd.read_excel('PNW_hydro/PNW_hydro_daily_{}.xlsx'.format(job_id),header=0)
    hydro = df_data.loc[year*365:year*365+364,'PNW']
    hydro = hydro.reset_index()
    df_mins = pd.read_excel('Hydro_setup/Minimum_hydro_profiles.xlsx',header=0)
       
    for i in range(0,len(hydro)):
    
        if df_mins.loc[i,'PNW']*24 >= hydro.loc[i,'PNW']:
            df_mins.loc[i,'PNW'] = hydro.loc[i,'PNW']/24
            hydro.loc[i,'PNW'] = 0
        
        else:
            hydro.loc[i,'PNW'] = np.max((0,hydro.loc[i,'PNW']-df_mins.loc[i,'PNW']*24))
    
    dispatchable_hydro = hydro
    dispatchable_hydro.to_csv('Hydro_setup/PNW_dispatchable_hydro_{}.csv'.format(job_id))
    
    # hourly minimum flow for hydro
    hourly = np.zeros((8760,1))
    
    df_data = pd.read_excel('PNW_hydro/PNW_hydro_daily_{}.xlsx'.format(job_id),header=0)
    hydro = df_data.loc[year*365:year*365+364,'PNW']
    hydro = hydro.reset_index()
        
    for i in range(0,365):
            
        hourly[i*24:i*24+24] = np.min((df_mins.loc[i,'PNW'],hydro.loc[i,'PNW']))
            
    H = pd.DataFrame(hourly)
    H.columns = ['PNW']
    H.to_csv('Hydro_setup/PNW_hydro_mins_{}.csv'.format(job_id))

    return None
