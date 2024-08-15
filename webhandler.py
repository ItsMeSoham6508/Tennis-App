# Imports
import requests
from bs4 import BeautifulSoup
from master_enums import Websites
from langHandler import LangHandler


class WebScraper:

    """
    WebScraper objects handle webscraping tasks

    Find articles with :py:meth:`WebScraper.find_articles` which returns
    :return:`list` of article links. Accepts parameters :param:`url` of type ``master_enums.Websites``

    Open said article with :py:meth:`WebScraper.open_article` which returns :return:`list`
    of article contents. Accepts parameters :param:`website` of type ``master_enums.Websites``, 
    :param:`url` of type ``str``, :param:`lang` of type ``str``
    """

    # All fields initialized
    def __init__(self) -> None:

        # Websites may end up checking this header string to make sure it is a browser that is making the request
        self.header = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36"}

        # Initialize a session which will manage connections
        # This will allow for reusing connections instead of starting a new one every time
        # Also deals with cookies
        self.my_session = requests.Session()

        self.lang_handler = LangHandler()


    # Method to find the articles off of the site
    def find_articles(self, url: Websites) -> list:
        
        # Make a request to the website
        html = self.my_session.get(url.value, headers=self.header)

        # Create Beautiful soup object which will allow me to go through it and get what i want
        soup = BeautifulSoup(html.content, "html.parser")

        # Links stored here and eventually returned
        vals = []
        
        # Different website means different operation so run check
        if (url == Websites.EUROSPORT):
                
            # Get all div tags with the specified class in a list
            links = [link for link in soup.find_all("div", attrs={"class":"flex flex-col","data-testid": "organism-secondary-card"})]

            # Loop through adding links to list and textbox
            for i in links:

                # Find a tags and get the href link
                link = (i.find("a")).get("href")

                if ("/highlights" not in link) and ("/exclusive" not in link):
                    vals.append(link)

        # For the next website
        if (url == Websites.TENNIS_DOTCOM):

            # Get all div tags of the specified class in a list
            links = [link for link in soup.find_all("div", attrs={"class":"d3-l-col__col-4"})]

            # Looping through adding links to list and text box
            for i in links:

                # Concatenate the strings as when it is retrieved from html is cut off partially
                link = "https://www.tennis.com" + str((i.find("a")).get("href"))

                # Add to list and textbox
                vals.append(link)

        # Next Website 
        if (url == Websites.ATPTOUR):

            # Get all a tags of the specified class
            links =  [link.get("href") for link in soup.find_all("a", attrs={"class":"card-link"})]

            # Loop through, same thing
            for i in links:
                link = "https://www.atptour.com" + str(i)
                
                if ("video" not in link):
                    vals.append(link)

        # Next website
        if (url == Websites.TENNIS365):

            # Find the a tag and get href link from a h2 tags with the specified class
            links = [link.find("a").get("href") for link in soup.find_all("h2", attrs={"class":"mb-2 mt-3 px-3 text-base font-semibold leading-snug text-title xs:px-4"})]

            # Same operation
            for i in links:
                link = str(i)
                vals.append(link)

        return vals
    
    # Once we have the articles, open them up
    def open_article(self, website: Websites, url: str, language: str) -> list:

        # Every text item stored here
        vals = []

        # Get the html
        html = self.my_session.get(url, headers=self.header)

        # Beautiful Soup object to parse 
        soup = BeautifulSoup(html.content, "html.parser")

        # If statements check website, as it affects the operation
        if (website == Websites.EUROSPORT):
            
            # Get the title, short summary at the start (h2_header, its in a h2 tag), and getting the content (like the actual paragraphs of info)
            title = soup.find("h1", attrs={"class":"mb-5 text-onLight-02 sm:mb-6 lg:mb-5 caps-s2-rs font-bold"})
            h2_header = soup.find("h2", attrs={"class":"mb-5 text-onLight-02 caption-s3-fx"})
            contents = soup.find_all("div", attrs={"data-testid": "atom-body-paragraph", "class":"break-words text-onLight-02 article-s4-rs"})

            # Put in vals
            vals = [title.text, h2_header.text]


        # Next website
        if (website == Websites.TENNIS_DOTCOM):

            # Title, summary, and contents, different classes though
            title = soup.find("h1",attrs={"class":"oc-c-article__title"})
            summary = soup.find("p",attrs={"class":"oc-c-article__summary"})
            contents = soup.find_all("div", attrs={"class":"oc-c-body-part oc-c-markdown-stories"})

            # Set vals
            vals =[title.text, summary.text]            

        # Next Website
        if (website == Websites.ATPTOUR):

            # Same stuff, different tags/classes
            title = soup.find("h2")
            tagline = soup.find("div", attrs={"class":"tagline"})
            contents = soup.find_all("p")

            # Set vals
            vals =[title.text, tagline.text]

        # Next website
        if (website == Websites.TENNIS365):

            # Title and contents
            title = soup.find("h1", attrs={"class":"py-4 text-xl font-normal text-title sm:text-2xl"})
            contents = soup.find_all("p")

            # Set vals
            vals = [title.text]

        # At end, insert contents, translating them 
        for i in contents:
            vals.append(str(i.text))
        
        vals = self.lang_handler.translate_text(vals=vals, target=language, source="en")
        
        # Finally give it back
        return vals
