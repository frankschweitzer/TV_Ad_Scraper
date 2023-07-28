from fileinput import filename
from flask import Flask, render_template, request, send_file, send_from_directory, abort, session
from bs4 import BeautifulSoup
import openpyxl
from openpyxl.styles import Font
from datetime import date, datetime, timedelta
from dateutil import parser
import pandas as pd
import io
import os

app = Flask(__name__)

output_file = ""


@app.route('/')
def home():
    return render_template('index1.html')


@app.route('/process', methods=['POST'])
def process():
    file = request.files['file']
    
    # Save the uploaded file
    file.save(file.filename)
    
    # Process the Excel file using your existing code
    main(file)
    
    return 'Processing completed, download the finished excel sheet by moving to: https://fjs-tv-webscrape.herokuapp.com/upload'


app.config["File Complete"] = "/Users/frankschweitzer/Documents/Emily Cadent/TV_Ad_Scraper"
app.config['UPLOADS_FOLDER'] = 'uploads'  # or 'uploads'

@app.route('/upload', methods=['GET'])
def upload():
    try:
        return send_from_directory(app.config["UPLOADS_FOLDER"], "tvDataWebApp.xlsx", as_attachment=True)
    except FileNotFoundError:
        abort(404)
  

def main(filename):
    networks = ["A&E", "AMC", "ANML", "BBCA", "BET", "BETHR", "BRAVO", "CMT", "E!", "FX", "FXM", "FYI", "GOLF", "HGTV", "HIST", "ID", "IFC", "LMN", "MLBN", "NGC", "NTGEO", "OWN", "PARAM", "POP", "SYFY", "TLC", "TNT", "TRV", "USA", "VH1", "VICE"]
    # networks_needed = ["BETHR", "GOLF", "MLBN", "NTGEO", "PARAM", "POP", "SYFY", "TLC", "TRV", "VH1", "VICE"]
    # reading the dates and times needed
    data, networks_needed = read_file(filename)
    desired_map = {}
    
    for i in range(len(data)):
        curr_network_list = desired_map.get(data[i][2], [])
        curr_data = []
        curr_data = [data[i][0], data[i][1]]
        curr_network_list.append(curr_data)
        desired_map[data[i][2]] = curr_network_list
    
    network_to_map = {}
    network_to_times = {}
    for network in networks_needed:
        # need to make a loop, then this returns the map for each network and we can create another map from networks to this map
        map, times_each_day, dates = show_data(network) # returns map from dates to map of shows and times
        network_to_times.update({network: times_each_day})
        network_to_map.update({network: map})
    
    # cleaning up dates to use for indices
    start_day = dates[0]
    end_day = dates[-1]
    start_date = parser.parse(start_day).date()
    end_date = parser.parse(end_day).date()
    date_length = (end_date - start_date).days
    dates = list_dates(start_date, date_length) # list of dates from start to end
    
    # get the shows I want
    results = [[]]
    for network, shows in network_to_map.items():
        times = network_to_times.get(network) # times list
        desired_list = desired_map.get(network) # day will be at first position, time wanted at second
        for curr in desired_list:
            curr_date = parser.parse(curr[0]).date()
            ind = (curr_date - start_date).days
            show_title = locate_show(times, curr[1], curr[0], ind, shows)
            if show_title == None:
                    previous_date = curr_date - timedelta(days=1)
                    formatted_date = previous_date.strftime("%A, %B %d")
                    ind = (previous_date-start_date).days
                    show_title = locate_show(times, "11:59 PM", formatted_date, ind, shows)
            current = []
            date_object = datetime.strptime((curr[0]+", 2023"), "%A, %B %d, %Y")
            formatted_date = date_object.strftime("%m/%d/%Y")
            current.append(formatted_date)
            current.append(curr[1])
            current.append(network)
            current.append(show_title)
            results.append(current)

    # write all the shows and times to file
    results.pop(0)
    output = write_to_file(results)
    return output


# extracting data needed from excel sheet
def read_file(name):
    df = pd.read_excel(name, engine='openpyxl')
    dates = df['Date'].tolist()
    times = df['Scheduled Time'].tolist()
    networks = df['Network'].tolist()
    unique_networks = list(set(networks))
    
    data = []
    for i in range(len(dates)):
        curr_list = []
        tmp_date = datetime.strptime(dates[i], "%m/%d/%Y")
        date_formatted = tmp_date.strftime("%A, %B %d")
        curr_list.append(date_formatted)
        tmp_time = times[i].split(" ")
        time = tmp_time[0][0:-3]+' '+tmp_time[1]
        curr_list.append(time)
        curr_list.append(networks[i])
        data.append(curr_list)
        
    return data, unique_networks
    
# returns a list of the dates that the html sheets cover
def list_dates(start, size):
    dates = []
    for i in range(size+1):
        target_date = start + timedelta(days=i)
        target_day = target_date.strftime("%A, %B %d")
        dates.append(target_day)
    return dates


# returns the show that will be playing at the given time
def locate_show(times, time_wanted, day, index, map):
    if day[-2] == "0":
        day = day[:-2] + day[-1]
    curr_map = {}
    curr_map = map.get(day)
    print(curr_map)
    curr_times = times[index]
    time_wanted = datetime.strptime(time_wanted, '%I:%M %p').time()
    
    start_time = None # might be helpful later on
    time_index = None
    
    for time in curr_times:
        curr_time = datetime.strptime(time, '%I:%M %p').time()
        if curr_time <= time_wanted:
            start_time = curr_time
            time_index = time
        else:
            break
    return curr_map.get(time_index)
    
# writes our inserted data into the file
def write_to_file(results):
    # print to an excel file
    workbook = openpyxl.Workbook()
    bold_font = Font(bold=True)
    sheet = workbook.active
    sheet["A1"] = "Advertiser"
    cell_A1 = sheet["A1"]
    cell_A1.font = bold_font
    sheet["B1"] = "Date"
    cell_B1 = sheet["B1"]
    cell_B1.font = bold_font
    sheet["C1"] = "Time"
    cell_C1 = sheet["C1"]
    cell_C1.font = bold_font
    sheet["D1"] = "Network"
    cell_D1 = sheet["D1"]
    cell_D1.font = bold_font
    sheet["E1"] = "Program"
    cell_E1 = sheet["E1"]
    cell_E1.font = bold_font
    row_num = 2
    for result in results:
        print(result)
        sheet[f"A{row_num}"] = "Red Bull"
        sheet[f"B{row_num}"] = result[0] # insert day
        sheet[f"C{row_num}"] = result[1] # insert time
        sheet[f"D{row_num}"] = result[2] # insert day
        sheet[f"E{row_num}"] = result[3] # insert show
        row_num += 1
    folder_name = 'uploads'
    file_name = 'tvDataWebApp.xlsx'
    file_path = os.path.join(folder_name, file_name)
    workbook.save(file_path)
    

# returns a map of all of the data given by day
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
    # grouping the shows and times by day - but here is where I need to only add the ones needed based on the
    # search and clean parsing I did from reading the excel file
    for curr_shows in shows_by_day:
        curr_times = times_by_day[i]
        curr_map = {}
        
        for j in range(len(curr_shows)):
            curr_map.update({curr_times[j]: curr_shows[j]})
        
        if i < len(days):
            map.update({days[i]: curr_map})
        
        i += 1
    
    return map, times_by_day, days


if __name__ == '__main__':
    app.debug = True
    app.run(host="0.0.0.0", port=5000) # host="0.0.0.0", port=5000 OR debug=True
