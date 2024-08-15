"""
Soham Mutalik Desai
Commander Schenk
3rd period IST
Master Project ImageHandler class
Started: 4/25/24
"""

# Imports
from io import BytesIO
from PIL import Image, ImageTk
from tkinter.filedialog import askopenfilename
from pathlib import Path
from master_enums import ImgSize

class ImageHandler:

    """
    Image handler objects manipulate and create images

    Resize images with :py:meth:`ImageHandler.image_resizer` which takes
    parameters :param:`binary` accepts `bytes`, :param:`size` accepts enum from
    ``master_enums.ImgSize``

    Return binary of file with :py:meth:`ImageHandler.read_bin` which takes
    parameters :param:`file_path` of type `str`

    Get file path with :py:meth:`ImageHandler.get_file`
    returns file path of type `str`

    BASE IMAGES

    ``ImageHander.court_img`` for match data win in ``masterGui.py`` of type ``ImageTk.PhotoImage``

    ``ImageHandler.blank_bg_image`` for placeholder image on homeTab of type ``ImageTk.PhotoImage``

    ``ImageHandler.blank_binary`` for blank image binary data to put in db if required of type ``bytes``

    ``ImageHandler.background_img`` for tab bgs
    """


    # All fields initialized
    def __init__(self) -> None:

        # Get dir. path
        self.dir_path = Path.cwd()
        
        # This this is the object that store the image for the window that the user opens to
        # Add match data in the sheet
        self.court_path = self.dir_path / "court.jpg"
        self.court_img = self.full_convert(file=self.court_path, size=ImgSize.COURT)

        # Blank white dummy image, used when user does npt specifiy a file for a record and on load
        self.blank_img_file = self.dir_path / "blank_image.png"
        self.blank_bg_image = self.full_convert(file=self.blank_img_file, size=ImgSize.REGULAR)

        # Get the binary of that to which is stored in db in the case that the user does 
        # not chose a file
        self.blank_binary = self.read_bin(self.blank_img_file)

        # Get the background images for the tabs stored in memory real quick
        self.background_img = self.full_convert(file=(self.dir_path / "background_edit.png"), size=ImgSize.BG_IMG)
        self.clay_bg = self.full_convert(file=(self.dir_path / "tennis-clay-court-view-birds-600nw-1298187775.png"), size=ImgSize.BG_IMG)

    # Image resizer method, accepts binary data, and bg_img (used for knowing what size to make it) as params
    def image_resizer(self, binary: bytes, size: ImgSize) -> ImageTk.PhotoImage:

        # BytesIo object is like a file object for handling binary data
        image_data = BytesIO(binary)

        image = Image.open(image_data).resize(size.value, Image.Resampling.LANCZOS)

        # Do the final conversion
        final_image = ImageTk.PhotoImage(image)

        # Hand it back
        return final_image

    # Simple, just open a file and return the binary
    def read_bin(self, file_path: str) -> bytes:
        with open(file_path, "rb") as file:
            binary_contents = file.read()
        return binary_contents
    
    # Ask user to choose a file path of .png or .jpeg
    def get_file(self) -> str:
        return askopenfilename(defaultextension=".png", filetypes=[("Image Files", ".png .jpeg")])
    
    # Combine a couple of these steps (shortens code)
    def full_convert(self, file: str, size: ImgSize) -> ImageTk.PhotoImage:
        binary_data = self.read_bin(file)
        image = self.image_resizer(binary_data, size)
        return image
    
