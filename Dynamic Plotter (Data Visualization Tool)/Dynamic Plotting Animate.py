
# coding: utf-8

# In[ ]:
import matplotlib
matplotlib.use('Tkagg')

import matplotlib.pyplot as plt
import matplotlib.animation as animation

# for transforming to exe
# avoid module not found error
    
# configuration handler
import os.path
import configparser
import time
import numpy as np
import math
import sys
import msvcrt
from datetime import datetime

ip_stop_flag = True
replay_ip_stop_flag = True
stop_key_detect = False

class information_plotter:
    def __init__(self, is_replay_mode = False, dedicated_file=None):
        
        plt.close('all')
        
        self.is_replay_mode = is_replay_mode
        
        self.raw_data_file_name = ""
        self.sliding_window_size = 0
        self.update_interval = 10
        self.plot_rows = 0
        self.plot_cols = 0
        self.cell_label_list = []
        self.group_list = []
        self.comment_list = [] # for command input
        self.annotate_list = [] # for annotate object, which shows command
        self.group_comment_enable = []
        self.status_list = []  # for rectangel object, which shows status
        self.group_status_enable = []
        self.group_list_title = []
        self.group_list_xlabel = []
        self.group_list_ylabel = []
        self.config_file_name = "information_plotter.cfg"
        self.color_list = ["blue", "green", "red", "cyan", "magenta", "yellow", "black",
                           "#fefefe","#e0e0e0","#abcdef","#fedcba"]
        self.cell_color_mapping = {}
        self.plot_size_vertical = 10
        self.plot_size_horizontal = 10
        self.axs = []
        self.total_accumulated_data = [] # a list of list
        self.marker_size = 3
        
        self.status_input_list = []
        self.status_prop_list = []
        self.status_enable_list = []
        self.total_status_count = 0
        self.status_font_size = 0
        self.comment_font_size = 0

        self.config = configparser.RawConfigParser()
        self.is_first_time_use = False
        
        if not os.path.exists(self.config_file_name):
            #print("File doest not exist. Generating cfg file...")
            global_print("File doest not exist. Generating cfg file...")
            self.init_log_file()
            #print("Cfg generation complete [information_plotter.cfg]")
            global_print("Cfg generation complete: [information_plotter.cfg]")
            tmBox.showinfo("Configuration Generation", "[information_plotter.cfg] generated. Use it for Dynamic Plotter's configuration!")
            self.is_first_time_use = True
        else:
            #print("Cfg File exists.")
            global_print("Cfg File exists.")
            
        #print("Initialzing from cfg file...")
        global_print("Initialzing from cfg file...")
        self.set_up_plotting_information()
        
        
        self.fig = plt.figure(figsize=(self.plot_size_horizontal,self.plot_size_vertical))
        self.ani_created = False
        self.is_replay_mode = is_replay_mode
        
        if dedicated_file is not None:
            self.raw_data_file_name = dedicated_file
       
        
        try:
            self.logfile = open(self.raw_data_file_name,"r") 
        except FileNotFoundError as f:
            tmBox.showerror("File not found error", str(f))
            
        if is_replay_mode:
            
            current_path = os.path.dirname(os.path.abspath(__file__))
            current_path = current_path + '\\ffmpeg\\bin\\ffmpeg.exe'
            #print("Init replay object...\n")
            global_print("Init replay object...\n")
            #print("The ffmpeg.exe for video converting should be in the following path:")
            global_print("The ffmpeg.exe for video converting should be in the following path:")
            #print(current_path)
            global_print(current_path)
            #print("If error occurrs, please inform mtk13645 for bug report")
            global_print("If error occurrs, please inform mtk13645 for bug report")
            
            
            plt.rcParams['animation.ffmpeg_path'] = current_path
            plt.rcParams['animation.ffmpeg_args'] = '-report'
        
            try:
                Writer = animation.writers['ffmpeg']
                # save the animation as an mp4.  This requires ffmpeg or mencoder to be
                # installed.  The extra_args ensure that the x264 codec is used, so that
                # the video can be embedded in html5.  You may need to adjust this for
                # your system: for more information
                self.writer = Writer(fps=5, metadata=dict(artist='Kun-Hao Yeh'), bitrate=1800, extra_args=['-vcodec', 'libx264'])
            except RuntimeError as e:
                global_print("Runtime error occurred: " + str(e))
                
                tmBox.showerror("Runtime error", str(e))
                
                if str(e) == "No MovieWriters available!":
                    tmBox.showerror(
                        "Runtime error occurred: " + str(e),
                        "Please download ffmpeg at https://ffmpeg.org/" +
                        "\nThen put the unzipped directory in the same path with [Dynamic Plotter.exe]")
                global app
                app.close(ask=False)
    
    def close(self):
        self.logfile.close()
        plt.clf()
        
    def is_first_time(self):
        temp = self.is_first_time_use
        self.is_first_time_use = False
        return temp
    
    def ini_setting(self):
        # setup subplots
        total_group_count = len(self.group_list)
        for i in range(total_group_count):
            self.axs.append(self.fig.add_subplot(self.plot_rows, self.plot_cols, i+1))
            for tag, cell_label in enumerate(self.group_list[i]):
                self.axs[i].plot([], [ ], self.cell_color_mapping[cell_label], label=cell_label)  # color ?
            self.axs[i].legend(loc='upper left')
        self.ondraw()
        
        self.logfile.seek(0,0) # read from the begin
        self.line_data = ""
            
    def follow(self):
        
        global ip_stop_flag, replay_ip_stop_flag
        count = 0
               
        while True:
           
            line = self.logfile.readline()
            
            if (ip_stop_flag == True and self.is_replay_mode == False) or (replay_ip_stop_flag == True and self.is_replay_mode == True):
                #print("infomation plotter stops")
                global_print("infomation plotter stops")
                #plt.close()
                break;
            elif not line:
                if self.is_replay_mode == True:
                    break
                time.sleep(0.1)
                continue
            yield line

    def start(self):
        global is_ip_running
        self.ani = animation.FuncAnimation(self.fig, self.run, self.follow, blit=False, interval=self.update_interval,
                              repeat=False, init_func=self.ini_setting)
        
        self.ani_created = True
         
        if self.is_replay_mode:
            time_string = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            time_string = time_string + ".mp4"
            self.ani.save(time_string, writer=self.writer) 
            global_print("Video Conversion Complete!")
            global_print("Video: " + time_string)
            
        else:
            plt.show(block=False)
        
        #print("!!!Start function end!!!")
        self.close()
        plt.close()
        
        return
       
    def run(self, line):
        
        if line == "":
            return
        
        cell_label_count = len(self.cell_label_list)
        status_input_count = self.total_status_count
        
        #self.line_data += loglines
        #print(self.line_data) 
        #print(line)
            
        # collect all data
        input_data = line.split("\n")
        current_part = input_data[0]
            
        current_line_part = current_part.split(",") #[data1, data2, ...]
        self.total_accumulated_data.append(current_line_part[0:cell_label_count+1]) # add one for label
        self.comment_list.append(current_line_part[cell_label_count+1])
        self.status_input_list.append(current_line_part[cell_label_count+2:])
            
        # truncate for transaction count: sliding_window_size
        accumulated_length = len(self.total_accumulated_data)
        if accumulated_length > self.sliding_window_size:
            self.total_accumulated_data = self.total_accumulated_data[accumulated_length-self.sliding_window_size : accumulated_length]
            self.comment_list = self.comment_list[accumulated_length-self.sliding_window_size : accumulated_length]
            self.status_input_list = self.status_input_list[accumulated_length-self.sliding_window_size : accumulated_length]
                
        # plot the all the cumulated data after truncated
        self.plot_accumulated_data()
        #plt.pause(self.update_interval)
        self.ondraw()
         
    def plot_accumulated_data(self):
        
        # initialize label-data mapping: label <-> a list of data
        # the 1st label is always used as the xticks
        data_dict = self.get_init_data_ticks()   
        
        # process acuumulated data
        for i, l in enumerate(self.total_accumulated_data):
            for j, d in enumerate(l):
                if j == 0:
                    data_dict["xticks"].append(d)
                else:
                    label = self.cell_label_list[j-1]
                    if(d == "NA"):
                        data_dict[label].append(None) #draw ignore missing data 
                    else:
                        data_dict[label].append(float(d))
                
        # all subplots share the same xticks
        plt.setp(self.axs, xticks=np.arange(len(data_dict["xticks"]))+1, xticklabels=data_dict["xticks"])
         
        # plot each subplots (namely each group, which might contain same label with another group)
        # each subplot contains several lines to be compared with each other
        for i, gl in enumerate(self.group_list):
            self.axs[i].set_xlim(left=0, right=len(data_dict["xticks"])+1)    
            for tag, cell_label in enumerate(gl):
                self.axs[i].lines.pop(0) 
                
                xvalues = np.arange(len(data_dict["xticks"]))+1
                yvalues = np.array(data_dict[cell_label]).astype(np.double)
                mask = np.isfinite(yvalues)
                
                self.axs[i].plot(
                    xvalues[mask], 
                    yvalues[mask], 
                    self.cell_color_mapping[cell_label], 
                    marker='o',
                    markersize=self.marker_size,
                    label=cell_label)
          
            self.axs[i].set_title(self.group_list_title[i])
            self.axs[i].set_xlabel(self.group_list_xlabel[i])
            self.axs[i].set_ylabel(self.group_list_ylabel[i])
            #self.axs[i].set_ylim(auto=True) # bottom=ylim[0]-10, top=ylim[1]+10)
            # recompute the ax.dataLim
            self.axs[i].relim()
            # update ax.viewLim using the new dataLim
            self.axs[i].autoscale_view()
            
            self.plot_annotate(i, data_dict)        
            self.plot_status(i)    
                
        return
    
    
    def ondraw(self): 
        plt.draw()

        
    def clear_plot_annotate(self, ax_index):
        # clear existing annotate
        for annotate in self.annotate_list[ax_index]:
            annotate.remove()
        for x in range(len(self.annotate_list[ax_index])):
            self.annotate_list[ax_index].pop(0)
            
    def plot_annotate(self, ax_index, data_dict):
        # check if this group is to show annotation
        
        total_comment_num = len(self.comment_list)
        if self.group_comment_enable[ax_index] == True:
            self.clear_plot_annotate(ax_index)

            # update annotate with new comments
            last_comment = ""
            for c, comment in enumerate(self.comment_list):
                if comment == "NA":
                    continue;
            
                if last_comment == "" or last_comment != comment:
                    last_comment = comment
                else:
                    continue
                    
                ypos_list = [data_dict[cell_label][c] for cell_label in self.group_list[ax_index]]
                ypos_list_without_none = [y for y in ypos_list if y is not None]
                min_y = min(ypos_list_without_none)
                max_y = max(ypos_list_without_none)
                offset = (max_y-min_y) / total_comment_num
                
                ylim = self.axs[ax_index].get_ylim()
                
                self.annotate_list[ax_index].append(
                    matplotlib.text.Annotation(
                        comment, 
                        xy=((c+1)/(total_comment_num+1), (min_y-ylim[0])/(ylim[1]-ylim[0])), xycoords='axes fraction', 
                        xytext=((c+1)/(total_comment_num+1),  0.1+(min_y-ylim[0])/(ylim[1]-ylim[0])), textcoords='axes fraction',
                        arrowprops=dict(visible=False), fontsize=self.comment_font_size, rotation=345
                    )
                )
                self.axs[ax_index].add_artist(self.annotate_list[ax_index][len(self.annotate_list[ax_index])-1])

    def clear_plot_status(self, ax_index):
        # clear existing status bar
        for st in self.status_list[ax_index]:
            st.remove()
        for x in range(len(self.status_list[ax_index])):
            self.status_list[ax_index].pop(0)
            
    def plot_status(self, ax_index):              
        
        if self.group_status_enable[ax_index] == True:
            self.clear_plot_status(ax_index)
           
            # iterate each status transaction
            total_data_count = len(self.status_input_list)
            last_final_status_string_list = []
            for input_count, sil in enumerate(self.status_input_list):
                
                # process each status bar
                counter = 0
                total_active_status_num = self.status_enable_list.count(True)
                used_prop_count = 0
                for pl_count, pl in enumerate(self.status_prop_list):
                    if self.status_enable_list[pl_count] == True:
                            
                        # each status bar = a collection of single property list with corresponding input values
                        final_status_string = ""
                        for p_count, p in enumerate(pl):
                            if p_count == 0:
                                final_status_string += (p + "=" + sil[counter])
                            else:
                                final_status_string += ("," + p + "=" + sil[counter])
                            counter += 1
        
                        # do not draw for the case that the last status is the same
                        # while the first status is always drawn
                        if input_count == 0:
                            last_final_status_string_list.append(final_status_string)
                        elif last_final_status_string_list[used_prop_count] == final_status_string:
                            used_prop_count += 1
                            continue; 
                        else:
                            last_final_status_string_list[used_prop_count] = final_status_string
                        used_prop_count += 1
                            
                        # draw the rectangle for that status
                        props = dict(boxstyle='round,pad=0', edgecolor='black', facecolor=self.color_list[pl_count], alpha=0.5)
                        
                        vertical_divisions = total_active_status_num + 10
                        offset = 2
                        sp_space =  vertical_divisions/2 - offset - total_active_status_num
                        x = (input_count + 1) / (total_data_count + 1)
                        y = (1-(pl_count + offset)/vertical_divisions)

                        if input_count % 2 == 1:
                            y = (0.5 - (sp_space + pl_count)/vertical_divisions) 

                        self.status_list[ax_index].append(
                            matplotlib.text.Text( 
                                x,y,
                                final_status_string,
                                transform=self.axs[ax_index].transAxes,
                                style='italic',
                                fontsize=self.status_font_size,
                                horizontalalignment='center',
                                verticalalignment='center',
                                bbox=props
                                )
                        )
                        self.axs[ax_index].add_artist(self.status_list[ax_index][len(self.status_list[ax_index])-1])
                           
                    
    def get_init_data_ticks(self):
        data_dict = {}
        data_dict["xticks"] = []
        
        for cell_label in self.cell_label_list:
            data_dict[cell_label] = []
            
        return data_dict

    def init_log_file(self):
        self.config.add_section('Common')
        self.config.set('Common', 'raw_data_file_name', 'test_raw_data') #test_raw_data SHOULD be replaced with real one
        self.config.set('Common', 'sliding_window_size', 20)
        self.config.set('Common', 'update_interval', 0.5)
        self.config.set('Common', 'plot_rows', 2)
        self.config.set('Common', 'plot_cols', 1)
        self.config.set('Common', 'plot_size_vertical', 10)
        self.config.set('Common', 'plot_size_horizontal', 20)
        self.config.set('Common', 'marker_size', 3)
        self.config.set('Common', 'cell_label_list', 'Pcell,nCell_1,nCell_2,nCell_3,nCell_4')
        self.config.set('Common', 'status font size', '10')
        self.config.set('Common', 'comment font size', '10')
        
        # grouping to show together in the same subplot
        self.config.add_section('group#0')
        self.config.set('group#0', 'list', 'Pcell,nCell_1,nCell_2,nCell_3,nCell_4')
        self.config.set('group#0', 'title', 'All Cells')
        self.config.set('group#0', 'x-label', 'SFN')
        self.config.set('group#0', 'y-label', 'RSRP')
        self.config.set('group#0', 'show annotation', True)
        self.config.set('group#0', 'show status', True)
        
        self.config.add_section('group#1')
        self.config.set('group#1', 'list', 'nCell_1,nCell_2,nCell_3,nCell_4')
        self.config.set('group#1', 'title', 'Neighbor Cells Only')
        self.config.set('group#1', 'x-label', 'SFN')
        self.config.set('group#1', 'y-label', 'RSRP')
        self.config.set('group#1', 'show annotation', False)
        self.config.set('group#1', 'show status', False)

        # each group can decide whether to show these status bar
        self.config.add_section('status#0')
        self.config.set('status#0', 'prop_list', 'ch')
        self.config.set('status#0', 'enabled', True)
        
        self.config.add_section('status#1')
        self.config.set('status#1', 'prop_list', 'earfcn,pci')
        self.config.set('status#1', 'enabled', True)
        
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
                    #print("cfg initialization failed.")
                    global_print("cfg initialization failed.")
                    return
                else:
                    #print("cfg initialization successed.")
                    global_print("cfg initialization successed.")
    
    def deleteRawDataContent(self):
        if self.is_replay_mode:
            return
        
        with open(self.raw_data_file_name, "w") as temp:
            temp.close()
    
    def deal_common_section(self):
        if self.config.has_option('Common', "raw_data_file_name"):
            self.raw_data_file_name = self.config.get('Common', 'raw_data_file_name')
            self.deleteRawDataContent()
        else:
            global_print("Now raw data file name is provided.")
            global_print("Please add \"raw_data_file_name = YOUR_RAW_DATA_FILE_NAME\" into the config file.")
            return False
        
        if self.config.has_option('Common', "cell_label_list"):
            self.cell_label_list = self.config.get('Common', 'cell_label_list').split(",")      
        else:
            global_print("Now cell label list is provided.")
            global_print("Please add \"cell_label_list = [CELL_LABEL_1,CELL_LABEL_2,...]\" into the config file.")
            return False
        
        group_num = 0
        while self.config.has_section("group#" + str(group_num)):
            section_name = "group#" + str(group_num)
            self.group_list.append(self.config.get(section_name, "list").split(","))
            self.group_list_title.append(self.config.get(section_name, "title"))
            self.group_list_xlabel.append(self.config.get(section_name, "x-label"))
            self.group_list_ylabel.append(self.config.get(section_name, "y-label"))
            self.group_comment_enable.append(self.config.getboolean(section_name, "show annotation"))
            self.group_status_enable.append(self.config.getboolean(section_name, "show status"))
            group_num += 1
            
        status_bar_count = 0
        while self.config.has_section("status#" + str(status_bar_count)):
            section_name = "status#" + str(status_bar_count)
            prop_list = self.config.get(section_name, "prop_list").split(",")
            self.status_prop_list.append(prop_list)
            self.total_status_count += len(prop_list)
            self.status_enable_list.append(self.config.getboolean(section_name, "enabled"))
            status_bar_count += 1
        
        for i, s in enumerate(self.group_list):
            self.annotate_list.append([])
            self.status_list.append([])
            
        availble_color_count = len(self.color_list)    
        for i, s in enumerate(self.cell_label_list):
            self.cell_color_mapping[s] = self.color_list[i%availble_color_count]
            
        try:
            self.sliding_window_size = self.config.getint('Common', 'sliding_window_size')
        except:
            self.sliding_window_size = 5
           
        try:
            self.update_interval = self.config.getint('Common', 'update_interval')
        except:
            self.update_interval = 10
         
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
            self.plot_size_vertical = 5
            
        try:
            self.plot_size_horizontal = self.config.getint('Common', 'plot_size_horizontal')
        except:
            self.plot_size_horizontal = 5
          
        try:
            self.status_font_size = self.config.getint('Common', 'status font size')
        except:
            self.status_font_size = 10
             
        try:
            self.comment_font_size = self.config.getint('Common', 'comment font size')
        except:
            self.comment_font_size = 10
            
        return True

    
