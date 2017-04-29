
# coding: utf-8

# In[ ]:
import matplotlib
matplotlib.use('Qt5Agg')

import matplotlib.pyplot as plt

# for transforming to exe
# avoid module not found error
    
# configuration handler
import os.path
import configparser
import time


def follow(thefile):
    thefile.seek(0,2)
    while True:
        line = thefile.readline()
        if not line:
            time.sleep(0.1)
            continue
        yield line
    
class information_plotter:
    def __init__(self):
        self.raw_data_file_name = ""
        self.sliding_window_size = 0
        self.update_interval = 1.0
        self.plot_rows = 0
        self.plot_cols = 0
        self.cell_label_list = []
        self.group_list = []
        self.config_file_name = "information_plotter.cfg"
        self.color_list = ["blue", "green", "red", "cyan", "magenta", "yellow", "black"]
        self.plot_size_vertical = 10
        self.plot_size_horizontal = 10
        self.axs = []
        self.total_accumulated_data = [] # a list of list
        self.marker_size = 3
        
    def run(self):
        self.config = configparser.RawConfigParser()
        
        if not os.path.exists(self.config_file_name):
            print("File doest not exist. Generating cfg file...")
            self.init_log_file()
            print("Cfg generation complete [information_plotter.cfg]")
            return
        else:
            print("File exists. Reading cfg file...")
            self.set_up_plotting_information()
         
        self.fig = plt.figure(figsize=(self.plot_size_vertical,self.plot_size_horizontal))
        plt.ion() # enable interactive plotting
        
        # setup subplots
        total_group_count = len(self.group_list)
        for i in range(total_group_count):
            self.axs.append(self.fig.add_subplot(self.plot_rows, self.plot_cols, i+1))
            for tag, cell_label in enumerate(self.group_list[i]):
                self.axs[i].plot([1,2,3,4], [tag+1,tag+2,tag+3,tag+4], self.color_list[tag], label=cell_label)  # color ?
            self.axs[i].legend(loc='upper left')
        
        """
        round = 0
        while True:
            for i in range(total_group_count):
                for tag, cell_label in enumerate(self.group_list[i]):
                    self.axs[i].lines.pop(0) 
                    self.axs[i].plot([1,2,3,4], [round+tag,round+tag+1,round+tag+2,round+tag+3], self.color_list[tag], label=cell_label)
            round += 1
            plt.pause(self.update_interval)
        """
        
        
        current_line_part = []
        current_part = ""
        next_part = ""
        
        logfile = open(self.raw_data_file_name,"r")
        loglines = follow(logfile)
        for line in loglines:
            print(line)
            
            # collect all data
            input_data = line.split("\n")
            current_part = next_part + input_data[0]
            
            # buffered for next line input
            if len(input_data) > 1:
                next_part = input_data[1]
            else:
                next_part = ""
            
            current_line_part = current_part.split(",") #[data1, data2, ...]
            self.total_accumulated_data.append(current_line_part)
            
            # truncate for transaction count: sliding_window_size
            accumulated_length = len(self.total_accumulated_data)
            if accumulated_length > self.sliding_window_size:
                self.total_accumulated_data = self.total_accumulated_data[accumulated_length-self.sliding_window_size : accumulated_length]
            
            # plot the all the cumulated data after truncated
            self.plot_accumulated_data()
                
    def plot_accumulated_data(self):
        
        # initialize label-data mapping: label <-> a list of data
        # the 1st label is always used as the xticks
        data_dict = self.get_init_data_ticks()   
        xticks = [] # a list of SFNs in string
        
        #print(self.total_accumulated_data)
        for i, l in enumerate(self.total_accumulated_data):
            for j, d in enumerate(l):
                if j == 0:
                    data_dict["xticks"].append(d)
                else:
                    label = self.cell_label_list[j-1]
                    if(d == "NA"):
                        data_dict[label].append(0.0)
                    else:
                        data_dict[label].append(float(d))
       
        #print("current data dic status:\n")
        #print(data_dict)
                
        # plot each subplots (namely each group, which might contain same label with another group)
        # each subplot contains several lines to be compared with each other
        for i, gl in enumerate(self.group_list):
            for tag, cell_label in enumerate(gl):
                self.axs[i].lines.pop(0)             
                self.axs[i].plot(
                    data_dict["xticks"], 
                    data_dict[cell_label], 
                    self.color_list[tag], 
                    marker='o',
                    markersize=self.marker_size,
                    label=cell_label)
                self.axs[i].set_xlim(auto=True)
                self.axs[i].set_ylim(auto=True)
        
        plt.pause(self.update_interval)
                
        return
   
    def get_init_data_ticks(self):
        data_dict = {}
        data_dict["xticks"] = []
        
        for cell_label in self.cell_label_list:
            data_dict[cell_label] = []
            
        return data_dict

    def init_log_file(self):
        self.config.add_section('Common')
        self.config.set('Common', 'raw_data_file_name', 'test_raw_data') #test_raw_data SHOULD be replaced with real one
        self.config.set('Common', 'sliding_window_size', 30)
        self.config.set('Common', 'update_interval', 0.1)
        self.config.set('Common', 'plot_rows', 2)
        self.config.set('Common', 'plot_cols', 2)
        self.config.set('Common', 'plot_size_vertical', 10)
        self.config.set('Common', 'plot_size_horizontal', 10)
        self.config.set('Common', 'marker_size', 3)
        self.config.set('Common', 'cell_label_list', 'pcell,ncell_1,ncell_2')
        # grouping to show together in the same subplot
        self.config.set('Common', 'group#0', 'pcell')
        self.config.set('Common', 'group#1', 'ncell_1,ncell_2')
        
        with open(self.config_file_name, 'w') as configfile:
            self.config.write(configfile)
        return 
    
    def set_up_plotting_information(self):
        self.config.read(self.config_file_name)
        section_list = self.config.sections()
        for sl in section_list:
            if sl == 'Common':
                is_success = self.deal_common_section()
                if is_success == False:
                    print("cfg initialization failed.")
                    return
                else:
                    print("cfg initialization successed.")
        
    def deal_common_section(self):
        if self.config.has_option('Common', "raw_data_file_name"):
            self.raw_data_file_name = self.config.get('Common', 'raw_data_file_name')
        else:
            print("Now raw data file name is provided.")
            print("Please add \"raw_data_file_name = YOUR_RAW_DATA_FILE_NAME\" into the config file.")
            return False
        
        if self.config.has_option('Common', "cell_label_list"):
            self.cell_label_list = self.config.get('Common', 'cell_label_list').split(",")      
        else:
            print("Now cell label list is provided.")
            print("Please add \"cell_label_list = [CELL_LABEL_1,CELL_LABEL_2,...]\" into the config file.")
            return False
        
        group_num = 0
        while self.config.has_option('Common', "group#" + str(group_num)):
            self.group_list.append(self.config.get('Common', "group#" + str(group_num)).split(","))  
            group_num += 1
        
        try:
            self.sliding_window_size = self.config.getint('Common', 'sliding_window_size')
        except:
            self.sliding_window_size = 30
           
        try:
            self.update_interval = self.config.getfloat('Common', 'update_interval')
        except:
            self.update_interval = 1.0
         
        try:
            self.plot_rows = self.config.getint('Common', 'plot_rows')
        except:
            self.plot_rows = 2
        
        try:
            self.plot_cols = self.config.getint('Common', 'plot_cols')
        except:
            self.plot_cols = group_num / 2
         
        try:
            self.plot_size_vertical = self.config.getint('Common', 'plot_size_vertical')
        except:
            self.plot_size_vertical = 10
            
        try:
            self.plot_size_horizontal = self.config.getint('Common', 'plot_size_horizontal')
        except:
            self.plot_size_horizontal = 10
          
        try:
            self.marker_size = self.config.getint('Common', 'marker_size')
        except:
            self.marker_size = 3
            
        return True


ip = information_plotter()
ip.run()

        