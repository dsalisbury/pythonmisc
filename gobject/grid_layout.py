import random

from gi.repository import Clutter
from gi.repository import GtkClutter
from gi.repository import Gtk

GtkClutter.init([])

window = Gtk.Window()

clutter_embed = GtkClutter.Embed()
window.add(clutter_embed)

stage = clutter_embed.get_stage()

# This gets bound onto the actor being managed by the layout; without it
# the actor won't know its width for reflowing content
bind_constraint = Clutter.BindConstraint.new(
    source=stage, coordinate=Clutter.BindCoordinate.SIZE, offset=0.0)

# Top-level container, managed by the layout manager
box = Clutter.Actor()
box.set_position(0, 0)
box.add_constraint(bind_constraint)

flow = Clutter.FlowLayout(orientation=Clutter.FlowOrientation.HORIZONTAL)
flow.set_column_spacing(20)
flow.set_row_spacing(10)
box.set_layout_manager(flow)
stage.add_actor(box)

num_rects = 22
for i in range(num_rects):
    red = Clutter.Color().new(255, 0, 0, 255)
    rect = Clutter.Actor.new()
    rect.set_background_color(red)
    rect.set_size(random.randrange(50.0, 100), random.randrange(50.0, 100))

    black = Clutter.Color().new(0, 0, 0, 255)
    t = Clutter.Text.new_with_text('Sans 20px', str(i))
    t.set_color(black)
    rect.add_child(t)
    box.add_child(rect)

window.connect('destroy', Gtk.main_quit)
window.show_all()
Gtk.main()
