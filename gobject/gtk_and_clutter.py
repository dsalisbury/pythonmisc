'''
Mixing Clutter things and GTK windows/widgets. The general idea is this:

Window
  + Vbox
    + GtkClutterEmbed
      + Stage
        + GtkClutterActor
          + GtkButton
    + GtkButton
'''
from gi.repository import GtkClutter
from gi.repository import Gtk

GtkClutter.init([])
Gtk.init([])

window = Gtk.Window()

vbox = Gtk.VBox(homogeneous=False, spacing=10)
window.add(vbox)

button = Gtk.Button('vbox_button')
button.connect('clicked', Gtk.main_quit)
vbox.pack_end(button, expand=False, fill=False, padding=0)

stage_button = Gtk.Button(label='stage_button')
stage_button.connect('clicked', lambda _: print('clicked the stage button!'))
button_actor = GtkClutter.Actor(contents=stage_button)

clutter_embed = GtkClutter.Embed()
stage = clutter_embed.get_stage()
stage.add_actor(button_actor)

vbox.pack_start(clutter_embed, expand=True, fill=True, padding=0)

window.connect('destroy', Gtk.main_quit)
window.show_all()
Gtk.main()
