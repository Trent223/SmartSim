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