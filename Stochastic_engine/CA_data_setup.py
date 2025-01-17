# -*- coding: utf-8 -*-
"""
Created on Wed May 03 15:01:31 2017

@author: jdkern
"""

import pandas as pd
import numpy as np

def setup(year,scenario,CAISO_bat_cap,bat_RoC_coeff,bat_RoD_coeff,bat_eff,job_id):

    #read generator parameters into DataFrame
    df_gen = pd.read_csv('CA_data_file/generators.csv',header=0)
       
    #read transmission path parameters into DataFrame
    df_paths = pd.read_csv('CA_data_file/paths.csv',header=0)
    
    #    #calendar
    #    df_calendar = pd.read_excel('CA_data_file/calendar.xlsx',header=0)
    
    #list zones
    zones = ['PGE_valley', 'PGE_bay', 'SCE', 'SDGE']
    
    ##time series of load for each zone
    filename = 'Synthetic_demand_pathflows/Sim_hourly_load_' + scenario + '_{}.csv'
    df_load = pd.read_csv(filename.format(job_id),header=0)
    df_load = df_load[zones]
    df_load = df_load.loc[year*8760:year*8760+8759]
    df_load = df_load.reset_index(drop=True)
    
    ##time series of operational reserves for each zone
    rv= df_load.values
    reserves = np.zeros((len(rv),1))
    for i in range(0,len(rv)):
            reserves[i] = np.sum(rv[i,:])*.04
    df_reserves = pd.DataFrame(reserves)
    df_reserves.columns = ['reserves']
    
    ##daily hydropower availability
    df_hydro = pd.read_csv('Hydro_setup/CA_dispatchable_hydro_{}.csv'.format(job_id),header=0)
    
    ##time series of wind generation for each zone
    df_wind = pd.read_csv('Synthetic_wind_power/wind_power_sim_{}.csv'.format(job_id),header=0)
    header = scenario + '_CAISO'
    df_wind = df_wind.loc[:,header]
    df_wind = df_wind.loc[year*8760:year*8760+8759]
    df_wind = df_wind.reset_index(drop=True)
    wind_caps = pd.read_excel('CA_data_file/wind_caps.xlsx')
    
    
    ##time series solar for each TAC
    df_solar = pd.read_csv('Synthetic_solar_power/solar_power_sim_{}.csv'.format(job_id),header=0)
    header = scenario + '_CAISO'
    df_solar = df_solar.loc[:,header]
    df_solar = df_solar.loc[year*8760:year*8760+8759]
    df_solar = df_solar.reset_index(drop=True)
    solar_caps = pd.read_excel('CA_data_file/solar_caps.xlsx')
    
    ##daily time series of dispatchable imports by path
    filename = 'Path_setup/CA_dispatchable_imports_' + scenario + '_{}.csv'
    df_imports = pd.read_csv(filename.format(job_id),header=0)
    
    ##hourly time series of exports by zone
    filename = 'Path_setup/CA_exports_' + scenario + '_{}.csv'
    df_exports = pd.read_csv(filename.format(job_id),header=0)
    
    #must run resources (LFG,ag_waste,nuclear)
    df_must = pd.read_excel('CA_data_file/must_run.xlsx',header=0)
    
    #natural gas prices
    df_ng = pd.read_excel('Gas_prices/NG_{}.xlsx'.format(job_id), header=0)
    df_ng = df_ng[zones]
    df_ng = df_ng.loc[year*365:year*365+364,:]
    df_ng = df_ng.reset_index(drop=True)
    
    #california imports hourly minimum flows
    filename = 'Path_setup/CA_path_mins_' + scenario + '_{}.csv'
    df_CA_import_mins = pd.read_csv(filename.format(job_id), header=0)
    
    #california hydro hourly minimum flows
    df_CA_hydro_mins = pd.read_csv('Hydro_setup/CA_hydro_mins_{}.csv'.format(job_id), header=0)
      
    # must run generation
    must_run_PGE_bay = np.ones((len(df_load),1))*df_must.loc[0,'PGE_bay']
    must_run_PGE_valley = np.ones((len(df_load),1))*df_must.loc[0,'PGE_valley']
    must_run_SCE = np.ones((len(df_load),1))*df_must.loc[0,'SCE']
    must_run_SDGE = np.ones((len(df_load),1))*df_must.loc[0,'SDGE']
    must_run = np.column_stack((must_run_PGE_valley,must_run_PGE_bay,must_run_SCE,must_run_SDGE))
    df_total_must_run =pd.DataFrame(must_run,columns=('PGE_valley','PGE_bay','SCE','SDGE'))
    df_total_must_run.to_csv('CA_data_file/must_run_hourly_{}.csv'.format(job_id))
    
    
    ############
    #  sets    #
    ############
    #write data.dat file
    import os
    from shutil import copy
    from pathlib import Path
    
    
    path=str(Path.cwd().parent) +str (Path('/UCED/LR/' + str(scenario) + '/CA' + str(year)))
    os.makedirs(path,exist_ok=True)
    
    generators_file='CA_data_file/generators.csv'
    dispatch_file='../UCED/CA_dispatch.py'
    dispatchLP_file='../UCED/CA_dispatchLP.py'
    wrapper_file='../UCED/CA_wrapper.py'
    simulation_file='../UCED/CA_simulation.py'
    emission_cal_file='../UCED/CA_emission_calculation.py'
    emission_gen_file = '../UCED/CA_emissions_generator.csv'
    
    #    with ExcelWriter('scenario_parameters.xlsx') as writer:
    #        df_bat_params.to_excel(writer, sheet_name='Capacities')
    #        ev_df.to_excel(writer, sheet_name='EV Load Profiles')
    #        identifier.to_excel(writer, sheet_name='Scenario and Year')
    #    scenario_param_file = 'scenario_parameters.xlsx'
    
    copy(dispatch_file,path)
    copy(wrapper_file,path)
    copy(simulation_file,path)
    copy(emission_cal_file,path)
    copy(dispatchLP_file,path)
    copy(generators_file,path)
    copy(emission_gen_file,path)
    #    copy(scenario_param_file,path)
    
    filename = path + '/data.dat'
    with open(filename, 'w') as f:
    
        # generator sets by zone
        for z in zones:
            # zone string
            z_int = zones.index(z)
            f.write('set Zone%dGenerators :=\n' % (z_int+1))
            # pull relevant generators
            for gen in range(0,len(df_gen)):
                if df_gen.loc[gen,'zone'] == z:
                    unit_name = df_gen.loc[gen,'name']
                    unit_name = unit_name.replace(' ','_')
                    f.write(unit_name + ' ')
            f.write(';\n\n')
    
        # battery sets by zone
        for z in zones:
            # zone string
            z_int = zones.index(z)
            f.write('set Zone%dBattery :=\n' % (z_int+1))
            unit_name = 'battery%d' % (z_int+1)
            f.write(unit_name + ' ')
            f.write(';\n\n')
    
        # WECC imports
        f.write('set WECCImportsSCE :=\n')
        # pull relevant generators
        for gen in range(0,len(df_gen)):
            if df_gen.loc[gen,'typ'] == 'imports' and df_gen.loc[gen,'zone'] == 'WECC_SCE':
                unit_name = df_gen.loc[gen,'name']
                unit_name = unit_name.replace(' ','_')
                f.write(unit_name + ' ')
        f.write(';\n\n')
    
        # WECC imports
        f.write('set WECCImportsSDGE :=\n')
        # pull relevant generators
        for gen in range(0,len(df_gen)):
            if df_gen.loc[gen,'typ'] == 'imports' and df_gen.loc[gen,'zone'] == 'WECC_SDGE':
                unit_name = df_gen.loc[gen,'name']
                unit_name = unit_name.replace(' ','_')
                f.write(unit_name + ' ')
        f.write(';\n\n')
    
        # WECC imports
        f.write('set WECCImportsPGEV :=\n')
        # pull relevant generators
        for gen in range(0,len(df_gen)):
            if df_gen.loc[gen,'typ'] == 'imports' and df_gen.loc[gen,'zone'] == 'WECC_PGEV':
                unit_name = df_gen.loc[gen,'name']
                unit_name = unit_name.replace(' ','_')
                f.write(unit_name + ' ')
        f.write(';\n\n')
    
        # generator sets by type
        # coal
        f.write('set Coal :=\n')
        # pull relevant generators
        for gen in range(0,len(df_gen)):
            if df_gen.loc[gen,'typ'] == 'coal':
                unit_name = df_gen.loc[gen,'name']
                unit_name = unit_name.replace(' ','_')
                f.write(unit_name + ' ')
        f.write(';\n\n')
    
        # oil
        f.write('set Oil :=\n')
        # pull relevant generators
        for gen in range(0,len(df_gen)):
            if df_gen.loc[gen,'typ'] == 'oil':
                unit_name = df_gen.loc[gen,'name']
                unit_name = unit_name.replace(' ','_')
                f.write(unit_name + ' ')
        f.write(';\n\n')
    
        # Pumped Storage
        f.write('set PSH :=\n')
        # pull relevant generators
        for gen in range(0,len(df_gen)):
            if df_gen.loc[gen,'typ'] == 'psh':
                unit_name = df_gen.loc[gen,'name']
                unit_name = unit_name.replace(' ','_')
                f.write(unit_name + ' ')
        f.write(';\n\n')
    
        # Slack
        f.write('set Slack :=\n')
        # pull relevant generators
        for gen in range(0,len(df_gen)):
            if df_gen.loc[gen,'typ'] == 'slack':
                unit_name = df_gen.loc[gen,'name']
                unit_name = unit_name.replace(' ','_')
                f.write(unit_name + ' ')
        f.write(';\n\n')
    
        # Hydro
        f.write('set Hydro :=\n')
        # pull relevant generators
        for gen in range(0,len(df_gen)):
            if df_gen.loc[gen,'typ'] == 'hydro':
                unit_name = df_gen.loc[gen,'name']
                unit_name = unit_name.replace(' ','_')
                f.write(unit_name + ' ')
        f.write(';\n\n')
    
        # Ramping
        f.write('set Ramping :=\n')
        # pull relevant generators
        for gen in range(0,len(df_gen)):
            if df_gen.loc[gen,'typ'] == 'hydro' or df_gen.loc[gen,'typ'] == 'imports':
                unit_name = df_gen.loc[gen,'name']
                unit_name = unit_name.replace(' ','_')
                f.write(unit_name + ' ')
        f.write(';\n\n')
    
    
        # gas generator sets by zone and type
        for z in zones:
            # zone string
            z_int = zones.index(z)
    
            # Natural Gas
            # find relevant generators
            trigger = 0
            for gen in range(0,len(df_gen)):
                if df_gen.loc[gen,'zone'] == z and (df_gen.loc[gen,'typ'] == 'ngcc' or df_gen.loc[gen,'typ'] == 'ngct' or df_gen.loc[gen,'typ'] == 'ngst'):
                    trigger = 1
            if trigger > 0:
                # pull relevant generators
                f.write('set Zone%dGas :=\n' % (z_int+1))
                for gen in range(0,len(df_gen)):
                    if df_gen.loc[gen,'zone'] == z and (df_gen.loc[gen,'typ'] == 'ngcc' or df_gen.loc[gen,'typ'] == 'ngct' or df_gen.loc[gen,'typ'] == 'ngst'):
                        unit_name = df_gen.loc[gen,'name']
                        unit_name = unit_name.replace(' ','_')
                        f.write(unit_name + ' ')
                f.write(';\n\n')
    
    
        # zones
        f.write('set zones :=\n')
        for z in zones:
            f.write(z + ' ')
        f.write(';\n\n')
    
        # sources
        f.write('set sources :=\n')
        for z in zones:
            f.write(z + ' ')
        f.write(';\n\n')
    
        # sinks
        f.write('set sinks :=\n')
        for z in zones:
            f.write(z + ' ')
        f.write(';\n\n')
    
    ################
    #  parameters  #
    ################
    
        # simulation details
        SimHours = 8760
        f.write('param SimHours := %d;' % SimHours)
        f.write('\n')
        f.write('param SimDays:= %d;' % int(SimHours/24))
        f.write('\n\n')
        HorizonHours = 48
        f.write('param HorizonHours := %d;' % HorizonHours)
        f.write('\n\n')
        HorizonDays = int(HorizonHours/24)
        f.write('param HorizonDays := %d;' % HorizonDays)
        f.write('\n\n')
    
    
    
        # create parameter matrix for transmission paths (source and sink connections)
        f.write('param:' + '\t' + 'limit' + '\t' +'hurdle :=' + '\n')
        for z in zones:
            for x in zones:
                f.write(z + '\t' + x + '\t')
                match = 0
                for p in range(0,len(df_paths)):
                    source = df_paths.loc[p,'start_zone']
                    sink = df_paths.loc[p,'end_zone']
                    if source == z and sink == x:
                        match = 1
                        p_match = p
                if match > 0:
                    f.write(str(df_paths.loc[p_match,'limit']) + '\t' + str(df_paths.loc[p_match,'hurdle']) + '\n')
                else:
                    f.write('0' + '\t' + '0' + '\n')
        f.write(';\n\n')
        
    
    # create parameter matrix for generators
        f.write('param:' + '\t')
        for c in df_gen.columns:
            if c != 'name':
                f.write(c + '\t')
        f.write(':=\n\n')
        for i in range(0,len(df_gen)):
            for c in df_gen.columns:
                if c == 'name':
                    unit_name = df_gen.loc[i,'name']
                    unit_name = unit_name.replace(' ','_')
                    f.write(unit_name + '\t')
                else:
                    f.write(str((df_gen.loc[i,c])) + '\t')
            f.write('\n')
    
        f.write(';\n\n')
        
        # create parameter matrix for batteries
         
        f.write('param:' + '\t' + 'bat_cap' + '\t' + 'bat_RoC' + '\t' + 'bat_RoD' + '\t' + 'bat_eff' + ':=\n\n')
        f.write('battery1' + '\t' + str(CAISO_bat_cap*0.09196) + '\t' + str(bat_RoC_coeff*CAISO_bat_cap*0.09196) + '\t' + str(bat_RoD_coeff*CAISO_bat_cap*0.09196) + '\t' + str(bat_eff) + '\n')
        f.write('battery2' + '\t' + str(CAISO_bat_cap*0.46037) + '\t' + str(bat_RoC_coeff*CAISO_bat_cap*0.46037) + '\t' + str(bat_RoD_coeff*CAISO_bat_cap*0.46037) + '\t' + str(bat_eff) + '\n')
        f.write('battery3' + '\t' + str(CAISO_bat_cap*0.25528) + '\t' + str(bat_RoC_coeff*CAISO_bat_cap*0.25528) + '\t' + str(bat_RoD_coeff*CAISO_bat_cap*0.25528) + '\t' + str(bat_eff) + '\n')
        f.write('battery4' + '\t' + str(CAISO_bat_cap*0.19239) + '\t' + str(bat_RoC_coeff*CAISO_bat_cap*0.19239) + '\t' + str(bat_RoD_coeff*CAISO_bat_cap*0.19239) + '\t' + str(bat_eff) + '\n')
        f.write(';\n\n')
        #scale factor for capacity is proportional load of each zone to CA as a whole
        
        # times series data
        # zonal (hourly)
        f.write('param:' + '\t' + 'SimDemand' + '\t' + 'SimWind' \
        + '\t' + 'SimSolar' + '\t' + 'SimMustRun:=' + '\n')
        for z in zones:
            sz = solar_caps.loc[0,z]
            wz = wind_caps.loc[0,z]
            for h in range(0,len(df_load)):
                f.write(z + '\t' + str(h+1) + '\t' + str(df_load.loc[h,z]) + '\t' + str(df_wind[h]*wz) + '\t' + str(df_solar[h]*sz) + '\t' + str(df_total_must_run.loc[h,z]) + '\n')
        f.write(';\n\n')
    
        # zonal (daily)
        f.write('param:' + '\t' + 'SimGasPrice:=' + '\n')
        for z in zones:
            for d in range(0,int(SimHours/24)):
                f.write(z + '\t' + str(d+1) + '\t' + str(df_ng.loc[d,z]) + '\n')
        f.write(';\n\n')
    
        #system wide (daily)
        f.write('param:' + '\t' + 'SimPath66_imports' + '\t' + 'SimPath46_SCE_imports' + '\t' + 'SimPath61_imports' + '\t' + 'SimPath42_imports' + '\t' + 'SimPath24_imports' + '\t' + 'SimPath45_imports' + '\t' + 'SimPGE_valley_hydro' + '\t' + 'SimSCE_hydro:=' + '\n')
        for d in range(0,len(df_imports)):
                f.write(str(d+1) + '\t' + str(df_imports.loc[d,'Path66']) + '\t' + str(df_imports.loc[d,'Path46_SCE']) + '\t' + str(df_imports.loc[d,'Path61']) + '\t' + str(df_imports.loc[d,'Path42']) + '\t' + str(df_imports.loc[d,'Path24']) + '\t' + str(df_imports.loc[d,'Path45']) + '\t' + str(df_hydro.loc[d,'PGE_valley']) + '\t' + str(df_hydro.loc[d,'SCE']) + '\n')
        f.write(';\n\n')
    
    
        #system wide (hourly)
        f.write('param:' + '\t' + 'SimPath66_exports' + '\t' + 'SimPath42_exports' + '\t' + 'SimPath24_exports' + '\t' + 'SimPath45_exports' + '\t' + 'SimReserves' + '\t' + 'SimSCE_hydro_minflow' + '\t' + 'SimPGE_valley_hydro_minflow' + '\t' + 'SimPath61_imports_minflow' + '\t' + 'SimPath66_imports_minflow' + '\t' + 'SimPath46_SCE_imports_minflow' + '\t' + 'SimPath42_imports_minflow:=' + '\n')
        for h in range(0,len(df_load)):
                f.write(str(h+1) + '\t' + str(df_exports.loc[h,'Path66']) + '\t' + str(df_exports.loc[h,'Path42']) + '\t' + str(df_exports.loc[h,'Path24']) + '\t' + str(df_exports.loc[h,'Path45']) + '\t' + str(df_reserves.loc[h,'reserves'])  + '\t' + str(df_CA_hydro_mins.loc[h,'SCE']) + '\t' + str(df_CA_hydro_mins.loc[h,'PGE_valley']) + '\t' + str(df_CA_import_mins.loc[h,'Path61']) + '\t' + str(df_CA_import_mins.loc[h,'Path66']) + '\t' + str(df_CA_import_mins.loc[h,'Path46_SCE']) + '\t' + str(df_CA_import_mins.loc[h,'Path42']) + '\n')
        f.write(';\n\n')
        
        
        ####################################################
        
    filename = path + '/dataLP.dat'
    with open(filename, 'w') as f:
    
        # generator sets by zone
        for z in zones:
            # zone string
            z_int = zones.index(z)
            f.write('set Zone%dGenerators :=\n' % (z_int+1))
            # pull relevant generators
            for gen in range(0,len(df_gen)):
                if df_gen.loc[gen,'zone'] == z:
                    unit_name = df_gen.loc[gen,'name']
                    unit_name = unit_name.replace(' ','_')
                    f.write(unit_name + ' ')
            f.write(';\n\n')
    
        # WECC imports
        f.write('set WECCImportsSCE :=\n')
        # pull relevant generators
        for gen in range(0,len(df_gen)):
            if df_gen.loc[gen,'typ'] == 'imports' and df_gen.loc[gen,'zone'] == 'WECC_SCE':
                unit_name = df_gen.loc[gen,'name']
                unit_name = unit_name.replace(' ','_')
                f.write(unit_name + ' ')
        f.write(';\n\n')
    
        # WECC imports
        f.write('set WECCImportsSDGE :=\n')
        # pull relevant generators
        for gen in range(0,len(df_gen)):
            if df_gen.loc[gen,'typ'] == 'imports' and df_gen.loc[gen,'zone'] == 'WECC_SDGE':
                unit_name = df_gen.loc[gen,'name']
                unit_name = unit_name.replace(' ','_')
                f.write(unit_name + ' ')
        f.write(';\n\n')
    
        # WECC imports
        f.write('set WECCImportsPGEV :=\n')
        # pull relevant generators
        for gen in range(0,len(df_gen)):
            if df_gen.loc[gen,'typ'] == 'imports' and df_gen.loc[gen,'zone'] == 'WECC_PGEV':
                unit_name = df_gen.loc[gen,'name']
                unit_name = unit_name.replace(' ','_')
                f.write(unit_name + ' ')
        f.write(';\n\n')
    
        # generator sets by type
        # coal
        f.write('set Coal :=\n')
        # pull relevant generators
        for gen in range(0,len(df_gen)):
            if df_gen.loc[gen,'typ'] == 'coal':
                unit_name = df_gen.loc[gen,'name']
                unit_name = unit_name.replace(' ','_')
                f.write(unit_name + ' ')
        f.write(';\n\n')
    
        # oil
        f.write('set Oil :=\n')
        # pull relevant generators
        for gen in range(0,len(df_gen)):
            if df_gen.loc[gen,'typ'] == 'oil':
                unit_name = df_gen.loc[gen,'name']
                unit_name = unit_name.replace(' ','_')
                f.write(unit_name + ' ')
        f.write(';\n\n')
    
        # Pumped Storage
        f.write('set PSH :=\n')
        # pull relevant generators
        for gen in range(0,len(df_gen)):
            if df_gen.loc[gen,'typ'] == 'psh':
                unit_name = df_gen.loc[gen,'name']
                unit_name = unit_name.replace(' ','_')
                f.write(unit_name + ' ')
        f.write(';\n\n')
    
        # Slack
        f.write('set Slack :=\n')
        # pull relevant generators
        for gen in range(0,len(df_gen)):
            if df_gen.loc[gen,'typ'] == 'slack':
                unit_name = df_gen.loc[gen,'name']
                unit_name = unit_name.replace(' ','_')
                f.write(unit_name + ' ')
        f.write(';\n\n')
    
        # Hydro
        f.write('set Hydro :=\n')
        # pull relevant generators
        for gen in range(0,len(df_gen)):
            if df_gen.loc[gen,'typ'] == 'hydro':
                unit_name = df_gen.loc[gen,'name']
                unit_name = unit_name.replace(' ','_')
                f.write(unit_name + ' ')
        f.write(';\n\n')
    
        # Ramping
        f.write('set Ramping :=\n')
        # pull relevant generators
        for gen in range(0,len(df_gen)):
            if df_gen.loc[gen,'typ'] == 'hydro' or df_gen.loc[gen,'typ'] == 'imports':
                unit_name = df_gen.loc[gen,'name']
                unit_name = unit_name.replace(' ','_')
                f.write(unit_name + ' ')
        f.write(';\n\n')
    
    
        # gas generator sets by zone and type
        for z in zones:
            # zone string
            z_int = zones.index(z)
    
            # Natural Gas
            # find relevant generators
            trigger = 0
            for gen in range(0,len(df_gen)):
                if df_gen.loc[gen,'zone'] == z and (df_gen.loc[gen,'typ'] == 'ngcc' or df_gen.loc[gen,'typ'] == 'ngct' or df_gen.loc[gen,'typ'] == 'ngst'):
                    trigger = 1
            if trigger > 0:
                # pull relevant generators
                f.write('set Zone%dGas :=\n' % (z_int+1))
                for gen in range(0,len(df_gen)):
                    if df_gen.loc[gen,'zone'] == z and (df_gen.loc[gen,'typ'] == 'ngcc' or df_gen.loc[gen,'typ'] == 'ngct' or df_gen.loc[gen,'typ'] == 'ngst'):
                        unit_name = df_gen.loc[gen,'name']
                        unit_name = unit_name.replace(' ','_')
                        f.write(unit_name + ' ')
                f.write(';\n\n')
    
    
        # zones
        f.write('set zones :=\n')
        for z in zones:
            f.write(z + ' ')
        f.write(';\n\n')
    
        # sources
        f.write('set sources :=\n')
        for z in zones:
            f.write(z + ' ')
        f.write(';\n\n')
    
        # sinks
        f.write('set sinks :=\n')
        for z in zones:
            f.write(z + ' ')
        f.write(';\n\n')
    
    ################
    #  parameters  #
    ################
    
        # simulation details
        SimHours = 8760
        f.write('param SimHours := %d;' % SimHours)
        f.write('\n')
        f.write('param SimDays:= %d;' % int(SimHours/24))
        f.write('\n\n')
        HorizonHours = 48
        f.write('param HorizonHours := %d;' % HorizonHours)
        f.write('\n\n')
        HorizonDays = int(HorizonHours/24)
        f.write('param HorizonDays := %d;' % HorizonDays)
        f.write('\n\n')
    
    
    
        # create parameter matrix for transmission paths (source and sink connections)
        f.write('param:' + '\t' + 'limit' + '\t' +'hurdle :=' + '\n')
        for z in zones:
            for x in zones:
                f.write(z + '\t' + x + '\t')
                match = 0
                for p in range(0,len(df_paths)):
                    source = df_paths.loc[p,'start_zone']
                    sink = df_paths.loc[p,'end_zone']
                    if source == z and sink == x:
                        match = 1
                        p_match = p
                if match > 0:
                    f.write(str(df_paths.loc[p_match,'limit']) + '\t' + str(df_paths.loc[p_match,'hurdle']) + '\n')
                else:
                    f.write('0' + '\t' + '0' + '\n')
        f.write(';\n\n')
        
    
    # create parameter matrix for generators
        f.write('param:' + '\t')
        for c in df_gen.columns:
            if c != 'name':
                f.write(c + '\t')
        f.write(':=\n\n')
        for i in range(0,len(df_gen)):
            for c in df_gen.columns:
                if c == 'name':
                    unit_name = df_gen.loc[i,'name']
                    unit_name = unit_name.replace(' ','_')
                    f.write(unit_name + '\t')
                else:
                    f.write(str((df_gen.loc[i,c])) + '\t')
            f.write('\n')
    
        f.write(';\n\n')
        
        
        # times series data
        # zonal (hourly)
        f.write('param:' + '\t' + 'SimDemand' + '\t' + 'SimWind' \
        + '\t' + 'SimSolar' + '\t' + 'SimMustRun:=' + '\n')
        for z in zones:
            sz = solar_caps.loc[0,z]
            wz = wind_caps.loc[0,z]
            for h in range(0,len(df_load)):
                f.write(z + '\t' + str(h+1) + '\t' + str(df_load.loc[h,z])\
                + '\t' + str(df_wind[h]*wz) + '\t' + str(df_solar[h]*sz)\
                + '\t' + str(df_total_must_run.loc[h,z]) + '\n')
        f.write(';\n\n')
    
        # zonal (daily)
        f.write('param:' + '\t' + 'SimGasPrice:=' + '\n')
        for z in zones:
            for d in range(0,int(SimHours/24)):
                f.write(z + '\t' + str(d+1) + '\t' + str(df_ng.loc[d,z]) + '\n')
        f.write(';\n\n')
    
        #system wide (daily)
        f.write('param:' + '\t' + 'SimPath66_imports' + '\t' + 'SimPath46_SCE_imports' + '\t' + 'SimPath61_imports' + '\t' + 'SimPath42_imports' + '\t' + 'SimPath24_imports' + '\t' + 'SimPath45_imports' + '\t' + 'SimPGE_valley_hydro' + '\t' + 'SimSCE_hydro:=' + '\n')
        for d in range(0,len(df_imports)):
                f.write(str(d+1) + '\t' + str(df_imports.loc[d,'Path66']) + '\t' + str(df_imports.loc[d,'Path46_SCE']) + '\t' + str(df_imports.loc[d,'Path61']) + '\t' + str(df_imports.loc[d,'Path42']) + '\t' + str(df_imports.loc[d,'Path24']) + '\t' + str(df_imports.loc[d,'Path45']) + '\t' + str(df_hydro.loc[d,'PGE_valley']) + '\t' + str(df_hydro.loc[d,'SCE']) + '\n')
        f.write(';\n\n')
    
    
        #system wide (hourly)
        f.write('param:' + '\t' + 'SimPath66_exports' + '\t' + 'SimPath42_exports' + '\t' + 'SimPath24_exports' + '\t' + 'SimPath45_exports' + '\t' + 'SimReserves' + '\t' + 'SimSCE_hydro_minflow' + '\t' + 'SimPGE_valley_hydro_minflow' + '\t' + 'SimPath61_imports_minflow' + '\t' + 'SimPath66_imports_minflow' + '\t' + 'SimPath46_SCE_imports_minflow' + '\t' + 'SimPath42_imports_minflow:=' + '\n')
        for h in range(0,len(df_load)):
                f.write(str(h+1) + '\t' + str(df_exports.loc[h,'Path66']) + '\t' + str(df_exports.loc[h,'Path42']) + '\t' + str(df_exports.loc[h,'Path24']) + '\t' + str(df_exports.loc[h,'Path45']) + '\t' + str(df_reserves.loc[h,'reserves'])  + '\t' + str(df_CA_hydro_mins.loc[h,'SCE']) + '\t' + str(df_CA_hydro_mins.loc[h,'PGE_valley']) + '\t' + str(df_CA_import_mins.loc[h,'Path61']) + '\t' + str(df_CA_import_mins.loc[h,'Path66']) + '\t' + str(df_CA_import_mins.loc[h,'Path46_SCE']) + '\t' + str(df_CA_import_mins.loc[h,'Path42']) + '\n')
        f.write(';\n\n')
    
        
        
        
        

    return None
