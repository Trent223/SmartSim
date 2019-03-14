# SmartSim GUI
# Version 1.0

# Imports
import matplotlib
matplotlib.use("TkAgg")
from matplotlib import pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import tkinter as tk
import tkinter.ttk as ttk
from tkinter import messagebox
import sys
from sympy import solve, Symbol
from config_funcs import get_optimizer_values, get_devsim_values, update_config_file, config_file #this is causing function to crash if no config file is found right off the bat. SEE COMMENT IN config_funcs.py JBS



# Create a root window that will be hidden. Will act as a driver to all other windows that may need to be spawned.
root = tk.Tk()
root.withdraw()
# This is the initial resolution of the slider and all other manual entry values
slider_resolution = 0.00001


# This function is called to load model data that will be used to create a new plot


def loadModel(selection, selection_index):
    # Get the name of the selected model
    selected_model = "config_"+selection
    # create a list to hold the value of every parameter in the model to be loaded
    all_param_values = []
    # create a list to hold the name of every parameter
    allParams = []
    # query will now hold all data for the selected model
    query = config_file.user_config[selected_model]
    # create three different lists to hold the three different types of parameters
    # and retrieve the values from the config file
    design_params = query["design_params"]
    devsim_params = query["devsim_params"]
    optimizer_params = query["optimizer_params"]
    # Get the model EQ
    modelEq = query["Model"]

    # Fill the list created earlier to hold all the parameter names
    for index in range(len(design_params)):
        allParams.append(design_params[index])
    for index in range(len(devsim_params)):
        allParams.append(devsim_params[index])
    for index in range(len(optimizer_params)):
        allParams.append(optimizer_params[index])

    # start parsing the model equation and filling in actual values for the params. Replace all parameter variables with their associated values
    for index in design_params:
        all_param_values.append(str(query[index]))
        modelEq = modelEq.replace(index, str(query[index]))

    # Replace all devsim parameter variables with their associated values
    if len(devsim_params) > 0:
        for index, val in enumerate(devsim_params):
            # If the values do not exist than retrieve them
            if query[devsim_params[index]][1] == "":
                                # query devsim to update the values if they do not exist
                get_devsim_values(selected_model)
                # reload the config file
                query = config_file.user_config[selected_model]
        # add the values to the list of all values for every parameter in this model
    for index in devsim_params:
        all_param_values.append(str(query[index][1]))
        modelEq = modelEq.replace(index, str(query[index][1]))

    # Replace all optimizer parameter variables with their associated values
    if len(optimizer_params) > 0:
        # If the values do not exist than retrieve them
        if query[optimizer_params[0]] == "":
                        # query the optimizer to update the values if they do not exist
            get_optimizer_values(selected_model)
            # reload the config file
            query = config_file.user_config[selected_model]
        # add the values to the list of all values for every parameter in this model
    for index in optimizer_params:
        all_param_values.append(str(query[index]))
        modelEq = modelEq.replace(index, str(query[index]))

    # Call the MainPage
    MainPage(query, selection, selection_index, allParams, all_param_values)
###### END OF LOADMODEL CLASS ######

# This class represents the main page of the GUI which contains the graph


