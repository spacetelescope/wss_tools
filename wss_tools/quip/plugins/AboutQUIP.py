"""
QUIP version info.

**Plugin Type: Global**

``AboutQUIP`` is a global plugin.  Only one instance can be opened.

**Usage**

This plugin allows access to view QUIP version information and operation
type for the current session.

"""
from __future__ import absolute_import, division, print_function

# GINGA
from ginga.GingaPlugin import GlobalPlugin
from ginga.gw import Widgets

__all__ = ['AboutQUIP']


class AboutQUIP(GlobalPlugin):

    def __init__(self, fv):
        super(AboutQUIP, self).__init__(fv)
        _no_value = 'unknown'
        self.op_type = _no_value

        try:
            from wss_tools.version import version
        except ImportError:
            self.version = _no_value
        else:
            self.version = version

        try:
            from wss_tools.quip.main import __taskname__, QUIP_DIRECTIVE
        except ImportError:
            self.taskname = _no_value
        else:
            self.taskname = __taskname__
            if QUIP_DIRECTIVE is not None:
                self.op_type = QUIP_DIRECTIVE.get('OPERATION_TYPE', _no_value)

    def build_gui(self, container):
        top = Widgets.VBox()
        top.set_border_width(4)

        vbox, sw, orientation = Widgets.get_oriented_box(container)
        vbox.set_border_width(4)
        vbox.set_spacing(2)

        # Take a text widget to show version info
        msgFont = self.fv.getFont('sansFont', 12)
        tw = Widgets.TextArea(wrap=True, editable=False)
        tw.set_font(msgFont)
        tw.set_text(self.info_string())

        vbox.add_widget(tw, stretch=0)
        top.add_widget(sw, stretch=1)

        btns = Widgets.HBox()
        btns.set_border_width(4)
        btns.set_spacing(3)

        btn = Widgets.Button('Close')
        btn.add_callback('activated', lambda w: self.close())
        btns.add_widget(btn, stretch=0)
        btns.add_widget(Widgets.Label(''), stretch=1)

        top.add_widget(btns, stretch=0)
        container.add_widget(top, stretch=1)

    def info_string(self):
        return '{0}\nOperation: {1}\nVersion: {2}'.format(
            self.taskname, self.op_type, self.version)

    def close(self):
        self.fv.stop_global_plugin(str(self))
        return True

    def __str__(self):
        return 'aboutquip'
