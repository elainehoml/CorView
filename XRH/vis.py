""" Module for generating visualisations of correlative imaging datasets

This module was created for visualising 2D histology images registered to 3D micro-CT datasets, but theoretically should apply to any 2D-3D dataset.

Last edited by Elaine Ho, University of Southampton

This code is licensed under the GNU General Public Licence v3.0.
"""

import os, sys, time
import numpy as np
import matplotlib.pyplot as plt
from PIL import Image
from IPython.display import display, clear_output
import ipywidgets as widgets
from ipyfilechooser import FileChooser
from skimage import io, util
import pandas as pd
from bokeh.plotting import figure, show
from bokeh.io import output_notebook, output_file
from bokeh.layouts import gridplot

instances_2D = {} # holds instances of 2D images
instances_3D = [] # holds instances of 3D images

class Image3D():
    """ 
    Imports a 3D image when button is pressed 
    
    Attributes
    ----------
    select_file : ipyfilechooser.FileChooser 
        Widget to choose file for 3D image
    load_button : ipywidgets.Button
        Button to load an image
    out
        Output to display from widgets
    img : array_like, uint8
        8-bit greyscale 3D image, (z,y,x)
    n_frames : int
        Number of frames in 3D image in z-direction
    
    Methods
    -------
    _create_widgets()
        Create widgets to select file and load image
    _on_load_button_clicked(change)
        Event handler to import image with PIL when load_button is clicked
    display_widgets()
        Displays widgets created in _create_widgets()
    get_img()
        Returns 3D image as uint8 array
    get_img_filename
        Returns filename of image as a string
    
    """
    
    def __init__(self):
        instances_3D.append(self) # stores self in a list of Image3D instances
    
    def _create_widgets(self):
        """ Create widgets to select file and load image """
        self.select_file = FileChooser(os.getcwd())
        self.load_button = widgets.Button(description="Load Image")
        self.load_button.on_click(self._on_load_button_clicked)
    
    def _on_load_button_clicked(self, change):
        """ Event handler to import image with PIL when load_button is clicked

        Parameters
        ----------
        change : event
            Event that load_button is clicked
        
        """
        self.out.clear_output()
        with self.out:
            print("Importing image {}, please wait...".format(self.select_file.selected_filename))
            img_import = io.imread(self.select_file.selected, plugin="pil")
            
            # Is the image a 3D stack?
            if len(img_import.shape) != 3:
                raise ValueError("Image is not a 3D stack, please choose another image")
                
            # Convert to 8-bit RGB
            self.img = util.img_as_ubyte(img_import)
            self.n_frames = int(len(self.img))
            print("Image successfully imported")
    
    def display_widgets(self):
        """ Displays widgets created in _create_widgets() """
        self._create_widgets()
        self.out = widgets.Output()
        display(self.select_file, self.load_button, self.out)
           
    def get_img(self):
        """ Returns 3D image as uint8 array

        Returns
        -------
        array_like
            uint8 array containing greyscale image pixel values arranged according to (z,y,x)
        
        """
        return self.img
    
    def get_img_filename(self):
        """ Returns filename of image as a string

        Returns
        -------
        str
            Filename of imported 3D image
        
        """

        return self.select_file.selected_filename

def show_3D_slider(img):
    """ Shows slice of image as determined by slider value

    Parameters
    ----------
    img : array_like
        Array containing 3D image
    
    """
    def show_slice(slice_number):
        """ Shows image slice from slice_number

        Parameters
        ----------
        slice_number : int
            Int between 0 and number of frames in 3D image
        
        """
        io.imshow(img[slice_number])
        io.show()
    slider = widgets.IntSlider(min=0, max=instances_3D[0].n_frames-1, step=1, description="Slice number")
    widgets.interact(show_slice, slice_number=slider)

