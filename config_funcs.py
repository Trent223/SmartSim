import subprocess

import sys
import os

try:
    # Check to see if application was called with an argument. Argument must represent 
    # a config file
    command = sys.argv[1]  
except:
    #if argument not given set default config file
    command = input("Enter name of config file: ") #This change allows the user to enter the name of the config file instead of the program assuming the name JBS
try:
    #Attempt to import the given config file
    config_file = __import__(command)
except:
    #If given config file could not be loaded walk user through creating a config file JBS
    config_file_name = input("Config file could not be imported. Enter name of config file to be created: ")
    config_file = create_config_file(config_file_name)
    
    
    
#Author: Justin Sturgill
def create_config_file(config_name):
    #Create config file JBS
    config_name = config_file+'.txt'
    f = open(config_name, 'a+')
    #initialize value for add_equation JBS
    add_equation = 'y'
    while add_equation == 'y':
        equation_name = input("Enter name of equation: ")
        f.write("%s = { \n" % equation_name)
        add_field = input("Would you like to add a field? Enter y or n: ")
        while add_field == 'y':
            field_name = input("Enter name of field: ")
            f.write("     %s : " %field_name)
            field_value = input("Enter field value: ")
            f.write("%s \n" % field_value)
            add_field = input("Add another field? Enter y or n: ")
        f.write("} \n")
        add_equation = input("Would you like to add another equation? Enter y or n: ")
    f.close()
    return config_name

def get_optimizer_values(metric):

    # format arguments and model
    args = config_file.user_config[metric]['x_axis'] + "," + \
        ",".join(config_file.user_config[metric]['optimizer_params'])
    mdl = config_file.user_config[metric]['Model']

    # insert numbers to equation
    for design_params in config_file.user_config[metric]['design_params']:
        mdl = mdl.replace(design_params, str(
            config_file.user_config[metric][design_params]))
    for devsim_params in config_file.user_config[metric]['devsim_params']:
        mdl = mdl.replace(devsim_params, str(
            config_file.user_config[metric][devsim_params][1]))

    # retrieve optimized constants
    new_opts = scipy_curve_fit.do_optimization(
        mdl, args, config_file.user_config[metric]['opt_x_data'], config_file.user_config[metric]['opt_y_data'])

    # loop through optimizer params and save new vals in the runtime environment

    for idx, param in enumerate(config_file.user_config[metric]['optimizer_params']):
        config_file.user_config[metric][param] = new_opts[idx]

    # update config file
    update_config_file()


def get_devsim_values(metric):
    # find all devsim commands in the metric entry of the config file

    dummy_mode = True

    if dummy_mode:
        for param in config_file.user_config[metric]['devsim_params']:
            config_file.user_config[metric][param][1] = 11

    else:
        for param in config_file.user_config[metric]['devsim_params']:
            # need to create input file
            with open('smart_sim_input.dsi', 'w') as f:
                f.seek(0)  # go to beginning of file
                f.write('Devsim Input File\n')
                f.write(config_file.user_config[metric]['models_path'] + '\n')
                f.write(config_file.user_config[metric]['corners'] + '\n')
                f.write(config_file.user_config[metric]
                        ['secondary_corners'] + '\n')
                f.write(
                    ",".join(config_file.user_config[metric]['headers'])[:-1] + '\n')

                for idx, val in enumerate(config_file.user_config[metric]['headers']):
                    if (val in config_file.user_config[metric]['design_params'] or val in config_file.user_config[metric]['devsim_params'] or val in config_file.user_config[metric]['optimizer_params']):
                        f.write(
                            str(config_file.user_config[metric][val]) + ',')
                    else:
                        f.write(
                            config_file.user_config[metric][param][0][idx] + ',')

            # run devsim
            devsim_path = "/data/home/rcwahl2/devsim/devsim"

            os.system(
                f"{devsim_path} -bsub \"\" -v 1 -o output.dso smart_sim_input.dsi")

            # need to parse output.dso
            result = subprocess.check_output(
                "cat output.dso | grep -A1 SIM | tail -n -1 | awk '{print $2}'", shell=True)
            # subprocess.check_output return value needs to be post-processed
            # get rid of leading b, trailing ,\n and convert to float
            result = float(result.decode('ascii')[slice(0, -2)])
            config_file.user_config[metric][param][1] = result

    update_config_file()


def update_config_file():
    # store the results in the config file
    with open('config_file.py', 'w') as f:
        f.seek(0)  # go to beginning of file
        for metric in config_file.user_config:
            f.write(f'{metric} = ' + '{\n')
            for key, value in config_file.user_config[metric].items():
                if isinstance(value, str):
                    f.write(f'\t\'{key}\' : \'{value}\',\n')
                else:
                    f.write(f'\t\'{key}\' : {value},\n')
            f.write('}\n')

        f.write('user_config = {')
        for metric in config_file.user_config:
            f.write(f'\'{metric}\' : {metric},')
        f.write('}')


def save_design_value(metric, param, new_value):
    config_file.user_config[metric][param] = new_value


# def main():
#    #usage python3 execName config_<metric name>
#
#    if len(sys.argv) != 2:
#        print('use one and only one command line argument')
#        sys.exit()
#    if sys.argv[1] not in config_file.user_config:
#        print('metric not found in config file')
#        sys.exit()
#
#    config_metric = sys.argv[1]
#    #print (config_metric)
#    get_devsim_values(config_metric)
#    #get_optimizer_values(config_metric)
##    save_design_value(config_metric, 'c', 5)
#
# main()
