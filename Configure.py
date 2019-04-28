'''
Author(s): Trent Minch
Purpose: Generate the SmartSim config file 
by reading from the available yaml files in the 
current directory and asking the user to provide
all other necessary information
'''
import os
import yaml

class ConfigData():
    '''
    Author: Trent Minch
    Holds all the relevant data to generate the program.
    This is the data that used to be stored in config_file.py
    '''
    
    #Actual config file data
    #This is a list of dictionaries of the form "MetricName" : {Data}
    metrics = []
    #Yaml files in the CWD that are useful to us, and their 
    #relevant fields. This list is a list of dictionaries of the 
    #form {"Field" : Fieldname, "File": PathToRelevantFile}
    YamlFiles = []
    #These are the relevant keywords we scan yaml files
    #for to determine if they are needed for our config 
    #info. 
    Keywords = {
        "Full" : "full",
        "MetricKeyword" : "metric",
        "ModelKeyword" : "model", 
        "XaxisKeyword" : "x axis",
        "DesignParamsKeyword" : "design params", 
        "DevsimParamsKeyword" : "devsim params",
        "OptmizerParamsKeyword" : "optimizer params",
        "ModelsPathKeyword" : "simulator language",
        "CornersKeyword" : "corners", 
        "SecondaryCornersKeyword" : "secondary corners",
        "HeadersKeyword" : "headers",
        }
    #These are the keys that must be in ConfigData for each 
    #Metric in order for the program to run
    RequiredKeys = ["Model", "Xaxis", "DesignParams", "DevsimParams", "OptimizerParams", "ModelsPath", "Corners", "SecondaryCorners", "Headers"]
    #Holds the path to a full config file, if the user provides one
    PathToFullConfig = ""

def ScanCurrentDirectory():
    '''
    Author: Trent Minch
    Purpose: Check the current working directory for 
    any yaml (.yml) files. Open those files and try to 
    determine which parts of the config we can determine
    from the available yaml files.
    
    Arguments: None
    Returns: nothing
    '''
    YAMLFilesInCWD = []
    for file in os.listdir('.'):
        if os.path.isfile(file) and (file.endswith(".yml") or file.endswith(".yaml")) :
            YAMLFilesInCWD.append(file)
            
    #Scan the YAML files to determine what part of the 
    #config they are trying to provide
    for file in YAMLFilesInCWD:
        with open(file, "r") as Yaml:
            YamlFile = yaml.safe_load(Yaml)
            #All Yaml files should have a top-level key called
            #"type" that gives the keyword for what config
            #file field the yaml file is trying to provide
            #print(YamlFile)
            #print(YamlFile[0])
            try: 
                field = YamlFile[0]["type"]
            except KeyError:
                print("YAML file {} did not contain a 'type' key with a valid keyword.".format(file))
                continue
            if field not in ConfigData.Keywords.values():
                print("YAML file {} did not have a valid keyword associated with 'type'".format(file))
                print("Valid keywords are: {}".format(ConfigData.Keywords.values()))
                continue
            else:
                print("Found valid file {} for config file field {}".format(file, field))
                #If we have multiple files for one field, we want to store them together TODO
                ConfigData.YamlFiles.append({"Field" : field, "File" : file})
    
def ParseFoundYamlFiles():
    '''
    Author: Trent Minch
    After the valid config files in the working
    directory are identified, go through them and 
    ask the user which values for each field to use
    
    TODO: If there is only one value in the file, store it by
    default
    '''
    #Check to see if there are any "full" config files
    for file in ConfigData.YamlFiles:
        if file["Field"] == "full":
            print("Full config file {} found. Use this config? Type 'y' or 'n'".format(file["File"]))
            choice = str(input())
            while True:
                if choice.upper() == "Y":
                    print("Loading config file {}...".format(file["File"]))
                    ConfigData.PathToFullConfig = file["File"]
                    return 1
                elif choice.upper() == "N":
                    print("Proceeding to identify other config files")
                    break
                else:
                    print("Invalid input. Enter 'y' or 'n' or use KeyboardInterrupt to exit")
                    choice = input()
    for file in ConfigData.YamlFiles:
        with open(file["File"], "r") as YFile: 
            Yaml = yaml.safe_load(YFile)
        CurrentKeys = Yaml.keys()
        #Descend down the Yaml tree until you reach the
        #end, asking the user which path to take each
        #step of the way   
    
