from bs4 import BeautifulSoup
import json
import requests
import sqlite3
import plotly.plotly as py
import plotly.graph_objs as go

conn = sqlite3.connect("broadwayshows.db")
cur = conn.cursor()


show_lst = []

def set_up_database():
    pre_state = "DROP TABLE IF EXISTS Shows"
    cur.execute(pre_state)
    pre_state2 = "DROP TABLE IF EXISTS ShowTimes"
    cur.execute(pre_state2)
    statement = "CREATE TABLE IF NOT EXISTS Shows (Id INTEGER PRIMARY KEY, Title TEXT, OpeningDate TEXT, PreviewDate TEXT, Address TEXT, Duration INTEGER)"
    cur.execute(statement)
    statement2 = "CREATE TABLE IF NOT EXISTS ShowTimes (Id INTEGER PRIMARY KEY, TitleId INTEGER, [Time] TEXT, WeekDay TEXT, Month TEXT, MonthDay INTEGER, TimeLink TEXT)"
    cur.execute(statement2)
    conn.commit()

CACHE_FNAME = 'cache.json'
try:
    cache_file = open(CACHE_FNAME, 'r')
    cache_contents = cache_file.read()
    CACHE_DICTION = json.loads(cache_contents)
    cache_file.close()
except:
    CACHE_DICTION = {}

def params_unique_combination(baseurl, params):
    alphabetized_keys = sorted(params.keys())
    res = []
    for k in alphabetized_keys:
        res.append("{}-{}".format(k, params[k]))
    return baseurl + "_".join(res)

def make_request_using_cache(baseurl, params= {}, auth = None):
    unique_ident = params_unique_combination(baseurl,params)

    if unique_ident in CACHE_DICTION:
        #print("Getting cached data...")
        return CACHE_DICTION[unique_ident]

    else:
        #print("Making a request for new data...")
        resp = requests.get(baseurl, params, auth=auth)
        CACHE_DICTION[unique_ident] = resp.text
        dumped_json_cache = json.dumps(CACHE_DICTION)
        fw = open(CACHE_FNAME,"w")
        fw.write(dumped_json_cache)
        fw.close()
        return CACHE_DICTION[unique_ident]


url = 'http://www.broadway.com'
title_link = {}
def get_show_lst(category):
    for page in range(1, 6):
        if category == "all_shows":
            baseurl = 'https://www.broadway.com/shows/tickets/?page={}'.format(page)
        else:
            baseurl = 'https://www.broadway.com/shows/tickets/?category={}&page={}'.format(category, page)
        page_text = make_request_using_cache(baseurl)
        page_soup = BeautifulSoup(page_text, 'html.parser')
        lst_shows = page_soup.find('div', class_ = "col-xs-12 col-lg-9 pts ptl-sm ptx-md bg-gray-eee plx-md pll hack-col-border flex-grid__item")
        if lst_shows:
            titles = lst_shows.find_all('div', class_ = "card card--hover card--shadow bg-white mtn")
            for t in titles:
                title_find = t.find('h3')
                title = title_find.find("a").text
                link = title_find.find('a')['href']
                if title not in title_link and link not in title_link:
                    title_link[title] = url+link
    #print(title_link)
    return title_link

class Shows:
    def __init__(self, show, opening, preview, address, runtime):
        self.show = show
        self.opening = opening
        self.preview = preview
        self.address = address
        self.runtime = runtime

    def __str__(self):
        return "{} runs for {}, opening on {}, previewing on {} at {}.".format(self.show, self.runtime, self.opening, self.preview, self.address)



