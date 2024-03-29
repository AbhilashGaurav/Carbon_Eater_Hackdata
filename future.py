# Wrangling or cleaning the data files
from turtle import colormode
from track import *
import tempfile
import cv2
import torch
import streamlit as st
import os
from re import A
import plotly.graph_objects as go 
import numpy as np
import pandas as pd
from PIL import Image
# https://app.cpcbccr.com/AQI_India/ to downlaod the excel file

import cv2
from vidgear.gears import CamGear
from pyfirmata import Arduino
from pandas.api.types import (
    is_categorical_dtype,
    is_datetime64_any_dtype,
    is_numeric_dtype,
    is_object_dtype,
)
st.markdown( """ <style> .sidebar .sidebar-content { background-image: linear-gradient(#2e7bcf,#2e7bcf); color: black; } </style> """, unsafe_allow_html=True )

#################################################################
# Main function of the program
if __name__ == '__main__':
    # st.echo("hi")
    st.markdown("""<style>body {color: blue;background-color: #111;}</style>""", unsafe_allow_html=True)
    ###########################################################################
    # AQI data part
    # read by default 1st sheet of an excel file
    dataframe1 = pd.read_excel('AQI_DATA.xlsx')  # change the file name to the downloaded file downloaded from the "https://app.cpcbccr.com/AQI_India/"
    col1, col2= st.columns([3,2])
    ################################################################################################
    # data garbage removal

    # dropping the unwanted columns

    dataframe1.drop([0,1,2],axis=0,inplace=True)
    # changing the column names
    dataframe1.rename(columns = {'Central Pollution Control Board':'Sr. No.'}, inplace = True)
    dataframe1.rename(columns = {'Unnamed: 1':'State'}, inplace = True)
    dataframe1.rename(columns = {'Unnamed: 2':'City'}, inplace = True)
    dataframe1.rename(columns = {'Unnamed: 3':'Station Name'}, inplace = True)
    dataframe1.rename(columns = {'Unnamed: 4':'Current_AQI_value'}, inplace = True)

    # resetting the index of the data frame
    dataframe_indi = dataframe1.reset_index()

    # droping the coulmn 0 of the dataframe
    dataframe_indi.pop(dataframe_indi.columns[0])
    df = dataframe_indi.fillna(method='ffill') # this is for filling the vacc

    #########################################################
    # saving the dataframe to csv file
    df.to_csv('current_csv.csv',index=False)

    ########################################################
    # filtering the dataframe in streamlit webapp


    df = pd.read_csv("current_csv.csv")  # read a CSV file inside the 'data" folder next to 'app.py'
    ########################################################################
    # container for data and graph

    #############################################
    st.title("Kindly Filter the AQI data to process")
    aqi_val = 0

    # filter function
    def filter_dataframe(df: pd.DataFrame) -> pd.DataFrame:

        modify = st.checkbox("Add filters")

        if not modify:
            return df

        df = df.copy()

        # Try to convert datetimes into a standard format (datetime, no timezone)
        for col in df.columns:
            if is_object_dtype(df[col]):
                try:
                    df[col] = pd.to_datetime(df[col])
                except Exception:
                    pass

            if is_datetime64_any_dtype(df[col]):
                df[col] = df[col].dt.tz_localize(None)

        modification_container = st.container()

        with modification_container:
            to_filter_columns = st.multiselect("Filter dataframe on", df.columns)
            for column in to_filter_columns:
                left, right = st.columns((1, 20))
                left.write("↳")
                # Treat columns with < 10 unique values as categorical
                if is_categorical_dtype(df[column]) or df[column].nunique() < 10:
                    # print(column)
                    user_cat_input = right.multiselect(
                        f"Values for {column}",
                        df[column].unique(),
                        default=list(df[column].unique()),
                    )
                    df = df[df[column].isin(user_cat_input)]
                elif is_numeric_dtype(df[column]):
                    _min = float(df[column].min())
                    _max = float(df[column].max())
                    step = (_max - _min) / 100
                    user_num_input = right.slider(
                        f"Values for {column}",
                        _min,
                        _max,
                        (_min, _max),
                        step=step,
                    )
                    df = df[df[column].between(*user_num_input)]
                elif is_datetime64_any_dtype(df[column]):
                    user_date_input = right.date_input(
                        f"Values for {column}",
                        value=(
                            df[column].min(),
                            df[column].max(),
                        ),
                    )
                    if len(user_date_input) == 2:
                        user_date_input = tuple(map(pd.to_datetime, user_date_input))
                        start_date, end_date = user_date_input
                        df = df.loc[df[column].between(start_date, end_date)]
                else:
                    user_text_input = right.text_input(
                        f"Substring or regex in {column}",
                    )
                    if user_text_input:
                        df = df[df[column].str.contains(user_text_input)]
        if (len(df.head())==1):
            global aqi_val
            aqi_val= int(df.iat[0,4])
        return df


    df = pd.read_csv(
        "current_csv.csv"
    )


    
