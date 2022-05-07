#!/usr/bin/python3.8

import datetime
import requests
import json
import csv
import os
import time

date_today = datetime.date.today()
date_arg = str(date_today.day)+ '-' + str(date_today.month) + '-' + str(date_today.year)

dist_inpt = input("Enter the district for which vaccine availability needs to be checked: ")

loc_id = -1
state_url = 'https://cdn-api.co-vin.in/api/v2/admin/location/states?User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.93 Safari/537.36'
state_response = requests.get(state_url)
parse_state_resp = json.loads(state_response.text)['states']
for i in parse_state_resp:
    st_id = i['state_id']
    dist_url = f'https://cdn-api.co-vin.in/api/v2/admin/location/districts/{st_id}'
    dist_respose = requests.get(dist_url)
    parse_dist_resp = json.loads(dist_respose.text)['districts']
    for j in parse_dist_resp:
        if (j['district_name'] == dist_inpt):
            loc_id = j['district_id']
            break

if loc_id == -1:
    print("District not found. Please enter correct name (along with case).")

url=f'https://cdn-api.co-vin.in/api/v2/appointment/sessions/public/calendarByDistrict?district_id={loc_id}&date={date_arg}'

vacc_type = input("Enter the vaccine which needs to be found: ")
need_vacc = vacc_type.upper()

data_list = []
file_exists = True

if not os.path.exists('vacc_log.csv'):
    file_exists = False

out_logfile = open('vacc_log.csv','a',newline='')
csv_writer = csv.writer(out_logfile)
csv_writer.writerow(['Program run on date: ', date_arg])

if not file_exists:
    csv_writer.writerow(['Center name','Vaccine','Min Age','Date','Dose-1','Dose-2'])
    file_exists = True

out_logfile.close()                

while(True):
    for j in range(6):
        curr_date = date_today + datetime.timedelta(j)
        date_arg = str(curr_date.day)+ '-' + str(curr_date.month) + '-' + str(curr_date.year)
        url=f'https://cdn-api.co-vin.in/api/v2/appointment/sessions/public/calendarByDistrict?district_id=312&date={date_arg}'
        
        response = requests.get(url)
        
        out_logfile = open('vacc_log.csv','a',newline='')
        csv_writer = csv.writer(out_logfile)
        csv_writer.writerow(['Timestamp: ', f'{datetime.date.today()}', f'{datetime.datetime.now().hour}:{datetime.datetime.now().minute}:{datetime.datetime.now().second}'])

        if (response.ok) and ('centers' in json.loads(response.text)):
            parsed = json.loads(response.text)['centers']

            if parsed is not None:

                for i in range(len(parsed)):
                    if parsed[i]['sessions'][0]['vaccine'].upper() == need_vacc:
                        for l in range(len(parsed[i]['sessions'])):
                            data_list = []
                            data_list.append(parsed[i]['name'])
                            data_list.append(parsed[i]['sessions'][l]['vaccine'])
                            data_list.append(parsed[i]['sessions'][l]['min_age_limit'])
                            data_list.append(parsed[i]['sessions'][l]['date'])
                            data_list.append(parsed[i]['sessions'][l]['available_capacity_dose1'])
                            data_list.append(parsed[i]['sessions'][l]['available_capacity_dose2'])
                            
                            if parsed[i]['sessions'][l]['available_capacity_dose1'] != 0: 
                                print(f"Available! {parsed[i]['sessions'][l]['available_capacity_dose1']} at {parsed[i]['name']}")
                        csv_writer.writerow(data_list)
    
    csv_writer.writerow([])
    out_logfile.close() 
    time.sleep(900)

csv_writer.writerow([])
csv_writer.writerow([])

out_logfile.close()                
                