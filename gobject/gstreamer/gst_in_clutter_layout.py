import signal

import asyncio
import gbulb

from gi.repository import Clutter
from gi.repository import GtkClutter
from gi.repository import Gtk
from gi.repository import Gst
from gi.repository import ClutterGst

# hokey way of importing from the directory above
import sys
from os.path import dirname, join
sys.path.append(join(dirname(__file__), '..'))

from helpers import maybe_stop_helper

if __name__ == '__main__':
    asyncio.set_event_loop_policy(gbulb.GtkEventLoopPolicy())
    GtkClutter.init([])
    Gst.init([])

    loop = asyncio.get_event_loop()

    window = Gtk.Window()

    clutter_embed = GtkClutter.Embed()
    window.add(clutter_embed)
    stage = clutter_embed.get_stage()

    # This gets bound onto the actor being managed by the layout; without it
    # the actor won't know its width for reflowing content
    bind_constraint = Clutter.BindConstraint.new(
        source=stage, coordinate=Clutter.BindCoordinate.SIZE, offset=0.0)

    # This is going to arrange our video elements
    layout = Clutter.GridLayout()
    layout.set_column_spacing(5)
    layout.set_row_spacing(5)

    # Top-level container, managed by the layout manager
    box = Clutter.Actor()
    box.set_position(0, 0)
    box.add_constraint(bind_constraint)
    box.set_layout_manager(layout)
    stage.add_actor(box)

    pipeline = Gst.Pipeline()
    patterns = ('ball', 'snow', 'smpte', 'spokes')
    for i, pattern in enumerate(patterns):
        video_in = Gst.ElementFactory.make('videotestsrc', 'vid{}'.format(i))
        video_in.set_property('pattern', pattern)
        pipeline.add(video_in)

        caps = Gst.Caps.from_string('video/x-raw, width=1280, height=720')
        capsfilter = Gst.ElementFactory.make("capsfilter", "f{}".format(i))
        capsfilter.set_property('caps', caps)
        pipeline.add(capsfilter)

        video_out = ClutterGst.VideoSink()
        pipeline.add(video_out)

        video_in.link(capsfilter)
        capsfilter.link(video_out)

        video_actor = Clutter.Actor()
        video_content = ClutterGst.Aspectratio()
        video_content.set_sink(video_out)
        video_actor.set_content(video_content)
        video_actor.set_width(320)
        video_actor.set_height(180)
        layout.attach(video_actor, i, i, 1, 1)
        video_actor.set_x_align(Clutter.ActorAlign.CENTER)

    window.show_all()

    pipeline.set_state(Gst.State.PLAYING)

    stage.connect('key-press-event', maybe_stop_helper(loop))
    loop.add_signal_handler(signal.SIGINT, loop.stop)
    loop.run_forever()
