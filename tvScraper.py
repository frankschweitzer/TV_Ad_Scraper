from bs4 import BeautifulSoup
import openpyxl
from openpyxl.styles import Font
from datetime import date, datetime, timedelta
from dateutil import parser
import pandas as pd

# opening the page via request but denied - can contact 
# import requests
# url = f"https://www.tvinsider.com/network/{nework}/schedule/"
# response = requests.get(url)
# html_content = response.text
# soup = BeautifulSoup(html_content, 'html.parser')

def main():
    network = "A&E"
    
    desired_time = "12:15 PM"
    
    map, times_each_day, dates = show_data(network) # returns map from dates to map of shwos and times
    
    # cleaning up dates
    start_day = dates[0]
    end_day = dates[-1]
    start_date = parser.parse(start_day).date()
    end_date = parser.parse(end_day).date()
    date_length = (end_date - start_date).days
    dates = list_dates(start_date, date_length) # list of dates from start to end
    
    count = 0
    # printing the show at the desired time for all of the dates
    for date in dates:
        # print(date + ' ' + locate_show(times_each_day, desired_time, date, count, map))
        count+=1
    
    # reading the dates and times needed
    # name = "SampleData.xlsx"
    # data = read_file(name)
    
    # write all the shows and times to file
    write_to_file(map, network)
    

# extracting data needed from excel sheet
# def read_file(name):
    # df = pd.read_excel(name, engine='openpyxl')
    # colA = df['A'].tolist()
    # colB = df['B'].tolist()
    # data = []
    # for i in range(len(colA)):
    #     curr_list = []
    #     curr_list[0] = colA[i]
    #     curr_list[1] = colB[i]
    #     data.append(curr_list)
    # return data
    
    
def list_dates(start, size):
    dates = []
    for i in range(size+1):
        target_date = start + timedelta(days=i)
        target_day = target_date.strftime("%A, %B %d")
        dates.append(target_day)
    return dates

    
def locate_show(times, time_wanted, day, index, map):
    curr_map = map.get(day)
    curr_times = times[index]
    time_wanted = datetime.strptime(time_wanted, '%I:%M %p').time()
    
    start_time = None
    time_index = None
    
    for time in curr_times:
        curr_time = datetime.strptime(time, '%I:%M %p').time()
        if curr_time <= time_wanted:
            start_time = curr_time
            time_index = time
        else:
            break
    return curr_map.get(time_index)
    

def write_to_file(map, network):
    # print to an excel file
    workbook = openpyxl.Workbook()
    bold_font = Font(bold=True)
    sheet = workbook.active
    sheet["A1"] = "Date"
    cell_A1 = sheet["A1"]
    cell_A1.font = bold_font
    sheet["B1"] = "Time"
    cell_B1 = sheet["B1"]
    cell_B1.font = bold_font
    sheet["C1"] = "Network"
    cell_C1 = sheet["C1"]
    cell_C1.font = bold_font
    sheet["D1"] = "Show"
    cell_D1 = sheet["D1"]
    cell_D1.font = bold_font
    row_num = 2
    for key, value in map.items():
        for subkey, subval in value.items():
            sheet[f"A{row_num}"] = key # insert day
            sheet[f"B{row_num}"] = subkey # insert time
            sheet[f"C{row_num}"] = network # insert day
            sheet[f"D{row_num}"] = subval # insert show
            row_num += 1
    workbook.save("tvData.xlsx")


def show_data(network):
    # open page via downloaded html file
    with open(f'{network}.html') as fp:
        soup = BeautifulSoup(fp, 'html.parser')

    # blocking off data by day
    dates = soup.find_all(class_="date")

    days = []
    shows_by_day = [[]]
    times_by_day = [[]]

    # iterate over each date
    for i in range(len(dates)):
        date = dates[i].text
        days.append(date)

        # find the next sibling elements until the next date element
        siblings = dates[i].find_next_siblings()
        curr_block = siblings[0]
        shows_per_day = curr_block.find_all(class_="show-upcoming")
        shows = []
        times = []
        # creating lists of shows and times per day
        for show in shows_per_day:
            times.append(show.time.get_text())
            if show.find(class_="balance-text") == None:
                shows.append(show.h3.get_text()) # tends to be paid programming
            else:
                shows.append(show.find(class_="balance-text").get_text())
        times_by_day.append(times)
        shows_by_day.append(shows)

    times_by_day.pop(0) # remove null list
    shows_by_day.pop(0) # remove null list
    map = {}
    i = 0
    # grouping the shows and times by day
    for curr_shows in shows_by_day:
        curr_times = times_by_day[i]
        curr_map = {}
        
        for j in range(len(curr_shows)):
            curr_map.update({curr_times[j]: curr_shows[j]})
        
        if i < len(days):
            map.update({days[i]: curr_map})
        
        i += 1
    
    return map, times_by_day, days


main()