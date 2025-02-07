#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jul 23 13:16:11 2024

@author: liamthompson

The program below only accounts for precip > 0 and precip < 0. For a more robutst testing, refer to v4 of this function. 

Bugs: (Bug that carries over from v4) Some cities do not have matching data frame lengths. I am not sure if this is due to the radnet or the precip data. 
majority of sites work and plot appropriately. 

#################### Version 5 ####################

v5 is a little less robust in the sense it does not plot as many conditions as v4. 

"""

# Import statements 

import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
import seaborn as sns    
import matplotlib.pyplot as plt
from sklearn.preprocessing import PolynomialFeatures
from scipy.stats import mannwhitneyu

# Files set in your /wd 
rad_file = [
    "/Users/liamthompson/Desktop/2022-2023 Rad Data/AZ_PHOENIX_2021.csv",
    "/Users/liamthompson/Desktop/2022-2023 Rad Data/AZ_PHOENIX_2022.csv",
    "/Users/liamthompson/Desktop/2022-2023 Rad Data/AZ_PHOENIX_2023.csv" 
] # Note the file name structure--You have to use AZ_PHOENIX, as an argument of the function below is the city name. 

# NOAA NCEI files are not named by city but by GHCN-H number. To date, I have not found a directory that lists the physical city name of each site. 

rain_file = [
    "/Users/liamthompson/Desktop/2022-2023 Precip Data/PHOENIX_AZ_2021.psv",
    "/Users/liamthompson/Desktop/2022-2023 Precip Data/PHOENIX_AZ_2022.psv",
    "/Users/liamthompson/Desktop/2022-2023 Precip Data/PHOENIX_AZ_2023.psv"
] # Note the file name structure--You have to use AZ_PHOENIX, as an argument of the function below is the city name. 

def load_data(city, rad_file, rain_file, start, end): # Note the city name. 
    rad_data = []
    
    for file_path in rad_file: 
        if city.upper() in file_path.upper():
            rad_data.append(pd.read_csv(file_path, dtype = str))
            
    rad_df = pd.concat(rad_data, ignore_index = True) 
        
    rain_data = []
    for file_path in rain_file:
        if city.upper() in file_path.upper():
            rain_data.append(pd.read_csv(file_path, delimiter = "|", dtype = str))
            
    rain_df = pd.concat(rain_data, ignore_index = True) 
            
    ##### ^ Above reads in and compiles data into a df. 
        
    rain_df["Time"] = pd.to_datetime(rain_df[["Year", "Month", "Day", "Hour", "Minute"]]) # establish a datetime obj. 
    rad_df["Time"] = pd.to_datetime(rad_df["SAMPLE COLLECTION TIME"])
    
    # Convert numeric columns to appropriate types
    rain_df["precipitation"] = pd.to_numeric(rain_df["precipitation"], errors="coerce")
    rain_df["temperature"] = pd.to_numeric(rain_df["temperature"], errors="coerce")
    rad_df["DOSE EQUIVALENT RATE (nSv/h)"] = pd.to_numeric(rad_df["DOSE EQUIVALENT RATE (nSv/h)"], errors="coerce")
    
    start = pd.to_datetime(start) # note that this does not matter as much as long as you specifcy begin and end in the function call
    end = pd.to_datetime(end) 
    
    # Filter data
    filtered_rain = rain_df[(rain_df["Time"] >= start) & (rain_df["Time"] <= end)]
    filtered_rad = rad_df[(rad_df["Time"] >= start) & (rad_df["Time"] <= end)] 

    filtered_rain["Time_round"] = filtered_rain["Time"].dt.round(freq = "H")
    filtered_rad["Time_round"] = filtered_rad["Time"].dt.round(freq = "H")

    rad_precip_merge = pd.merge(filtered_rain, filtered_rad, on = "Time_round", how = "inner")
        
    return city, rad_precip_merge

city, rad_precip_merge = load_data("Phoenix", rad_file, rain_file, "2022-07-01", "2022-10-01")
print(rad_precip_merge)         # Precip data is ready to go. 

###################################################################################````````````````````````````````````

def generate_plots(city, rad_precip_merge):
    
    # Drop NaN values in the target column
    rad_precip_merge = rad_precip_merge.dropna(subset=["precipitation", "DOSE EQUIVALENT RATE (nSv/h)"])
    
    # Separate the data into two groups
    rad_precip_zero = rad_precip_merge[rad_precip_merge['precipitation'] == 0]
    rad_precip_nonzero = rad_precip_merge[rad_precip_merge['precipitation'] != 0]  

    # Calculate mean and median values
    mean_no_precip = np.mean(rad_precip_zero["DOSE EQUIVALENT RATE (nSv/h)"])
    mean_precip =  np.mean(rad_precip_nonzero["DOSE EQUIVALENT RATE (nSv/h)"])
    
    median_no_precip = np.median(rad_precip_zero["DOSE EQUIVALENT RATE (nSv/h)"])
    median_precip = np.median(rad_precip_nonzero["DOSE EQUIVALENT RATE (nSv/h)"])
    
    mean_change = ((mean_precip - mean_no_precip) / mean_no_precip) * 100
    median_change = ((median_precip - median_no_precip) / median_no_precip) * 100
    
    print("The mean Dose when no precip is", mean_no_precip)
    print("The mean Dose when there is precip is", mean_precip)
    print("The percentage increase in the mean dose equivalent when there is precip is", mean_change,"%")

    print("The median Dose when no precip is", median_no_precip)
    print("The median Dose when there is precip is", median_precip)
    print("The percentage increase in the median dose equivalent when there is precip is", median_change,"%")
    
    """    # Conduct a Mann-Whitney U test
        dose_no_precip = rad_precip_zero["DOSE EQUIVALENT RATE (nSv/h)"]
        dose_precip = rad_precip_nonzero["DOSE EQUIVALENT RATE (nSv/h)"]
        u_stat, p_value = mannwhitneyu(dose_no_precip, dose_precip, alternative='two-sided')
        
        print("U-statistic:", u_stat)
        print("p-value:", p_value)
        
        if p_value < 0.05:
            print("The difference in dose equivalent rates with and without precipitation is statistically significant.")
        else:
            print("The difference in dose equivalent rates with and without precipitation is not statistically significant.") 
    """ # If pval calculations are desire, uncomment and adjust indents appr. 
    
    # Plot the boxplots and time series
    plt.figure(figsize=(16, 15), dpi=600)
    
    ax1 = plt.subplot2grid((3,3), (0, 0))
    ax2 = plt.subplot2grid((3,3), (0, 1), colspan=3)
        
####### Boxplot
    combined_data = pd.concat([rad_precip_zero.assign(group="Precipitation\n = 0 mm/hr"),
                               rad_precip_nonzero.assign(group="Precipitation\n > 0 mm/hr")])
    
    ax1 = sns.boxplot(x="group", y="DOSE EQUIVALENT RATE (nSv/h)", color="#0073e6", linewidth=1.5, showfliers=True, data=combined_data, ax=ax1)
    
    ax1.set_xlabel("Condition", size=13, weight="bold")
    ax1.set_ylabel("Dose Equivalent Rate (nSv/hr)", size=13, weight="bold")
    ax1.set_title("Boxplot", weight="bold", size=13)
    
    # Annotate medians
    ax1.annotate(f'Median: {median_no_precip}', xy=(0, median_no_precip), xytext=(-0.1, median_no_precip + 3),
                 arrowprops=dict(facecolor='black', shrink=0.05))
    ax1.annotate(f'Median: {median_precip}', xy=(1, median_precip), xytext=(0.9, median_precip + 3),
                 arrowprops=dict(facecolor='black', shrink=0.05))
    
####### Time series plot
    ax2.plot(rad_precip_merge["Time_y"], rad_precip_merge["DOSE EQUIVALENT RATE (nSv/h)"].rolling(window=10).mean(), label="Dose Equivalent Rate\n (nSv/hr)", color="orange", lw=2)
    ax2.set_ylabel('Dose Equivalent Rate (nSv/hr)', color='orange', size=13, weight="bold")
    ax2.set_xlabel("Time", size=13, weight="bold")
    
    ax2_sec = ax2.twinx()
    ax2_sec.plot(rad_precip_merge["Time_y"], rad_precip_merge["precipitation"].rolling(window=1).mean(), label="Precipitation (mm/hr)", color="#0073e6")
    ax2_sec.set_ylabel('Precipitation (mm/hr)', color='#0073e6', size=13, weight="bold")
    
    ax2.set_title("Precipitation (mm/hr) and Dose Equivalent Rate (nSv/hr) Time Series", weight="bold", size=13)
    
    plt.suptitle(f"{city}", size=16, weight="bold", y=0.92)
    plt.show()

"""
Note how the file structures and functions are called. Don't fret if you run into a couple cities that say the dataframes have to be the same length. 
I am not sure why this bug exists as a vast majority of the sites work and are pltoted appropriately. 
"""
        
      
#%% Dover AFB 

rad_file = [
    "/Users/liamthompson/Desktop/2022-2023 Rad Data_1/DE_DOVER_2021.csv",
    "/Users/liamthompson/Desktop/2022-2023 Rad Data_1/DE_DOVER_2022.csv",
    "/Users/liamthompson/Desktop/2022-2023 Rad Data_1/DE_DOVER_2023.csv"
    ]

rain_file = [
    "/Users/liamthompson/Desktop/2022-2023 Precip Data/DOVER_DE_2023.psv",
    "/Users/liamthompson/Desktop/2022-2023 Precip Data/DOVER_DE_2022.psv",
    "/Users/liamthompson/Desktop/2022-2023 Precip Data/DOVER_DE_2021.psv"
    ]

city, rad_precip_merge = load_data("DOVER", rad_file, rain_file, "2021-01-01", "2021-05-30")

print(rad_precip_merge)        

generate_plots(city, rad_precip_merge)  

#%% Houston hobby airport 

rad_file = [
    "/Users/liamthompson/Desktop/2022-2023 Rad Data_1/TX_HOUSTON_2021.csv",
    "/Users/liamthompson/Desktop/2022-2023 Rad Data_1/TX_HOUSTON_2022.csv",
    "/Users/liamthompson/Desktop/2022-2023 Rad Data_1/TX_HOUSTON_2023.csv"
    ]

rain_file = [
    "/Users/liamthompson/Desktop/2022-2023 Precip Data/HOUSTON_TX_2023.psv",
    "/Users/liamthompson/Desktop/2022-2023 Precip Data/HOUSTON_TX_2022.psv",
    "/Users/liamthompson/Desktop/2022-2023 Precip Data/HOUSTON_TX_2021.psv"
    ]

city, rad_precip_merge = load_data("HOUSTON", rad_file, rain_file, "2021-01-01", "2021-01-14")

print(rad_precip_merge)        

generate_plots(city, rad_precip_merge)  


#%% Idaho falls 

rad_file = [
    "/Users/liamthompson/Desktop/2022-2023 Rad Data_1/ID_IDAHO_FALLS_2021.csv",
    "/Users/liamthompson/Desktop/2022-2023 Rad Data_1/ID_IDAHO_FALLS_2022.csv",
    "/Users/liamthompson/Desktop/2022-2023 Rad Data_1/ID_IDAHO_FALLS_2023.csv"
    ]

rain_file = [
    "/Users/liamthompson/Desktop/2022-2023 Precip Data/IDAHO_FALLS_ID_2023.psv",
    "/Users/liamthompson/Desktop/2022-2023 Precip Data/IDAHO_FALLS_ID_2022.psv",
    "/Users/liamthompson/Desktop/2022-2023 Precip Data/IDAHO_FALLS_ID_2021.psv"
    ]

city, rad_precip_merge = load_data("IDAHO_FALLS", rad_file, rain_file, "2021-01-01", "2023-06-30")

print(rad_precip_merge)        

generate_plots(city, rad_precip_merge)  # Poor data do not use 


#%%  Jackson Hawkins field airport 

rad_file = [
    "/Users/liamthompson/Desktop/2022-2023 Rad Data_1/MS_JACKSON_2021.csv",
    "/Users/liamthompson/Desktop/2022-2023 Rad Data_1/MS_JACKSON_2022.csv",
    "/Users/liamthompson/Desktop/2022-2023 Rad Data_1/MS_JACKSON_2023.csv"
    ]

rain_file = [
    "/Users/liamthompson/Desktop/2022-2023 Precip Data/JACKSON_MS_2023.psv",
    "/Users/liamthompson/Desktop/2022-2023 Precip Data/JACKSON_MS_2022.psv",
    "/Users/liamthompson/Desktop/2022-2023 Precip Data/JACKSON_MS_2021.psv"
    ]

city, rad_precip_merge = load_data("JACKSON", rad_file, rain_file, "2023-04-01", "2023-04-15")

print(rad_precip_merge)        

generate_plots(city, rad_precip_merge)  


#%% Las Vegas McCarran 

rad_file = [
    "/Users/liamthompson/Desktop/2022-2023 Rad Data_1/NV_LAS_VEGAS_2021.csv",
    "/Users/liamthompson/Desktop/2022-2023 Rad Data_1/NV_LAS_VEGAS_2022.csv",
    "/Users/liamthompson/Desktop/2022-2023 Rad Data_1/NV_LAS_VEGAS_2023.csv"
    ]

rain_file = [
    "/Users/liamthompson/Desktop/2022-2023 Precip Data/LAS_VEGAS_NV_2023.psv",
    "/Users/liamthompson/Desktop/2022-2023 Precip Data/LAS_VEGAS_NV_2022.psv",
    "/Users/liamthompson/Desktop/2022-2023 Precip Data/LAS_VEGAS_NV_2021.psv"
    ]

city, rad_precip_merge = load_data("LAS_VEGAS", rad_file, rain_file, "2021-01-01", "2021-05-31")

print(rad_precip_merge)        

generate_plots(city, rad_precip_merge)  


#%% Louisvillle bowman 

rad_file = [
    "/Users/liamthompson/Desktop/2022-2023 Rad Data_1/KY_LOUISVILLE_2021.csv",
    "/Users/liamthompson/Desktop/2022-2023 Rad Data_1/KY_LOUISVILLE_2022.csv",
    "/Users/liamthompson/Desktop/2022-2023 Rad Data_1/KY_LOUISVILLE_2023.csv"
    ]

rain_file = [
    "/Users/liamthompson/Desktop/2022-2023 Precip Data/LOUISVILLE_KY_2023.psv",
    "/Users/liamthompson/Desktop/2022-2023 Precip Data/LOUISVILLE_KY_2022.psv",
    "/Users/liamthompson/Desktop/2022-2023 Precip Data/LOUISVILLE_KY_2021.psv"
    ]

city, rad_precip_merge = load_data("LOUISVILLE", rad_file, rain_file, "2021-01-01", "2021-05-31")

print(rad_precip_merge)        

generate_plots(city, rad_precip_merge)  


#%% Salt Lake City International 

rad_file = [
    "/Users/liamthompson/Desktop/2022-2023 Rad Data_1/UT_SALT_LAKE_CITY_2021.csv",
    "/Users/liamthompson/Desktop/2022-2023 Rad Data_1/UT_SALT_LAKE_CITY_2022.csv",
    "/Users/liamthompson/Desktop/2022-2023 Rad Data_1/UT_SALT_LAKE_CITY_2023.csv"
    ]

rain_file = [
    "/Users/liamthompson/Desktop/2022-2023 Precip Data/SALT_LAKE_CITY_UT_2023.psv",
    "/Users/liamthompson/Desktop/2022-2023 Precip Data/SALT_LAKE_CITY_UT_2022.psv",
    "/Users/liamthompson/Desktop/2022-2023 Precip Data/SALT_LAKE_CITY_UT_2021.psv"
    ]

city, rad_precip_merge = load_data("SALT_LAKE_CITY", rad_file, rain_file, "2021-01-27", "2021-02-10")

print(rad_precip_merge)        

generate_plots(city, rad_precip_merge)  

# DOE Salt lake city site 

#%% Shawano municipal airport 

rad_file = [
    "/Users/liamthompson/Desktop/2022-2023 Rad Data_1/WI_SHAWANO_2021.csv",
    "/Users/liamthompson/Desktop/2022-2023 Rad Data_1/WI_SHAWANO_2022.csv",
    "/Users/liamthompson/Desktop/2022-2023 Rad Data_1/WI_SHAWANO_2023.csv"
    ]

rain_file = [
    "/Users/liamthompson/Desktop/2022-2023 Precip Data/SHAWANO_WI_2023.psv",
    "/Users/liamthompson/Desktop/2022-2023 Precip Data/SHAWANO_WI_2022.psv",
    "/Users/liamthompson/Desktop/2022-2023 Precip Data/SHAWANO_WI_2021.psv"
    ]

city, rad_precip_merge = load_data("SHAWANO", rad_file, rain_file, "2021-01-01", "2023-05-31")

print(rad_precip_merge)        

generate_plots(city, rad_precip_merge)  


#%% Shirley Brookhaven 

rad_file = [
    "/Users/liamthompson/Desktop/2022-2023 Rad Data_1/NY_YAPHANK_2021.csv",
    "/Users/liamthompson/Desktop/2022-2023 Rad Data_1/NY_YAPHANK_2022.csv",
    "/Users/liamthompson/Desktop/2022-2023 Rad Data_1/NY_YAPHANK_2023.csv"
    ]

rain_file = [
    "/Users/liamthompson/Desktop/2022-2023 Precip Data/YAPHANK_NY_2023.psv",
    "/Users/liamthompson/Desktop/2022-2023 Precip Data/YAPHANK_NY_2022.psv",
    "/Users/liamthompson/Desktop/2022-2023 Precip Data/YAPHANK_NY_2021.psv"
    ]

city, rad_precip_merge = load_data("YAPHANK", rad_file, rain_file, "2023-01-12", "2023-01-26")

print(rad_precip_merge)        

generate_plots(city, rad_precip_merge)  


#%% Tallahassee 

rad_file = [
    "/Users/liamthompson/Desktop/2022-2023 Rad Data_1/FL_TALLAHASSEE_2021.csv",
    "/Users/liamthompson/Desktop/2022-2023 Rad Data_1/FL_TALLAHASSEE_2022.csv",
    "/Users/liamthompson/Desktop/2022-2023 Rad Data_1/FL_TALLAHASSEE_2023.csv"
    ]

rain_file = [
    "/Users/liamthompson/Desktop/2022-2023 Precip Data/TALLAHASSEE_FL_2023.psv",
    "/Users/liamthompson/Desktop/2022-2023 Precip Data/TALLAHASSEE_FL_2022.psv",
    "/Users/liamthompson/Desktop/2022-2023 Precip Data/TALLAHASSEE_FL_2021.psv"
    ]

city, rad_precip_merge = load_data("TALLAHASSEE", rad_file, rain_file, "2022-07-01", "2022-07-15")

print(rad_precip_merge)        

generate_plots(city, rad_precip_merge)  


#%% Yuma

rad_file = [
    "/Users/liamthompson/Desktop/2022-2023 Rad Data_1/AZ_YUMA_2021.csv",
    "/Users/liamthompson/Desktop/2022-2023 Rad Data_1/AZ_YUMA_2022.csv",
    "/Users/liamthompson/Desktop/2022-2023 Rad Data_1/AZ_YUMA_2023.csv"
    ]

rain_file = [
    "/Users/liamthompson/Desktop/2022-2023 Precip Data/YUMA_AZ_2023.psv",
    "/Users/liamthompson/Desktop/2022-2023 Precip Data/YUMA_AZ_2022.psv",
    "/Users/liamthompson/Desktop/2022-2023 Precip Data/YUMA_AZ_2021.psv"
    ]

city, rad_precip_merge = load_data("YUMA", rad_file, rain_file, "2021-01-01", "2023-05-31")

print(rad_precip_merge)        

generate_plots(city, rad_precip_merge)  # Do not use. poor data 


#%% Dodge city 

rad_file = [
    "/Users/liamthompson/Desktop/2022-2023 Rad Data_1/KS_DODGE_CITY_2021.csv",
    "/Users/liamthompson/Desktop/2022-2023 Rad Data_1/KS_DODGE_CITY_2022.csv",
    "/Users/liamthompson/Desktop/2022-2023 Rad Data_1/KS_DODGE_CITY_2023.csv"
    ]

rain_file = [
    "/Users/liamthompson/Desktop/2022-2023 Precip Data/DODGE_CITY_KS_2023.psv",
    "/Users/liamthompson/Desktop/2022-2023 Precip Data/DODGE_CITY_KS_2022.psv",
    "/Users/liamthompson/Desktop/2022-2023 Precip Data/DODGE_CITY_KS_2021.psv"
    ]

city, rad_precip_merge = load_data("DODGE_CITY", rad_file, rain_file, "2021-01-01", "2023-05-31")

print(rad_precip_merge)        

generate_plots(city, rad_precip_merge)  


#%% Ellensburg, ellensburg bower field 

rad_file = [
    "/Users/liamthompson/Desktop/2022-2023 Rad Data_1/WA_ELLENSBURG_2021.csv",
    "/Users/liamthompson/Desktop/2022-2023 Rad Data_1/WA_ELLENSBURG_2022.csv",
    "/Users/liamthompson/Desktop/2022-2023 Rad Data_1/WA_ELLENSBURG_2023.csv"
    ]

rain_file = [
    "/Users/liamthompson/Desktop/2022-2023 Precip Data/ELLENSBURG_WA_2023.psv",
    "/Users/liamthompson/Desktop/2022-2023 Precip Data/ELLENSBURG_WA_2022.psv",
    "/Users/liamthompson/Desktop/2022-2023 Precip Data/ELLENSBURG_WA_2021.psv"
    ]

city, rad_precip_merge = load_data("ELLENSBURG", rad_file, rain_file, "2021-01-01", "2023-05-31")

print(rad_precip_merge)        

generate_plots(city, rad_precip_merge)  


#%% Fort Madison 

rad_file = [
    "/Users/liamthompson/Desktop/2022-2023 Rad Data_1/IA_FORT_MADISON_2021.csv",
    "/Users/liamthompson/Desktop/2022-2023 Rad Data_1/IA_FORT_MADISON_2022.csv",
    "/Users/liamthompson/Desktop/2022-2023 Rad Data_1/IA_FORT_MADISON_2023.csv"
    ]

rain_file = [
    "/Users/liamthompson/Desktop/2022-2023 Precip Data/FORT_MADISON_IA_2023.psv",
    "/Users/liamthompson/Desktop/2022-2023 Precip Data/FORT_MADISON_IA_2022.psv",
    "/Users/liamthompson/Desktop/2022-2023 Precip Data/FORT_MADISON_IA_2021.psv"
    ]

city, rad_precip_merge = load_data("FORT_MADISON", rad_file, rain_file, "2021-01-01", "2023-05-31")

print(rad_precip_merge)        

generate_plots(city, rad_precip_merge)  


#%% Kalispell glacier park 

rad_file = [
    "/Users/liamthompson/Desktop/2022-2023 Rad Data_1/MT_KALISPELL_2021.csv",
    "/Users/liamthompson/Desktop/2022-2023 Rad Data_1/MT_KALISPELL_2022.csv",
    "/Users/liamthompson/Desktop/2022-2023 Rad Data_1/MT_KALISPELL_2023.csv"
    ]

rain_file = [
    "/Users/liamthompson/Desktop/2022-2023 Precip Data/KALISPELL_MT_2023.psv",
    "/Users/liamthompson/Desktop/2022-2023 Precip Data/KALISPELL_MT_2022.psv",
    "/Users/liamthompson/Desktop/2022-2023 Precip Data/KALISPELL_MT_2021.psv"
    ]

city, rad_precip_merge = load_data("KALISPELL", rad_file, rain_file, "2022-06-01", "2022-06-30")

print(rad_precip_merge)        

generate_plots(city, rad_precip_merge)  


#%% Pierre regional 

rad_file = [
    "/Users/liamthompson/Desktop/2022-2023 Rad Data_1/SD_PIERRE_2021.csv",
    "/Users/liamthompson/Desktop/2022-2023 Rad Data_1/SD_PIERRE_2022.csv",
    "/Users/liamthompson/Desktop/2022-2023 Rad Data_1/SD_PIERRE_2023.csv"
    ]

rain_file = [
    "/Users/liamthompson/Desktop/2022-2023 Precip Data/PIERRE_SD_2023.psv",
    "/Users/liamthompson/Desktop/2022-2023 Precip Data/PIERRE_SD_2022.psv",
    "/Users/liamthompson/Desktop/2022-2023 Precip Data/PIERRE_SD_2021.psv"
    ]

city, rad_precip_merge = load_data("PIERRE", rad_file, rain_file, "2022-06-10", "2022-06-26")

print(rad_precip_merge)        

generate_plots(city, rad_precip_merge)  


#%% San Diego 

rad_file = [
    "/Users/liamthompson/Desktop/2022-2023 Rad Data_1/CA_SAN_DIEGO_2021.csv",
    "/Users/liamthompson/Desktop/2022-2023 Rad Data_1/CA_SAN_DIEGO_2022.csv",
    "/Users/liamthompson/Desktop/2022-2023 Rad Data_1/CA_SAN_DIEGO_2023.csv"
    ]

rain_file = [
    "/Users/liamthompson/Desktop/2022-2023 Precip Data/SAN_DIEGO_CA_2023.psv",
    "/Users/liamthompson/Desktop/2022-2023 Precip Data/SAN_DIEGO_CA_2022.psv",
    "/Users/liamthompson/Desktop/2022-2023 Precip Data/SAN_DIEGO_CA_2021.psv"
    ]

#city, rad_precip_merge = load_data("SAN_DIEGO", rad_file, rain_file, "2023-02-21", "2023-03-05")
city, rad_precip_merge = load_data("SAN_DIEGO", rad_file, rain_file, "2021-01-01", "2023-06-05")

print(rad_precip_merge)        

generate_plots(city, rad_precip_merge)  # Do not use, poor data 


#%% Bismarck municipal 

rad_file = [
    "/Users/liamthompson/Desktop/2022-2023 Rad Data_1/ND_BISMARCK_2021.csv",
    "/Users/liamthompson/Desktop/2022-2023 Rad Data_1/ND_BISMARCK_2022.csv",
    "/Users/liamthompson/Desktop/2022-2023 Rad Data_1/ND_BISMARCK_2023.csv"
    ]

rain_file = [
    "/Users/liamthompson/Desktop/2022-2023 Precip Data/BISMARCK_ND_2023.psv",
    "/Users/liamthompson/Desktop/2022-2023 Precip Data/BISMARCK_ND_2022.psv",
    "/Users/liamthompson/Desktop/2022-2023 Precip Data/BISMARCK_ND_2021.psv"
    ]

#city, rad_precip_merge = load_data("BISMARCK", rad_file, rain_file, "2022-06-14", "2022-07-01")
city, rad_precip_merge = load_data("BISMARCK", rad_file, rain_file, "2022-06-14", "2022-07-15")

print(rad_precip_merge)        

generate_plots(city, rad_precip_merge)  


#%% Burlington international 

rad_file = [
    "/Users/liamthompson/Desktop/2022-2023 Rad Data_1/VT_BURLINGTON_2021.csv",
    "/Users/liamthompson/Desktop/2022-2023 Rad Data_1/VT_BURLINGTON_2022.csv"
   # "/Users/liamthompson/Desktop/2022-2023 Rad Data_1/VT_BURLINGTON_2023.csv" DNE
    ]

rain_file = [
    "/Users/liamthompson/Desktop/2022-2023 Precip Data/BURLINGTON_VT_2023.psv",
    "/Users/liamthompson/Desktop/2022-2023 Precip Data/BURLINGTON_VT_2022.psv",
    "/Users/liamthompson/Desktop/2022-2023 Precip Data/BURLINGTON_VT_2021.psv"
    ]

city, rad_precip_merge = load_data("BURLINGTON", rad_file, rain_file, "2022-07-01", "2022-09-30")

print(rad_precip_merge)        

generate_plots(city, rad_precip_merge)  


#%% Camp Mary / Austin city 

rad_file = [
    "/Users/liamthompson/Desktop/2022-2023 Rad Data_1/TX_AUSTIN_2021.csv",
    "/Users/liamthompson/Desktop/2022-2023 Rad Data_1/TX_AUSTIN_2022.csv",
    "/Users/liamthompson/Desktop/2022-2023 Rad Data_1/TX_AUSTIN_2023.csv"
    ]

rain_file = [
    "/Users/liamthompson/Desktop/2022-2023 Precip Data/AUSTIN_TX_2023.psv",
    "/Users/liamthompson/Desktop/2022-2023 Precip Data/AUSTIN_TX_2022.psv",
    "/Users/liamthompson/Desktop/2022-2023 Precip Data/AUSTIN_TX_2021.psv"
    ]

city, rad_precip_merge = load_data("AUSTIN", rad_file, rain_file, "2022-11-12", "2022-11-30")

print(rad_precip_merge)        

generate_plots(city, rad_precip_merge)  


#%% Charles wheeler downtown 

rad_file = [
    "/Users/liamthompson/Desktop/2022-2023 Rad Data_1/KS_KANSAS_CITY_2021.csv",
    "/Users/liamthompson/Desktop/2022-2023 Rad Data_1/KS_KANSAS_CITY_2022.csv",
    "/Users/liamthompson/Desktop/2022-2023 Rad Data_1/KS_KANSAS_CITY_2023.csv"
    ]

rain_file = [
    "/Users/liamthompson/Desktop/2022-2023 Precip Data/KANSAS_CITY_KS_2023.psv",
    "/Users/liamthompson/Desktop/2022-2023 Precip Data/KANSAS_CITY_KS_2022.psv",
    "/Users/liamthompson/Desktop/2022-2023 Precip Data/KANSAS_CITY_KS_2021.psv"
    ]

city, rad_precip_merge = load_data("KANSAS_CITY", rad_file, rain_file, "2021-01-01", "2023-05-31")

print(rad_precip_merge)        

generate_plots(city, rad_precip_merge)  


#%% Charleston eager airport 

rad_file = [
    "/Users/liamthompson/Desktop/2022-2023 Rad Data_1/WV_CHARLESTON_2021.csv",
    "/Users/liamthompson/Desktop/2022-2023 Rad Data_1/WV_CHARLESTON_2022.csv",
    "/Users/liamthompson/Desktop/2022-2023 Rad Data_1/WV_CHARLESTON_2023.csv"
    ]

rain_file = [
    "/Users/liamthompson/Desktop/2022-2023 Precip Data/CHARLESTON_WV_2023.psv",
    "/Users/liamthompson/Desktop/2022-2023 Precip Data/CHARLESTON_WV_2022.psv",
    "/Users/liamthompson/Desktop/2022-2023 Precip Data/CHARLESTON_WV_2021.psv"
    ]

city, rad_precip_merge = load_data("CHARLESTON", rad_file, rain_file, "2021-01-01", "2023-05-31")

print(rad_precip_merge)        

generate_plots(city, rad_precip_merge)  


#%% Cleveland lake burke front 

rad_file = [
    "/Users/liamthompson/Desktop/2022-2023 Rad Data_1/OH_CLEVELAND_2021.csv",
    "/Users/liamthompson/Desktop/2022-2023 Rad Data_1/OH_CLEVELAND_2022.csv",
    "/Users/liamthompson/Desktop/2022-2023 Rad Data_1/OH_CLEVELAND_2023.csv"
    ]

rain_file = [
    "/Users/liamthompson/Desktop/2022-2023 Precip Data/CLEVELAND_OH_2023.psv",
    "/Users/liamthompson/Desktop/2022-2023 Precip Data/CLEVELAND_OH_2022.psv",
    "/Users/liamthompson/Desktop/2022-2023 Precip Data/CLEVELAND_OH_2021.psv"
    ]

city, rad_precip_merge = load_data("CLEVELAND", rad_file, rain_file, "2022-07-15", "2022-07-31")

print(rad_precip_merge)        

generate_plots(city, rad_precip_merge)  


#%% Concord municipal 

rad_file = [
    "/Users/liamthompson/Desktop/2022-2023 Rad Data_1/NH_CONCORD_2021.csv",
    "/Users/liamthompson/Desktop/2022-2023 Rad Data_1/NH_CONCORD_2022.csv",
    "/Users/liamthompson/Desktop/2022-2023 Rad Data_1/NH_CONCORD_2023.csv"
    ]

rain_file = [
    "/Users/liamthompson/Desktop/2022-2023 Precip Data/CONCORD_NH_2023.psv",
    "/Users/liamthompson/Desktop/2022-2023 Precip Data/CONCORD_NH_2022.psv",
    "/Users/liamthompson/Desktop/2022-2023 Precip Data/CONCORD_NH_2021.psv"
    ]

city, rad_precip_merge = load_data("CONCORD", rad_file, rain_file, "2021-01-01", "2023-05-31")

print(rad_precip_merge)        

generate_plots(city, rad_precip_merge)  



#%% Fresno 

rad_file = [
    "/Users/liamthompson/Desktop/2022-2023 Rad Data_1/CA_FRESNO_2021.csv",
    "/Users/liamthompson/Desktop/2022-2023 Rad Data_1/CA_FRESNO_2022.csv",
    "/Users/liamthompson/Desktop/2022-2023 Rad Data_1/CA_FRESNO_2023.csv"
    ]

rain_file = [
    "/Users/liamthompson/Desktop/2022-2023 Precip Data/FRESNO_CA_2023.psv",
    "/Users/liamthompson/Desktop/2022-2023 Precip Data/FRESNO_CA_2022.psv",
    "/Users/liamthompson/Desktop/2022-2023 Precip Data/FRESNO_CA_2021.psv"
    ]

city, rad_precip_merge = load_data("FRESNO", rad_file, rain_file, "2023-03-01", "2023-03-17")

print(rad_precip_merge)        

generate_plots(city, rad_precip_merge)  


#%% Jefferson City memorial 

rad_file = [
    "/Users/liamthompson/Desktop/2022-2023 Rad Data_1/MO_JEFFERSON_CITY_2021.csv",
    "/Users/liamthompson/Desktop/2022-2023 Rad Data_1/MO_JEFFERSON_CITY_2022.csv"
    ]

rain_file = [
    "/Users/liamthompson/Desktop/2022-2023 Precip Data/JEFFERSON_CITY_MO_2023.psv",
    "/Users/liamthompson/Desktop/2022-2023 Precip Data/JEFFERSON_CITY_MO_2022.psv",
    "/Users/liamthompson/Desktop/2022-2023 Precip Data/JEFFERSON_CITY_MO_2021.psv"
    ]

#city, rad_precip_merge = load_data("JEFFERSON_CITY", rad_file, rain_file, "2021-07-01", "2021-10-31")

city, rad_precip_merge = load_data("JEFFERSON_CITY", rad_file, rain_file, "2021-01-01", "2023-09-18")

print(rad_precip_merge)        

generate_plots(city, rad_precip_merge)  


#%% Juneau 

rad_file = [
    "/Users/liamthompson/Desktop/2022-2023 Rad Data_1/AK_JUNEAU_2021.csv",
    "/Users/liamthompson/Desktop/2022-2023 Rad Data_1/AK_JUNEAU_2022.csv",
    "/Users/liamthompson/Desktop/2022-2023 Rad Data_1/AK_JUNEAU_2023.csv"
    ]

rain_file = [
    "/Users/liamthompson/Desktop/2022-2023 Precip Data/JUNEAU_AK_2023.psv",
    "/Users/liamthompson/Desktop/2022-2023 Precip Data/JUNEAU_AK_2022.psv",
    "/Users/liamthompson/Desktop/2022-2023 Precip Data/JUNEAU_AK_2021.psv"
    ]

city, rad_precip_merge = load_data("JUNEAU", rad_file, rain_file, "2023-04-24", "2023-05-06")

print(rad_precip_merge)        

generate_plots(city, rad_precip_merge)  


#%% Los Angeles 

rad_file = [
    "/Users/liamthompson/Desktop/2022-2023 Rad Data_1/CA_LOS_ANGELES_2021.csv",
    "/Users/liamthompson/Desktop/2022-2023 Rad Data_1/CA_LOS_ANGELES_2022.csv",
    "/Users/liamthompson/Desktop/2022-2023 Rad Data_1/CA_LOS_ANGELES_2023.csv"
    ]

rain_file = [
    "/Users/liamthompson/Desktop/2022-2023 Precip Data/LOS_ANGELES_CA_2023.psv",
    "/Users/liamthompson/Desktop/2022-2023 Precip Data/LOS_ANGELES_CA_2022.psv",
    "/Users/liamthompson/Desktop/2022-2023 Precip Data/LOS_ANGELES_CA_2021.psv"
    ]

city, rad_precip_merge = load_data("LOS_ANGELES", rad_file, rain_file, "2023-01-04", "2023-01-18")

print(rad_precip_merge)        

generate_plots(city, rad_precip_merge)  


#%% Laredo international airport 

rad_file = [
    "/Users/liamthompson/Desktop/2022-2023 Rad Data_1/TX_LAREDO_2021.csv",
    "/Users/liamthompson/Desktop/2022-2023 Rad Data_1/TX_LAREDO_2022.csv",
    "/Users/liamthompson/Desktop/2022-2023 Rad Data_1/TX_LAREDO_2023.csv"
    ]

rain_file = [
    "/Users/liamthompson/Desktop/2022-2023 Precip Data/LAREDO_TX_2023.psv",
    "/Users/liamthompson/Desktop/2022-2023 Precip Data/LAREDO_TX_2022.psv",
    "/Users/liamthompson/Desktop/2022-2023 Precip Data/LAREDO_TX_2021.psv"
    ]

#city, rad_precip_merge = load_data("LAREDO", rad_file, rain_file, "2021-05-14", "2021-06-05")
city, rad_precip_merge = load_data("LAREDO", rad_file, rain_file, "2021-05-14", "2021-05-28")

print(rad_precip_merge)        

generate_plots(city, rad_precip_merge)  


#%% Olympia, Olympia airport 

rad_file = [
    "/Users/liamthompson/Desktop/2022-2023 Rad Data_1/WA_OLYMPIA_2021.csv",
    "/Users/liamthompson/Desktop/2022-2023 Rad Data_1/WA_OLYMPIA_2022.csv"
    #"/Users/liamthompson/Desktop/2022-2023 Rad Data_1/WA_OLYMPIA_2023.csv" DNE
    ]

rain_file = [
    "/Users/liamthompson/Desktop/2022-2023 Precip Data/OLYMPIA_WA_2023.psv",
    "/Users/liamthompson/Desktop/2022-2023 Precip Data/OLYMPIA_WA_2022.psv",
    "/Users/liamthompson/Desktop/2022-2023 Precip Data/OLYMPIA_WA_2021.psv"
    ]

city, rad_precip_merge = load_data("OLYMPIA", rad_file, rain_file, "2022-11-22", "2022-12-14")

print(rad_precip_merge)        

generate_plots(city, rad_precip_merge)  


#%% Reagan 

rad_file = [
    "/Users/liamthompson/Desktop/2022-2023 Rad Data_1/DC_WASHINGTON_2021.csv",
    "/Users/liamthompson/Desktop/2022-2023 Rad Data_1/DC_WASHINGTON_2022.csv",
    "/Users/liamthompson/Desktop/2022-2023 Rad Data_1/DC_WASHINGTON_2023.csv"
    ]

rain_file = [
    "/Users/liamthompson/Desktop/2022-2023 Precip Data/WASHINGTON_DC_2023.psv",
    "/Users/liamthompson/Desktop/2022-2023 Precip Data/WASHINGTON_DC_2022.psv",
    "/Users/liamthompson/Desktop/2022-2023 Precip Data/WASHINGTON_DC_2021.psv"
    ]

city, rad_precip_merge = load_data("DC", rad_file, rain_file, "2022-07-01", "2022-07-18")
#city, rad_precip_merge = load_data("DC", rad_file, rain_file, "2021-08-01", "2021-09-01")


print(rad_precip_merge)        

generate_plots(city, rad_precip_merge)  


#%% San Jose 

rad_file = [
    "/Users/liamthompson/Desktop/2022-2023 Rad Data_1/CA_SAN_JOSE_2021.csv",
    "/Users/liamthompson/Desktop/2022-2023 Rad Data_1/CA_SAN_JOSE_2022.csv",
    "/Users/liamthompson/Desktop/2022-2023 Rad Data_1/CA_SAN_JOSE_2023.csv"
    ]

rain_file = [
    "/Users/liamthompson/Desktop/2022-2023 Precip Data/SAN_JOSE_CA_2023.psv",
    "/Users/liamthompson/Desktop/2022-2023 Precip Data/SAN_JOSE_CA_2022.psv",
    "/Users/liamthompson/Desktop/2022-2023 Precip Data/SAN_JOSE_CA_2021.psv"
    ]

city, rad_precip_merge = load_data("SAN_JOSE", rad_file, rain_file, "2023-03-14", "2023-04-01")

print(rad_precip_merge)        

generate_plots(city, rad_precip_merge)  


#%% St Paul downtown Holman 

rad_file = [
    "/Users/liamthompson/Desktop/2022-2023 Rad Data_1/MN_ST._PAUL_2021.csv",
    "/Users/liamthompson/Desktop/2022-2023 Rad Data_1/MN_ST._PAUL_2022.csv",
    "/Users/liamthompson/Desktop/2022-2023 Rad Data_1/MN_ST._PAUL_2023.csv"
    ]

rain_file = [
    "/Users/liamthompson/Desktop/2022-2023 Precip Data/ST._PAUL_MN_2023.psv",
    "/Users/liamthompson/Desktop/2022-2023 Precip Data/ST._PAUL_MN_2022.psv",
    "/Users/liamthompson/Desktop/2022-2023 Precip Data/ST._PAUL_MN_2021.psv"
    ]

city, rad_precip_merge = load_data("ST._PAUL", rad_file, rain_file, "2021-08-01", "2021-09-30")

print(rad_precip_merge)        

generate_plots(city, rad_precip_merge)  


#%% Portland international Jetport

rad_file = [
    "/Users/liamthompson/Desktop/2022-2023 Rad Data_1/ME_PORTLAND_2021.csv",
    "/Users/liamthompson/Desktop/2022-2023 Rad Data_1/ME_PORTLAND_2022.csv",
    "/Users/liamthompson/Desktop/2022-2023 Rad Data_1/ME_PORTLAND_2023.csv"
    ]

rain_file = [
    "/Users/liamthompson/Desktop/2022-2023 Precip Data/PORTLAND_ME_2023.psv",
    "/Users/liamthompson/Desktop/2022-2023 Precip Data/PORTLAND_ME_2022.psv",
    "/Users/liamthompson/Desktop/2022-2023 Precip Data/PORTLAND_ME_2021.psv"
    ]

city, rad_precip_merge = load_data("PORTLAND", rad_file, rain_file, "2021-01-01", "2023-05-31")

print(rad_precip_merge)        

generate_plots(city, rad_precip_merge)  

#%% Honolulu HI 

rad_file = [
    "/Users/liamthompson/Desktop/2022-2023 Rad Data_1/HI_HONOLULU_2021.csv",
    "/Users/liamthompson/Desktop/2022-2023 Rad Data_1/HI_HONOLULU_2022.csv"
    ]

rain_file = [
    "/Users/liamthompson/Desktop/2022-2023 Precip Data/HONOLULU_HI_2021.psv",
    "/Users/liamthompson/Desktop/2022-2023 Precip Data/HONOLULU_HI_2022.psv",
    "/Users/liamthompson/Desktop/2022-2023 Precip Data/HONOLULU_HI_2023.psv"
    ]

city, rad_precip_merge = load_data("HONOLULU", rad_file, rain_file, "2021-01-01", "2023-05-31")

print(rad_precip_merge)        

generate_plots(city, rad_precip_merge)  


"/Users/liamthompson/Desktop/2022-2023 Precip Data/HONOLULU_HI_2021.psv"
"/Users/liamthompson/Desktop/2022-2023 Precip Data/HONOLULU_HI_2022.psv"
"/Users/liamthompson/Desktop/2022-2023 Precip Data/HONOLULU_HI_2023.psv"

#%% Miami Fl 

rad_file = [
    "/Users/liamthompson/Desktop/2022-2023 Rad Data_1/FL_MIAMI_2021.csv",
    "/Users/liamthompson/Desktop/2022-2023 Rad Data_1/FL_MIAMI_2022.csv",
    "/Users/liamthompson/Desktop/2022-2023 Rad Data_1/FL_MIAMI_2023.csv"
    ]

rain_file = [
    "/Users/liamthompson/Desktop/2022-2023 Precip Data/MIAMI_FL_2021.psv",
    "/Users/liamthompson/Desktop/2022-2023 Precip Data/MIAMI_FL_2022.psv",
    "/Users/liamthompson/Desktop/2022-2023 Precip Data/MIAMI_FL_2023.psv"
    ]

city, rad_precip_merge = load_data("MIAMI", rad_file, rain_file, "2021-01-01", "2023-05-31")

print(rad_precip_merge)        

generate_plots(city, rad_precip_merge)  


    
    
    
    

    

    

