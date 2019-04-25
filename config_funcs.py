import subprocess
from Configure import ConfigData
import sys
import os
import yaml
import scipy_curve_fit
def get_optimizer_values(metricindex, metric):

    # format arguments and model
    args = ConfigData.metrics[metricindex][metric]['x_axis'] + "," + \
        ",".join(ConfigData.metrics[metricindex][metric]['optimizer params'])
    mdl = ConfigData.metrics[metricindex][metric]['model']

    # insert numbers to equation
    for design_params in ConfigData.metrics[metricindex][metric]['design params']:
        mdl = mdl.replace(design_params, str(
            ConfigData.metrics[metricindex][metric][design_params]))
    for devsim_params in ConfigData.metrics[metricindex][metric]['devsim params']:
        mdl = mdl.replace(devsim_params, str(
            ConfigData.metrics[metricindex][metric][devsim_params][1]))

    # retrieve optimized constants
    new_opts = scipy_curve_fit.do_optimization(
        mdl, args, [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10], [5, 4.5, 4, 3.5, 3, 2.5, 2, 1.5, 1, 0.5, 0])

    # loop through optimizer params and save new vals in the runtime environment

    #for idx, param in enumerate(ConfigData.metrics[metricindex][metric]['optimizer params']):
     #   ConfigData.metrics[metricindex][metric][param] = new_opts[idx]
    for i in range(len(ConfigData.metrics[metricindex][metric]['optimizer params'])):
        print(new_opts[i])
        ConfigData.metrics[metricindex][metric][ConfigData.metrics[metricindex][metric]['optimizer params'][i]] = float(new_opts[i])

    # update config file
    update_config_file()


def get_devsim_values(metricindex, metric):
    # find all devsim commands in the metric entry of the config file

    dummy_mode = True

    if dummy_mode:
        for param in ConfigData.metrics[metricindex][metric]['devsim params']:
            param = 11

    else:
        for param in ConfigData.metrics[metricindex][metric]['devsim params']:
            # need to create input file
            with open('smart_sim_input.dsi', 'w') as f:
                f.seek(0)  # go to beginning of file
                f.write('Devsim Input File\n')
                f.write(ConfigData.metrics[metricindex][metric]['models_path'] + '\n')
                f.write(ConfigData.metrics[metricindex][metric]['corners'] + '\n')
                f.write(ConfigData.metrics[metricindex][metric]
                        ['secondary_corners'] + '\n')
                f.write(
                    ",".join(ConfigData.metrics[metricindex][metric]['headers'])[:-1] + '\n')

                for idx, val in enumerate(ConfigData.metrics[metricindex][metric]['headers']):
                    if (val in ConfigData.metrics[metricindex][metric]['design params'] or val in ConfigData.metrics[metricindex][metric]['devsim params'] or val in ConfigData.metrics[metricindex][metric]['optimizer_params']):
                        f.write(
                            str(ConfigData.metrics[metricindex][metric][val]) + ',')
                    else:
                        f.write(
                            ConfigData.metrics[metricindex][metric][param][0][idx] + ',')

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
            ConfigData.metrics[metricindex][metric][param][1] = result

    update_config_file()


def update_config_file():
    # store the results in the config file
    if ConfigData.PathToFullConfig == "":
        #Make a new config
        ConfigData.PathToFullConfig ="NewConfig.yml"
        #print(ConfigData.metrics)
    
    with open(ConfigData.PathToFullConfig, "w+") as  f:
        ConfigData.metrics.insert(0, {'type': 'full'})
        yaml.dump(ConfigData.metrics, f)
    #Take the type line back out
    ConfigData.metrics.pop(0)


def save_design_value(metric, param, new_value):
    ConfigData.metrics[metricindex][metric][param] = new_value


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
