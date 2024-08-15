"""
Soham Mutalik Desai
Commander Schenk
3rd period IST
Master Project GUI class
Started: 3/25/24
"""

# Tkinter imports
import tkinter as tk
from tkinter import ttk
from typing import Any, Callable
import tksheet
from tkinter import messagebox

# To Create Ids
import string
import random
 
# For the graphs
import numpy as np
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk

# Open a website
from webbrowser import open as open_url, Error as WebBrowserErr

# Run tasks with the web scraper, etc. Makes program more responsive because threads run simultaneously with it
from threading import Thread

# For catching errors
from requests.exceptions import ConnectionError
from deep_translator.exceptions import RequestError
from deep_translator.exceptions import NotValidLength
from langdetect.lang_detect_exception import LangDetectException

# Poco classes + Enums
from masterDb import MasterDb
from jsonhandler import JsonHandler
from webhandler import WebScraper
from imagehandler import ImageHandler
from master_enums import *
from langHandler import LangHandler
from errorsWhyNot import *


class GUI:

    """Master Project GUI"""
    
    # All fields safely initialized
    def __init__(self) -> None:
        
        # Making the tk object 'root' and setting sizing attributes and name of window
        root = tk.Tk()
        root.geometry("900x680")
        root.resizable(False, False)
        root.title("Tennis Player Registry")
        self.root = root

        # VARS to handle operations                                                                                                             
        self.updateCommit, self.addCommit, self.connected, self.emptyDb = False, False, False, False                
        self.sorted_recs, self.records, self.match_ids = [], [], []
        self.img, self.tab_img = None, ""
        self.index, self.topIndex = 0, 0
        self.sort_type: str = "None"
        self.tab_dict: dict[str, list[tuple, tk.PhotoImage]] = {}
        self.narrowed_search, self.search_list = [], []
        self.news_mode: NewsViewMode = NewsViewMode.FINDER
        self.news_scroller_index, self.news_scroller_topindex = 0, 0
        self.news_articles = []

        # Connector object + json handler obj
        self.connector = MasterDb()
        self.json_handler = JsonHandler()
        self.web_scraper = WebScraper()
        self.image_handler = ImageHandler()
        self.lang_handler = LangHandler()

        # Get settings from json
        settings = self.json_handler.get_settings()
        self.graph_color_dict = settings[0]
        self.languages = settings[1]
        self.current_language = settings[2]
        custom_themes = settings[3]
        bg_img = settings[4]

        # Create a ttk notebook which will allow for tab control in the window
        self.notebook = ttk.Notebook()

        # Creating our tabs
        self.homeTab = ttk.Frame(self.notebook)
        self.listView = ttk.Frame(self.notebook)
        self.graphTab = ttk.Frame(self.notebook)
        self.latest_news_tab = ttk.Frame(self.notebook)

        # Adding tabs to the notebook
        self.notebook.add(self.homeTab, text="Home")
        self.notebook.add(self.listView, text="Search")
        self.notebook.add(self.graphTab, text="Graph View")
        self.notebook.add(self.latest_news_tab, text="Latest News")
        self.notebook.pack(expand=1, fill="both")

        # Setting bg image label for self.homeTab
        self.homeTab_bg = tk.Label(self.homeTab)
        self.homeTab_bg.place(x=-10,y=-10)

        # Setting bg image label for search tab
        self.listView_bg = tk.Label(self.listView)
        self.listView_bg.place(x=-10,y=-10)

        # Setting bg image label for graph tab
        self.graph_bg = tk.Label(self.graphTab)
        self.graph_bg.place(x=-10,y=-10)

        # For the news tab too
        self.lat_news_bg = tk.Label(self.latest_news_tab)
        self.lat_news_bg.place(x=-10,y=-10)

        # Drop box that contains all of the matches the user has put in
        self.drop_box = ttk.Combobox(state="readonly", master=self.graphTab, width=30)

        # Making and adding my menu
        self.appMenu = tk.Menu(root)
        file_menu = tk.Menu(self.appMenu, tearoff=0)
        analysis_menu = tk.Menu(self.appMenu, tearoff=0)
        themes_menu = tk.Menu(analysis_menu, tearoff=0)
        help_menu = tk.Menu(self.appMenu, tearoff=0)
        self.custom_themes_menu = tk.Menu(analysis_menu, tearoff=0)
        self.news_menu = tk.Menu(self.appMenu, tearoff=0)
        self.news_mode_menu = tk.Menu(self.news_menu, tearoff=0)
        languages_menu = tk.Menu(self.news_menu, tearoff=0)
        self.bg_menu = tk.Menu(file_menu, tearoff=0)

        # Mode buttons news menu
        self.news_mode_menu.add_radiobutton(label="Finder Mode (Default)", command=lambda x=NewsViewMode.FINDER: self.switchNewsViewMode(mode=x))
        self.news_mode_menu.add_radiobutton(label="Db mode", command=lambda x=NewsViewMode.SCROLLER: self.switchNewsViewMode(mode=x))

        # Adding stuff to the news menu
        self.news_menu.add_cascade(label="Change Mode", menu=self.news_mode_menu)
        self.news_menu.add_cascade(label="News Lang. Translation", menu=languages_menu)
        self.news_menu.add_command(label="Open in Browser", command=self.open_website)
        self.news_menu.add_command(label="Save Current Article", command=self.save_article)
        self.news_menu.add_command(label="Update Current Article", command=self.update_article)
        self.news_menu.add_command(label="Delete Current Article", command=self.delete_article)

        # Help menu work
        help_menu.add_command(label="About", command=self.about_info)

        # Looping through the options creating radiobuttons for the sort listbox menu
        sort_menu = tk.Menu(file_menu, tearoff=0)
        sort_options: list[str] = ["None", "Rank", "Ratio", "Age"]
        lang_list: list[str] = ["English", "Spanish", "French", "German", "Chinese", "Korean", "Arabic", "Marathi"]
        bg_list: list[str] = ["Clay", "Grass"]

        # Sorting options in the menu
        for x in sort_options:
            sort_menu.add_radiobutton(label=x, command=lambda opt=x: self.listbox_sorter(option=opt))

        # Same looping for themes menu
        themes: list[str] = ["Regular", "Monokai", "Dracula", "One Dark Pro", "Material", "Night Owl", "Solarized Dark"]
        for i in themes:
            themes_menu.add_radiobutton(label=i, command=lambda opt=i: self.change_graph_theme(theme=opt))

        # Load custom user themes from the json file and loop through once more for cutom menu buttons
        for x in custom_themes:
            self.custom_themes_menu.add_radiobutton(label=f"{x}", command=lambda opt=str(x): self.custom_theme_handler(name=opt))

        # Add languages to menu
        for x in lang_list:
            languages_menu.add_radiobutton(label=x, command=lambda opt=x: self.change_language(lang=opt))

        # If there are no custom themes, just put none in there
        if (len(custom_themes) == 0):
            self.custom_themes_menu.add_command(label="None", command=self.doNothing)

        # Add the bg options to that menu
        for x in bg_list:
            self.bg_menu.add_radiobutton(label=x, command=lambda opt=x: self.set_bg_img_type(name=opt))
                
        # Adding the submenus to their associated menus, arranging things
        file_menu.add_cascade(label="Sort List View", menu=sort_menu)
        file_menu.add_command(label="Remove all tabs", command=self.remove_all_tabs)
        file_menu.add_command(label="Advanced Settings Config.", command=self.json_config_win)
        analysis_menu.add_command(label="New Analysis", command=lambda x=False, rec=None, rec2=None, names=None: self.match_data_win(update_mode=x, rec=rec, rec2=rec2, names=names))
        analysis_menu.add_command(label="Edit Current Analysis", command=self.update_analysis)
        analysis_menu.add_command(label="Delete Current Analysis", command=self.del_analysis)
        analysis_menu.add_cascade(label="Graph Themes", menu=themes_menu)
        analysis_menu.add_cascade(label="Custom themes", menu=self.custom_themes_menu)
        file_menu.add_command(label="Add Custom Graph Theme", command=lambda: self.custom_theme_win(None, None, None))
        file_menu.add_cascade(label="Set Background", menu=self.bg_menu)
        file_menu.add_command(label="Edit Current Theme", command=self.edit_current_theme)
        file_menu.add_separator()
        file_menu.add_command(label="EXIT", command=self.exit_command)
        self.appMenu.add_cascade(label="File", menu=file_menu)
        self.appMenu.add_command(label="Connect", command=self.connectionManager)
        self.appMenu.add_cascade(label="Analysis settings", menu=analysis_menu)
        self.appMenu.add_cascade(label="News", menu=self.news_menu)
        self.appMenu.add_cascade(label="Help", menu=help_menu)

        # Setting the menu
        root.config(menu=self.appMenu)

        # Wigdets for the Add New tab, where the user will be able to add a new player
        self.namelbl = tk.Label(self.homeTab, text="Name:", font=("Cascadia code", 14, "bold"), fg="white", bg="#282626")
        self.namelbl.place(x=60,y=55)

        # Name typed in here
        self.namebox = tk.Text(self.homeTab, width=25, height=1, font=("Cascadia code", 13))
        self.namebox.place(x=125,y=58)

        # 'Age' is shown on a label
        self.agelbl = tk.Label(self.homeTab, text="Age:", font=("Cascadia code", 14, "bold"), fg="white", bg="#282626")
        self.agelbl.place(x=60, y=110)
        
        # User types info here
        self.agebox = tk.Text(self.homeTab, height=1, width=5, font=("Cascadia code", 13))
        self.agebox.place(x=113, y=114)

        # Labels rank
        self.ranklbl = tk.Label(self.homeTab, text="Global Rank:", font=("Cascadia code", 14, "bold"), fg="white", bg="#282626")
        self.ranklbl.place(x=60, y=165)

        # User types info here
        self.rankbox = tk.Text(self.homeTab, width=10, height=1, font=("Cascadia code", 13))
        self.rankbox.place(x=200, y=169)

        # Says W
        self.winlbl = tk.Label(self.homeTab, text=" W ", font=("Cascadia code", 14, "bold"), fg="white", bg="#282626")
        self.winlbl.place(x=59, y=215)

        # User types info here, number of wins
        self.winbox = tk.Text(self.homeTab, width=3,height=1, font=("Cascadia code", 13))
        self.winbox.place(x=62, y=250)
        
        # Says L
        self.loselbl = tk.Label(self.homeTab, text="  L  ", font=("Cascadia code", 14, "bold"), fg="white", bg="#282626")
        self.loselbl.place(x=106,y=215)

        # User types info here, number of losses
        self.losebox = tk.Text(self.homeTab, width=3,height=1, font=("Cascadia code", 13))
        self.losebox.place(x=120, y=250)

        # Takes the numbers of wins and losses and gives back a ratio
        self.calculate_ratio_btn = tk.Button(self.homeTab, text="Calculate -->", command=self.calculate_ratio, bg="#1e1e1e", fg="White", font=("cascadia code", 9))
        self.calculate_ratio_btn.place(x=174, y=250)

        self.ratiolbl = tk.Label(self.homeTab, text="Ratio", font=("Cascadia code", 14, "bold"), fg="white", bg="#282626")
        self.ratiolbl.place(x=289, y=215)

        # That ratio is displayed here
        self.ratiobox = tk.Text(self.homeTab, width=5,height=1, font=("Cascadia code", 13))
        self.ratiobox.place(x=292,y=250)

        # Says 'achievements'
        self.achievementlbl = tk.Label(self.homeTab, text="Achievements", font=("Cascadia code", 14, "bold"), fg="white", bg="#282626")
        self.achievementlbl.place(x=60, y=300)

        # User types info here, notable wins, achievements, etc.
        self.achievementsbox = tk.Text(self.homeTab, width=36, height=9, font=("Cascadia code light", 11))
        self.achievementsbox.place(x=61, y=331)

        # This is to create the black bar at the bottom of the window that sits behind the buttons and feedback label
        self.btn_canvas = tk.Canvas(self.homeTab, width=1000, height=100)
        self.btn_canvas.place(x=-10, y=580)
        self.btn_canvas.create_rectangle(0,0,self.btn_canvas.winfo_reqwidth(), self.btn_canvas.winfo_reqheight(), fill="#1A1A1A", outline="#1A1A1A")

        # This is to create the black bar at the bottom of the window that sits behind the buttons and feedback label
        self.list_canvas = tk.Canvas(self.listView, width=1000, height=100)
        self.list_canvas.place(x=-10, y=580)
        self.list_canvas.create_rectangle(0,0,self.btn_canvas.winfo_reqwidth(), self.btn_canvas.winfo_reqheight(), fill="#1A1A1A", outline="#1A1A1A")

        # This is to create the black bar at the bottom of the window that sits behind the buttons and feedback label
        self.graph_canvas = tk.Canvas(self.graphTab, width=1000, height=100)
        self.graph_canvas.place(x=-10, y=580)
        self.graph_canvas.create_rectangle(0,0,self.btn_canvas.winfo_reqwidth(), self.btn_canvas.winfo_reqheight(), fill="#1A1A1A", outline="#1A1A1A")

        # This is to create the black bar at the bottom of the window that sits behind the buttons and feedback label
        self.lat_new_canvas = tk.Canvas(self.latest_news_tab, width=1000, height=100)
        self.lat_new_canvas.place(x=-10, y=580)
        self.lat_new_canvas.create_rectangle(0,0,self.btn_canvas.winfo_reqwidth(), self.btn_canvas.winfo_reqheight(), fill="#1A1A1A", outline="#1A1A1A")


        # For user feedback, gets configured every time I have to warn the user or let them know something
        self.feedbacklbl = tk.Label(self.homeTab, text="System: ", fg="white", bg="#1a1a1a")
        self.feedbacklbl.place(x=8, y=630)
        self.feedbacklbl.lift()


        # From here, all of my scroll and crud buttons that have been gridded into the frame above
        self.goToFirst = tk.Button(self.homeTab, text="|<--", command=lambda incr=0,key="First": self.switchRec(increment=incr, key=key), width=5,height=2)
        self.goToFirst.place(x=10, y=590)

        # Go back three records
        self.back_three = tk.Button(self.homeTab, text="<<<", command=lambda incr=3,key="Backward Three": self.switchRec(increment=incr, key=key), width=5,height=2)
        self.back_three.place(x=65, y=590)

        # Back 1
        self.prevRecBtn = tk.Button(self.homeTab, text="<--", command=lambda incr=1,key="Backward": self.switchRec(increment=incr, key=key), width=5,height=2)
        self.prevRecBtn.place(x=120, y=590)

        # Forward 1
        self.nextRecBtn = tk.Button(self.homeTab, text="-->", command=lambda incr=1,key="Forward": self.switchRec(increment=incr, key=key), width=5,height=2)
        self.nextRecBtn.place(x=175, y=590)

        # Forward three
        self.fd_three = tk.Button(self.homeTab, text=">>>", command=lambda incr=3,key="Forward Three": self.switchRec(increment=incr, key=key), width=5,height=2)
        self.fd_three.place(x=230, y=590)

        # Last Rec
        self.goToLast = tk.Button(self.homeTab, text="-->|", command=lambda incr=0,key="Last": self.switchRec(increment=incr, key=key), width=5,height=2)
        self.goToLast.place(x=285, y=590)

        # Add a record
        self.addBtn = tk.Button(self.homeTab, text="Add New", command=self.addPlayer, width=10, height=2)
        self.addBtn.place(x=605, y=590)

        # Delete a record
        self.delBtn = tk.Button(self.homeTab, text="Delete", command=self.delete_scroller, width=10, height=2)
        self.delBtn.place(x=705, y=590)

        # Update a record
        self.updateBtn = tk.Button(self.homeTab, text="Update", command=self.updatePlayer, width=10, height=2)
        self.updateBtn.place(x=805, y=590)

        # User can upload an image that will be displayed in window
        self.upload_img = tk.Button(self.homeTab, command=self.upload_image, text="Upload Image", width=13, height=2)
        self.upload_img.place(x=485,y=590)

        # As a default, set a blank white image on the image label
        self.blank_binary = self.image_handler.blank_binary
        self.blank_image = self.image_handler.blank_bg_image

        # White border frame for the image label
        self.img_frame = tk.Frame(self.homeTab, relief="solid", bg="white")
        self.img_frame.place(x=458,y=75)

        # Sits on the frame
        self.image_label = tk.Label(self.img_frame)
        self.image_label.pack(fill="both", expand=True, padx=2, pady=2)
        
        # Setting to blank image
        self.image_label.config(image=self.blank_image)

        # Creating the list view box
        self.listbox = tk.Listbox(self.listView, height=30, width=130, borderwidth=5, relief="solid")

        # For the listbox. Will open up a new tab containing the record the user selected
        self.new_tab_btn = tk.Button(self.listView, text="Open in New Tab", command=self.create_tab, height=2, width=20)
        self.new_tab_btn.place(x=10, y=590)

        # Delete that record
        self.del_list_item = tk.Button(self.listView, text="Delete", height=2, width=9, command=self.delete_listView)
        self.del_list_item.place(x=170, y=590)

        # Feedback label
        self.feedbacklbl2 = tk.Label(self.listView, text="System: ", bg="#1a1a1a", fg="white")
        self.feedbacklbl2.place(x=8, y=630)

        # Says "Search"
        self.searchLbl = tk.Label(self.listView, text='Search: ', bg="#1a1a1a", fg="white")
        self.searchLbl.place(x=280,y=600)

        # Where the user will type the query
        self.search_box = tk.Entry(self.listView, width=18)
        self.search_box.place(x=330, y=600)

        # User hits this and the program will try to find the record
        self.search_btn = tk.Button(self.listView, text="Enter", command=self.search)
        self.search_btn.place(x=450, y=598)

        # Will create the graph based off of the data
        self.graph_data_btn = tk.Button(self.graphTab, text="See Graph", command=self.see_graph)

        # Another feedback label
        self.graph_feedback = tk.Label(self.graphTab, bg="#1a1a1a", fg="white", text="System: ")
        self.graph_feedback.place(x=8, y=630)

        # Labels for the graphs
        self.sets = [' Set 1 ', ' Set 2 ', ' Set 3 ', ' Set 4 ', ' Set 5 ', ' Set 6 ', ' Set 7 ']

        # Making the figure object which will act as a container for the plots
        self.figure = Figure(figsize=(7,6))
        
        # Setting size attributes that'll make it look good
        self.figure.tight_layout()
        self.figure.subplots_adjust(hspace=.512, wspace=.312)

        # Making plot 1 in the figure and setting attributes
        self.plot1 = self.figure.add_subplot(221)
        self.plot1.set_title('Games Won per Set')
        self.plot1.set_xlabel('Sets')
        self.plot1.set_ylabel('Games Won')

        # Making plot 2 in the figure and setting attributes
        self.plot2 = self.figure.add_subplot(222)
        self.plot2.set_title('Aces per set')
        self.plot2.set_xlabel('Sets')
        self.plot2.set_ylabel('# Aces')

        # Making plot 3 in the figure and setting attributes
        self.plot3 = self.figure.add_subplot(223)
        self.plot3.set_title('Double Faults')
        self.plot3.set_xlabel('Sets')
        self.plot3.set_ylabel('Faults')

        # Making plot 4 in the figure and setting attributes
        self.plot4 = self.figure.add_subplot(224)
        self.plot4.set_title('First Serve Wins Per Set')
        self.plot4.set_xlabel('Sets')
        self.plot4.set_ylabel('Games')
        
        # Creating the canvas that the figure will sit on top of
        self.canvas = FigureCanvasTkAgg(self.figure, master=self.graphTab)
        self.canvas.draw()

        # Navigation toolbar that will allow user to play around with the graphs 
        toolbar = NavigationToolbar2Tk(self.canvas, self.graphTab)
        toolbar.update()
        toolbar.place(x=10,y=590)

        # Says "winner"
        self.winner_lbl = tk.Label(self.graphTab, text="Winner: ", bg="#1e1e1e", fg="white")

        # A text box for the articles to go
        self.latest_news_box = tk.Text(self.latest_news_tab, width=90, height=27, borderwidth=4, relief="solid")
        self.latest_news_box.place(x=83,y=75)

        # Websites I go to to retrieve information
        tennis_news_websites: list[Websites.value] = [website.value for website in Websites]

        # Dropbox for the list above
        self.drop_box2 = ttk.Combobox(state="readonly", master=self.latest_news_tab, width=30, values=tennis_news_websites)
        self.drop_box2.place(x=83,y=45)

        # Holds the article links that are taken from the websites above
        self.drop_box3 = ttk.Combobox(state="readonly", master=self.latest_news_tab, width=81)
        self.drop_box3.place(x=300,y=45)

        # Button for opening the article and reading it, threading massively speeds up the process
        self.get_article = tk.Button(self.latest_news_tab, text="Open Article", command=self.open_article, width=12, height=2)
        self.get_article.place(x=110, y=590)

        # Gets the articles in the first place, threading massively speeds up the process
        self.see_news_btn = tk.Button(self.latest_news_tab, text="Find Articles", width=12,height=2, command=self.find_articles)
        self.see_news_btn.place(x=10, y=590)

        # Another feedback label, will be configured if anything goes wrong while making a request to the site
        self.news_feedback = tk.Label(self.latest_news_tab, bg="#1a1a1a", fg="white", text="System: ")
        self.news_feedback.place(x=8, y=630)

        # Next article on click
        self.next_article_btn = tk.Button(self.latest_news_tab,text=">", height=10, width=2, command=lambda key="Fd", incr=1: self.news_scroller_btn_commands(increment=incr, key=key))

        # Prev article
        self.prev_article_btn = tk.Button(self.latest_news_tab, text="<", height=10, width=2, command=lambda key="Bk", incr=1: self.news_scroller_btn_commands(increment=incr, key=key))
        
        # Disable the buttons (in NewsViewMode.FINDER mode)
        self.next_article_btn.config(state="disabled")
        self.prev_article_btn.config(state="disabled")

        # Progress bar for the news tab
        self.progress_bar = ttk.Progressbar(self.latest_news_tab, orient="horizontal", length=450, mode="determinate")

        # Summarization feature
        self.summarize_txt_btn = tk.Button(self.latest_news_tab, text="Summarize", width=10, height=2, command=self.summarize_txt)
        self.summarize_txt_btn.place(x=210, y=590)
        
        # Setting X button command
        root.protocol("WM_DELETE_WINDOW", self.exit_command)

        # Set the background + adjust widgets in Gui with setting loaded from json
        self.set_bg_imgs(bg_img=bg_img)
        
        # Event Loop
        root.mainloop()

    # Edit the current graph color theme (will not allow to edit default themes)
    def edit_current_theme(self) -> None:

        # Get the themes
        contents = self.json_handler.get_all()

        # Get the current one
        current_colors = contents["User Theme"]["User"]

        # Loop through and check if it is a default theme, if it is tell the user they cannot edit it
        for x in contents["Default Graph Themes"]:
            if (current_colors == contents["Default Graph Themes"][x]):
                self.feedbacklbl.config(text=f"System: Cannot Edit Default Graph Theme: {x}")
                self.feedbacklbl2.config(text=f"System: Cannot Edit Default Graph Theme: {x}")
                self.news_feedback.config(text=f"System: Cannot Edit Default Graph Theme: {x}")
                self.graph_feedback.config(text=f"System: Cannot Edit Default Graph Theme: {x}")

        # Loop through and check if it is a custom theme, if so open in the editing window
        for x in contents["Custom Graph Themes"]:
            if (current_colors == contents["Custom Graph Themes"][x]):
                color_dict = contents["Custom Graph Themes"][x]
                self.feedbacklbl.config(text=f"You are now editing {x}")
                self.feedbacklbl2.config(text=f"You are now editing {x}")
                self.news_feedback.config(text=f"You are now editing {x}")
                self.graph_feedback.config(text=f"You are now editing {x}")
                self.custom_theme_win(edit_mode=True, color_dict=color_dict, name=x)

    # Set background images and adjust widgets
    def set_bg_imgs(self, bg_img: str) -> None:

        if (bg_img == "Grass"):
            self.background_img = self.image_handler.background_img
            self.canvas.get_tk_widget().config(width=748,height=440)
            self.canvas.get_tk_widget().place(x=75,y=76)
            self.drop_box.place(x=75,y=45)
            self.graph_data_btn.place(x=295, y=43)
            self.winner_lbl.place(x=385, y=45)
            self.listbox.place(x=53, y=42)
            self.next_article_btn.place(x=818, y=220)
            self.prev_article_btn.place(x=53, y=220)

        if (bg_img == "Clay"):
            self.background_img = self.image_handler.clay_bg
            self.canvas.get_tk_widget().config(width=770,height=460)
            self.canvas.get_tk_widget().place(x=65,y=70)
            self.drop_box.place(x=70,y=40)
            self.graph_data_btn.place(x=290, y=37)
            self.winner_lbl.place(x=380, y=40)
            self.listbox.place(x=53, y=40)
            self.next_article_btn.place(x=820, y=220)
            self.prev_article_btn.place(x=50, y=220)

        # Config bg imgs
        self.homeTab_bg.config(image=self.background_img)
        self.listView_bg.config(image=self.background_img)
        self.graph_bg.config(image=self.background_img)
        self.lat_news_bg.config(image=self.background_img)

        # Lower the images on the stacking order so that the other widgets show up
        self.homeTab_bg.lower()
        self.listView_bg.lower()
        self.graph_bg.lower()
        self.lat_news_bg.lower()

    # Configure the bg img after the fact (menu btns)
    def set_bg_img_type(self, name: str) -> None:

        # Get settings, configure, set img + adjust widgets
        contents = self.json_handler.get_all()
        contents["User Theme"]["Bg"]["Background"] = contents["Bg_imgs"][name]
        self.json_handler.save_to_json(contents)
        settings = self.json_handler.get_settings()
        bg = settings[4]
        self.set_bg_imgs(bg)

    # Decorator that takes a method and executes it in a thread
    def threader(func: Callable) -> Callable:
        def wrapper(*args, **kwargs) -> Any:
            mythread = Thread(target=func, args=args, kwargs=kwargs)
            mythread.start()
        return wrapper

    # Summarizer method that runs in a thread (could take time to execute)
    @threader
    def summarize_txt(self) -> None:

        # Try this
        try:
            
            # Get text from box
            text = self.latest_news_box.get("1.0", tk.END)

            # Detect which language it is and get the associated abbreviation
            lang = self.lang_handler.get_lang(text)
            
            # If there is text there and its not in chinese or korean (summarizer can't do those)
            if (len(text) > 0) and (lang not in ["zh-CN", 'ko']):

                # Summarize and put into the text box
                summary = self.lang_handler.summarize(text=text)
                self.latest_news_box.delete("1.0", tk.END)
                self.latest_news_box.insert(tk.END, "Summary:\n\n" + summary)
                self.summarize_txt_btn.place_forget() 
                self.news_feedback.config(text="System: Here's your summary...")

            # If it is 
            if (lang in ["zh-CN", "ko"]):

                # Translate to english, then summarize, then translate back, and put 
                # in the text box
                translated = self.lang_handler.translate_text(vals=[text], target="en", source="auto")
                summary = self.lang_handler.summarize(text=translated[0])
                translated = self.lang_handler.translate_text(vals=[summary], target=lang, source="auto")
                self.latest_news_box.delete("1.0", tk.END)
                self.latest_news_box.insert(tk.END, "Summary:\n\n")

                for x in translated:
                    self.latest_news_box.insert(tk.END, x + '\n\n')
                self.summarize_txt_btn.place_forget() 
                self.news_feedback.config(text="System: Here's your summary...")
        
        # Rare translator api connection error
        except RequestError:
            self.news_feedback.config(text="System: Something went wrong...")
    
    # crUd for the article
    def update_article(self) -> None:

        # If connected and in db mode on news tab
        if (self.connected) and (self.news_mode == NewsViewMode.SCROLLER):

            # Get the news from the box, the record, the id from that record
            # them feed it to the connector, load, and let the user know
            updated_article = self.latest_news_box.get('1.0', tk.END)
            rec_tuple = self.news_articles[self.news_scroller_index]
            identifier = rec_tuple[0]
            self.connector.update_article(identifier, updated_article)
            self.news_load()
            self.news_feedback.config(text=f"System: Article at Id:{identifier} is updated!! Db reloaded...")


    # cruD for the news tab
    def delete_article(self) -> None:

        # Try this
        try:

            # If connected and in the appropriate mode
            if (self.connected and self.news_mode == NewsViewMode.SCROLLER):

                # Get the record and make sure the user wants to delete it
                rec_tuple = self.news_articles[self.news_scroller_index]
                confirm_bool = messagebox.askyesno(title="DELETE CONFIRMATION", message=f"Must you delete this article from {rec_tuple[1]}?")
            
            # If not connected, raise error
            if (not self.connected):
                raise DbConnectionNotFound(message="Database connection not found, also may be in finder mode")
            
            # If in finder mode, tell the user to switch
            if (self.news_mode == NewsViewMode.FINDER):
                raise Exception("Can't delete in finder mode, switch to db mode in menu and choose rec to delete")
            
            # If the user selected yes on record, delete it, load and the user know
            if (confirm_bool):
                identifier = rec_tuple[0]
                self.connector.del_article(identifier)
                self.news_load()
                self.news_feedback.config(text=f"System: Article from {rec_tuple[1]} has been deleted...Db reloaded")

            # If not, the user should know their record is fine
            if (not confirm_bool):
                self.news_feedback.config(text=f"System: Article from {rec_tuple[1]} has not been deleted..")

        # Catch exceptions
        except Exception as e:
            self.news_feedback.config(text=f"System: {e}")

    # Switch the mode in the news tab
    def switchNewsViewMode(self, mode: NewsViewMode) -> None:

        # Set var
        self.news_mode = mode

        # Load if scroller
        if (mode == NewsViewMode.SCROLLER):
            self.news_load()

        # If not, load finder mode
        if (mode == NewsViewMode.FINDER):

            # Set drop box vals
            self.drop_box2.config(state="readonly", values=[website.value for website in Websites])
            self.drop_box3.config(state="readonly", values=[])
            self.drop_box3.set('')

            # Del text from box and clear the list
            self.latest_news_box.delete("1.0", tk.END)
            self.news_articles.clear()

            # Disable the scroller btns
            self.next_article_btn.config(state="disabled")
            self.prev_article_btn.config(state="disabled")

    # Btn commands for the scroller btns
    def news_scroller_btn_commands(self, increment: int, key: str) -> None:

        # If check, then go to command
        if (self.connected) and (self.news_mode == NewsViewMode.SCROLLER):

            # Key tells the button what to do
            match (key):

                # Forward one rec
                case "Fd":
                    if(self.news_scroller_index != self.news_scroller_topindex):
                        self.news_scroller_index += increment

                # Back one record
                case "Bk":
                    if (self.news_scroller_index != 0):
                        self.news_scroller_index -= increment
            
            # Insert and place the summarize btn
            self.newsInserter(self.news_scroller_index)
            self.summarize_txt_btn.place(x=210, y=590)
                
    # Load for the news tab
    def news_load(self) -> None:

        # If not connected, tell the user to do so
        if (not self.connected):
            self.news_feedback.config(text="System: Please connect to db first and hit db mode again")

        # If connected, activate the scroller btns, set dropbox vals, and vars to control the scroller
        # Insert first rec.
        else:
            self.next_article_btn.config(state="normal")
            self.prev_article_btn.config(state="normal")
            self.news_articles = self.connector.load_saved_articles()
            self.drop_box2.config(values=[i[1] for i in self.news_articles], state="disabled")
            self.drop_box3.config(values=[i[2] for i in self.news_articles], state="disabled")
            self.news_scroller_index, self.news_scroller_topindex = 0, len(self.news_articles) - 1
            self.newsInserter(self.news_scroller_index)

    # Insert into the box
    def newsInserter(self, index: int) -> None:
        self.drop_box2.current(index)
        self.drop_box3.current(index)
        self.latest_news_box.delete("1.0", tk.END)
        self.latest_news_box.insert(tk.END, self.news_articles[index][3])

    # (c)rud for the news tab
    def save_article(self) -> None:

        # Get the dropbox vals as well as the associated website enum
        host_website = Websites(self.drop_box2.get())
        sub_url = self.drop_box3.get()
        article_contents = self.latest_news_box.get("1.0", tk.END)

        # If nothing is empty, insert the record
        if (host_website and sub_url and article_contents and self.connected):
            self.connector.insert_article(host_website, sub_url, article_contents)
            self.news_feedback.config(text="System: Saved to db!!")

        # If not connected, tell the user to do so
        if (not self.connected):
            self.news_feedback.config(text="System: Connect to db!!")

    # Window to both add and edit custom themes, based on parameters
    def custom_theme_win(self, edit_mode: bool | None, color_dict: dict | None, name: str | None) -> None:

        # Create window
        win = tk.Toplevel(self.root)
        win.geometry("450x450")
        win.resizable(False, False)
        win.title("Add custom theme")
        win.configure(bg="#1e1e1e")

        # List of colors the user can choose from
        colors_list = [
            ["blue", "orange"],
            ["green", "red"],
            ["purple", "yellow"],
            ["cyan", "magenta"],
            ["lime", "pink"],
            ["teal", "brown"],
            ["lavender", "gray"],
            ["olive", "skyblue"],
            ["darkgreen", "lightblue"],
            ["darkred", "lightgreen"],
            ["darkblue", "lightyellow"]
        ]

        # MAKING ALL OF THE WIDGETS 
        label = tk.Label(win, text="Add Custom Theme", bg="#1e1e1e",fg="white", font=("Cascadia code", 12))
        label.pack(pady=10)

        self.entry_box = tk.Entry(win, width=20)
        self.entry_box.pack(pady=10)

        label = tk.Label(win, text="1", bg="#1e1e1e",fg="white", font=("Cascadia code", 12))
        label.place(x=60, y=100)

        label2 = tk.Label(win, text="2", bg="#1e1e1e",fg="white", font=("Cascadia code", 12))
        label2.place(x=280, y=100)

        label3 = tk.Label(win, text="3", bg="#1e1e1e",fg="white", font=("Cascadia code", 12))
        label3.place(x=60, y=235)

        label4 = tk.Label(win, text="4", bg="#1e1e1e",fg="white", font=("Cascadia code", 12))
        label4.place(x=280, y=235)
        
        # DROPBOXES WHERE THE USER WILL SELECT THE COLORS
        self.color_box = ttk.Combobox(win, width=16, values=colors_list)
        self.color_box.place(x=60, y=125)

        self.color_box2 = ttk.Combobox(win, width=16, values=colors_list)
        self.color_box2.place(x=60, y=260)

        self.color_box3 = ttk.Combobox(win, width=16, values=colors_list)
        self.color_box3.place(x=280, y=125)

        self.color_box4 = ttk.Combobox(win, width=16, values=colors_list)
        self.color_box4.place(x=280, y=260)

        # Save btn that saves the theme the user created 
        self.save_btn = tk.Button(win, text="Save", command=self.create_custom_theme, height=2, width=10)
        self.save_btn.place(x=180,y=360)

        # Feedback label for this
        self.theme_label = tk.Label(win, bg="#1e1e1e",fg="white", font=("Cascadia code", 10), text="System: ", wraplength=550)
        self.theme_label.place(x=10, y=415)

        # If we are in edit mode, fill up the boxes and dropboxes with the values of that theme
        if (edit_mode):
            color_list = []
            for x in color_dict:
                color_dict[x][0] = color_dict[x][0].replace("{","")
                color_dict[x][0] = color_dict[x][0].replace("}","")
                color_list.append(color_dict[x])

            # Add in the colors
            self.color_box.set(color_list[0][0] + " " + color_list[0][1])
            self.color_box3.set(color_list[1][0] + " " + color_list[1][1])
            self.color_box2.set(color_list[2][0] + " " + color_list[2][1])
            self.color_box4.set(color_list[3][0] + " " + color_list[3][1])
            self.entry_box.insert(tk.END, name)
            self.entry_box.config(state="disabled")

        # Event loop
        win.mainloop()

    # Method tied to the save btn above
    def create_custom_theme(self) -> None:
        
        # Try this
        try:

            # Get the vals from the boxes
            name_of_theme = self.entry_box.get()
            c1a, c1b = self.color_box.get().split(" ")
            c2a, c2b = self.color_box2.get().split(" ")
            c3a, c3b = self.color_box3.get().split(" ")
            c4a, c4b = self.color_box4.get().split(" ")

            # If name is empty, let the user know
            if (name_of_theme == ""):
                raise EmptyFields(indice=None, sheet_num=None, specific_field="Name of theme")

            # Prepare the dicionary to be passed to the json file
            self.graph_color_dict = {
                "1": [c1a, c1b],
                "2": [c3a, c3b],
                "3": [c2a, c2b],
                "4": [c4a, c4b]
            }

            # Save it to the current settings in the json file and set the settings here in gui
            contents = self.json_handler.get_all()
            contents["Custom Graph Themes"][name_of_theme] = self.graph_color_dict
            contents["User Theme"]["User"] = self.graph_color_dict
            self.json_handler.save_to_json(contents)
            settings = self.json_handler.get_settings()
            custom_themes = settings[3]

            # Configure the menu that allows the user to select one of these themes
            self.custom_themes_menu.delete(0, tk.END)
            for x in custom_themes:
                self.custom_themes_menu.add_radiobutton(label=x, command=lambda opt=x: self.custom_theme_handler(opt))

            # Let the user know
            self.theme_label.config(text="System: Success!! You are free to close this window")

        # Something is wrong
        except Exception as e:
            self.theme_label.config(text=f"System Error: {e}")



    # WEB SCRAPING METHODS HERE -----

    # This method takes the website and goes through the html for links to the articles within it
    @threader
    def find_articles(self) -> None:
        
        # Try this
        try:
            
            # Show the progress bar
            self.progress_bar.place(x=400, y=595)

            # If in scroller mode, then tell the user to switch
            if (self.news_mode == NewsViewMode.SCROLLER):
                self.news_feedback.config(text="System: If you want to look up articles, change mode...")
                url = None 
            
            # If in finder mode, then get the chosen website            
            if (self.news_mode == NewsViewMode.FINDER):
                url = Websites(self.drop_box2.get())
                self.progress_bar['value'] = 30
                self.root.update_idletasks()

            # If it is not empty, feed to the webscraper object to get the urls
            # of the articles. then display
            if (url):
                vals = self.web_scraper.find_articles(url)

                self.progress_bar['value'] = 60
                self.root.update_idletasks()
                
                self.latest_news_box.delete("1.0", tk.END)
                for i in vals:  
                    self.latest_news_box.insert(tk.END, str(i) + "\n\n")
                        
                # set drop box values to the links
                self.drop_box3.config(values=vals)
                self.news_feedback.config(text="System: Articles Found!! You can pick one in the dropbox!!")
                self.progress_bar['value'] = 100
                self.root.update_idletasks()


        # Something goes wrong, no connection.
        except ConnectionError:
            self.news_feedback.config(text="System: Failed to resolve. Perhaps check your internet connection...")
        
        # Catch anything else
        except Exception as e:
            self.news_feedback.config(text=f"System: {e}")
            self.progress_bar['value'] = 0
            self.root.update_idletasks()

        # Finally, remove the progress bar, and set the btn config to normal
        finally:
            self.progress_bar.place_forget()
            self.get_article.config(state="normal")

        
    # Now that we have the articles, we can open them up and extract the information
    @threader
    def open_article(self) -> None:

        # Try this
        try:
            
            # Loading bar
            self.progress_bar.place(x=400, y=595)

            if (self.news_mode == NewsViewMode.SCROLLER):
                self.news_feedback.config(text="System: Switch to finder mode pls")
                website, url = None, None

            # Get the website name, url of the article chosen in the dropbox
            if (self.news_mode == NewsViewMode.FINDER):
                website = Websites(self.drop_box2.get())
                url = self.drop_box3.get()
            
            # If nothing is empty
            if (website) and (url):
                
                # Disable the btn so that the user can't just keep mashing it and creating new threads
                self.get_article.config(state="disabled")

                self.progress_bar['value'] = 30
                self.root.update_idletasks()

                # Get the contents of the article
                vals = self.web_scraper.open_article(website, url, self.current_language)

                self.progress_bar['value'] = 60
                self.root.update_idletasks()
                
                self.latest_news_box.delete("1.0", tk.END)

                # Loop through and add the contents to the text box
                for i in vals:
                    self.latest_news_box.insert(tk.END, str(i) + "\n\n")
                    self.progress_bar['value'] = self.progress_bar['value'] + 4
                    self.root.update_idletasks()

                self.progress_bar['value'] = 100
                self.root.update_idletasks()

                # Tell the the work has been done and place the summarize btn
                self.news_feedback.config(text=f"System: Opened '{vals[0]}'", wraplength=900)
                self.summarize_txt_btn.place(x=210, y=590)

        # Internet connection error
        except ConnectionError:
            self.news_feedback.config(text="System: Failed to resolve. Perhaps check your internet connection...")

        # Anything else occurs
        except Exception as e:
            self.news_feedback.config(text=f'System Error: {e}')
            self.progress_bar['value'] = 0
            self.root.update_idletasks()

        # No matter what, the btn should go back to normal and remove the progress bar
        finally:
            self.progress_bar.place_forget()
            self.get_article.config(state="normal")
    
    # Open website in browser
    def open_website(self) -> None:

        # Get the selected website
        website = self.drop_box3.get()

        # Try this
        try:
            
            # If there is something there
            if (len(website) > 0):

                # Open it with webbrowser.open and tell the user
                open_url(url=website)
                self.news_feedback.config(text=f"Opened {website} in browser!!", wraplength=10000)
            
            # If nothing is there tell the user
            else:
                self.news_feedback.config(text="Please choose a website in the dropbox... or select a website to get articles")

        # Something goes wrong with the webbrowser lib (shouldn't ever happen really but just in case handle the specific exception)
        except WebBrowserErr:
            self.news_feedback.config(text=f"System: Browser support may be down at the moment...")

        # Anything else
        except Exception as err:
            self.news_feedback.config(text=f"System: {err}")


    # HELP MENU METHODS

    # About Info messagebox method
    def about_info(self) -> None:
        message = """CREATOR: Sohamerson
VERSION: 1.24j43jkh432
Use this program to store tennis players and more!!"""
        
        messagebox.showinfo(title="About", message=message)


    # JSON SETTINGS METHODS - json stores color settings for graphs

    # Opens the advanced settings window where the user can directly configure the json themselves
    def json_config_win(self) -> None:

        # Make toplevel window, Toplevel acts as a child window to the parent Tk
        textEditor = tk.Toplevel(self.root)
        textEditor.title("Settings For Nerds")
        textEditor.geometry('1085x600')
        textEditor.resizable(False, False)
        self.textEditor = textEditor

        # Text box where json will go
        self.text_box = tk.Text(textEditor, width=114, height=30, font=("", 12))
        self.text_box.place(x=20,y=30)

        # Open Json file and load settings to contents
        contents = self.json_handler.get_all()

        # Convert to a string
        contents = self.json_handler.convert_str(contents)

        # Insert into the box
        self.text_box.insert("insert", contents)

        # Save buttons
        self.save_file = tk.Button(textEditor, text="Save", command=self.save_json)
        self.save_file.place(x=110-50 -20-20,y=2)

        # The feedback label for this one
        self.json_config_lbl = tk.Label(textEditor, text="System: ")
        self.json_config_lbl.place(x=80,y=2)

        # Run it
        textEditor.mainloop()

    # Save command for button in window above
    def save_json(self) -> None:

        # Get the stuff from the text box
        contents = (self.text_box.get("1.0",tk.END)).strip()

        # Open the file and put in the stuff
        contents = self.json_handler.convert_json(contents)
        self.json_handler.save_to_json(contents)

        # Let the user know
        self.json_config_lbl.config(text="System: Json Configured!! You're free to close this window")

        # Open the file back up to load color settings into the menu
        settings = self.json_handler.get_settings()
        self.graph_color_dict = settings[0]
        self.languages = settings[1]
        self.current_language = settings[2]
        custom_themes = settings[3]
        bg_img = settings[4]

        # Delete menu items (custom themes)
        self.custom_themes_menu.delete(0, tk.END)
        self.set_bg_img_type(bg_img)

        # Put in all custom theme buttons into the menu
        for x in custom_themes:
            self.custom_themes_menu.add_radiobutton(label=x, command=lambda opt=x: self.custom_theme_handler(name=opt))


    # MATCH DATA COMMANDS

    # Opens a window that either allows the user to edit the data or add match data
    def match_data_win(self, update_mode: bool, rec: None | list[list], rec2: None | list[list], names: None | list[str]) -> None:

        # Create TopLevel window, acts as a child window to parent Tk window, prevents overlap or errors, specifically in adding a background image
        win = tk.Toplevel(self.root)

        # Set attributs
        win.geometry("700x560")
        win.title("Singles Match Data Analysis")
        win.resizable(False,False)

        court_img = self.image_handler.court_img

        # Configure to image
        self.image_label3 = tk.Label(win, image=court_img)
        self.image_label3.pack()

        # Title label
        self.title_lbl = tk.Label(win, text="Title")
        self.title_lbl.place(x=30, y=10)

        # Title box
        self.title_box = tk.Entry(win, width=20)
        self.title_box.place(x=30,y=30)

        # Date label
        self.date_lbl = tk.Label(win, text="Date (YYYY-MM-DD)")
        self.date_lbl.place(x=180,y=10)

        # Date Box
        self.date_box = tk.Entry(win, width=20)
        self.date_box.place(x=180, y=30)

        # 1st player label
        self.player_one_lbl = tk.Label(win, text="Player Name: ")
        self.player_one_lbl.place(x=30,y=70)

        # user types in the player name
        self.player_one_box = tk.Entry(win, width=21)
        self.player_one_box.place(x=130, y=70)

        # What the tksheet rows and column headers should be
        rows = ['Games Won', 'Aces', 'First Serve Win', 'Double Faults', 'Winner (1 or 0)']
        column = ['1','2','3','4','5','6','7']

        # Creating the data tables (the rows and columns)
        data = [["" for _ in rows] for _ in column]
        data2 = [["" for _ in rows] for _ in column]

        # Make the first tk sheet and add the first data table
        self.my_sheet = tksheet.Sheet(win)
        self.my_sheet.place(x=30,y=120, width=650,height=180)
        self.my_sheet.set_sheet_data(data)


        # Set column widths
        self.my_sheet.set_all_column_widths(width=150)

        # Add headers
        self.my_sheet.headers(column, index='row')
        self.my_sheet.headers(rows, index='col')

        # Bindings for the table, to do various actions like copy paste
        self.my_sheet.enable_bindings(("single_select",
                                "row_select",
                                "column_width_resize",
                                "arrowkeys",
                                "right_click_popup_menu",
                                "rc_select",
                                "rc_insert_row",
                                "rc_delete_row",
                                "copy",
                                "cut",
                                "paste",
                                "delete",
                                "undo", 
                            "edit_cell"))
        
        # Doing it again
        self.my_sheet2 = tksheet.Sheet(win)
        self.my_sheet2.place(x=30,y=350, width=650,height=180)
        self.my_sheet2.set_sheet_data(data2)

        # Set column widths
        self.my_sheet2.set_all_column_widths(width=150)

        # Add headers
        self.my_sheet2.headers(column, index='row')
        self.my_sheet2.headers(rows, index='col')

        # Same bindings to allow for various actions
        self.my_sheet2.enable_bindings(("single_select",
                                "row_select",
                                "column_width_resize",
                                "arrowkeys",
                                "right_click_popup_menu",
                                "rc_select",
                                "rc_insert_row",
                                "rc_delete_row",
                                "copy",
                                "cut",
                                "paste",
                                "delete",
                                "undo", 
                            "edit_cell"))
        
        # Second player label
        self.player_two_lbl = tk.Label(win, text="Player 2:")
        self.player_two_lbl.place(x=30, y=320)

        # User will type in the second players name
        self.player_two_box = tk.Entry(win, width=21)
        self.player_two_box.place(x=90, y=320)

        # Commit changes to db btn
        self.commit_btn = tk.Button(win, text="Commit", command=self.get_sheet_vals, width=15,height=2)
        self.commit_btn.place(x=550, y=30)

        # Feedback label, gets configured when stuff goes right or wrong
        self.data_feedback = tk.Label(win, text="System: ")
        self.data_feedback.place(x=30, y=536)

        # If this boolean is true, then 'Edit current analysis' has been hit and the program
        # Will gather the data from the selected record into the table
        if (update_mode):
            self.my_sheet.set_sheet_data(rec)
            self.my_sheet2.set_sheet_data(rec2)
            self.title_box.insert(tk.END, names[0])
            self.player_one_box.insert(tk.END, names[1])
            self.player_two_box.insert(tk.END, names[2])
            self.date_box.insert(tk.END, names[3])

            # Config the button with something else
            self.commit_btn.config(command=self.update_data)

        # Mainloop
        win.mainloop()


    # Get the values the user typed in and put them in the db
    def get_sheet_vals(self) -> None:

        # Try This
        try:
            
            # Highlight all cells in my sheet
            self.my_sheet.select_all()

            # get_selected_cells returns a set of coordinates for each cell in a random order
            # Sort them so that it looks like this [(0,0), (0,1), ...]
            coords = list(self.my_sheet.get_selected_cells())
            coords = sorted(coords, key=lambda x: x[0])
            coords = sorted(coords, key=lambda x: x[1])

            # Clear selection
            self.my_sheet.selection_clear()

            # Same thing for sheet 2
            self.my_sheet2.select_all()
            coords2 = list(self.my_sheet2.get_selected_cells())
            coords2 = sorted(coords2, key=lambda x: x[0])
            coords2 = sorted(coords2, key=lambda x: x[1])

            # Create lists to store the values
            player_one_vals, player_two_vals = [], []

            # Loop through, getting values from cells and adding them to the lists
            for i in coords2:
                player_two_vals.append(self.my_sheet2.get_cell_data(i[0], i[1]))

            for i in coords:
                player_one_vals.append(self.my_sheet.get_cell_data(i[0], i[1]))

            # Loop through those lists and make sure none are empty, if so raise error
            for i, v in enumerate(player_one_vals):
                if (v == ''):
                    indice = list(coords[i])
                    self.my_sheet.selection_clear()
                    self.my_sheet.select_cell(row=indice[0], column=indice[1])
                    raise EmptyFields(indice=indice, sheet_num=1, specific_field=None)

            for i, v in enumerate(player_two_vals):
                if (v == ''):
                    indice = list(coords[i])
                    self.my_sheet2.selection_clear()
                    self.my_sheet2.select_cell(row=indice[0], column=indice[1])
                    raise EmptyFields(indice=coords[i], sheet_num=2, specific_field=None)
            
            # Sorting out the various parts of the list into the 5 categories
            # GAMES WON, ACES, DOUBLE FAULTS, FIRST SERVES
            player_games_won1 = player_one_vals[0:7:1]
            player_aces1 = player_one_vals[7:14:1]
            player_doubFault1 = player_one_vals[14:21:1]
            player_firstServe1 = player_one_vals[21:28:1]
            player_games_won2 = player_two_vals[0:7:1]
            player_aces2 = player_two_vals[7:14:1]
            player_doubFault2 = player_two_vals[14:21:1]
            player_firstServe2 = player_two_vals[21:28:1]
            
            # Booleans for win, either 1 or 0
            player_wins1, player_wins2 = [int(i) for i in (player_one_vals[28:35:1])], [int(i) for i in (player_two_vals[28:35:1])]

            # Getting the other values from text boxes
            title = self.title_box.get()
            date = self.date_box.get()
            player_one = self.player_one_box.get()
            player_two = self.player_two_box.get()

            # Combining them all to the insert rec which is feed to the connector object
            insert_rec = [player_games_won1, player_aces1, player_doubFault1, player_firstServe1, player_wins1, player_games_won2, player_aces2, player_doubFault2, player_firstServe2, player_wins2]

            # If nothing is empty and all is right, insert in db and let the user know, and load
            if (len(title) > 0 and len(date) > 0 and len(player_one) > 0 and len(player_two) > 0) and (self.connected):
                my_id = self.generate_id()
                self.connector.create_set_table(match_name=title, name=player_one, name2=player_two, date=date, record=insert_rec, identifier=my_id)
                self.data_feedback.config(text="System: Added Data!! You are free to close this window")
                self.graph_load()

            # If Anything is empty, let the user know
            if (len(title) == 0):
                raise EmptyFields(None, None, "Title")

            if (len(date) == 0):
                raise EmptyFields(None, None, "Date")

            if (len(player_one) == 0):
                raise EmptyFields(None, None, "Player One Name")

            if (len(player_two) == 0):
                raise EmptyFields(None, None, "Player Two Name")
            
            # No connection, raise error
            if (not self.connected):
                raise DbConnectionNotFound()
        
        # Catch exception
        except Exception as e:
            self.data_feedback.config(text=f"System: {e}")
            
        
    # This method takes the record the user has inserted and displays it in the graphs
    def see_graph(self) -> None:

        try:
            # Get the chosen option for dropbox
            var = self.drop_box.get()

            # Match the id to a record in db if selected and connected
            if (len(var) > 0) and (self.connected):
                identifier = int((var.split("ID:"))[-1])
                for i in self.match_ids:
                    if (identifier == i[0]):
                        rec = i

                # Get the table values with connector
                player_one_stats = self.connector.get_match_stats(table=rec[2])
                player_two_stats = self.connector.get_match_stats(table=rec[3])
                
                # Sort into lists
                games_won = [[i[1] for i in player_one_stats], [i[1] for i in player_two_stats]]
                aces = [[i[2] for i in player_one_stats], [i[2] for i in player_two_stats]]
                first_serve = [[i[3] for i in player_one_stats], [i[3] for i in player_two_stats]]
                double_fault = [[i[4] for i in player_one_stats], [i[4] for i in player_two_stats]]
                win_or_lose = [sum([i[5] for i in player_one_stats]), sum([i[5] for i in player_two_stats])]
                
                # Graph games_won to plot 1 and set legend with player names
                self.plot1.clear()
                self.plot1.plot(self.sets, games_won[0], color=self.graph_color_dict['1'][0], marker='o', label=f'{rec[4]}')
                self.plot1.plot(self.sets, games_won[1], color=self.graph_color_dict['1'][1], marker='s', label=f'{rec[5]}')
                self.plot1.set_title('Games Won per Set')
                self.plot1.set_xlabel('Sets')
                self.plot1.set_ylabel('Games Won')
                self.plot1.legend()

                # Clear graph and set bar width (for group bar plot)
                self.plot2.clear()
                bar_width: float = .25
                
                # Create an even array of values for the len of self.sets <- [" Set 1 ", ...]
                bar_pos1 = np.arange(len(self.sets))

                # bar_pos2 is the value for the position of the second bar in each plot
                # Just add .25
                bar_pos2 = bar_pos1 + bar_width

                # Set plot2 with the data and positions determined above
                self.plot2.bar(bar_pos1, aces[0], color=self.graph_color_dict['2'][0], width=bar_width, label=f'{rec[4]}')
                self.plot2.bar(bar_pos2, aces[1], color=self.graph_color_dict['2'][1], width=bar_width, label=f"{rec[5]}")
                self.plot2.set_title('Aces per set')
                self.plot2.set_xlabel('Sets')
                self.plot2.set_ylabel('# Aces')
                self.plot2.set_xticks(bar_pos1+bar_width/2, self.sets)
                self.plot2.legend()

                # Same thing, except it is a horizontal bar chart
                self.plot3.clear()
                self.plot3.barh(bar_pos1, double_fault[0], bar_width, color=self.graph_color_dict['3'][0], label=f'{rec[4]}')
                self.plot3.barh(bar_pos2, double_fault[1], bar_width, color=self.graph_color_dict['3'][1], label=f'{rec[5]}')
                self.plot3.set_xlabel("Double Faults")
                self.plot3.set_ylabel("Sets")

                # Set y labels
                self.plot3.set_yticks(bar_pos1+bar_width/2, self.sets)

                # Title and legend
                self.plot3.set_title("Double Faults Per Set")
                self.plot3.legend()

                # Plot 3 is a line chart. 
                self.plot4.clear()
                self.plot4.plot(self.sets, first_serve[0],color=self.graph_color_dict['4'][0], label=f'{rec[4]}')
                self.plot4.plot(self.sets, first_serve[1], color=self.graph_color_dict['4'][1], label=f'{rec[5]}')

                # Set the grid
                self.plot4.grid(True, which="both", linestyle='--', linewidth=.5)

                # Titles, and legend
                self.plot4.set_title("First Serve Wins Per Set")
                self.plot4.set_ylabel("# 1st Serve Wins")
                self.plot4.legend()

                # We took the sum of the wins and losses of the players earlier
                # Now we compare them and configure label correctly
                if (win_or_lose[0] > win_or_lose[1]):
                    self.winner_lbl.config(text=f"Winner: {rec[4]}")
                if (win_or_lose[0] < win_or_lose[1]):
                    self.winner_lbl.config(text=f"Winner: {rec[5]}")

                # Draw it
                self.canvas.draw()

            # Connection err
            if (not self.connected):
                raise DbConnectionNotFound()

        # Catch exception
        except Exception as e:
            self.graph_feedback.config(text=f"System: {e}")

        
    
    # crUd for the graph data
    def update_analysis(self) -> None:
        
        # Get the selected drop box item
        var = self.drop_box.get()

        # If everything checks out, find the associated record
        if (len(var) > 0 and self.connected):
            identifier = int((var.split("ID:"))[-1])
            for i in self.match_ids:
                if (identifier == i[0]):
                    rec = i

            # Get the fields from the record
            title: str = rec[1]
            name1: str = rec[4]
            name2: str = rec[5]
            date = str(rec[-1])

            # Make a list out of them
            info_list = [title, name1, name2, date]

            # The numerical data from those records
            player_one_stats = [list(i[1:]) for i in self.connector.get_match_stats(table=rec[2])]
            player_two_stats = [list(i[1:]) for i in self.connector.get_match_stats(table=rec[3])]

            # Feed it in match_data_win with update mode set to true
            self.match_data_win(update_mode=True, rec=player_one_stats, rec2=player_two_stats, names=info_list)

    # Method tied to commit btn in win if update_mode is true
    def update_data(self) -> None:

        # Try this
        try:

            # Same coordinate collecting sorting scheme from earlier
            # Take coordinates and sort them out till I got then in the order I want
            self.my_sheet.select_all()
            coords = list(self.my_sheet.get_selected_cells())
            coords = sorted(coords, key=lambda x: x[0])
            coords = sorted(coords, key=lambda x: x[1])
            self.my_sheet.selection_clear()

            self.my_sheet2.select_all()
            coords2 = list(self.my_sheet2.get_selected_cells())
            coords2 = sorted(coords2, key=lambda x: x[0])
            coords2 = sorted(coords2, key=lambda x: x[1])

            # Make the lists that will store the data
            player_one_vals, player_two_vals = [], []

            # Loop through and get all of that cell data
            for i in coords2:
                player_two_vals.append(self.my_sheet2.get_cell_data(i[0], i[1]))

            for i in coords:
                player_one_vals.append(self.my_sheet.get_cell_data(i[0], i[1]))


            # Loop through and check if anything is empty and let the user know if anything is empty
            for i, v in enumerate(player_one_vals):
                if (v == ''):
                    indice = list(coords[i])
                    self.my_sheet.selection_clear()
                    self.my_sheet.select_cell(row=indice[0], column=indice[1])
                    raise EmptyFields(indice=indice, sheet_num=1, specific_field=None)

            for i, v in enumerate(player_two_vals):
                if (v == ''):
                    indice = list(coords[i])
                    self.my_sheet2.selection_clear()
                    self.my_sheet2.select_cell(row=indice[0], column=indice[1])
                    raise EmptyFields(indice=coords[i], sheet_num=2, specific_field=None)
            

            # Sort them out by categories
            player_games_won1 = player_one_vals[0:7:1]
            player_aces1 = player_one_vals[7:14:1]
            player_doubFault1 = player_one_vals[14:21:1]
            player_firstServe1 = player_one_vals[21:28:1]
            player_games_won2 = player_two_vals[0:7:1]
            player_aces2 = player_two_vals[7:14:1]
            player_doubFault2 = player_two_vals[14:21:1]
            player_firstServe2 = player_two_vals[21:28:1]
            player_wins1, player_wins2 = [int(i) for i in (player_one_vals[28:35:1])], [int(i) for i in (player_two_vals[28:35:1])]

            # Get the other attributes
            title = self.title_box.get()
            date = self.date_box.get()
            player_one = self.player_one_box.get()
            player_two = self.player_two_box.get()
            insert_rec = [player_games_won1, player_aces1, player_doubFault1, player_firstServe1, player_wins1, player_games_won2, player_aces2, player_doubFault2, player_firstServe2, player_wins2]

            # Get the id of the record in match_ids which stores tables names along with other info
            var = self.drop_box.get()
            identifier = int((var.split("ID:"))[-1])
            for i in self.match_ids:
                if (identifier == i[0]):
                    rec = i

            # Id
            my_id: int = rec[0]

            # Names of tables in db
            table1_name: str = rec[2]
            table2_name: str = rec[3]
            names_list: list[str] = [title, player_one, player_two, date]

            # If all is good, feed the stuff to the connector, let the user know, and load
            if (rec) and (self.connected) and (len(title) > 0 and len(date) > 0 and len(player_one) > 0 and len(player_two) > 0):
                self.connector.update_match_stats(table1=table1_name, table2=table2_name, rec=insert_rec, identifier=my_id, names_list=names_list)
                self.data_feedback.config(text="Updated!! Feel free to close this window")
                self.graph_load()
            
            # Something is empty, raise error
            if (len(title) == 0):
                raise EmptyFields(indice=None, sheet_num=None, specific_field="Title")

            if (len(date) == 0):
                raise EmptyFields(indice=None, sheet_num=None, specific_field="Date")

            if (len(player_one) == 0):
                raise EmptyFields(indice=None, sheet_num=None, specific_field="Player One Name")

            if (len(player_two) == 0):
                raise EmptyFields(indice=None, sheet_num=None, specific_field="Player Two Name")
            
            # No connection, raise error
            if (not self.connected):
                raise DbConnectionNotFound()
        
        # Catch exception
        except Exception as e:
            self.data_feedback.config(text=f"System: {e}")

    # cruD for match_data
    def del_analysis(self) -> None:
        
        try: 
            # Get the record id
            var = self.drop_box.get()
            identifier = int((var.split("ID:"))[-1])
            for i in self.match_ids:
                if (identifier == i[0]):
                    rec = i

            # Table names
            table1_name: str = rec[2]
            table2_name: str = rec[3]

            # Ask the user if they must go through with it
            confirm_bool = messagebox.askyesno(title="DELETE CONFIRMATION", message=f"Are you sure you want to delete {rec[1].strip()}")

            # If so, do the work, let the user know it's been done, and load
            if (confirm_bool):
                self.connector.del_match_stats(table1=table1_name, table2=table2_name, identifier=identifier)
                self.graph_load()
                self.graph_feedback.config(text=f"{rec[1].strip()} has been deleted")
            
            # Let them know their record is fine
            else:
                self.graph_feedback.config(text=f"{rec[1].strip()} has not been deleted")
        
        except Exception as e:
            self.graph_feedback.config(text=f"Error: {e}")

    # THEME HANDLER METHODS 

    # This is the method that allows for changing the theme fo rthe graph colors
    def change_graph_theme(self, theme: str) -> None:
        self.json_handler.change_graph_theme(theme=theme)
        settings = self.json_handler.get_settings()
        self.graph_color_dict = settings[0]

    # Change language for news translation feature
    @threader
    def change_language(self, lang: str) -> None:

        # Try this
        try:

            translator = LangHandler()
            
            # Progress bar
            self.progress_bar.place(x=400, y=595)
            self.progress_bar["value"] = 20
            self.root.update_idletasks()

            # Change in json and here
            self.json_handler.change_language(lang=lang)
            settings = self.json_handler.get_settings()
            self.current_language = settings[2]

            self.progress_bar["value"] = 40
            self.root.update_idletasks()

            # Get the text from the box
            text = [self.latest_news_box.get("1.0", tk.END).strip()]
            
            # If its empty, raise error
            if (len(text[0]) == 0):
                raise EmptyFields(None, None, "Article")
            
            self.progress_bar["value"] = 45
            self.root.update_idletasks()

            # Detect the language and get the tag of the lang it is going to translate to ("French" -> "fr")
            abbr = translator.get_tag(lang)
            source = translator.get_lang(text=text[0])

            # Some reason, it doesn't do Chinese right
            if (lang == "Chinese"):
                source = "zh-CN"

            if (lang == "Korean"):
                source = "auto"

            # If in scroller mode
            if (self.news_mode == NewsViewMode.SCROLLER) and (len(text[0]) > 0):
                self.progress_bar["value"] = 65
                self.root.update_idletasks()

                # Translate and put in text box
                translated_text = translator.translate_text(vals=text, source=source, target=abbr)
                self.latest_news_box.delete("1.0", tk.END)

                self.progress_bar["value"] = 85
                self.root.update_idletasks()

                self.latest_news_box.insert(tk.END, translated_text[0])

                self.progress_bar["value"] = 100
                self.root.update_idletasks()

                self.news_feedback.config(text="System: Translated!!")

            # If in finder, tell the user to refresh article
            if (self.news_mode == NewsViewMode.FINDER) and (len(text[0]) > 0):

                self.progress_bar["value"] = 100
                self.root.update_idletasks()
                
                self.news_feedback.config(text=f"Language set to {lang}!! Refresh to see translation")

        # If it exceeds 5k characters
        except NotValidLength:

            # Progress bar
            self.progress_bar.place(x=400, y=595)

            self.progress_bar["value"] = 20
            self.root.update_idletasks()

            # Split from newline characters
            substrings = self.latest_news_box.get("1.0", tk.END).split("\n\n")

            self.progress_bar["value"] = 40
            self.root.update_idletasks()

            # Now feed it in
            translated = translator.translate_text(substrings, target=abbr, source=source)

            self.progress_bar["value"] = 60
            self.root.update_idletasks()

            # Clear box
            self.latest_news_box.delete("1.0", tk.END)

            self.progress_bar["value"] = 80
            self.root.update_idletasks()

            # Insert
            for x in translated:
                self.progress_bar["value"] = self.progress_bar['value'] + 1
                self.root.update_idletasks()
                self.latest_news_box.insert(tk.END, str(x) + "\n\n")

        # API error
        except RequestError as e:
            self.news_feedback.config(text="System: Translator API error, sorry...Perhaps check internet connection")

        # User types in gibberish that exists in no language
        except LangDetectException:
            self.news_feedback.config(text="Can't detect that language...perhaps you need to select an article")

        # Everything else
        except Exception as e:
            self.news_feedback.config(text=f"System: {e}")

        # Remove loading bar
        finally:
            self.progress_bar.place_forget()
    
    # Change custom theme for graph colors
    def custom_theme_handler(self, name: str) -> None:

        # Change setting in json and over here in gui
        self.json_handler.custom_theme_handler(name=name)
        settings = self.json_handler.get_settings()
        self.graph_color_dict = settings[0]

    # Dummy Method (used in testing
    def doNothing(self) -> None:
        pass

    # Exit command, tied to X button from window manager and EXIT in menu
    def exit_command(self) -> None:

        # Checks connection, if True, close it
        if (self.connected):
            self.connector.disconnect()

        # Close window
        self.root.destroy()

    # Sort list box items
    def listbox_sorter(self, option: str) -> None:
        
        # Just checking
        if (self.connected):

            # Match option to a case
            match (option):

                # Sort based of of this case with sorted()
                case "Rank":
                    self.sorted_recs = sorted(self.records, key=lambda x: x[3])
                case "Ratio":
                    self.sorted_recs = sorted(self.records, key=lambda x: x[5], reverse=True)
                case "Age":
                    self.sorted_recs = sorted(self.records, key=lambda x: x[2])
                case "None":
                    self.sorted_recs = self.records
                    
            # Load it in
            self.sort_type: str = option
            self.list_load(self.sorted_recs)

    # Method to clear all of my boxes (parameters to check which things to clear)
    def setBlanks(self, listboxdel: bool, graph_del: bool, scroller_del: bool) -> None:

        # Clear in scroller
        if (scroller_del):
            self.namebox.delete("1.0","end-1c")
            self.agebox.delete("1.0","end-1c")
            self.rankbox.delete("1.0","end-1c")
            self.ratiobox.delete("1.0","end-1c")
            self.winbox.delete("1.0","end-1c")
            self.losebox.delete("1.0","end-1c")
            self.achievementsbox.delete("1.0","end-1c")
            self.image_label.config(image=self.blank_image)
            self.img = None

        # Clear listbox
        if (listboxdel):
            self.listbox.delete(0, tk.END)

        # Clear listbox
        if (graph_del):
            self.plot1.clear()
            self.plot2.clear()
            self.plot3.clear()
            self.plot4.clear()

            self.plot1.set_title('Games Won per Set')
            self.plot1.set_xlabel('Sets')
            self.plot1.set_ylabel('Games Won')

            self.plot2.set_title('Aces per set')
            self.plot2.set_xlabel('Sets')
            self.plot2.set_ylabel('# Aces')

            self.plot3.set_title('Double Faults')
            self.plot3.set_xlabel('Sets')
            self.plot3.set_ylabel('Faults')


            self.plot4.set_title('First Serve Wins Per Set')
            self.plot4.set_xlabel('Sets')
            self.plot4.set_ylabel('Games')

            self.canvas.draw()

    # Method for user to upload image to the program
    def upload_image(self) -> None:
        try:

            file_path = self.image_handler.get_file()
            contents = self.image_handler.read_bin(file_path=file_path)
            self.new_image = self.image_handler.image_resizer(contents, size=ImgSize.REGULAR)

            # Display it
            self.image_label.config(image=self.new_image)            

            # Setting the self.img variable to the file path
            self.img = contents

        # User exits or something
        except:
            pass
        
        # Let the user know 
        finally:
            if (not self.connected):
                self.feedbacklbl.config(text="System: Nice Image!!! It won't save because you are not connected. :(")

    # To calculate that win/loss ratio
    def calculate_ratio(self) -> None:

        # Try this
        try:
            # Getting the numbers the user has typed in
            wins = self.winbox.get("1.0",tk.END).strip()
            losses = self.losebox.get("1.0",tk.END).strip()

            # If anything is empty
            if (wins == ""):
                raise EmptyFields(indice=None, sheet_num=None, specific_field="Wins")
            
            if (losses == ""):
                raise EmptyFields(indice=None, sheet_num=None, specific_field="Losses")
            
            wins = int(wins)
            losses = int(losses)

            # Calculate and insert
            ratio = wins/losses
            self.ratiobox.delete("1.0", "end-1c")
            self.ratiobox.insert("insert", ratio)

        # Letters, anything
        except ValueError:
            self.feedbacklbl.config(text="System: Wrong Datatype, only integers")
        
        # If user types in nothing or something invalid
        except Exception as e:
            self.feedbacklbl.config(text=f"System: {e}")

    # Load method to get records from db
    def load(self) -> None:

        # Get records
        self.records: list[tuple] = self.connector.getRecords()
        
        # If there are none, let the user know
        if (len(self.records) == 0):
            self.feedbacklbl.config(text="No Records")
            self.feedbacklbl2.config(text="No Records")
            image = self.image_handler.blank_bg_image
            self.image_label.config(image=image)
            self.emptyDb = True
        
        # If there are, insert the first one and load up the listbox
        else:
            self.index, self.topIndex, self.sorted_recs = 0, len(self.records) - 1, self.records
            self.recInserter(index=self.index)
            self.list_load(self.sorted_recs)
            self.emptyDb = False
    
    # Load method for graphs, just checks db for new records
    def graph_load(self) -> None:

        # If connected
        if (self.connected):

            # Get records 
            self.match_ids = self.connector.get_table_names()

            # Set drop box options
            self.drop_box_options = []
            for i in self.match_ids:
                self.drop_box_options.append(i[1] + ' ' + str(i[6]) + " ID:" + str(i[0]))
            self.drop_box.config(values=self.drop_box_options)
            
            # Clear out 
            self.setBlanks(listboxdel=False, graph_del=True, scroller_del=False)

   
    # Load for the listbox
    def list_load(self, recs: list[tuple]) -> None:
        
        # Clear it
        self.listbox.delete(0,tk.END)

        # Loop through adding the records (v) at the given index (i)
        for i, v in enumerate(recs):
            v = f"{v[1]}  :  {v[5]} W/L Ratio  :  Age {v[2]}  :  Rank {v[3]}"
            self.listbox.insert(i, v)

    # All encompassing method for scroll buttons, increment is how much they want to increase, key is a keyword
    # type thing where specific words like "Forward" are tied to their own command
    def switchRec(self, increment: int, key: str) -> None:

        # Match is kind of like switch in c, using it to match up what command tie what button to
        match (key):

            # Go forward one
            case "Forward":

                # If we are at last record or no connection, pass
                if (self.index >= self.topIndex):
                    pass
                
                # Else add one
                else:
                    self.index += increment

            # Go back one
            case "Backward":

                # If going back one, check if we are at very first record, and if so, pass
                if (self.index <= 0):
                    pass
                
                # Else go forth
                else:
                    self.index -= increment

            # Jump three records
            case "Forward Three":

                # Check if going three forward is too far (higher than top index)
                if ((self.index + increment) >= self.topIndex):
                    self.index = self.topIndex
                
                # If all is good, keep going
                else:
                    self.index += increment

            # Go back three records
            case "Backward Three":

                # If going back three if too far or there is no connection, do nothing
                if ((self.index - increment) <= 0): 
                    self.index = 0
                
                # Else go ahead
                else:
                    self.index -= increment

            # Display first record
            case "First":
                self.index = 0


            # Display the last
            case "Last":
                self.index = self.topIndex

        # If we are connected, display
        if (self.connected and not self.emptyDb):
            self.recInserter(index=self.index)


    # Inserter method, allows you to just send and index through it and watch as the record at that index is displayed on screen. 
    def recInserter(self, index: int) -> None:

        # Clear all first
        self.setBlanks(listboxdel=False, graph_del=False, scroller_del=True)

        # Get the record and store in display rec using index parameter
        display_rec: tuple =  self.records[index]
 
        # Insert into text boxes
        self.namebox.insert("1.0", display_rec[1])
        self.agebox.insert("1.0", display_rec[2])
        self.rankbox.insert("1.0", display_rec[3])
        self.achievementsbox.insert("1.0", display_rec[4])
        self.ratiobox.insert("1.0", display_rec[5])

        # Get the file path from the record, resize it and configure to label
        binary_data = display_rec[6]

        self.new_image = self.image_handler.image_resizer(binary=binary_data, size=ImgSize.REGULAR)
        self.image_label.config(image=self.new_image)

    # Connect method for gui
    def connectionManager(self) -> None:
        
        try:
            # If false, (for toggle)
            if (not self.connected):

                # Configure menu button, toggle bool, connect, configure labels, and load
                self.appMenu.entryconfigure(2, label='Disconnect')
                self.connected = True
                self.connector.connect()
                self.feedbacklbl.config(text="System: Connected to database")
                self.feedbacklbl2.config(text="System: Connected to database")
                self.graph_feedback.config(text="System: Connected to database")
                self.news_feedback.config(text="System: Connected to database")
                self.load()
                self.graph_load()
            
            # Toggle off
            else:

                # Toggle bool, disconnect, set blanks to all, clear, configure labels,  clear dropbox and menu btn
                self.connected = False
                self.connector.disconnect()
                self.setBlanks(listboxdel=True, graph_del=True, scroller_del=True)
                self.records.clear()
                self.feedbacklbl.config(text="System: Disconnected from database")
                self.feedbacklbl2.config(text="System: Disconnected from database")
                self.news_feedback.config(text="System: Disconnected from database")
                self.graph_feedback.config(text="System: Disconnected from database")
                vals = []
                self.drop_box.config(values=vals)
                self.image_label.config(image=self.blank_image)
                self.appMenu.entryconfigure(2, label='Connect')

        # Never should happen, but have to make sure
        except Exception as e:
            self.feedbacklbl.config(text=f"System: {e}")
            self.feedbacklbl2.config(text=f"System: {e}")
            self.graph_feedback.config(text=f"System: {e}")
            self.news_feedback.config(text=f"System: {e}")

    # Crud, adding a record
    def addPlayer(self) -> None:

        # Try this
        try:

            # Getting the file path that is stored here
            image = self.img

            # This would occur if the user chooses not to upload anything
            # If so, set it to the blank white dummy image
            if (image is None):
                image = self.blank_binary
            
            # Else, keep going
            else:
                pass

            if (not self.connected):
                raise DbConnectionNotFound()

            # For toggle
            if (not self.addCommit) and (self.connected):
                
                # Alter boolean, configure button text, now waiting for user to hit commit
                self.addCommit = True
                self.addBtn.config(text="Commit")
                self.setBlanks(listboxdel=False, graph_del=False, scroller_del=True)
                self.feedbacklbl.config(text="System: Type in new player and hit commit")

            else:

                # Get the stuff the user has typed in
                name = self.namebox.get("1.0", tk.END)
                age = int(self.agebox.get("1.0", tk.END))
                rank = int(self.rankbox.get("1.0",tk.END))
                ratio = float(self.ratiobox.get("1.0", tk.END))
                achievements = self.achievementsbox.get("1.0",tk.END)

                # Turn all the elements into a tuple and pass it on to the inserter db method
                record: tuple = (name, age, rank, achievements, ratio, image)
                self.connector.insert(record=record)

                # For toggle functionality and also giving some user feedback
                self.addCommit = False
                self.addBtn.config(text="Add New")
                self.feedbacklbl.config(text="System: New player added! Db reloaded")

                # Load and set img to None. Blank slate for user to pick image from
                self.load()
                self.img = None

        # If something goes wrong, let the user know in the feedback label
        except Exception as err:
            self.feedbacklbl.config(text=f"System: {err}")

    # Check if the user has actually added an img
    def image_check(self, img):
        if (img != self.img) and (self.img is not None):
                img = self.img
        return img
     
    # Method to update record
    def updatePlayer(self) -> None:
        if (self.connected):
            # Get the current record
            rec_tuple: tuple = self.records[self.index]

            # Get the id
            identifier: int = rec_tuple[0]
            img = rec_tuple[6]
            img = self.image_check(img)
            
        # Try this
        try:
            
            # No connection
            if (not self.connected):
                raise DbConnectionNotFound()
            
            # Toggle
            if (not self.updateCommit):
                self.updateCommit = True
                self.updateBtn.config(text="Commit")
                self.feedbacklbl.config(text="Change what you need to and press commit")
            
            # Else, do the work, get the values and update, let the user know, load
            else:
                name = self.namebox.get("1.0", "end-1c")
                age = int(self.agebox.get("1.0", tk.END))
                rank = int(self.rankbox.get("1.0",tk.END))
                ratio = float(self.ratiobox.get("1.0", tk.END))
                achievements = self.achievementsbox.get("1.0",tk.END)
                record = (name, age, rank, achievements, ratio, img)
                self.connector.update(identifier=identifier, changed_elements=record)
                self.load()
                self.updateCommit = False
                self.updateBtn.config(text="Update")
                self.feedbacklbl.config(text="Updated Successfully! Db reloaded")

        # Something goes wrong
        except Exception as err:
            self.feedbacklbl.config(text=f"Error: {err}")

    # Actually create the tab
    def create_tab(self) -> None:

        # Try this
        try:
            
            # Just making sure
            if (not self.connected):
                raise DbConnectionNotFound()

            # Get selected record in listbox
            selected_player = (self.listbox.curselection())[0]

            # Get that rec
            rec_tuple: tuple = self.sorted_recs[selected_player]
            my_binary: bytes = rec_tuple[6]

            photo = self.image_handler.image_resizer(binary=my_binary, size=ImgSize.REGULAR)
            self.tab_dict[identifier := self.generate_id()] = [rec_tuple, photo]

            # Create title of tab
            title: str = f"Player: {rec_tuple[1].strip()}"

            # Lambda, for the delete btn
            tab_delete = lambda: self.tab_rec_delete()
            
            # EVERY VARIABLE HAS THE IDENTIFIER APPENDED TO IT. 'self.varname_{identifier}'
            # MAKES TABS COMPLETELY UNIQUE

            # Create new frame
            exec(f"self.new_tab_{identifier} = ttk.Frame(self.notebook)")
            exec(f"self.notebook.add(self.new_tab_{identifier}, text='{title}')")

            exec(f"self.tab_bg_{identifier} = tk.Label(self.new_tab_{identifier}, image=self.background_img)")
            exec(f"self.tab_bg_{identifier}.place(x=-10,y=-10)")

            exec(f"self.tab_canvas = tk.Canvas(self.new_tab_{identifier}, width=1000, height=100)")
            exec(f"self.tab_canvas.place(x=-10, y=580)")

            exec(f"self.tab_canvas.create_rectangle(0,0,self.tab_canvas.winfo_reqwidth(), self.tab_canvas.winfo_reqheight(), fill='#1A1A1A', outline='#1A1A1A')")

            # Name lbl
            exec(f"namelbl_{identifier} = tk.Label(self.new_tab_{identifier}, text='Name:', font=('Cascadia code', 14, 'bold'), fg='white', bg='#282626')")
            exec(f"namelbl_{identifier}.place(x=60,y=55)")

            # Name typed in here
            exec(f"self.namebox_{identifier} = tk.Text(self.new_tab_{identifier}, width=25, height=1, font=('Cascadia code', 13))")
            exec(f"self.namebox_{identifier}.place(x=125,y=58)")
            exec(f"self.namebox_{identifier}.insert(tk.END, rec_tuple[1])")

            # 'Age' is shown on a label
            exec(f"agelbl_{identifier} = tk.Label(self.new_tab_{identifier}, text='Age:', font=('Cascadia code', 14, 'bold'), fg='white', bg='#282626')")
            exec(f"agelbl_{identifier}.place(x=60, y=110)")

            # User types info here
            exec(f"self.agebox_{identifier} = tk.Text(self.new_tab_{identifier}, height=1, width=5, font=('Cascadia code', 13))")
            exec(f"self.agebox_{identifier}.place(x=113, y=114)")
            exec(f"self.agebox_{identifier}.insert(tk.END, rec_tuple[2])")

            # Rank here
            exec(f"ranklbl_{identifier} = tk.Label(self.new_tab_{identifier}, text='Global Rank:', font=('Cascadia code', 14, 'bold'), fg='white', bg='#282626')")
            exec(f"ranklbl_{identifier}.place(x=60, y=165)")

            # User types info here
            exec(f"self.rankbox_{identifier} = tk.Text(self.new_tab_{identifier}, width=10, height=1, font=('Cascadia code', 13))")
            exec(f"self.rankbox_{identifier}.place(x=200, y=169)")
            exec(f"self.rankbox_{identifier}.insert(tk.END, rec_tuple[3])")

            # Wins here
            exec(f"winlbl_{identifier} = tk.Label(self.new_tab_{identifier}, text=' W ', font=('Cascadia code', 14, 'bold'), fg='white', bg='#282626')")
            exec(f"winlbl_{identifier}.place(x=59, y=215)")

            # User types info here, number of wins
            exec(f"self.winbox_{identifier} = tk.Text(self.new_tab_{identifier}, width=3,height=1, font=('Cascadia code', 13))")
            exec(f"self.winbox_{identifier}.place(x=62, y=250)")


            # Loss label    
            exec(f"loselbl_{identifier} = tk.Label(self.new_tab_{identifier}, text='  L  ', font=('Cascadia code', 14, 'bold'), fg='white', bg='#282626')")
            exec(f"loselbl_{identifier}.place(x=106,y=215)")

            # User types info here, number of losses
            exec(f"self.losebox_{identifier} = tk.Text(self.new_tab_{identifier}, width=3,height=1, font=('Cascadia code', 13))")
            exec(f"self.losebox_{identifier}.place(x=120, y=250)")

            # Takes the numbers of wins and losses and gives back a ratio
            exec(f"calculate_ratio_btn_{identifier} = tk.Button(self.new_tab_{identifier}, text='Calculate -->', command=self.calc2, bg='#1e1e1e', fg='White', font=('cascadia code', 9))")
            exec(f"calculate_ratio_btn_{identifier}.place(x=174, y=250)")

            # Ratio here
            exec(f"ratiolbl_{identifier} = tk.Label(self.new_tab_{identifier}, text='Ratio', font=('Cascadia code', 14, 'bold'), fg='white', bg='#282626')")
            exec(f"ratiolbl_{identifier}.place(x=289, y=215)")

            # That ratio is displayed here
            exec(f"self.ratiobox_{identifier} = tk.Text(self.new_tab_{identifier}, width=5,height=1, font=('Cascadia code', 13))")
            exec(f"self.ratiobox_{identifier}.place(x=292,y=250)")
            exec(f"self.ratiobox_{identifier}.insert(tk.END, rec_tuple[5])")

            # Achivement lbl
            exec(f"achievementlbl_{identifier} = tk.Label(self.new_tab_{identifier}, text='Achievements', font=('Cascadia code', 14, 'bold'), fg='white', bg='#282626')")
            exec(f"achievementlbl_{identifier}.place(x=60, y=300)")

            # User types info here, notable wins, achievements, etc.
            exec(f"self.achievementsbox_{identifier} = tk.Text(self.new_tab_{identifier}, width=36, height=9, font=('Cascadia code light', 11))")
            exec(f"self.achievementsbox_{identifier}.place(x=61, y=331)")
            exec(f"self.achievementsbox_{identifier}.insert(tk.END, rec_tuple[4])")

            exec(f"self.img_frame_{identifier} = tk.Frame(self.new_tab_{identifier}, relief='solid', bg='white')")
            exec(f"self.img_frame_{identifier}.place(x=458,y=75)")

            # Border for the image label, makes it look like a picture frame
            exec(f"self.image_label_{identifier} = tk.Label(self.img_frame_{identifier})")
            exec(f"self.image_label_{identifier}.pack(fill='both', expand=True, padx=2, pady=2)")

            # Config it with the photoimage created earlier
            exec(f"self.image_label_{identifier}.config(image=self.tab_dict[identifier][1])")

            # Close the tab
            exec(f"self.close_tab_btn_{identifier} = tk.Button(self.new_tab_{identifier}, text='Close Tab', width=10, height=2, command=self.close_tab)")
            exec(f"self.close_tab_btn_{identifier}.place(x=10, y=590)")

            # Delete, got the lambda assigned here
            exec(f"self.del_tab_btn_{identifier} = tk.Button(self.new_tab_{identifier}, text='Delete', width=9, height=2, command=tab_delete)")
            exec(f"self.del_tab_btn_{identifier}.place(x=105, y=590)")

            # Label, gets configured when update or delete
            exec(f"self.feedbackTabLbl_{identifier} = tk.Label(self.new_tab_{identifier}, text='System: ', fg='white', bg='#1a1a1a')")
            exec(f"self.feedbackTabLbl_{identifier}.place(x=8, y=630)")
            
            # Update here
            exec(f"self.update_btn_tab_{identifier} = tk.Button(self.new_tab_{identifier}, text='Update', command=self.update_from_tab, height=2, width=8)")
            exec(f"self.update_btn_tab_{identifier}.place(x=195, y=590)")

            # Image upload here
            exec(f"self.upload_image_btn_{identifier} = tk.Button(self.new_tab_{identifier}, text='Upload an Image', command=self.image_from_tab, width=20, height=2)")
            exec(f"self.upload_image_btn_{identifier}.place(x=280, y=590)")

            # Put the user onto the new tab
            exec(f"self.notebook.select(self.new_tab_{identifier})")

        # Shouldn't really happen, but handle just in case
        except Exception as e:
            self.feedbacklbl2.config(text=f"System: {e}")

    # Close the tab but also remove it from the dict
    def close_tab(self) -> None:
        index = self.notebook.index("current")
        identifier = self.get_tab_id()
        self.notebook.forget(index)
        self.tab_dict.pop(identifier)

    # Search for the list tab
    def search(self) -> None:

        try: 
            keep_going = False

            # Clear the lists
            self.search_list.clear()
            self.narrowed_search.clear()

            # Append all the record names into the list
            for i in self.sorted_recs:
                self.search_list.append(i[1].strip().lower())

            # Get what the user typed in
            user_search = self.search_box.get().lower()
            
            # If user has not typed in anything
            if (len(user_search) == 0):
                keep_going = False
                raise EmptyFields(indice=None, sheet_num=None, specific_field="Search")

            # If they have
            else:
                
                # More narrow search. Seeing if what the user has typed in is in any of the search list items
                for i in self.search_list:
                    if (user_search in i):
                        self.narrowed_search.append(i)

                keep_going = True

            # If it goes through
            if (len(self.narrowed_search) > 0) and (keep_going):

                # Find the first instance of the user's search
                search_index = self.search_list.index(self.narrowed_search[0])
                self.listbox.selection_clear("0",tk.END)
                self.listbox.selection_set(search_index)
                self.feedbacklbl2.config(text="Found it!")

            # If it doesn't go through, let them know...
            else:
                self.feedbacklbl2.config(text="Can't Find That...")

        # If any exception
        except Exception as e:
            self.feedbacklbl2.config(text=f"System: {e}")

    # Return a random jumble of letters (import random, import string)
    def generate_id(self) -> str:
        return "".join(random.choices(string.ascii_uppercase, k=12))

    # Calculate ratio btn from tab
    def calc2(self) -> None:

        # Get the identifier of tab user is on
        identifier = self.get_tab_id()

        # Try this
        try:

            # Get win and loss number user typed in. Calculate and insert into record box
            exec(f"wins = int(self.winbox_{identifier}.get('1.0',tk.END))")
            exec(f"losses = int(self.losebox_{identifier}.get('1.0',tk.END))")
            exec(f"ratio: float = wins/losses")
            exec(f"self.ratiobox_{identifier}.delete('1.0',tk.END)")
            exec(f"self.ratiobox_{identifier}.insert(tk.END, ratio)")

        # Typed it something invalid
        except ValueError as e:
            exec(f'self.feedbackTabLbl_{identifier}.config(text=e)')
    
    # Getting the Identifier of the current tab
    def get_tab_id(self) -> str:

        # Get current id of tab. Get the id keys from tab_dict
        index = self.notebook.index("current")
        mykeys = [i for i in self.tab_dict.keys()]

        # The tab's index corresponds with the list item 4 indexes behind
        return mykeys[index - 4]
    
    # Method to upload image and display it in its tab
    def image_from_tab(self) -> None:

        # Try this
        try:
            # Ask the user which file they want of the specified types
            file_path = self.image_handler.get_file()
            

            # Get that into binary and send it to the resizer which returns the proper photoimage object
            # Set self.tab_img which is for updating the record (if the user decides to do so, insert the binary stored here into db)
            contents = self.image_handler.read_bin(file_path=file_path)
            self.tab_img = contents
            self.photo = self.image_handler.image_resizer(binary=contents, size=ImgSize.REGULAR)

            # Get the specific tab identifier of the tab that the user is on
            identifier = self.get_tab_id()

            # Config the label to that image
            exec(f"self.image_label_{identifier}.config(image=self.photo)")

        # User does not choose a file
        except:
            pass
    
    def update_from_tab(self) -> None:
        
        # Try this
        try:

            # Get the tab id first so that the program knows what tab the user is one and what record it is associated with
            identifier: str = self.get_tab_id()

            # Get the stuff the user has typed in
            exec(f"name = self.namebox_{identifier}.get('1.0', tk.END)")
            exec(f"age = self.agebox_{identifier}.get('1.0', tk.END)")
            exec(f"rank = self.rankbox_{identifier}.get('1.0',tk.END)")
            exec(f"ratio = self.ratiobox_{identifier}.get('1.0', tk.END)")
            exec(f"achievements = self.achievementsbox_{identifier}.get('1.0', tk.END)")

            # As default self.tab_image is set to empty string ""
            # When the user chooses an image to update the record to, it gets updated
            # If statement checks to see if it has changed and if it isn't the same as the previous image
            if (self.tab_img != "") and (self.tab_img != self.tab_dict[identifier][0][6]):
                exec(f"image_file = self.tab_img")
            
            # If the conditions are false, leave image_file as the same image (pull from dict)
            else:
                exec(f"image_file = self.tab_dict['{identifier}'][0][6]")

            

            # Create the tuple to send to the connector
            exec(f"rec_tuple = (name, age, rank, achievements, ratio, image_file)")
            
            # Get the record Id so the program knows what to delete
            rec_id = self.tab_dict[identifier][0][0]

            # Go through with it, and reset self.tab_img
            exec(f"self.connector.update(identifier=rec_id,changed_elements=rec_tuple)")
            exec(f"self.feedbackTabLbl_{identifier}.config(text='System: Updated!!')")
            self.load()
            self.tab_img = ""
        
        # Something goes wrong, let user know
        except Exception as err:
            exec(f"self.feedbackTabLbl_{identifier}.config(text=err)")

    # Method to remove all tabs that the user has opened
    def remove_all_tabs(self) -> None:
        
        # Pull the total number of tabs
        num_tabs = self.notebook.index("end")

        # If that goes over 4 (4 tabs {home and listView and graph and news} are default and always stay on screen)
        if (num_tabs > 4):

            # List of the tab indexes 
            # EXAMPLE: If we have 5 tabs this list will be [4,3,2]
            list_tab = [i for i in range(0,num_tabs)][4:][::-1]

            # Delete and clear the dictionary
            for x in list_tab: self.notebook.forget(x)

            self.tab_dict.clear()

    # Delete for home tab
    def delete_scroller(self) -> None:
        try:
            
            # If connected, select the record and ask the user if they actually want to go through with it
            if (self.connected):
                rec_tuple = self.records[self.index]
                record_id = rec_tuple[0]
                name = rec_tuple[1]

                confirm_bool: bool = self.connector.delete(record_id, name)

            # If no connection, raise err
            else: raise DbConnectionNotFound()

            # If statements handle user feedback
            if (confirm_bool):
                self.feedbacklbl.config(text=f'{name.strip()} has been deleted. Db reloaded.')
                self.load()

            if (not confirm_bool):
                self.feedbacklbl.config(text='Canceled Deletion.')

        # Anything goes wrong
        except Exception as err:
            self.feedbacklbl.config(text=f"System: {err}")

    # Delete from the list view
    def delete_listView(self) -> None:
        try:

            # If connected get the record and ask the user if they want to
            if (self.connected):
                selected_player: int = self.listbox.curselection()[0]
                rec_tuple: tuple = self.sorted_recs[selected_player]
                record_id, name = rec_tuple[0], rec_tuple[1]

                confirm_bool: bool = self.connector.delete(record_id, name)

            # Connection not found
            else: raise DbConnectionNotFound()

            # Handles user feedback
            if (confirm_bool):
                self.feedbacklbl2.config(text=f'{name.strip()} has been deleted. Db reloaded.')
                self.load()

            if (not confirm_bool):
                self.feedbacklbl2.config(text='Canceled Deletion.')

        # If the user hasn't selected anything in the listbox
        except IndexError:
            self.feedbacklbl2.config(text="System: Perhaps choose a record if you want to delete...")

        # Anything else
        except Exception as err:
            self.feedbacklbl2.config(text=f"System: {err}")

    # From tabs
    def tab_rec_delete(self) -> None:
        try:
            
            # Get the tab id and the label on the tab with getattr
            tab_identifier: str = self.get_tab_id()
            label: tk.Label = getattr(self, f'feedbackTabLbl_{tab_identifier}')

            # If connected, get the rec and ask the user if they want to 
            if (self.connected):
                record_id: int = self.tab_dict[tab_identifier][0][0]
                name: str = self.tab_dict[tab_identifier][0][1]
                confirm_bool: bool = self.connector.delete(record_id, name)

            # Connection not found
            else: raise DbConnectionNotFound()

            # Handles user feed back and send them back to the list tab
            if (confirm_bool):
                self.feedbacklbl2.config(text=f'{name.strip()} has been deleted. Db reloaded.')
                self.load()
                self.close_tab()
                self.notebook.select(1)

            if (not confirm_bool):
                label.config(text='Canceled Deletion.')
        
        # Anything happens
        except Exception as err:
            label.config(text=f'System Error: {err}')