class Image2D():
    """
    Imports a 2D image and records instances of itself
    
    Attributes
    ----------
    time_imported : str
        MM/DDHHMMSS string of time image is imported, used as unique ID in instances_2D dict
    select_file : ipyfilechooser.FileChooser 
        Widget to choose file for 3D image
    load_button : ipywidgets.Button
        Button to load an image
    position : ipywidgets.BoundedFloatText
        Textbox for user to type in corresponding microCT slice that matches 2D image, min=0, max=n_frames
    out
        Output to display from widgets
    img_2d : array_like
        uint8 array containing RGB 2D image (x,y,RGB)
    
    Methods
    -------
    _create_widgets()
        Create widgets for selecting file, loading image, typing in position of matching microCT slice
    _on_load_button_clicked(change)
        Event handler to import image with PIL when load_button is clicked
    display_widgets()
        Displays widgets created in _create_widgets()
    get_2D_img_fname()
        Returns filename of image as a string
    get_2D_img()
        Returns array containing imported image
    get_position()
        Returns position of matching microCT slice
    """
    
    def __init__(self):
        self.time_imported = time.strftime("%D%H%M%S", time.localtime()) # saves the time as a unique ID
        instances_2D[self.time_imported] = self
    
    def _create_widgets(self):
        """ Create widgets for selecting file, loading image, typing in position of matching microCT slice """
        self.select_file = FileChooser(os.getcwd())
        self.load_button = widgets.Button(description="Load image")
        self.position = widgets.BoundedFloatText(min=0, max=instances_3D[0].n_frames-1, step=1, description="Position of 2D image")
        self.load_button.on_click(self._on_load_button_clicked)
    
    def _on_load_button_clicked(self, change):
        """ Event handler to import image with PIL when load_button is clicked

        Parameters
        ----------
        change : event
            Event that load_button is clicked
        
        """
        self.out.clear_output()
        with self.out:
            print("Importing image {}, please wait...".format(self.select_file.selected_filename))
            img_import = io.imread(self.select_file.selected, plugin='pil')
            if len(img_import.shape) != 3:
                raise ValueError("Image is not 2D, please choose a 2D image")
            self.img_2d = util.img_as_ubyte(img_import) # 8bit RGB
            print("Image successfully imported")
    
    def display_widgets(self):
        """ Displays widgets created in _create_widgets() """
        self._create_widgets()
        self.out = widgets.Output()
        display(self.select_file, self.position, self.load_button, self.out)
    
    def get_2D_img_fname(self):
        """ Returns image filename

        Returns
        -------
        str
            Image filename
        """
        return self.select_file.selected_filename
    
    def get_2D_img(self):
        """ Returns array containing 2D image
        
        Returns
        -------
        array_like
            Array containing 2D RGB image
        """
        return self.img_2d
    
    def get_position(self):
        """ Returns position of matching microCT slice
        
        Returns
        -------
        int
            Slice number from microCT stack which matches histology
        """
        return int(self.position.value)

