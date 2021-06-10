"""
Using the serial communication of the arduino to import voltage data for the AFE4490 Module
"""

# Imports various modules to be used in the code
import sys
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib import style
import random
import csv
from datetime import datetime
from datetime import date
import tkinter as tk
from tkinter import *
from tkinter import ttk
from PIL import Image, ImageTk
from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg,
                                               NavigationToolbar2Tk)
from matplotlib.figure import Figure
import os

# Enter Desired Filename
fileName = "Finger Probe Voltage_002.csv"  # name of CSV file generated

# Sets current directory for file management
current_dir = os.getcwd()
print(current_dir)

# Select com port for arduino
# com = '/dev/ttyACM0' #comp port for arduino on Jetson
# com = 'COM9'  # com port for windows
# com = 'COM5'  # com port for windows tablet


def getcom():
    global com
    com = COMt.get()
    print("com port =", com)


def ComSelect():
    """
    Creates combo box selection of com port
    """
    global COMt
    COMt = StringVar()
    combobox = ttk.Combobox(comframe, textvariable=COMt)
    combobox.grid(row=1, column=0)
    combobox.config(values=('COM1', 'COM2', 'COM3', 'COM4',
                    'COM5', 'COM6', 'COM7', 'COM8', 'COM9', 'COM10'))
    COMt.set('COM9')


# To initialize tkinter, we have to create a Tk root widget, which is a window with a title bar and other decoration provided
# by the window manager. The root widget has to be created before any other widgets and there can only be one root widget.
root = tk.Tk()

# Gives title to GUI
root.title("Dye Densiometer GUI")

# Brings in pngs for GUI buttons
# stop_image = Image.open(
# 'G:\My Drive\## Elliott Lab Shared Files\Devices\Dye Densitometer\Jetson NX Development\Code\VS Code\Images\stop3.bmp')
stop_image = Image.open(
    'stop3.bmp')
# The (20, 20) is (height, width)
stop_image = stop_image.resize((20, 20), Image.ANTIALIAS)
end_button = ImageTk.PhotoImage(stop_image)

# start_image = Image.open(
# 'G:\My Drive\## Elliott Lab Shared Files\Devices\Dye Densitometer\Jetson NX Development\Code\VS Code\Images\start3.bmp')
start_image = Image.open(
    'start3.bmp')
# The (20, 20) is (height, width)
start_image = start_image.resize((20, 20), Image.ANTIALIAS)
record_button = ImageTk.PhotoImage(start_image)

# creates gui figure
fig = Figure(figsize=(5, 4), dpi=100)
canvas = FigureCanvasTkAgg(fig, master=root)

"""
For Windows only
"""
x = 1
prevran = False


def openserial():
    # Intialize Serial Port
    if prevran == False:
        getcom()  # sets COM port to whatever is selected in the combobox
        import serial  # Imports PySerial Library
        global arduino
        # arduino = serial.Serial(com, 57600)  # , timeout=.1)
        # arduino = serial.Serial(com, 115200)  # , timeout=.1)
        try:
            # , timeout=.1), sets baud rate
            # arduino = serial.Serial(com, 57600)
            arduino = serial.Serial(com, 250000)
        except:  # NameError:  # exception arduino not defined
            show_error("Wrong com port selected")

    # Check Serial Port is Open
    if arduino.is_open == True:
        print("\nAll right, serial port now open. Configuration:\n")
        print(arduino, "\n")  # print serial parameters

    # display the data to the terminal
    getData = str(arduino.readline())
    data = getData[0:][:-2]
    print(data)


# Variables to store incoming data
xs = []  # store sample numbers here (n)
ys = []  # store RED temp values here
y2s = []  # Store IR temp values here
y3s = []  # Store RED ambient values here
y4s = []  # Store IR ambient values here
y5s = []  # Store RED raw - RED ambient values here
y6s = []  # Store IR raw - IR ambient values here


def CreateDateTime():
    # Create date and time variable dd/mm/YY H: M: S
    global now
    now = datetime.now()
    print(now)
    global dt_string
    dt_string = [
        f'{now.month}/{now.day}/{now.year} {now.hour}:{now.minute}:{now.second}']
    print("date and time =", dt_string)


# setting up csv file for arduino data
fields = ['Ch : RED', 'Ch : RED AMBIENT', 'Ch : IR',
          'Ch: IR AMBIENT', 'Ch : RED - RED AMBIENT', 'Ch : IR - IR AMBIENT']