def get_shows(show, time_link = None):
    link_to_show = title_link[show]
    page_text = make_request_using_cache(link_to_show)
    page_soup = BeautifulSoup(page_text, 'html.parser')

    sidebar = page_soup.find('div', class_ = 'display-cell vtop rail-fixed-left_sm border_black_r')

    if sidebar.find('div', class_ = "wht-dk"):
        if len(sidebar.find_all('div', class_ = "wht-dk")) >= 3:
            runtime = sidebar.find_all('div', class_ = "wht-dk")[2].text
        else:
            runtime = None
    else:
        runtime = None

    if sidebar.find_all('div', class_ = "gray-lt font-14"):
        if sidebar.find_all('div', class_ = "wht-dk mbl"):
            preview = sidebar.find_all('div', class_ = "wht-dk mbl")[0].text
        else:
            preview = None
    else:
        preview = None

    if sidebar.find_all('div', class_ = "gray-lt font-14"):
        if len(sidebar.find_all('div', class_ = "wht-dk mbl")) == 1:
            opening = sidebar.find_all('div', class_ = "wht-dk mbl")[0].text
        elif len(sidebar.find_all('div', class_ = "wht-dk mbl")) == 0:
            opening = None
        else:
            opening = sidebar.find_all('div', class_ = "wht-dk mbl")[1].text
    else:
        opening = None

    if sidebar.find('p', class_ = 'wht-dk font-14 lh-norm font-lt mts'):
        address_ = sidebar.find('p', class_ = 'wht-dk font-14 lh-norm font-lt mts').text.strip().replace("\n", " ").replace("  ", "")
    else:
        address_ = None


    y = Shows(show, opening, preview, address_, runtime)
    show_titles = [x.show for x in show_lst]
    if y.show not in show_titles:
        show_lst.append(y)


    statement3 = "INSERT INTO Shows VALUES(?, ?, ?, ?, ?, ?)"
    x = cur.execute(statement3, (None, show, opening, preview, address_, runtime))
    #print((None, show, opening, preview, address_, runtime))
    show_id = "SELECT Id FROM Shows WHERE Title = ?"
    cur.execute(show_id, (show,))
    show_id = cur.fetchone()[0]
    conn.commit()

    show_times = page_soup.find('table')
    if show_times:
        dates_lst = [(index, date.text.strip().replace("\n", " ")) for index, date in enumerate(show_times.find_all('th'))]
        showtimes_by_day = show_times.find("tbody").find_all('td')
        for index, showtimes in enumerate(showtimes_by_day):
            for x in dates_lst[index][1]:
                show_weekday = dates_lst[index][1].split()[0]
                show_month = dates_lst[index][1].split()[1]
                show_monthdate = dates_lst[index][1].split()[2]
            for specific_time in showtimes.find_all("div"):
                if specific_time.find("a"):
                    showing_time = specific_time.find('a', class_ = 'btn btn-bwy btn-bwy_secondary_blue-white pam mhl mvm block').text
                    time_link = specific_time.find("a")["href"]


                    statement4 = "INSERT INTO ShowTimes Values(?, ?, ?, ?, ?, ?, ?)"
                    cur.execute(statement4, (None, show_id, showing_time, show_weekday, show_month, show_monthdate, time_link))
                    conn.commit()

    return runtime, preview, opening

def getShowsByOpeningDate():
    try:
        year_list = []
        cur.execute("SELECT OpeningDate from Shows")
        for row in cur:
            for item in row:
                try:
                    splt = item.split(",")
                    year = splt[1]
                    year_list.append(year)
                except:
                    pass
    except:
        pass
    year_frequency = {year : year_list.count(year) for year in year_list}
    return year_frequency
    conn.commit()

def getRunTimes():
    cur.execute("SELECT Duration from Shows")
    try:
        results = cur.fetchall()
        lengths = []
        for res in results:
            if type(results) == None:
                pass
            else:
                time = res[0]
                minutes = 0
            if "hr" in time or "min" in time:
                try:
                    splt = time.split(',')
                    hr = splt[0][0]
                    min =  splt[1][0:3]
                    t = (int(hr)*60)+int(min)
                    lengths.append(t)
                except:
                    pass
            else:
                pass
    except:
        pass
    length_dict = {"short" : 0, "medium" : 0, "long" : 0}
    for length in lengths:
        if length > 150:
            length_dict["long"] += 1
        elif length > 115:
            length_dict["medium"] += 1
        else:
            length_dict["short"] += 1
    return length_dict

    conn.commit()

