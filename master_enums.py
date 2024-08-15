# Imports
from enum import Enum, auto

class Websites(Enum):
    """
    Stores Website links for easy access/validation
    
    ``Websites.EUROSPORT`` = https://www.eurosport.com/tennis/

    ``Websites.TENNIS_DOTCOM`` = https://www.tennis.com/news/

    ``Websites.ATPTOUR`` = https://www.atptour.com/en/news/

    ``Websites.TENNIS365`` = https://www.tennis365.com
    """

    EUROSPORT = "https://www.eurosport.com/tennis/"
    TENNIS_DOTCOM = "https://www.tennis.com/news/"
    ATPTOUR = "https://www.atptour.com/en/news/" 
    TENNIS365 = "https://www.tennis365.com"

class ImgSize(Enum):
    """
    Sizes for images across program

    ``ImgSize.COURT`` for bg image of the match data win, 

    ``ImgSize.BG_IMAGE`` for tab bg images, 

    ``ImgSize.REGULAR`` for home tab rec images
    """

    COURT = (700,570)
    BG_IMG = (910, 590)
    REGULAR = (350, 400)

class NewsViewMode(Enum):
    """
    Use for switching modes in news tab in gui

    ``NewsViewMode.FINDER`` for web scraper mode

    ``NewsViewMode.SCROLLER`` for db, connected mode
    
    """

    FINDER = auto()
    SCROLLER = auto()
