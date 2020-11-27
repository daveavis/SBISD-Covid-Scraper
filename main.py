import requests
import pandas as pd
from bs4 import BeautifulSoup as bs
import dateutil.parser as dparser
import os
from datetime import datetime

USER_AGENT = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/44.0.2403.157 Safari/537.36"
# US english
LANGUAGE = "en-US,en;q=0.5"

def get_soup(url):
  """Constructs and returns a soup using the HTML content 'url' passed"""
  # initialize a session
  session = requests.Session()
  # set the User-Agent as a regular browser
  session.headers['User-Agent'] = USER_AGENT
  # request for english content (optional)
  session.headers['Accept-Language'] = LANGUAGE
  session.headers['Content-Language'] = LANGUAGE
  #make the request
  html = session.get(url)
  # return the soup
  return bs(html.content, "html.parser")

def get_all_tables(soup):
  """Extracts and returns all tables in a soup object"""
  return soup.find_all("table")

def get_table_headers(table):
  """Given a table soup, returns all the headers."""
  headers = []
  for th in table.find("tr").find_all("th"):
    headers.append(th.text.strip())
  return headers

def get_table_rows(table):
  """Given a table, returns all its rows"""
  rows = []
  for tr in table.find_all("tr")[1:]:
    cells = []
    # grab all the th tags in the table row
    ths = tr.find_all("th")
    for th in ths:
      cells.append(th.text.strip())
    # grab all the td tags in the table row
    tds = tr.find_all("td")
    for td in tds:
      cells.append(td.text.strip())
    rows.append(cells)
  #print(rows)
  return rows

def get_update_date(soup):
  update_date = ""
  ems = soup.find_all("em")
  """"
  for em in ems:
    if em.find("Last Updated") != -1:  # why doesn't this work?
  """
  #print(ems[1])
  update_date = dparser.parse(ems[1], fuzzy = True)
  print('Last Update: ', update_date)
  return update_date

def save_as_csv(table_name, headers, rows):
  # if the file does not exist write headers, otherwise don't
  # if the update date is already in the table then don't update (weekends)
  pd.DataFrame(rows, columns=headers).to_csv(table_name, index = False)
  # mode = 'a' to append

def write_files(headers, rows, update_date):
  '''
  Write one file per campus containing a header row,
  and columns for date, staff, students, total
  '''
  for row in rows:
    csv_dir = './csvs/'
    if not os.path.exists(csv_dir):
      os.makedirs(csv_dir)
    filename = csv_dir + row[0] + '.csv'
    need_headers = False
    start_date = ''
    last_date = ''
    try:
      with open(filename, mode='r') as f:
        lines = f.readlines()
        #print(lines)
        start_date = lines[1][:lines[1].find(' ')]
        end_of_date = lines[-1].find(',')
        last_date = lines[-1][:end_of_date]
    except IOError:
      #print('File ' + filename + ' not accessible')
      need_headers = True
    with open(filename, mode='a') as f:
      if need_headers:
        f.write('Date,Days After Start,' + headers[1] + ',' + headers[2] + ',' + headers[3] + '\n')
      #end_of_date = lines[-1].find(',')
      #last_date = lines[-1][:end_of_date]
      #print('last_date = ' + last_date)
      #print('update_date = ' + str(update_date))
      if start_date == '':
        day = 0
      else:
        #print('start_date = ' + str(start_date))
        #print('update_date = ' + str(update_date))
        d1 = datetime.strptime(start_date, "%Y-%m-%d")
        d2 = datetime.strptime(str(update_date)[:str(update_date).find(' ')], "%Y-%m-%d")
        day = abs((d2 - d1).days)

      if last_date != str(update_date):
        f.write(str(update_date) + ',' + str(day) + ',' + row[1] + ',' + row[2] + ',' + row[3] + '\n')
      

def main(url):
  # get the soup
  soup = get_soup(url)
  last_updated = get_update_date(soup)
  # extract all the tables from the web page
  tables = get_all_tables(soup)
  #print("[+] Found a total of " + str(len(tables)) + " tables.")
  # iterate over all tables
  for i, table in enumerate(tables, start=1):
    # get the table headers
    headers = get_table_headers(table)
    # get all the rows of the table
    rows = get_table_rows(table)
    # save table as a csv file
    #table_name = f"table-{i}"
    #print(f"[+] Saving {table_name}")
    #save_as_csv(table_name, headers, rows)
    write_files(headers, rows, last_updated)
  #print(last_updated)
  #print(headers)
  #print(rows)

if __name__ == "__main__":
  url = "https://covid19.springbranchisd.com/dashboard"
  main(url)  