def writedata(redraw, irraw, redtemp, irtemp, redtot, irtot):
    """
    Writes data to CSV
    """
    # Sets data directory for data storage
    dat_dir = ''.join([current_dir, "/Data"])
    print(dat_dir)
    os.chdir(dat_dir)
    print(os.getcwd)

    with open(fileName, 'w', newline='') as f:
        # creating a csv writer object
        wc = csv.writer(f)

        # Write Field Names
        wc.writerow(dt_string)
        wc.writerow(['Volts'])
        wc.writerow(fields)
        print("Created File")

    with open(fileName, 'a', newline='') as f:
        # creating a csv writer object
        wc = csv.writer(f)

        for i in range(len(ys)):
            irow = [redraw[i], irraw[i], redtemp[i],
                    irtemp[i], redtot[i], irtot[i]]
            wc.writerow(irow)


def stop_preview():
    global running
    running = False
    # show_message("Data from Preview, close windows to collect data")
    progressbar.stop()
    new_message("")

    root.quit()
    global prevtrue
    prevtrue = False
    global prevran
    prevran = True

    plotdata()


running = False
SampleCount = 0
prevtrue = False


def dataread():
    """
    This function reads and stores the SPI data
    """
    global prevtrue
    if running:
        # Aquire and parse data from serial port
        line = arduino.readline()[:-2]
        line_as_list = line.split(b',')
        count = line_as_list[0]

        try:
            if len(line_as_list) != 4:  # Verifies that serial data is voltage values
                raise Exception
                # print("line as list = ", line_as_list)

        except Exception:
            print("skipped ", count)

        else:
            # i = int(line_as_list[0])
            REDtemp = line_as_list[0]
            IRtemp = line_as_list[1]
            REDamb = line_as_list[2]
            IRamb = line_as_list[3]

            REDtemp_as_list = REDtemp.split(b'\n')
            IRtemp_as_list = IRtemp.split(b'\n')
            REDamb_as_list = REDamb.split(b'\n')
            IRamb_as_list = IRamb.split(b'\n')

            try:
                REDtemp_float = float(REDtemp_as_list[0])
                IRtemp_float = float(IRtemp_as_list[0])
                REDamb_float = float(REDamb_as_list[0])
                IRamb_float = float(IRamb_as_list[0])

                REDminus_float = REDtemp_float - REDamb_float
                IRminus_float = IRtemp_float - IRamb_float
            except Exception as err:
                print(err)
            else:
                # Add x and y to lists
                global SampleCount
                SampleCount += 1
                # print("i =", SampleCount)

                xs.append(SampleCount)
                ys.append(REDtemp_float)
                y2s.append(IRtemp_float)
                y3s.append(REDamb_float)
                y4s.append(IRamb_float)
                y5s.append(REDminus_float)
                y6s.append(IRminus_float)
                # print('Sample # = ', SampleCount, ', IR Raw = ',
                #   IRtemp_float, ', RED Raw = ', REDtemp_float)
    if prevtrue:
        # progressbar.step(1)
        if SampleCount == 1500:
            stop_preview()
            # root.quit()
            # prevtrue = False

    root.after(1, dataread)


def plotdata():
    """
    Plots the data after it has been collected for verification
    """
    fig2, ax = plt.subplots(nrows=1)
    plt.plot(xs[5:-1], y5s[5:-1], label="RED Raw - Ambient")
    plt.plot(xs[5:-1], y6s[5:-1], label="IR Raw - Ambient")

    plt.xticks(rotation=45, ha='right')
    plt.subplots_adjust(bottom=0.30)
    plt.ylabel('Voltage')
    plt.xlabel('Sample #')
    plt.legend(loc='lower left')

    # fig3, ax = plt.subplots(nrows=1)
    # plt.plot(xs[5:-1], y3s[5:-1], label="RED Ambient")
    # plt.plot(xs[5:-1], y4s[5:-1], label="IR Ambient")

    # # Format plot
    # plt.xticks(rotation=45, ha='right')
    # plt.subplots_adjust(bottom=0.30)
    # plt.ylabel('Voltage')
    # plt.xlabel('Sample #')
    # plt.legend(loc='lower left')

    plt.tight_layout()
    plt.show()


def createfilename(patID, injID):
    """
    Creates filename from user input and datetime
    """
    fn_string = [
        f'{patID}_{injID}_{now.year}{now.month}{now.day}_{now.hour}{now.minute}{now.second}.csv']

    # fileName = patID + "_" + injID + "_" + now.year + now.
    print("filename =", fn_string)
    fn_string = ' '.join(map(str, fn_string))

    global fileName
    fileName = fn_string


cfn = False
fncreated = False