def getShowTimes():
    cur.execute("SELECT Duration, ShowTimes.Time from Shows JOIN ShowTimes ON Shows.Id = ShowTimes.TitleId")
    results = cur.fetchall()
    lengths = []
    for res in results:
        time = res[0]
        minutes = 0
        if "hr" in time or "min" in time:
            if len(time.split(",")) >= 2:
                processed = ''.join(ch for ch in time if ch.isdigit() or ch == ",")
                for str_num in processed.split(","):
                    num = int(str_num)
                    if num <= 3:
                        minutes += num*60
                    else:
                        minutes += num
        lengths.append(minutes)
    conn.commit()
    processed_time = []
    for res in results:
        time_of_day = res[1]
        if "AM" in time_of_day:
            processed_time.append(float(time_of_day.replace("AM", "").replace(":", ".")))
        elif "12" in time_of_day and "PM" in time_of_day:
            processed_time.append(float(time_of_day.replace("PM", "").replace(":", ".").replace("AM", "")))
        else:
            processed_time.append(12+float(time_of_day.replace("PM", "").replace(":", ".")))
            #military time
    #print(lengths)
    #print(processed_time)
    return lengths, processed_time

def getShowsByPreviewMonth():
    cur.execute("SELECT PreviewDate from Shows")
    try:
        month_list = []
        for row in cur.fetchall():
            for item in row:
                if type(item) == str:
                    splt = item.split()
                    month = splt[0]
                    month_list.append(month)
                else:
                    pass
    except:
        pass
    conn.commit()
    # month_list = [(tup[0].split(",")[0][:3]) for tup in results if len(tup[0].split(",")) >= 2]
    month_frequency = {month : month_list.count(month) for month in month_list}
    return month_frequency

def load_help_text():
    with open('help.txt') as f:
        return f.read()

def interactive_prompt():
    help_text = load_help_text()
    response = ''
    # for category, note that if they are doing more than one word like off broadway, you need to write off-broadway
    while response != 'exit':
        response = input('Enter a Command for instructions or help: ')
        words_lst = response.split()
        if response == "exit":
            print("Bye!")

        elif response == 'help':
            print(help_text)
            continue
            
        item = 1
        if response[:8] == "category":
            set_up_database()
            shows = []

            results = get_show_lst(words_lst[1])
            for r in results:
                shows.append(r)
                get_shows(r)
            print('\nShows: ')

            for s in shows:
                print(item, s)
                item +=1

        if response[:4] == "info":
            info = []
            if len(shows) == 0:
                print("Get theater list first")
            else:
                try:
                    print('\nInfo: ')
                    i = shows[int(words_lst[1])-1]
                    new_results = get_shows(i)
                    print("Runtime: " + new_results[0] + "\nPreview Date: " + new_results[1] + "\nOpening Date: " + new_results[2])

                except:
                    print("Sorry, no information available.")
                    continue

                for i in info:
                    print(item, i)
                    item +=1

        if response[:1] == "1":
            data = getShowsByOpeningDate()

            plotly_data = [go.Bar(
                x=list(data.keys()),
                y=list(data.values())
            )]

            py.plot(plotly_data, filename='shows_by_opening_year')

        if response[:1] == "2":
            data = getRunTimes()
            plotly_data = [go.Pie(
                labels=list(data.keys()),
                values=list(data.values())
            )]

            py.plot(plotly_data, filename='shows_by_runtime')

        if response[:1] == "3":
            durations, starttimes = getShowTimes()

            plotly_data = [go.Scatter(
                y=durations,
                x=starttimes,
                mode = 'markers'
            )]

            py.plot(plotly_data, filename='shows_by_show_and_run_time')

        if response[:1] == "4":
            data = getShowsByPreviewMonth()

            plotly_data = [go.Bar(
                x=list(data.keys()),
                y=list(data.values())
            )]

            py.plot(plotly_data, filename='shows_by_preview_month')


if __name__ == "__main__":
    interactive_prompt()
