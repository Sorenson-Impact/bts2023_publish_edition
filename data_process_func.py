#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon May  8 20:35:33 2023

@author: potato
"""

import pandas as pd
from datetime import date,datetime
import pymysql
import requests
import os
def df_to_dict_univ_region(df)->dict:
    result_dict = {}
    sz1,sz2 = df.shape
    for i in range(sz1):
        if(df.iloc[i,0] in result_dict):
            result_dict[df.iloc[i,0]].add(df.iloc[i,1])
        else:
            temp_set = set()
            result_dict[df.iloc[i,0]] = temp_set
            result_dict[df.iloc[i,0]].add(df.iloc[i,1])
        
        
    
    
    
    
    
    return result_dict

def df_to_dict_topic_qlist(df)->dict:
    result_dict = {}
    df_header = list(df.columns)
    sz1,sz2 = df.shape
    for i in range(sz2-1):
        temp_dict = {}
        #temp_name = df_header[i+1]
        for j in range(sz1):
            temp_set = parse_to_set(df.iloc[j,i+1])
            temp_dict[df.iloc[j,0]] = temp_set
        
        result_dict[df_header[i+1]]=temp_dict
    
    return result_dict
    


def df_to_dict_qlist(df)->dict:
    result_dict = {}
    sz1,_ = df.shape
    for i in range(sz1):
        result_dict[df.iloc[i,0]] = df.iloc[i,1]
        
            
    
    return result_dict


def parse_to_set(ostr:str)->set:
    result_list = ostr.split(",")
    result_set = set(result_list)
    return result_set 


def display_dict(dict1:dict)->dict:
    result_dict = {}
    for k,_ in dict1.items():
        result_dict[k] = k
    
    
    return result_dict
def list_display(list1)->dict:
    result_dict = {}
    for i in range(len(list1)):
        result_dict[list1[i]] = list1[i]
        
    return result_dict
    
    
    
    

def get_qlist_by_cate(qlist:list,qlist_qcontent_dict):
    result_dict = {}
    for i in range(len(qlist)):
        result_dict[qlist_qcontent_dict[qlist[i]]]= qlist_qcontent_dict[qlist[i]]
    
    
    
    return result_dict
    
    

def get_v_count(df):
    return 



def get_univreg_by_school_dict(df):
    sz1,_ = df.shape
    lea_dict = {}
    for i in range(sz1):
        if df.iloc[i,1] not in lea_dict:
            lea_dict[df.iloc[i,1]]= df.iloc[i,0]
        
    return lea_dict
    



def record_login(role):
    
    url = "https://worldtimeapi.org/api/timezone/America/Denver"
    response = requests.get(url)
    result = response.json()
    date_in = result["datetime"]
    date = date_in[0:10]
    time = date_in[11:19]
  

    connection = pymysql.connect(host='database-2.czikup7sd3q9.us-east-2.rds.amazonaws.com',
                             user='admin',
                             password='admintest',
                             database='login_db',
                             charset='utf8mb4',
                             cursorclass=pymysql.cursors.DictCursor)
    cursor = connection.cursor()
    #cursor.execute("use login_db;")
    curr_query = "insert into login_n values ( '"+str(date) +"','"+ str(time) +"','"+role+ "')"

    try:
        cursor.execute(curr_query)
        connection.commit()
        print("Query run succeed")
        """
        cursor.execute("select * from login_n;")
        result1 = cursor.fetchall()
        for row in result1:
            print(row)
        #
        """
    except Exception as error:
        print("There is exception happened:", type(error).__name__,"-",error)

    cursor.close()
    return 

    
    
    
    