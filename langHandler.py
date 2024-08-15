# Imports
from langdetect import detect
from langcodes import standardize_tag, find as find_tag
from deep_translator import GoogleTranslator
from nltk.corpus import stopwords 
from nltk.tokenize import word_tokenize, sent_tokenize 

# POCO class
class LangHandler:
    
    # Initialize the translator object
    def __init__(self) -> None:
        self.translator = GoogleTranslator()
    
    # Translates text
    def translate_text(self, vals: list, target: str, source: str) -> list:

        # Set the source and target languages
        self.source_targ(source, target)
        translated_vals = []

        # Translate and return
        for x in vals:
            translated_vals.append(self.translator.translate(x))

        return translated_vals
    
    # Set the source and target languages (properties of translator object)
    def source_targ(self, source: str, target: str) -> None:
        self.translator.source = source
        self.translator.target = target

    # Return tag of language after detecting and abbreviating
    def get_lang(self, text: str) -> str:
        detected_lang = detect(text)
        abbr = standardize_tag(detected_lang)
        return abbr
    
    # Get the tag straight from the language's name
    def get_tag(self, lang: str) -> str:
        return find_tag(lang)

    def summarize(self, text: str) -> str:

        # First step is to tokenize or shorten down the text into words
        # Stopwords are words that don't carry to much value in the language
        stop_words = set(stopwords.words("english")) 
        words = word_tokenize(text) 


        # Create a frequency table that tracks how many times a words appears in the text
        # Dont add stopwords
        freq_table = dict() 
        for word in words: 
            word = word.lower() 
            if word in stop_words: 
                continue
            if word in freq_table: 
                freq_table[word] += 1
            else: 
                freq_table[word] = 1

        # Get the sentences from the text
        # Iterate over and check for words from frequency table
        # Give a sentence score for that which is used for determining the 
        # value of the sentence in the text overall
        sentences = sent_tokenize(text) 
        sentence_value = dict() 
        for sentence in sentences: 
            for word, freq in freq_table.items(): 
                if word in sentence.lower(): 
                    if sentence in sentence_value: 
                        sentence_value[sentence] += freq 
                    else: 
                        sentence_value[sentence] = freq 


        # Calculate the average sentence value
        sumValues = 0
        for sentence in sentence_value: 
            sumValues += sentence_value[sentence]
        average = int(sumValues / len(sentence_value)) 

       
        # See if sentences are worth having in the summary
        # They have to meet a certain threshold (number) to be added
        # If important
        summary = '' 
        for sentence in sentences: 
            if (sentence in sentence_value) and (sentence_value[sentence] > (1.2 * average)): 
                summary += " " + sentence 
        
        return summary
