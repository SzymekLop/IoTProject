#!/usr/bin/env python3

import paho.mqtt.client as mqtt
import tkinter
import sqlite3
import time

# The broker name or IP address.
broker = "localhost"
# broker = "127.0.0.1"
# broker = "10.0.0.1"

# The MQTT client.
client = mqtt.Client()



def process_message(client, userdata, message):
    # Decode message.
    # message_decoded = (str(message.payload.decode("utf-8"))).split(".")
    print('got a message:')
    print(message.payload.decode('utf-8'))
    card_id, log_time = str(message.payload.decode('utf-8')).split('@')

    # Print message to console.
    print(log_time + " | " + card_id + " used the RFID card.")
    print(type(card_id))
    connention = sqlite3.connect("employees.db")
    cursor = connention.cursor()
    cursor.execute("SELECT * FROM log WHERE card_id = (?)", [card_id])
    log_entries = cursor.fetchall()
    if len(log_entries) % 2 == 0:
        print('dzien dobry')
    else:
        print('do widzenia')
    # Save to sqlite database.
    connention = sqlite3.connect("employees.db")
    cursor = connention.cursor()
    cursor.execute("INSERT INTO log (card_id, time) VALUES (?, ?)",
                   (card_id, log_time))
    connention.commit()
    connention.close()


def print_log_to_window():
    connention = sqlite3.connect("employees.db")
    cursor = connention.cursor()
    cursor.execute("SELECT * FROM logs")
    log_entries = cursor.fetchall()
    labels_log_entry = []
    print_log_window = tkinter.Tk()

    for log_entry in log_entries:
        labels_log_entry.append(tkinter.Label(print_log_window, text=(
                "On %s, %s used the terminal" % (log_entry[0], log_entry[1]))))

    for label in labels_log_entry:
        label.pack(side="top")

    connention.commit()
    connention.close()

    # Display this window.
    print_log_window.mainloop()




def connect_to_broker():
    # Connect to the broker.
    client.connect(broker, keepalive=600)
    # Send message about conenction.
    client.on_message = process_message
    # Starts client and subscribe.
    client.loop_start()
    client.subscribe("id/card", 2)


def disconnect_from_broker():
    # Disconnet the client.
    client.loop_stop()
    client.disconnect()


def run_receiver():
    connect_to_broker()
    # this
    inp = ""
    while inp != "exit":
        inp = input()
    # or
    disconnect_from_broker()


if __name__ == "__main__":
    run_receiver()
