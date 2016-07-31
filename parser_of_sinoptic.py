# -*- encoding: utf-8 -*-

"""A small parser of sinoptik.ua with possibility of sending a mail."""
import argparse
import datetime
import smtplib
from urllib.request import urlopen
from urllib.parse import quote

from bs4 import BeautifulSoup


def parsing_of_atguments():
    """Parsing of arguments in command line"""
    parser = argparse.ArgumentParser()
    parser.add_argument("city", help="The city name in which you want to know the weather. Example: ровно", type=str)
    parser.add_argument("sender_email", help="Your email. Example: your_email@gmail.com", type=str)
    parser.add_argument("sender_password", help="Your password. Example: 12qr8789", type=str)
    parser.add_argument("receiver_email", help="Receiver email. Example: receiver_email@gmail.com", type=str)
    parser.add_argument("-sn", dest="smtp_server_name", help="Your SMTP server name. Example: smtp.gmail.com", type=str,
                        default="smtp.gmail.com")
    return parser


def get_html(url):
    """Get the HTML data of requested URL"""
    response = urlopen(url)
    return response.read()


def parse(html):
    """Parsing of data and creating a dictionary of necessary information"""
    soup = BeautifulSoup(html, "html.parser")
    table = soup.find('table', class_='weatherDetails')
    rows = table.find_all('tr')
    new_rows = [rows[1], rows[3], rows[8]]
    cols = [row.find_all('td') for row in new_rows]
    data = []
    for i in range(8):
        data.append({
            'time': cols[0][i].get_text(),
            'temperature': str(cols[1][i].get_text()).rstrip('\xb0'),
            'chance of precipitation': cols[2][i].get_text()
        })
    return data


def formatting_data_for_mail(data):
    """Beautiful formatting data special for mail (making of multi-line string from a dictionary)"""
    now = datetime.datetime.now()
    data_for_sending = '\nWeather in Rivne on {}:\n\n'.format(now.strftime("%d.%m.%Y"))
    for element in data:
        for key, value in element.items():
            data_for_sending += str(key) + ": " + str(element[key]) + "\n"
        data_for_sending += "\n"
    return data_for_sending


def send_to_email(data_for_sending):
    """Send a mail with information of weather to recipient"""
    server = smtplib.SMTP(args.smtp_server_name, 587)
    server.starttls()
    server.login(args.sender_email, args.sender_password)
    server.sendmail(args.sender_email, args.receiver_email, data_for_sending)
    print("Message successfully sent")
    server.close()


if __name__ == '__main__':
    args = parsing_of_atguments().parse_args()
    base_url = 'https://sinoptik.ua{}'.format(quote('/погода-' + args.city))
    data = parse(get_html(base_url))
    data_for_sending = formatting_data_for_mail(data)
    send_to_email(data_for_sending)
