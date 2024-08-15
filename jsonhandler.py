# Imports
import json
from typing import Any

class JsonHandler:

    """
    JsonHandler objects handle json settings

    Get filtered settings with :py:meth:`JsonHandler.get_settings`
    it returns :return:`list`

    Get everything with :py:meth:`JsonHandler.get_all`

    Change language in settings with :py:meth:`JsonHandler.change_language`
    Accepts parameter :param:`lang` of type ``str``

    Save newly update settings with :py:meth:`JsonHandler.save_to_json`
    Accepts parameter :param:`contents` of type ``Any`` returns object of type ``Any``

    Deserialize instance containing json doc with :py:meth:`JsonHandler.convert_json`
    Accepts parameter :param:`contents` of type ``Any``

    Set custom theme with :py:meth:`JsonHandler.custom_theme_handler` 
    Accepts parameter :param:`name` of type ``str``

    Change theme of graphs with :py:meth:`JsonHandler.change_graph_theme`
    Accepts parameter :param:`theme` of type ``str``

    Serialize object to json formatted str with :py:meth:`JsonHandler.convert_str`
    parameter :param:`contents` of type ``Any`` returns :return:`str`
    """
    
    # Keep the file path in memory
    def __init__(self) -> None:
        self.json_settings = r"C:\Users\OMSAI\OneDrive\Desktop\ORGANIZER\IST\master project 2024\master_settings.json"

    # Method to get the lists of themes and current settings from file
    def get_settings(self) -> list:
        
        # Open the file
        with open(self.json_settings, "r") as json_file:

            # Load and get all settings
            contents = json.load(json_file)
            graph_color_dict = contents["User Theme"]["User"]
            languages = contents["Supported languages"]
            current_language = contents["User Theme"]["Lang"]["Language"]
            custom_themes = contents["Custom Graph Themes"]
            bg_img = contents["User Theme"]["Bg"]["Background"]

        # Return in list
        return [graph_color_dict, languages, current_language, custom_themes, bg_img]
    
    # While the method above gathers and returns settings in specific way
    # this just pulls all of it
    def get_all(self):
        with open(self.json_settings, "r") as json_file:
            return json.load(json_file)
    
    # Method to change the language in settings
    def change_language(self, lang: str) -> None:
        
        # Get the contents 
        contents = self.get_all()

        # Set the language
        self.current_language = contents["Supported languages"][lang]

        # Put in dict.
        contents["User Theme"]["Lang"]["Language"] = self.current_language

        # Save
        self.save_to_json(contents)

    # Save parameterized contents to file
    def save_to_json(self, contents: Any) -> None:
        with open(self.json_settings, 'w') as file:
            json.dump(contents, file, indent=4, ensure_ascii=True)

    # Str -> Usable Json
    def convert_json(self, contents) -> Any:
        return json.loads(contents)

    # Set the custom theme
    def custom_theme_handler(self, name: str) -> None:
        
        # Pull settings from Json
        contents = self.get_all()
            
        # Set to the name of the custom theme (parameter)
        self.graph_color_dict = contents["Custom Graph Themes"][name]

        # Set current setting
        contents["User Theme"]["User"] = self.graph_color_dict

        # Write to json file
        self.save_to_json(contents)

    # Change graph colors
    def change_graph_theme(self, theme: str) -> None:

        # Get it
        contents = self.get_all()
        
        # The theme name is a parameter so now just match it to the appropriate theme
        self.graph_color_dict = contents["Default Graph Themes"][theme]

        # Set ["User Theme"]["User"] which always just holds the current setting
        contents["User Theme"]["User"] = self.graph_color_dict

        # Write to the json file
        self.save_to_json(contents)

    # Json -> Usable Str
    def convert_str(self, contents: Any) -> str:
        return json.dumps(contents, indent=4)
