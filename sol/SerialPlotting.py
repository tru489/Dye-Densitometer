#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun May  9 09:55:24 2021
@author: thomasusherwood
"""

import matplotlib.pyplot as plt
import csv
from datetime import datetime
import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
import serial
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg,
                                               NavigationToolbar2Tk)
import os


class SerialPlotting:
    def __init__(self, filename):
        self.fileName = filename
        self.COMt = None
        self.com = None
        self.now = None
        self.dt_string = None
        # Variables to store incoming data
        self.xs = []  # store sample numbers here (n)
        self.ys = []  # store RED temp values here
        self.y2s = []  # Store IR temp values here
        self.y3s = []  # Store RED ambient values here
        self.y4s = []  # Store IR ambient values here
        self.y5s = []  # Store RED raw - RED ambient values here
        self.y6s = []  # Store IR raw - IR ambient values here
        self.running = False
        self.prevtrue = False
        self.prevran = False
        self.cfn = False
        self.fncreated = False
        self.msg = None
        self.progressbar = None
        self.SampleCount = 0
        # setting up csv file for arduino data
        self.fields = ['Ch : RED', 'Ch : RED AMBIENT', 'Ch : IR',
                       'Ch: IR AMBIENT', 'Ch : RED - RED AMBIENT', 'Ch : IR - IR AMBIENT']
        # Sets current directory for file management
        self.current_dir = os.getcwd()

        # To initialize tkinter, we have to create a Tk root widget, which is a window
        # with a title bar and other decoration provided by the window manager. The
        # root widget has to be created before any other widgets and there can only
        # be one root widget.
        self.root = tk.Tk()

    def getcom(self):
        self.com = self.COMt.get()
        print("com port =", self.com)

    def ComSelect(self, comframe):
        """
        Creates combo box selection of com port
        """
        self.COMt = tk.StringVar()
        combobox = ttk.Combobox(comframe, textvariable=self.COMt)
        combobox.grid(row=1, column=0)
        combobox.config(values=('COM1', 'COM2', 'COM3', 'COM4',
                        'COM5', 'COM6', 'COM7', 'COM8', 'COM9', 'COM10'))
        self.COMt.set('COM9')

    def openserial(self):
        # Intialize Serial Port
        if self.prevran == False:
            self.getcom()  # sets COM port to whatever is selected in the combobox
            global arduino
            # arduino = serial.Serial(com, 57600)  # , timeout=.1)
            # arduino = serial.Serial(com, 115200)  # , timeout=.1)
            try:
                # , timeout=.1), sets baud rate
                # arduino = serial.Serial(com, 57600)
                arduino = serial.Serial(self.com, 250000)
            except:  # NameError:  # exception arduino not defined
                self.show_error("Wrong com port selected")

        # Check Serial Port is Open
        if arduino.is_open == True:
            print("\nAll right, serial port now open. Configuration:\n")
            print(arduino, "\n")  # print serial parameters

        # display the data to the terminal
        getData = str(arduino.readline())
        data = getData[0:][:-2]
        print(data)

    def CreateDateTime(self):
        # Create date and time variable dd/mm/YY H: M: S
        self.now = datetime.now()
        print(self.now)
        self.dt_string = [
            f'{self.now.month}/{self.now.day}/{self.now.year} ' +
            f'{self.now.hour}:{self.now.minute}:{self.now.second}']
        print("date and time =", self.dt_string)

    def writedata(self, redraw, irraw, redtemp, irtemp, redtot, irtot):
        """
        Writes data to CSV
        """
        # Sets data directory for data storage
        dat_dir = self.current_dir + "/Data"
        print(dat_dir)
        os.chdir(dat_dir)
        print(os.getcwd)

        with open(self.fileName, 'w', newline='') as f:
            # creating a csv writer object
            wc = csv.writer(f)

            # Write Field Names
            wc.writerow(self.dt_string)
            wc.writerow(['Volts'])
            wc.writerow(self.fields)
            print("Created File")

        with open(self.fileName, 'a', newline='') as f:
            # creating a csv writer object
            wc = csv.writer(f)

            for i in range(len(self.ys)):
                irow = [redraw[i], irraw[i], redtemp[i],
                        irtemp[i], redtot[i], irtot[i]]
                wc.writerow(irow)

    def stop_preview(self):
        self.running = False
        # show_message("Data from Preview, close windows to collect data")
        self.progressbar.stop()
        self.new_message("")

        self.root.quit()
        self.prevtrue = False
        self.prevran = True

        self.plotdata()

    def dataread(self):
        """
        This function reads and stores the SPI data
        """
        if self.running:
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

                    self.SampleCount += 1
                    # print("i =", SampleCount)

                    self.xs.append(self.SampleCount)
                    self.ys.append(REDtemp_float)
                    self.y2s.append(IRtemp_float)
                    self.y3s.append(REDamb_float)
                    self.y4s.append(IRamb_float)
                    self.y5s.append(REDminus_float)
                    self.y6s.append(IRminus_float)
                    # print('Sample # = ', SampleCount, ', IR Raw = ',
                    #   IRtemp_float, ', RED Raw = ', REDtemp_float)
        if self.prevtrue:
            # progressbar.step(1)
            if self.SampleCount == 1500:
                self.stop_preview()
                # root.quit()
                # prevtrue = False

        self.root.after(1, self.dataread)

    def plotdata(self):
        """
        Plots the data after it has been collected for verification
        """
        fig2, ax = plt.subplots(nrows=1)
        plt.plot(self.xs[5:-1], self.y5s[5:-1], label="RED Raw - Ambient")
        plt.plot(self.xs[5:-1], self.y6s[5:-1], label="IR Raw - Ambient")

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

    def createfilename(self, patID, injID):
        """
        Creates filename from user input and datetime
        """
        fn_string = [
            f'{patID}_{injID}_{self.now.year}{self.now.month}{self.now.day}' +
            f'_{self.now.hour}{self.now.minute}{self.now.second}.csv']

        # fileName = patID + "_" + injID + "_" + now.year + now.
        print("filename =", fn_string)
        fn_string = ' '.join(map(str, fn_string))

        global fileName
        fileName = fn_string

    def dataentry(self, IDframe):
        """
        Creates widget to bring in user input for Patient and Injection ID
        """
        def retrieve():
            self.CreateDateTime()
            patID = my_entry.get()
            injID = my_entry2.get()
            print(patID)
            print(injID)
            self.cfn = True
            if self.cfn:
                self.createfilename(patID, injID)
                self.fncreated = True

        # sets the size of the GUI & prevents user from being able to resize
        self.root.geometry("450x200")
        self.root.resizable(False, False)

        frame = tk.Frame(self.root)
        frame.grid()

        my_entry = tk.Entry(IDframe, width=25)
        my_entry.insert(0, 'Patient ID (eg. DH-xxx)')
        my_entry.grid(row=1, column=0, padx=5, pady=5)

        my_entry2 = tk.Entry(IDframe, width=25)
        my_entry2.insert(0, 'Injection ID (eg. ICG-xx)')
        my_entry2.grid(row=2, column=0, padx=5, pady=5)
        submitbutton = tk.Button(IDframe, text="Submit", command=retrieve)
        submitbutton.grid(row=1, column=1)

    def show_error(self, text):
        tk.messagebox.showerror("Error", text)

    def show_message(self, txt):
        # shows a message in the GUI
        self.msg = ttk.Label(self.root, text=txt)
        self.msg.grid(row=7, column=0)

    def new_message(self, txt):
        # Reconfigures message from GUI to allow new message
        self.msg.config(text=txt)

    def stop_collection(self):
        """
        Button to stop data collection & export collected data to CSV with timestamp
        """
        self.new_message("Data Collection complete")
        self.progressbar.stop()

        self.running = False

        self.writedata(self.ys, self.y3s, self.y2s, self.y4s, self.y5s,
                       self.y6s)
        print("filename = ", fileName)
        self.plotdata()

    def start_collection(self):
        """
        Defines the command for starting the data collection
        """
        if self.fncreated:
            if self.prevran:  # checks to see if the preview was run
                self.new_message("Data Collection in Progress")

                # If a preview was run, clears data from previous collection
                self.SampleCount = 0
                self.xs = []   # store sample numbers here (n)
                self.ys = []   # store RED temp values here
                self.y2s = []  # Store IR temp values here
                self.y3s = []  # Store RED ambient values here
                self.y4s = []  # Store IR ambient values here
                self.y5s = []  # Store RED raw - RED ambient values here
                self.y6s = []  # Store IR raw - IR ambient values here

            else:
                self.show_message("Data Collection in Progress")

            self.progressbar.config(mode='indeterminate')
            try:
                self.openserial()
            except:
                print("Serial Already Open")
            self.progressbar.start()
            self.running = True

            self.prevran = True

            # Re-enters main loop if it was quit via preview button
            # After 1 millisecond, call scanning
            self.root.after(1, self.dataread)
            self.root.mainloop()

        else:
            self.show_error("Enter Patient ID and Injection ID First")

    def preview_data(self):
        """
        Creates a preview of the Data
        """
        # progressbar.config(mode='determinate', maximum=1500, value=1)
        self.show_message("Collecting Data for Preview")
        self.progressbar.config(mode='indeterminate')
        self.progressbar.start()
        self.running = True
        self.prevtrue = True
        self.openserial()

    def start_GUI(self):
        print(self.current_dir)

        # Select com port for arduino
        # com = '/dev/ttyACM0' #comp port for arduino on Jetson
        # com = 'COM9'  # com port for windows
        # com = 'COM5'  # com port for windows tablet

        # Gives title to GUI
        self.root.title("Dye Densiometer GUI")

        # Brings in pngs for GUI buttons
        # stop_image = Image.open(
        # 'G:\My Drive\## Elliott Lab Shared Files\Devices\Dye Densitometer
        # \Jetson NX Development\Code\VS Code\Images\stop3.bmp')
        stop_image = Image.open('stop3.bmp')

        # The (20, 20) is (height, width)
        stop_image = stop_image.resize((20, 20), Image.ANTIALIAS)
        end_button = ImageTk.PhotoImage(stop_image)

        # start_image = Image.open(
        # 'G:\My Drive\## Elliott Lab Shared Files\Devices\Dye Densitometer\
        # Jetson NX Development\Code\VS Code\Images\start3.bmp')
        start_image = Image.open('start3.bmp')
        # The (20, 20) is (height, width)
        start_image = start_image.resize((20, 20), Image.ANTIALIAS)
        record_button = ImageTk.PhotoImage(start_image)

        # creates gui figure
        fig = Figure(figsize=(5, 4), dpi=100)
        canvas = FigureCanvasTkAgg(fig, master=self.root)

        """
        For Windows only
        """
        # x = 1
        # prevran = False

        self.running = False
        self.prevtrue = False

        # Creates a Frame for Selections
        selframe = ttk.Frame(self.root)
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
        self.ComSelect(comframe)
        self.dataentry(IDframe)

        # Creates frame for preview, start and stop buttons in GUI
        frame = ttk.Frame(self.root)
        frame.grid(row=3, column=0, rowspan=3)

        # Creates a Preview Button for Previewing the Data
        preview_button = tk.Button(frame, text="Preview", fg="white",
                                   bg="black", command=self.preview_data,
                                   font=('Arial', 18))

        # Create a start button, passing two options:
        start_button = tk.Button(frame, text="Start", fg="green",
                                 command=self.start_collection,
                                 font=('Arial', 18), image=record_button)
        start_button.config(compound='left')

        # Create a stop button, passing two options:
        stop_button = tk.Button(frame, text="Stop", fg="red",
                                command=self.stop_collection,
                                font=('Arial', 18), image=end_button)
        stop_button.config(compound='left')

        # Creates a progress bar
        self.progressbar = ttk.Progressbar(self.root, orient='horizontal',
                                           length=200)

        # Adds start and stop buttons, and progressbar to the frame
        preview_button.grid(row=0, column=0)
        start_button.grid(row=0, column=1)
        stop_button.grid(row=0, column=2)
        self.progressbar.grid(row=6, column=0)
        self.progressbar.config(mode='indeterminate')

        # Enters into the Tkinter event loop to make window appear:
        self.root.after(1, self.dataread)  # After 1 millisecond, call scanning
        self.root.mainloop()


if __name__ == "__main__":
    splot = SerialPlotting("Finger Probe Voltage_002.csv")
    splot.start_GUI()
