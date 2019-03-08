from ginga import GingaPlugin
from ginga.gw import Widgets

import os.path

# Plugin to draw helpful annotations for segment ID.
# based on Ginga example code MyGlobalPlugin.py
# modified by Marshall Perrin.


class SegIDHelper(GingaPlugin.GlobalPlugin):

    def __init__(self, fv):
        """
        This method is called when the plugin is loaded for the  first
        time.  ``fv`` is a reference to the Ginga (reference viewer) shell.

        """
        super(SegIDHelper, self).__init__(fv)

        # init some stuff for drawing annotations

        self.layertag = 'segidhelper-canvas'

        self.dc = fv.getDrawClasses()
        self.canvas = self.dc.DrawingCanvas()

    def build_gui(self, container):
        """
        This method is called when the plugin is invoked.  It builds the
        GUI used by the plugin into the widget layout passed as
        ``container``.
        This method could be called several times if the plugin is opened
        and closed.  The method may be omitted if there is no GUI for the
        plugin.

        This specific example uses the GUI widget set agnostic wrappers
        to build the GUI, but you can also just as easily use explicit
        toolkit calls here if you only want to support one widget set.
        """
        top = Widgets.VBox()
        top.set_border_width(4)

        # this is a little trick for making plugins that work either in
        # a vertical or horizontal orientation.  It returns a box container,
        # a scroll widget and an orientation ('vertical', 'horizontal')
        vbox, sw, orientation = Widgets.get_oriented_box(container)
        vbox.set_border_width(4)
        vbox.set_spacing(2)

        # Take a text widget to show some instructions
        self.msgFont = self.fv.getFont("sansFont", 12)
        tw = Widgets.TextArea(wrap=True, editable=False)
        tw.set_font(self.msgFont)
        self.tw = tw

        # Frame for instructions and add the text widget with another
        # blank widget to stretch as needed to fill emp
        fr = Widgets.Frame("Status")
        vbox2 = Widgets.VBox()
        vbox2.add_widget(tw)
        vbox2.add_widget(Widgets.Label(''), stretch=1)
        fr.set_widget(vbox2)
        vbox.add_widget(fr, stretch=0)

        # Add a spacer to stretch the rest of the way to the end of the
        # plugin space
        spacer = Widgets.Label('')
        vbox.add_widget(spacer, stretch=1)

        # scroll bars will allow lots of content to be accessed
        top.add_widget(sw, stretch=1)

        # A button box that is always visible at the bottom
        btns = Widgets.HBox()
        btns.set_spacing(3)

        # Add a close button for the convenience of the user
        btn = Widgets.Button("Close")
        btn.add_callback('activated', lambda w: self.close())
        btns.add_widget(btn, stretch=0)
        btns.add_widget(Widgets.Label(''), stretch=1)
        top.add_widget(btns, stretch=0)

        # Add our GUI to the container
        container.add_widget(top, stretch=1)

    # CALLBACKS

    def redo(self, channel, image):
        # Update display in response to new image
        fitsimage = channel.fitsimage

        # Ensure this plugin's canvas is added on top of
        # the current image's display
        p_canvas = fitsimage.get_canvas()
        if not p_canvas.has_object(self.canvas):
            p_canvas.add(self.canvas, tag=self.layertag)

        # auto zoom to fit
        fitsimage.zoom_fit()

        # clean out any prior annotations
        self.canvas.delete_all_objects()

        # add new annotations
        Text = self.canvas.get_draw_class('text')

        filename = os.path.basename(image.metadata['path'])
        t1 = Text(50, 50, filename, color='yellow', fontsize=20,
                  coord='window')
        self.canvas.add(t1)

        # Hard coded locations for NIRCam SW SCAs.
        # This will need updating if you change the mosaic settings.

        im_size = 256   # must match call to _segid_mosaics in QUIP main.py
        o = 20            # offset of text relative to SCA
        sw_sep = 21       # separation between SCAs in same module
        ab_gap = 150      # separation between modules A and B
        bot = im_size-o   # Y pos for bottom row
        top = bot + im_size+sw_sep    # Y pos for top row
        SCA_info = {
                'A1': [o, bot],
                'A2': [o, top],
                'A3': [o+im_size+sw_sep, bot],
                'A4': [o+im_size+sw_sep, top],
                'B1': [o+im_size*3+sw_sep*2+ab_gap, top],
                'B2': [o+im_size*3+sw_sep*2+ab_gap, bot],
                'B3': [o+im_size*2+sw_sep+ab_gap, top],
                'B4': [o+im_size*2+sw_sep+ab_gap, bot],
                }

        for scaname, location in SCA_info.items():
            # Annotate text for each SCA.

            # Repeated 2x for a hacky drop shadow effect,
            # for better visibility across a wider range of stretches
            t2s = Text(location[0]+1, location[1]-1, scaname,
                       color='black', fontsize=18, coord='data')
            self.canvas.add(t2s)

            t2 = Text(location[0], location[1], scaname,
                      color='orange', fontsize=18, coord='data')
            self.canvas.add(t2)

    def close(self):
        self.fv.stop_global_plugin(str(self))
        return True

    def __str__(self):
        """
        This method should be provided and should return the lower case
        name of the plugin.
        """
        return 'segidhelper'
