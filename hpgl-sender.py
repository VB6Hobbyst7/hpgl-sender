#!/usr/bin/env python3

import os
import sys
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gio, GdkPixbuf
import plotlib

APP_VERSION = '0.1.0'
APP_NAME = 'HPGL Sender v.' + APP_VERSION

class Status:
    IDLE = 'IDLE'
    PLOTTING = 'PLOTTING'
    ERROR = 'ERROR'
    DONE = 'DONE'

class Widgets:
    builder = None
    window = None
    filechooser = None
    plot_button = None
    plotter_preferences_button = None
    plotter_refresh_button = None
    plotter_dropdown = None
    status_label = None

    def initialize(self, app, handler):
        self.initialize_builder(app, handler)
        self.initialize_window(app, handler)
        self.initialize_filechooser(app, handler)
        self.initialize_plot_button(app, handler)
        self.initialize_plotter_preferences_button(app, handler)
        self.initialize_plotter_refresh_button(app, handler)
        self.initialize_plotter_dropdown(app, handler)
        self.initialize_status_label(app, handler)

    def initialize_builder(self, app, handler):
        self.builder = Gtk.Builder()
        self.builder.add_from_file('ui.glade')

    def initialize_window(self, app, handler):
        self.window = self.builder.get_object('main_window')
        self.window.set_application(app)
        self.window.show_all()
        self.window.set_title(APP_NAME)
        self.window.connect('destroy', handler.on_window_destroy)

    def initialize_filechooser(self, app, handler):
        self.filechooser = self.builder.get_object('open_file_button')
        self.filechooser.connect('file-set', handler.on_file_chosen)

    def initialize_plot_button(self, app, handler):
        self.plot_button = self.builder.get_object('plot_button')
        self.plot_button.set_sensitive(False)
        self.plot_button.connect('clicked', handler.on_plot_clicked)

    def initialize_plotter_preferences_button(self, app, handler):
        self.plotter_preferences_button = self.builder.get_object('plotter_preferences_button')
        self.plotter_preferences_button.set_sensitive(False)

    def initialize_plotter_refresh_button(self, app, handler):
        self.plotter_refresh_button = self.builder.get_object('plotter_refresh_button')
        self.plotter_refresh_button.set_sensitive(True)
        self.plotter_refresh_button.connect('clicked', handler.on_plotter_refresh_clicked)

    def initialize_plotter_dropdown(self, app, handler):
        self.plotter_dropdown = self.builder.get_object('choose_plotter_dropdown')
        self.plotter_dropdown.connect('changed', handler.on_plotter_selected)

    def initialize_status_label(self, app, handler):
        self.status_label = self.builder.get_object('status_label')

class HPGLSender:
    app = None
    widgets = None
    file = None
    plotter_port = None
    plotter_baud_rate = 9600
    status = None

    def __init__(self):
        self.app = Gtk.Application.new('pl.jsph.hpgl-sender', Gio.ApplicationFlags(0))
        self.app.connect('activate', self.on_app_activate)
        self.app.connect('shutdown', self.on_app_shutdown)
        self.widgets = Widgets()

    def on_app_activate(self, app):
        self.widgets.initialize(app, self)
        self.set_status(Status.IDLE)
        self.list_plotters()

    def on_app_shutdown(self, app):
        self.app.quit()

    def on_window_destroy(self,window):
        window.close()

    def on_file_chosen(self, widget):
        self.file = widget.get_file()
        self.maybe_set_ready()

    def on_plot_clicked(self, widget):
        self.set_status(Status.PLOTTING)
        self.maybe_set_ready()
        try:
            plotlib.plot(self.plotter_port, self.plotter_baud_rate, self.file)
        except Exception as e:
            self.set_status(Status.ERROR)
            print(e)
        else:
            self.set_status(Status.DONE)
        self.maybe_set_ready()

    def on_plotter_selected(self, widget):
        self.plotter_port = widget.get_active_text()
        self.maybe_set_ready()

    def on_plotter_refresh_clicked(self, widget):
        self.list_plotters()

    def maybe_set_ready(self):
        if self.file is not None and self.plotter_port is not None and self.is_ready():
            self.widgets.plot_button.set_sensitive(True)
        else:
            self.widgets.plot_button.set_sensitive(False)

    def is_ready(self):
        return self.status in [Status.IDLE, Status.DONE, Status.ERROR]

    def set_status(self, status):
        messages = {
            Status.IDLE: 'Ready',
            Status.DONE: 'Job completed',
            Status.PLOTTING: 'Currently working…',
            Status.ERROR: 'Error',
        }
        self.status = status
        self.widgets.status_label.set_text(messages[status])

    def list_plotters(self):
        self.widgets.plotter_dropdown.remove_all()
        for port in plotlib.list_serial_ports():
            self.widgets.plotter_dropdown.append(port.device, port.device)

    def run(self, argv):
        self.app.run(argv)

app = HPGLSender()
app.run(sys.argv)