class MainPage:
    def __init__(self, query, metricName, metricIndex, allParams, all_param_values):
                # copy all parameters into class variables that can be used with 'self' throughout this class
        self.allParams = allParams
        self.all_param_values = all_param_values
        self.metricName = metricName
        self.metricIndex = metricIndex
        self.query = query
        self.labels = []
        global slider_resolution

        # Create the main window
        self.currentWindow = tk.Toplevel(root)
        # close the window if the user hits the 'x' button on the GUI
        self.currentWindow.protocol("WM_DELETE_WINDOW", self.on_closing)
        # set the title of the window
        self.currentWindow.title("MainPage")
        # set the size and location of the window
        self.currentWindow.geometry("1080x680+200+0")

        # LABEL: SmartSim title
        title = tk.Label(self.currentWindow, text="SmartSim")
        # set the location within the window and font size
        title.place(relx=.5, rely=.05, anchor="center")
        title.config(font=("Courier", 24))

        # LABEL: Other options
        otherLbl = tk.Label(self.currentWindow, text="Other Options")
        # set the location within the window and font size
        otherLbl.place(relx=.02, rely=.1)
        otherLbl.config(font=("Courier", 12))

        # BUTTON: Overlay Button
        overlayBtn = tk.Button(self.currentWindow, text="Overlay Simulated Data",
                               bg="deep sky blue", command=lambda: self.DrawGraph(2))
        # set the location within the window and font size
        overlayBtn.place(relx=.02, rely=.14)

        # BUTTON: Redo-Config Button
        configBtn = tk.Button(self.currentWindow, text="Redo-Config",
                              command=lambda: self.RedoConfig(self.metricName), bg="deep sky blue")
        # set the location within the window and font size
        configBtn.place(relx=.195, rely=.14)

        # LABEL: Select new metric
        metricLbl = tk.Label(self.currentWindow, text="Select New Metric")
        # set the location within the window and font size
        metricLbl.place(relx=.02, rely=.2)
        metricLbl.config(font=("Courier", 12))

        # LABEL: Edit Parameter
        editLbl = tk.Label(self.currentWindow, text="Edit Parameter")
        # set the location within the window and font size
        editLbl.place(relx=.2, rely=.2)
        editLbl.config(font=("Courier", 12))

        #LABEL: Parameters
        paramLbl = tk.Label(self.currentWindow, text="Parameters")
        # set the location within the window and font size
        paramLbl.place(relx=.02, rely=.29)
        paramLbl.config(font=("Courier", 12))

        # Create a List that will be used to populate the combobox
        model_list = []

        ### COMBOBOX for Select Metric ###
        # Load all models that are currently stored in the configuration file
        for model in config_file.user_config:
            model_list.append(config_file.user_config[model]["Metric"])

        # String to store the comboBox selection
        selected_model = tk.StringVar()
        # COMBOBOX: Select Model to Load
        self.model_combo = ttk.Combobox(
            self.currentWindow, textvariable=selected_model)
        # add the model_list values to the combobox
        self.model_combo['values'] = model_list
        # set the default value to be displayed in the comboBox to the currently selected metric
        self.model_combo.current(self.metricIndex)
        # set the location within the window and font size
        self.model_combo.place(relx=.02, rely=.24)

        # Called when the user makes a selection within the combobox
        def callback(eventObject):
            loop_counter = 0
            for model in model_list:
                if (selected_model.get() == model):
                    self.metricIndex = loop_counter
                    break
                loop_counter = loop_counter + 1
            self.Close(selected_model.get())
            # binds the combobox to the callback function so that it is called when the user makes a selection
        self.model_combo.bind("<<ComboboxSelected>>", callback)

        ### COMBOBOX for Edit ###
        # Sting to store the comboBox selection
        selected_parameter = tk.StringVar()
        self.editCombo = ttk.Combobox(
            self.currentWindow, textvariable=selected_parameter)
        # add the list of all parameter names to the combobox
        self.editCombo['values'] = self.allParams
        # set the first index of the list as the default value to be displayed
        self.editCombo.current(0)
        # set the location within the window and font size
        self.editCombo.place(relx=.2, rely=.24)
        # set the current parameter
        self.currParam = selected_parameter.get()
        # Called when the user makes a selection within the combobox

        def editCallback(eventObject):
            self.Edit(selected_parameter.get(), self.editCombo.current(), 1)
            self.currParam = selected_parameter.get()
            # binds the edit combobox to the editCallback function so that it is called when the user makes a selection
        self.editCombo.bind("<<ComboboxSelected>>", editCallback)

        # Call the function that displays all the parameters in order to update them when a selection is made
        self.Display_Parameters(0)
        # Call the function that draws the graph
        self.DrawGraph(0)
        # update the parameter values of all labels
        self.Edit(allParams[0], 0, 0)

    # This function is called to display all parameters.
    def Display_Parameters(self, flag):
        # If this is not the first time the function is called than labels for the parameters already exist.
                # These existing labels need to be deleted or the new ones are just drawn over them and they still exist.
        if(flag == 1):
            for index in range(len(self.allParams)):
                currentLbl = self.labels[index]
                currentLbl.destroy()
                # clear the list of all label names
            self.labels.clear()
        ##### Design Parameters #####
        column = 0
        row = 0
        # create a label for each parameter and display them on the window
        for index in range(len(self.allParams)):
                        # convert the value of the parameter to a float
            floatValue = float(self.all_param_values[index])
            floatValue = round(floatValue, 6)
            # LABEL: label for the current param
            Lbl = tk.Label(self.currentWindow,
                           text=self.allParams[index]+": "+str(floatValue))
            # set the location within the window and font size
            Lbl.place(relx=.02+(column*.1), rely=.32+(row*.025))
            Lbl.config(font=("Courier", 9))
            # add the label to the list of all labels for parameters
            self.labels.append(Lbl)
            # location of labels is based around rows and columns
            row = row + 1
            if row == 17:
                row = 0
                column = column + 1

        # LABEL: Current Parameter
        if(flag == 1):
                        # if the label already exists thatn destroy it
            self.currentLbl.destroy()
        self.currentLbl = tk.Label(self.currentWindow, text="Current Parameter: " + str(
            self.allParams[self.editCombo.current()]) + ", Current Value = " + str(self.all_param_values[self.editCombo.current()]))
        # set the location within the window and font size
        self.currentLbl.place(relx=.21, rely=.975, anchor="center")
        self.currentLbl.config(font=("Courier", 10))

    # This function is responsible for creating the widgets on the bottom left of the GUI that allow you to edit
        # a parameter, set a goal value and use the slider.
    def Edit(self, selection, index, flag):
        global slider_resolution
        if (flag == 1):
            # If this is not the first time the function is called than widgets already exist.
            # Delete them of the new ones will just be created on top of them and they will still exist.
            self.manualLbl.destroy()
            self.value.destroy()
            self.updateBtn.destroy()
            self.minLbl.destroy()
            self.minimum.destroy()
            self.maxLbl.destroy()
            self.maximum.destroy()
            self.resLbl.destroy()
            self.resolution.destroy()
            self.slider.destroy()

        # Update the labels
        self.Display_Parameters(1)

        # LABEL: Set Goal Label
        self.goalLbl = tk.Label(self.currentWindow, text="Enter Target Value:")
        # set the location within the window and font size
        self.goalLbl.place(relx=.0175, rely=.77)
        self.goalLbl.config(font=("Courier", 10))

        # ENTRY: Goal Entry Box
        self.goalText = tk.StringVar()
        self.goal = tk.Entry(self.currentWindow,
                             textvariable=self.goalText, width=8)
        # set the location within the window and font size
        self.goal.place(relx=0.16, rely=.768)

        # LABEL: X Label
        self.XLbl = tk.Label(self.currentWindow, text="for X =")
        # set the location within the window and font size
        self.XLbl.place(relx=.225, rely=.77)
        self.XLbl.config(font=("Courier", 10))

        # ENTRY: X Entry Label
        self.XText = tk.StringVar()
        self.X = tk.Entry(self.currentWindow, textvariable=self.XText, width=8)
        # set the location within the window and font size
        self.X.place(relx=0.28, rely=.768)

        # LABEL: Manual Label
        self.manualLbl = tk.Label(self.currentWindow, text="Set Value:")
        # set the location within the window and font size
        self.manualLbl.place(relx=.0175, rely=.825)
        self.manualLbl.config(font=("Courier", 10))

        # ENTRY: Value Textbox
        self.manualText = tk.StringVar()
        self.value = tk.Entry(self.currentWindow,
                              textvariable=self.manualText, width=8)
        # set the location within the window and font size
        self.value.place(relx=0.095, rely=.823)

        # This function handles the manual entry of parameter values
        def ManualEntry(eventObject):
            global slider_resolution
            try:
                        # set the parameter being edited to the value entered in the textbox
                self.all_param_values[index] = float(self.manualText.get())
                splitText = self.manualText.get().split(".")
                if len(splitText) > 1:
                    slider_resolution = 10**(-1*len(splitText[1]))
                else:
                    slider_resolution = 10**(-1)

                    # update the configfile.
                # check if the parameter is a devsim parameter
                devsim_params = self.query["devsim_params"]
                if self.allParams[index] in devsim_params:
                    tempValue = config_file.user_config["config_" +
                                                        self.metricName][self.allParams[index]][0]
                    config_file.user_config["config_"+self.metricName][self.allParams[index]] = [
                        tempValue, self.all_param_values[index]]
                else:
                    config_file.user_config["config_" +
                                            self.metricName][self.allParams[index]] = self.all_param_values[index]
                    # update the label associated with this parameter
                self.Display_Parameters(1)
                # Redraw the graph
                self.DrawGraph(1)
                # destroy the existing slider to avoid a memory leak
                self.slider.destroy()
                self.slider = tk.Scale(self.currentWindow, from_=float(self.manualText.get()) - 5.0, to=float(self.manualText.get(
                )) + 5.0, resolution=slider_resolution, digits=6, orient="horizontal", length=450, command=getSliderValue)
                self.slider.set(float(self.manualText.get()))
                # set the location within the window and font size
                self.slider.place(relx=.21, rely=.92, anchor="center")
                # Update the min, max and res labels of the slider
                self.minimum.delete(0, 20)
                self.minimum.insert(
                    0, float(self.all_param_values[index]) - 5.0)
                self.maximum.delete(0, 20)
                self.maximum.insert(
                    0, float(self.all_param_values[index]) + 5.0)
                self.resolution.delete(0, 20)
                self.resolution.insert(0, float(slider_resolution))

                # update config file
                update_config_file()
            except:
                self.value.delete(0, 10)
                self.value.insert(0, "Error")
                # bind the textbox to the function above so that it is called when the user hits 'return'
        self.value.bind('<Return>', ManualEntry)

        # BUTTON: Update Button
        self.updateBtn = tk.Button(self.currentWindow, text="Update Slider", command=lambda: UpdateSlider(
            self.minText, self.maxText, self.resText), bg="deep sky blue", height=1, width=13, font=("Courier", 10))
        # set the location within the window and font size
        self.updateBtn.place(relx=.18, rely=.81)

        # BUTTON: Goal Button
        self.goalBtn = tk.Button(self.currentWindow, text="Optimize", command=lambda: self.Solve(
            self.goalText, self.XText, index), bg="deep sky blue", height=1, width=9, font=("Courier", 10))
        # set the location within the window and font size
        self.goalBtn.place(relx=.3, rely=.81)

        # LABEL: Min Label
        self.minLbl = tk.Label(self.currentWindow, text="Min:")
        # set the location within the window and font size
        self.minLbl.place(relx=.0175, rely=.86)
        self.minLbl.config(font=("Courier", 10))

        # ENTRY: Min Textbox
        self.minText = tk.StringVar()
        self.minimum = tk.Entry(
            self.currentWindow, textvariable=self.minText, width=8)
        # delete the default 0 added to the textbox
        self.minimum.delete(0, 1)
        # set the default value to be displayed
        self.minimum.insert(0, float(self.all_param_values[index]) - 5.0)
        # set the location within the window and font size
        self.minimum.place(relx=0.05, rely=0.86)

        # LABEL: Max Label
        self.maxLbl = tk.Label(self.currentWindow, text="Max:")
        # set the location within the window and font size
        self.maxLbl.place(relx=.125, rely=.86)
        self.maxLbl.config(font=("Courier", 10))

        # TEXTBOX: Max Textbox
        self.maxText = tk.StringVar()
        self.maximum = tk.Entry(
            self.currentWindow, textvariable=self.maxText, width=8)
        # delete the default o added to the textbox
        self.maximum.delete(0, 1)
        # set the default value to be displayed
        self.maximum.insert(0, float(self.all_param_values[index]) + 5.0)
        # set the location within the window and font size
        self.maximum.place(relx=0.1575, rely=0.86)

        # LABEL: Resolution Label
        self.resLbl = tk.Label(self.currentWindow, text="Resolution:")
        # set the location within the window and font size
        self.resLbl.place(relx=.2325, rely=.86)
        self.resLbl.config(font=("Courier", 10))

        # TEXTBOX: Resolution Textbox
        self.resText = tk.StringVar()
        self.resolution = tk.Entry(
            self.currentWindow, textvariable=self.resText, width=8)
        # delete the default 0 added to the textbox
        self.resolution.delete(0, 20)
        # set the default value to be displayed
        self.resolution.insert(0, float(slider_resolution))
        # set the location within the window and font size
        self.resolution.place(relx=0.32, rely=0.86)

        # Get the value of the slider when the user moves the mouse. called for each tick of the slider and not just when the user lets go.
        def getSliderValue(value):
                        # update the parameter being edited
            self.all_param_values[index] = float(value)

            # update the config file
            # check if the parameter is a devsim parameter
            devsim_params = self.query["devsim_params"]
            if self.allParams[index] in devsim_params:
                tempValue = config_file.user_config["config_" +
                                                    self.metricName][self.allParams[index]][0]
                config_file.user_config["config_"+self.metricName][self.allParams[index]] = [
                    tempValue, self.all_param_values[index]]
            else:
                config_file.user_config["config_" +
                                        self.metricName][self.allParams[index]] = self.all_param_values[index]

            # reload the label associated with this parameter
            self.Display_Parameters(1)
            # redraw the graph
            self.DrawGraph(1)
            # update the manual entry box to display current value
            self.value.delete(0, 10)
            self.value.insert(0, value)
            # update config file
            update_config_file()

            # SLIDER: slider that allows you to edit any given parameter
        self.slider = tk.Scale(self.currentWindow, from_=float(self.all_param_values[index]) - 5.0, to=float(
            self.all_param_values[index]) + 5.0, orient="horizontal", length=450, digits=10, resolution=slider_resolution, command=getSliderValue)
        self.slider.set(float(self.all_param_values[index]))
        # set the location within the window and font size
        self.slider.place(relx=.21, rely=.92, anchor="center")

        # update the slider with the users prefrence for min, max and resolution
        def UpdateSlider(minimun, maximun, resolution):
            global slider_resolution
            slider_resolution = float(resolution.get())
            # destroy the existing slider to avoid a memory leak
            self.slider.destroy()
            try:
                self.slider = tk.Scale(self.currentWindow, from_=float(minimun.get()), to=float(maximun.get(
                )), resolution=slider_resolution, digits=10, orient="horizontal", length=450, command=getSliderValue)
                # set the location within the window and font size
                self.slider.place(relx=.21, rely=.92, anchor="center")
            except:
                print(
                    "Invalid entry for either the min, max or resolution of the slider. Please enter an appropriate value")

    # This function is responsible for drawing the graph
    def DrawGraph(self, flag):

                # get the equation for the model
        selected_parameter = tk.StringVar()
        modelEq = self.query["Model"]
        # retrieve the x values from the config file
        opt_x_data = self.query["opt_x_data"]
        opt_y_data = self.query["opt_y_data"]
        x_axis = self.query["x_axis"]
        # create a list to hold the generated y values
        Y_dataPoints = []
        counter = 0
        # replace all parameters in the model equation with their actual values
        for index in self.allParams:
            modelEq = modelEq.replace(
                index, str(self.all_param_values[counter]))
            counter = counter + 1
        # after all parameter variables have been replaced with their actual values evaluate the equation

        self.eqn = modelEq
        # at different values of x to generate the y data points for the graph
        for dataPoint in opt_x_data:
            currentEq = modelEq.replace(x_axis, str(dataPoint))
            # append each point to the list of y data points
            try:
                Y_dataPoints.append(eval(currentEq))
            except:
                print("attempted to divide by zero. Value ignored")

        if (flag == 0):
            # INIT Graph: set the size of the graph window
            fig = Figure(figsize=(6, 6), dpi=100)
            # add the plot to the graph window
            self.plot = fig.add_subplot(111)
            # plot the x and y data points from each list
            self.plot.plot(opt_x_data, Y_dataPoints, color='blue')
            # set the title of the plot
            self.plot.set_title("Current Metric: " +
                                self.query["Metric"], fontsize=14)
            # set the y axis title of the plot
            self.plot.set_ylabel("Y", fontsize=14)
            # add a grid to the plot
            self.plot.grid(True)
            # set the x axis title of the plot
            self.plot.set_xlabel("X", fontsize=14)
            # actually draw the graph window and plot
            self.canvas = FigureCanvasTkAgg(fig, master=self.currentWindow)
            self.canvas.get_tk_widget().place(relx=0.43, rely=0.1)
            self.canvas.draw()
            # remove the existing plot if another one needs to be added. this is the redraw functionality
        else:
            # Update the range of the graph
            if(flag == 1):
                max_X = max(opt_x_data)
                min_X = min(opt_x_data)
                max_Y = max(Y_dataPoints)
                min_Y = min(Y_dataPoints)
                if ((max_X != min_X) and (max_Y != min_Y)):
                    self.plot.set_xlim([min_X, max_X])
                    self.plot.set_ylim([min_Y, max_Y])
                    self.plot.lines.pop(0)
                self.plot.plot(opt_x_data, Y_dataPoints, color='blue')
                self.canvas.draw()
            else:
                max_X = max(opt_x_data)
                min_X = min(opt_x_data)
                if (max(opt_y_data) < max(Y_dataPoints)):
                    max_Y = max(Y_dataPoints)
                else:
                    max_Y = max(opt_y_data)
                if (min(opt_y_data) > min(Y_dataPoints)):
                    min_Y = min(Y_dataPoints)
                else:
                    min_Y = min(opt_y_data)
                self.plot.set_xlim([min_X, max_X])
                self.plot.set_ylim([min_Y, max_Y])
                self.plot.scatter(opt_x_data, opt_y_data, color='red')
                self.canvas.draw()

        # Called to update the paramaters from the configuration file
    def RedoConfig(self, selection):
                # retrieve the values of the devsim and optimizer values from the appropriate place. These may be set to random
                # values at the moment by the user
        get_devsim_values("config_"+selection)
        get_optimizer_values("config_"+selection)
        # destroy the current window
        self.currentWindow.destroy()
        # load the new model
        loadModel(selection, self.metricIndex)

    # Solve for the goal value
    def Solve(self, goal, x, selected_param):
        try:
            goal_val = float(goal.get())
            x_val = float(x.get())
        except:
            self.goal.delete(0, 20)
            self.goal.insert(0, "Error")
            self.X.delete(0, 20)
            self.X.insert(0, "Error")
            return
        # current model
        modelEq = self.query["Model"]
        currX_label = self.query["x_axis"]
        # target parameter to be solved
        target_var = self.currParam
        tv = Symbol(target_var)

        modelEq = modelEq.replace(target_var, "tv")
        modelEq = modelEq.replace(currX_label, str(x_val))

        # replace all parameters in the model equation with their actual values
        for idx, param in enumerate(self.allParams):
            if param != "tv":
                modelEq = modelEq.replace(
                    param, str(self.all_param_values[idx]))

        if goal_val < 0:
            modelEq += str(goal_val)
        else:
            modelEq += "-" + str(goal_val)
        func = eval(modelEq)
        res = solve(func)

        if(len(res) > 1):
            self.all_param_values[selected_param] = res[1]
        else:
            self.all_param_values[selected_param] = res[0]

        # update the manual entry box to display current value
        self.value.delete(0, 10)
        self.value.insert(0, self.all_param_values[selected_param])

        # check if the parameter is a devsim parameter
        devsim_params = self.query["devsim_params"]
        if self.allParams[selected_param] in devsim_params:
            tempValue = config_file.user_config["config_" +
                                                self.metricName][self.allParams[selected_param]][0]
            config_file.user_config["config_"+self.metricName][self.allParams[selected_param]] = [
                tempValue, self.all_param_values[selected_param]]
        else:
            config_file.user_config["config_"+self.metricName][self.allParams[selected_param]
                                                               ] = self.all_param_values[selected_param]
        update_config_file()
        self.Display_Parameters(1)
        self.DrawGraph(1)

    # Called to close the current window when transitioning to a new window
    def Close(self, selection):
                # close the current window
        self.currentWindow.destroy()
        # load the new model
        loadModel(selection, self.metricIndex)

    # Captures the event of a user hitting the red 'X' button to close a window
    def on_closing(self):
                # close the current window
        self.currentWindow.destroy
        if messagebox.askokcancel("Quit", "Do you want to quit?"):
            # This will kill the entire application
            root.destroy()


def main():
    # This is a little nasty, but I had to use a for loop to get the first metric of
    # the config file. Not sure how else to do it as it will not accept an integer and
    # I am not sure what models the file may contain. TODO: Find a cleaner solution to
        # this issue if time permits
    for metric in config_file.user_config:
        loadModel(config_file.user_config[metric]["Metric"], 0)
        break
        # This try except loop had to be implemented due to a known bug with the current version of tkinter
        # and Mac's OS. When a Mac user opens the GUI and attempts to scroll with a mouse the GUI will immediately
        # crash. This is not an issue with our GUI, but tkinter itself.
    while True:
        try:
            root.mainloop()
            break
        except UnicodeDecodeError:
            pass


if __name__ == '__main__':
    main()
