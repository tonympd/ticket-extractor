import os
import sys
import email.utils
import re
import csv
from imaplib import IMAP4, IMAP4_SSL
from bs4 import BeautifulSoup
import config
import time
import json


def parse_ticketmaster(msg):

    link_type = 'ticketmaster'

    # First find if its typical format
    if msg.find("table") is not None:

        order = re.search(r'(?<=Order # )[^\s]*', msg.find("table").text).group(0)
        price = re.search(r'(?<=Total: \$)[^\s]*', msg.find("table").text.replace(u'\xa0', " ")).group(0)

        table = msg.find_all("td", {"class": ["mobile-padding25B"]})[0]
        rows = table.find_all("tr")

        band = rows[0].text.strip()
        date_time = rows[1].text.strip()
        date = date_time.split(" • ")[1].strip()
        time = date_time.split(" • ")[2].strip()
        location = rows[2].text.strip()
        section = rows[4].text.strip().replace(u'\xa0', " ")

        try:
            sec = section.split(",")[0].replace("Sec","").strip()
            row = section.split(",")[1].replace("Row", "").strip()
            seat = section.split(",")[2].replace("Seat", "").strip()

        except:
            sec = "NA"
            row = "NA"
            seat = "NA"

        print(sec)

    # Create Gift Card Dictionary
    ticket = {'order': order,
              'band': band,
              'date': date,
              'time': time,
              'venue': location,
              'section_summary': section,
              'section': sec,
              'row': row,
              'seat': seat,
              'price': price}

    return ticket


def parse_axs(msg):

    link_type = 'axs'

    # First find if its typical format
    if msg.find_all("table") is not None:

        order = re.search(r'(?<=confirmation number is )[^\s\.]*', msg.text).group(0)


        table = msg.find_all("table")[1]
        rows = table.find_all("tr")

        price = "0"
        for row in rows:
            if "Grand Total" in row.find_all("td")[0].text:
                price = row.find_all("td")[1].text

        band = rows[0].find("strong").text.strip()
        date_time = re.search(r'(?<=scheduled on )[^\n]*', rows[0].text.strip()).group(0)
        date = date_time.split(" ")[0].strip()
        time = date_time.split(" ")[1].strip() + date_time.split(" ")[2].strip()
        location = rows[0].text.replace(u'\r\n', " ").strip()

        try:

            i = 0
            for r in rows:
                if "Quantity" in r.find_all("td")[0].text:
                    section = rows[i + 2].find_all("td")[0].text
                    sec = rows[i + 2].find_all("td")[3].text
                    row = rows[i + 2].find_all("td")[4].text.replace("\n", "")
                    seat = rows[i + 2].find_all("td")[5].text.replace("\n", "")
                i = i + 1

        except:
            sec = "NA"
            row = "NA"
            seat = "NA"

    # Create Gift Card Dictionary
    ticket = {'order': order,
              'band': band,
              'date': date,
              'time': time,
              'venue': location,
              'section_summary': section,
              'section': sec,
              'row': row,
              'seat': seat,
              'price': price}

    return ticket


def write_header():

    print("Writing Header")

    # Write the details to the CSV
    csv_writer.writerow(["email", "order", "band", "date", "time", "venue", "section_summary", "section", "row", "seat", "price"])


def write_ticket(ticket, email):

    print("Writing ticket")

    # Write the details to the CSV
    csv_writer.writerow([email, ticket['order'], ticket['band'], ticket['date'], ticket['time'], ticket['venue'], ticket['section_summary'], ticket['section'], ticket['row'], ticket['seat'], ticket['price']])

    # Print out the details to the console
    print("FROM {}: {}".format(email, ticket))


##################
# Main Code Logic
##################
if os.name == 'nt':
    sys.stdout = open(sys.stdout.fileno(), mode='w', encoding='utf8', buffering=1)

# Connect to the server
if config.IMAP_SSL:
    mailbox = IMAP4_SSL(host=config.IMAP_HOST, port=config.IMAP_PORT)
else:
    mailbox = IMAP4(host=config.IMAP_HOST, port=config.IMAP_PORT)

# Log in and select the configured folder
mailbox.login(config.IMAP_USERNAME, config.IMAP_PASSWORD)
mailbox.select(config.FOLDER)

# Grab epoch timestamp for SINGLE_CSV_FILE
epoch = str(time.time()).split('.')[0]

if True:
    # Search for matching emails
    status, messages = mailbox.search(None, 'ALL')

    if status == "OK":
        # Convert the result list to an array of message IDs
        messages = messages[0].split()

        if len(messages) < 1:
            # No matching messages, stop
            if config.DEBUG:
                print("No matching messages found for {}, nothing to do.".format(from_email))

        else:

            csv_filename = 'tickets_' + epoch + '.csv'

            with open(csv_filename, 'a', newline='') as csv_file:

                # Start the browser and the CSV writer
                csv_writer = csv.writer(csv_file)
                write_header()

                # For each matching email...
                for msg_id in messages:
                    if config.DEBUG:
                        print("--> Processing message id {}...".format(msg_id.decode('UTF-8')))

                    # Fetch it from the server
                    status, data = mailbox.fetch(msg_id, '(RFC822)')

                    if status == "OK":
                        # Convert it to an Email object
                        msg = email.message_from_bytes(data[0][1])
                        msg_from = msg['From']

                        # Get the HTML body payload.
                        if not msg.is_multipart():
                            msg_html = msg.get_payload(decode=True)
                        else:
                            try:
                                msg_html = msg.get_payload(1).get_payload(decode=True)
                            except IndexError:
                                msg_html = msg.get_payload(0).get_payload(decode=True)

                        # Parse the message
                        msg_parsed = BeautifulSoup(msg_html, 'html.parser')

                        # Determine Message type to parse accordingly
                        # Ticketmaster
                        if "Ticketmaster. All rights reserved." in msg_parsed.text:

                            if config.DEBUG:
                                print('Ticketmaster')

                            ticket = parse_ticketmaster(msg_parsed)

                        elif "AXS Terms of Use" in msg_parsed.text:
                            if config.DEBUG:
                                print('Axs')

                            ticket = parse_axs(msg_parsed)

                        else:
                            print(msg_parsed)
                            print("ERROR: Couldn't determine gift card type")
                            exit()

                        # Write Card to CSV
                        write_ticket(ticket, msg_from)

                    else:
                        print("ERROR: Unable to fetch message {}, skipping.".format(msg_id.decode('UTF-8')))


    else:
        print("FATAL ERROR: Unable to fetch list of messages from server.")

print("")
print("Thank you, come again!")
print("")