from tkinter import *
from tkinter.filedialog import askopenfilename
import tkinter.messagebox as tmBox

class Application(Frame):
    def __init__(self,master):
        self.frame = Frame.__init__(self,master, width = 68, height = 35)
        #self.frame.pack(fill=tk.BOTH, expand=1)
        
        self.grid()
        self.is_ip_running = False
        self.is_replay_ip_running = False
        
        self.create_widgets()
        
    def create_widgets(self):
        self.start_button = Button(self, text="Start Plotting")
        self.start_button["command"] = self.start_recording
        self.start_button.grid(row = 0, column = 0, sticky=W)
        
        self.replay_button = Button(self, text="Convert Video")
        self.replay_button["command"] = self.start_replaying
        self.replay_button.grid(row = 0, column = 1, sticky=W)
   
        self.text = Text(self.master, width = 68, height = 35, wrap = WORD)
        self.vertscroll = Scrollbar(self.master)
        self.vertscroll.config(command=self.text.yview)
        self.text.config(yscrollcommand=self.vertscroll.set)
        self.text.grid(column = 0, row = 2)
        self.vertscroll.grid(column=2, row=2, sticky='NS')
  
        
    def stop(self):
        self.is_ip_running = False
        self.is_replay_ip_running = False
        
    def start_recording(self):
        global ip_stop_flag
        
        #print("Press start")
        
        if(self.is_ip_running):
            return
        
        ip = information_plotter()
        
        if ip.is_first_time() and not tmBox.askyesno("Config the Plotter", "Do you want to use default configuration?"):
            ip.close()
            pass
        else:
            self.is_ip_running = True
            ip_stop_flag = False
            ip.start()        
            
            self.start_replaying(ask=True)
        
    def start_replaying(self, ask=False):
        global replay_ip_stop_flag
        
        if self.is_ip_running or self.is_replay_ip_running:
            return
        
        if ask == False or tmBox.askyesno("Convert Video", "Do you want to save the video ?"):
            
            if ask == False: # replay mode
                filename = askopenfilename()
                if filename == "":
                    return
                global_print("Enter replay mode")
                global_print("Selected file: " + filename)
            else:
                filename = None
                global_print("Generating video from the records...")
            
            self.is_replay_ip_running = True
            replay_ip_stop_flag = False
            replay_ip = information_plotter(is_replay_mode=True, dedicated_file=filename)
            replay_ip.start()
            self.is_replay_ip_running = False


    def close(self, ask=True):
        global stop_key_detect
        if ask == False or tmBox.askokcancel("Quit", "Do you want to quit?"):
            stop_key_detect = True
            self.master.destroy()
            sys.exit()
            

    def add_to_console(self, output):
        # insert text to the GUI
        output = output + "\n"
        self.text.insert(END,output)