def dataentry():
    """
    Creates widget to bring in user input for Patient and Injection ID
    """
    def retrieve():
        CreateDateTime()
        patID = my_entry.get()
        injID = my_entry2.get()
        print(patID)
        print(injID)
        cfn = True
        if cfn:
            createfilename(patID, injID)
            global fncreated
            fncreated = True

    # sets the size of the GUI & prevents user from being able to resize
    root.geometry("450x200")
    root.resizable(False, False)

    frame = Frame(root)
    frame.grid()

    my_entry = Entry(IDframe, width=25)
    my_entry.insert(0, 'Patient ID (eg. DH-xxx)')
    my_entry.grid(row=1, column=0, padx=5, pady=5)

    my_entry2 = Entry(IDframe, width=25)
    my_entry2.insert(0, 'Injection ID (eg. ICG-xx)')
    my_entry2.grid(row=2, column=0, padx=5, pady=5)
    submitbutton = Button(IDframe, text="Submit", command=retrieve)
    submitbutton.grid(row=1, column=1)


def show_error(text):
    tk.messagebox.showerror("Error", text)


def show_message(txt):
    # shows a message in the GUI
    global msg
    msg = ttk.Label(root, text=txt)
    msg.grid(row=7, column=0)


def new_message(txt):
    # Reconfigures message from GUI to allow new message
    global msg
    msg.config(text=txt)


def stop_collection():
    """
    Button to stop data collection & export collected data to CSV with timestamp
    """
    new_message("Data Collection complete")
    progressbar.stop()

    global running
    running = False

    writedata(ys, y3s, y2s, y4s, y5s, y6s)
    print("filename = ", fileName)
    plotdata()


def start_collection():
    """
    Defines the command for starting the data collection
    """
    global prevran
    if fncreated:
        if prevran:  # checks to see if the preview was run
            new_message("Data Collection in Progress")

            # If a preview was run, clears data from previous collection
            global SampleCount, xs, ys, y2s, y3s, y4s, y5s, y6s
            SampleCount = 0
            xs = []   # store sample numbers here (n)
            ys = []   # store RED temp values here
            y2s = []  # Store IR temp values here
            y3s = []  # Store RED ambient values here
            y4s = []  # Store IR ambient values here
            y5s = []  # Store RED raw - RED ambient values here
            y6s = []  # Store IR raw - IR ambient values here

        else:
            show_message("Data Collection in Progress")

        progressbar.config(mode='indeterminate')
        try:
            openserial()
        except:
            print("Serial Already Open")
        progressbar.start()
        global running
        running = True

        prevran = True

        # Re-enters main loop if it was quit via preview button
        root.after(1, dataread)  # After 1 millisecond, call scanning
        root.mainloop()

    else:
        show_error("Enter Patient ID and Injection ID First")


def preview_data():
    """
    Creates a preview of the Data
    """
    # progressbar.config(mode='determinate', maximum=1500, value=1)
    show_message("Collecting Data for Preview")
    progressbar.config(mode='indeterminate')
    progressbar.start()
    global running
    running = True
    global prevtrue
    prevtrue = True
    openserial()


# Creates a Frame for Selections
selframe = ttk.Frame(root)
selframe.grid(row=0, column=0)

# Creates COM Port Selection Frame
comframe = ttk.Frame(selframe)
comframe.grid(row=0, column=0, padx=10)
commsg = ttk.Label(comframe, text='Select correct COM Port:',
                   font=('Arial', 10, 'bold'))
commsg.grid(row=0, column=0)

# Creates the Patient ID and Injection ID Entry Frame
IDframe = ttk.Frame(selframe)
IDframe.grid(row=0, column=2, pady=5)
IDmsg = ttk.Label(
    IDframe, text="""Enter ID for Patient & Injection 
    then click \'submit\'""", font=('Arial', 10, 'bold'))
IDmsg.grid(row=0, column=0)


# Places widgets into the the GUI
ComSelect()
dataentry()


# Creates frame for preview, start and stop buttons in GUI
frame = ttk.Frame(root)
frame.grid(row=3, column=0, rowspan=3)

# Creates a Preview Button for Previewing the Data
preview_button = tk.Button(frame, text="Preview", fg="white", bg="black",
                           command=preview_data, font=('Arial', 18))

# Create a start button, passing two options:
start_button = tk.Button(frame, text="Start", fg="green",
                         command=start_collection, font=('Arial', 18), image=record_button)
start_button.config(compound='left')

# Create a stop button, passing two options:
stop_button = tk.Button(frame, text="Stop", fg="red",
                        command=stop_collection, font=('Arial', 18), image=end_button)
stop_button.config(compound='left')

# Creates a progress bar
progressbar = ttk.Progressbar(root, orient=HORIZONTAL, length=200)

# Adds start and stop buttons, and progressbar to the frame
preview_button.grid(row=0, column=0)
start_button.grid(row=0, column=1)
stop_button.grid(row=0, column=2)
progressbar.grid(row=6, column=0)
progressbar.config(mode='indeterminate')

# Enters into the Tkinter event loop to make window appear:
root.after(1, dataread)  # After 1 millisecond, call scanning
root.mainloop()
