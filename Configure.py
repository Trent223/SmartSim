'''
Author: Trent Minch
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
    metrics = []
    #Yaml files in the CWD that are useful to us, and their 
    #relevant fields. This list is a list of dictionaries of the 
    #form {"Field" : Fieldname, "File": PathToRelevantFile}
    YamlFiles = []
    #These are the relevant keywords we scan yaml files
    #for to determine if they are needed for our config 
    #info. 
    Keywords = {
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
            try: 
                field = YamlFile["type"]
            except KeyError:
                print("YAML file {} did not contain a 'type' key with a valid keyword.".format(file))
                continue
            if field not in ConfigData.Keywords.values():
                print("YAML file {} did not have a valid keyword associated with 'type'".format(file))
                print("Valid keywords are: {}".format(ConfigData.Keywords.values()))
                continue
            else:
                print("Found valid file {} for config file field {}".format(file, field))
                ConfigData.YamlFiles.append({"Field" : field, "File" : file})
    
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
    

    
    return ConfigIsGood

def main():
    '''
    Main function exists only for testing purposes and should 
    either be commented out, removed, or changed to another
    function name in production code
    '''
    
    ScanCurrentDirectory()
    print(ConfigData.YamlFiles)
    
main()