from threading import Thread
import win32con, ctypes, ctypes.wintypes

def handle_stop():
    global ip_stop_flag, replay_ip_stop_flag
    #print("Stop request sent!!!")
    ip_stop_flag = True
    replay_ip_stop_flag = True
    app.stop()

def threaded_function():
    
    global stop_key_detect
    
    #ctypes.windll.user32.RegisterHotKey(None, 1, 0, win32con.VK_F1)
    #ctypes.windll.user32.RegisterHotKey(None, 2, 0, win32con.VK_F2)
    ctypes.windll.user32.RegisterHotKey(None, 3, 0, win32con.VK_F3)
    
    
    try:
        msg = ctypes.wintypes.MSG()
        
        while True:
            if ctypes.windll.user32.PeekMessageA(msg, None, 0, 0, win32con.PM_NOREMOVE) != 0:
                ctypes.windll.user32.GetMessageA(ctypes.byref(msg), None, 0, 0)
                if msg.message == win32con.WM_HOTKEY:
                    if msg.wParam == 1:
                        app.start_recording()
                    elif msg.wParam == 2:
                        app.start_replaying()
                    elif msg.wParam == 3:
                        handle_stop()
                    
                    #print(msg.wParam) # can be used as another short cut key
                
                ctypes.windll.user32.TranslateMessage(ctypes.byref(msg))
                ctypes.windll.user32.DispatchMessageA(ctypes.byref(msg))
            
            if stop_key_detect:
                ctypes.windll.user32.UnregisterHotKey(None, 3)
                return
    finally:
        ctypes.windll.user32.UnregisterHotKey(None, 1)
        ctypes.windll.user32.UnregisterHotKey(None, 2)
        ctypes.windll.user32.UnregisterHotKey(None, 3)
        

def global_print(output):
    global app
    app.add_to_console(output)

def print_test():
    counter = 0
    while(counter < 100):
        counter += 1
        global_print("this is a test")
        

try:
    root = Tk()
    root.title("Dynamic Plotter (Ver 2.0)")
    root.geometry("500x500")
    root.resizable(0, 0)
    app = Application(root)


    keyboard_detect = Thread(target = threaded_function,)
    keyboard_detect.start()
    global_print("key board stroker thread running")

    root.protocol("WM_DELETE_WINDOW", app.close)
    root.mainloop()
    keyboard_detect.join()
    
except RuntimeError as e:
    global_print("Runtime error occurrs: " + str(e))
    global_print("Please email to Kun-Hao.Yeh@mediatek.com for bug report, thank you!")
        