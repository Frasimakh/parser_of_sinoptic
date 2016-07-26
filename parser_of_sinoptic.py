# -*- encoding: utf-8 -*-

import csv
import smtplib
import datetime
from urllib.request import urlopen

from bs4 import BeautifulSoup

BASE_URL = 'https://sinoptik.ua/%D0%BF%D0%BE%D0%B3%D0%BE%D0%B4%D0%B0-%D1%80%D0%BE%D0%B2%D0%BD%D0%BE'
SMTP_SERVER_NAME = "smtp.gmail.com"
SENDER_EMAIL = "your_email@gmail.com"
SENDER_PASSWORD = "********"
RECEIVER_EMAIL = "receiver_email@gmail.com"


def get_html(url):
    """Get the HTML data of requested URL"""
    response = urlopen(url)
    return response.read()


def parse(html):
    """Parsing of data"""
    soup = BeautifulSoup(html, "html.parser")
    table = soup.find('table', class_='weatherDetails')
    rows = table.find_all('tr')
    new_rows = []
    new_rows.append(rows[1])
    new_rows.append(rows[3])
    new_rows.append(rows[8])
    cols = []
    for row in new_rows:
        cols.append(row.find_all('td'))
    data = []
    for i in range(8):
        data.append({
            'time': cols[0][i].get_text(),
            'temperature': str(cols[1][i].get_text()).rstrip('\xb0'),
            'chance of precipitation': cols[2][i].get_text()})
    return data


def save(projects, path):
    """Save the data of weather in csv-file"""
    with open(path, 'w') as csvfile:
        text_writer = csv.writer(csvfile, delimiter=';')

        text_writer.writerow(('Time', 'Temperature', 'Chance of precipitation'))
        text_writer.writerows(
            (project['time'], ''.join(project['temperature']), project['chance of precipitation']) for project
            in projects
        )
        csvfile.close()


def formatting_data_for_mail(data):
    """Formatting data special for mail"""
    data_for_sending = '\nWeather in Rivne on {}:\n\n'.format(now.strftime("%d.%m.%Y"))
    for element in data:
        for key, value in element.items():
            data_for_sending += str(key) + ": " + str(element[key]) + "\n"
        data_for_sending += "\n"
    return data_for_sending


def send_to_email(data_for_sending):
    """Send a mail with data to recipient"""
    server = smtplib.SMTP(SMTP_SERVER_NAME, 587)
    server.starttls()
    server.login(SENDER_EMAIL, SENDER_PASSWORD)
    server.sendmail(SENDER_EMAIL, RECEIVER_EMAIL, data_for_sending)
    server.close()


if __name__ == '__main__':
    now = datetime.datetime.now()
    data = parse(get_html(BASE_URL))
    save(data, 'data.csv')
    data_for_sending = formatting_data_for_mail(data)
    send_to_email(data_for_sending)