def VerifyConfigData():
    
    '''
    Author: Trent Minch
    Makes sure there is enough information in ConfigData.metrics
    to generate the program. 
    
    Arguments: None
    Returns: bool
    True if the config file is sufficiently filled out to generate the program
    False otherwise
    '''
    #Start true. If any required field is missing, switch to false and return
    ConfigIsGood = True
    for i in range(len(ConfigData.metrics)):
        CurrentMetric = list(ConfigData.metrics[i].keys())[0]
        CurrentMetricDataKeys = list(ConfigData.metrics[i][CurrentMetric].keys())
        for key in ConfigData.RequiredKeys:
            if key not in CurrentMetricDataKeys:
                print("Required key {} not in Metric {}".format(key, CurrentMetric))
                ConfigIsGood = False
    
    return ConfigIsGood

def UpdateConfigData(Metric, Field, Value):
    '''
    Author: Trent Minch
    Updates the data in ConfigData with provided data
    Arguments: Metric, Field, Value
    
    Metric: Which metric in ConfigData.metrics to update.
    If this Metric isn't in ConfigData already, add it
    
    Field: Which field in the Metric's config data to update. If the field
    isn't already in the config data for that metric, add it.
    
    Value: The value corresponding to the given field
    
    Returns: nothing
    '''
    #If the metric is not already in the config file, add it
    MetricExists = False
    for item in ConfigData.metrics:
        if Metric in item:
            MetricExists = True
    if not MetricExists:
        ConfigData.metrics.append({Metric : {}})
    #Within that metric, if the field doesn't exist, add it
    #Otherwise, update it
    MetricIndex = 0
    for item in ConfigData.metrics:
        if Metric in item.keys():
            MetricIndex = ConfigData.metrics.index(item)
    
    ConfigData.metrics[MetricIndex][Metric].update({Field, Value})
    
def LoadFullConfig():
    '''
    Author: Trent Minch
    In the event of a full config, load the data
    straight into our ConfigData class
    '''
    #Open the yaml config file
    with open(ConfigData.PathToFullConfig, "r") as yml:
        FullConfigData = yaml.safe_load(yml)
    #print(FullConfigData)
    ConfigData.metrics = FullConfigData
    #FullConfigKeys = list(FullConfigData[0].keys())
    #for key in FullConfigKeys:
        #if key.startswith("metric"):
            #CurrentMetric = FullConfigData[key]
            #CurrentMetricName = CurrentMetric["metric"]
            #ConfigData.metrics.append({CurrentMetricName : {}})
            ##We need the index of the metric we're updating
            #CurrentMetricIndex = 0
            #for item in ConfigData.metrics:
                #if CurrentMetricName in list(item.keys()):
                    #CurrentMetricIndex = ConfigData.metrics.index(item)            
            #for subkey in list(CurrentMetric.keys()):
                #if subkey == 'metric':
                    ##We already got the name of the metric, it's the key for this dict
                    #continue
                #ConfigData.metrics[CurrentMetricIndex][CurrentMetricName].update({subkey : CurrentMetric[subkey]})
                

def ConfigSetup():
    '''
    Author: Trent Minch
    Calls other functions in this file to set up the config file
    '''
    print("Setting up config")
    ScanCurrentDirectory()
    ParseFoundYamlFiles()
    #Add all the currently known data into ConfigData
    if ConfigData.PathToFullConfig != "":
        LoadFullConfig()
        return
     
    #print(ConfigData.metrics)


def main():
    '''
    Main function exists only for testing purposes and should 
    either be commented out, removed, or changed to another
    function name in production code
    '''
    
    ConfigSetup()
    #print(ConfigData.YamlFiles)    
    #print(ConfigData.metrics)
    
main()