class CreateImage2D():
    """ 
    Creates Image2D instances 

    Attributes
    ----------
    widget_layout : widgets.Layout
        Sets widget appearances
    new_img_button : widgets.Button
        Button to add new image
    update_instances_button : widgets.Button
        Button to display instances of imported Image2D objects
    clear_all_button : widgets.Button
        Button to clear all instances of imported Image2D objects from instances_2D
    out
        Output from widgets
    
    Methods
    -------
    _create_widgets()
        Creates widgets to add new instance of Image2D, display instances recorded in instances_2D, clear all instances from instances_2D
    _import_2D(change)
        Creates instance of Image2D when new_img_button is pressed
    _display_instances(change)
        Displays instances of Image2D in instances_2D when update_instances_button is pressed
    _clear_all(change)
        Deletes instances of Image2D from instances_2D dict when clear_all_button is pressed
    display_widgets()
        Displays widgets created in _create_widgets()

    """
    def __init__(self):
        self.widget_layout = widgets.Layout(width='auto', height='40px')
    
    def _create_widgets(self):
        """ Creates widgets to add new instance of Image2D, display instances recorded in instances_2D, clear all instances from instances_2D """
        self.new_img_button = widgets.Button(description="Add new image", layout=self.widget_layout)
        self.new_img_button.on_click(self._import_2D)
        self.update_instances_button = widgets.Button(description="Display list of loaded images", 
                                                      layout=self.widget_layout)
        self.update_instances_button.on_click(self._display_instances)
        self.clear_all_button = widgets.Button(description="Clear all 2D images", layout=self.widget_layout)
        self.clear_all_button.on_click(self._clear_all)
        
    def _import_2D(self, change):
        """ Create instance of ImageImport2D 
        
        Parameters
        ----------
        change : event
            Checks if new_img_button is pressed

        """
        Img2D = Image2D()
        Img2D.display_widgets()
    
    def _display_instances(self, change):
        """ Displays all instances of ImageImport2D 
        
        Parameters
        ----------
        change : event
            Checks if update_instances_button has been pressed

        """
        clear_output()
        self.display_widgets()
        instance_2D_fnames = []
        instance_2D_positions = []
        for key in [*instances_2D.keys()]:
            instance_2D_fnames.append(instances_2D[key].get_2D_img_fname())
            instance_2D_positions.append(instances_2D[key].get_position())
        instance_2D_data = {'Key': [*instances_2D.keys()], 'Filenames': instance_2D_fnames, 
                            'Positions': instance_2D_positions}
        instance_2D_df = pd.DataFrame(data=instance_2D_data)
        display(instance_2D_df)
        
    def _clear_all(self, change):
        """ Deletes all instances of ImageImport2D from instance_2D dict. 
        Note that these instances are not deleted themselves, just the record of their existence.

        Parameters
        ----------
        change : event
            Checks if clear_all_button has been pressed
        
        """
        clear_output()
        self.display_widgets()
        with self.out:
            print("Clearing all 2D images")
            instances_2D.clear()
            print("Cleared all 2D images")
    
    def display_widgets(self):
        """ Displays widgets created in _create_widgets() """
        self._create_widgets()
        self.out = widgets.Output()
        hbox = widgets.HBox([self.new_img_button, self.update_instances_button, self.clear_all_button])
        vbox = widgets.VBox([hbox, self.out])
        display(vbox)

def rgba(img_2D, alpha=255):
    """ Convert RGB to RGBA image with alpha 
    
    Parameters
    ----------
    img_2D : array_like, shape = (x, y, 3)
        Array containing 2D RGB image
    
    alpha : int, default=255
        Alpha to display image when converted to RGBA image
    
    Returns
    -------
    array_like, shape = (x, y, 4)
        RGBA version of img_2D
    
    """
    shape = img_2D.shape
    alpha = np.full(shape=(shape[0],shape[1],1), fill_value=alpha, dtype='uint8') # create an alpha channel at full alpha
    img_rgba = np.concatenate((img_2D, alpha), axis=2) # join to rgb to make a rgba image

    return img_rgba

class CreateVis():
    """ Creates visualisations for given images 
    
    Attributes
    ----------
    img_3D : Image3D object
        3D image to display (this is microCT)
    widget_layout : widgets.Layout
        Settings for widgets appearance
    widget_style : dict
        kwargs for more widget appearance settings
    output_fname_textbox : widgets.Text
        Textbox for user to enter output filename
    output_fname : str
        Filename to save output file
    instances_2D_dropdown : widgets.Dropdown
        Dropdown menu to choose instance of Image2D to use
    img_2D : Image2D object
        Image2D instance chosen in instances_2D_dropdown
    generate_vis_button : widgets.Button
        Generates bokeh visualisation
    out
        Display output from widgets

    Methods
    -------
    _create_widgets()
        Creates widgets for user to input their desired output filename, select 2D image to display, button to generate visualisation
    _on_change_output_filename(change)
        Updates output_fname attribute when output_fname_textbox is updated
    _on_change_instances_2D(change)
        Updates img_2D attribute when instances_2D_dropdown is changed
    _generate_plot(change)
        Generates visualisation when generate_vis_button is pressed
    display_widgets()
        Displays widgets created in _create_widgets()

    """
    
    def __init__(self):
        if len(instances_3D) < 1:
            raise NameError("No CT image imported")
        else:
            self.img_3D = instances_3D[0]
        self.widget_layout = widgets.Layout(width='auto', height='40px')
        self.widget_style = {'description_width': 'auto'}
    
    def _create_widgets(self):
        """ Creates widgets for user to input their desired output filename, select 2D image to display, button to generate visualisation """

        # Choose output filename
        self.output_fname_textbox = widgets.Text(value="3DXRH-Vis.html", description="Enter desired output filename",
                                                layout=self.widget_layout, style=self.widget_style)
        self.output_fname = self.output_fname_textbox.value
        if self.output_fname.endswith('.html') == False:
            self.output_fname+='.html' # ensures correct file extension
        self.output_fname_textbox.observe(self._on_change_output_filename, names='value')
        
        # Select one of 2D instances to display
        options = []
        for key in [*instances_2D.keys()]:
            options.append(("{} at position {}".format(instances_2D[key].get_2D_img_fname(), 
                                                            instances_2D[key].get_position()), key))
        self.instances_2D_dropdown = widgets.Dropdown(options=options, value=[*instances_2D.keys()][0],
                                                     description="2D image to display", layout=self.widget_layout,
                                                     style=self.widget_style)
        self.instances_2D_dropdown.observe(self._on_change_instances_2D, names='value')
        self.img_2D = instances_2D[self.instances_2D_dropdown.value]
    
        # Button to generate visualisation
        self.generate_vis_button = widgets.Button(description="Generate visualisation", layout=self.widget_layout,
                                                 style=self.widget_style)
        self.generate_vis_button.on_click(self._generate_plot)
          
    def _on_change_output_filename(self, change):
        """ Updates self.output_fname attribute when dropdown menu is changed 
        
        Parameters
        ----------
        change : event
            Checks if output_fname_textbox has changed value

        """
        self.output_fname = change.new
        if self.output_fname.endswith('.html') == False:
            self.output_fname+='.html' # ensures correct file extension
    
    def _on_change_instances_2D(self, change):
        """ Updates self.img_2D attribute when dropdown menu is changed 
        
        Parameters
        ----------
        change : event
            Checks if instances_2D_dropdown has changed value

        """
        self.img_2D = instances_2D[change.new]
    
    def _generate_plot(self, change):
        """ Generates visualisation when generate_vis_button is pressed 
        
        Parameters
        ----------
        change : event
            Checks if generate_vis_button has been pressed
        
        """
        img_CT = self.img_3D.get_img()
        img_histo = self.img_2D.get_2D_img()
        CT_slice = self.img_2D.get_position()
        tools = "pan, wheel_zoom, box_zoom, reset"
        
        # set up Bokeh
        output_file(self.output_fname, "Correlative micro-CT and histology")
        
        # show CT
        p_CT = figure(plot_width=500, plot_height=500, title="CT slice {}".format(str(CT_slice)), tools=tools)
        p_CT.image(image=[img_CT[int(CT_slice)]], x=[0], y=[0], dw=[img_CT.shape[2]], dh=[img_CT.shape[1]],palette="Greys256")

        # show histo
        p_histo = figure(plot_width=500, plot_height=500, x_range=p_CT.x_range, y_range=p_CT.y_range, 
                         title="Histology {}".format(self.img_2D.get_2D_img_fname()), tools=tools)
        p_histo.image_rgba(image=[rgba(img_histo)], x=[0], y=[0], dw=[img_CT.shape[2]], dh=[img_CT.shape[1]])

        p = gridplot([[p_CT, p_histo]])
        show(p)
        
    def display_widgets(self):
        """ Displays widgets created in _create_widgets() """
        self._create_widgets()
        self.out = widgets.Output()
        hbox = widgets.HBox([self.output_fname_textbox, self.instances_2D_dropdown])
        vbox = widgets.VBox([hbox, self.generate_vis_button, self.out])
        display(vbox)