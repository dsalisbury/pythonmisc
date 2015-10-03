import signal

import asyncio
import gbulb

from gi.repository import Clutter
from gi.repository import GtkClutter
from gi.repository import Gtk

from helpers import maybe_stop_helper
from show_hide_timer import ControlHider


class ConstrainedControlHider(ControlHider):
    def build_controls(self):
        super().build_controls()
        align_constraint = Clutter.AlignConstraint.new(
            source=self.stage, axis=Clutter.AlignAxis.X_AXIS, factor=0.5)
        self.actor.add_constraint(align_constraint)


if __name__ == '__main__':
    asyncio.set_event_loop_policy(gbulb.GtkEventLoopPolicy())
    GtkClutter.init([])
    loop = asyncio.get_event_loop()

    window = Gtk.Window()

    clutter_embed = GtkClutter.Embed()
    window.add(clutter_embed)

    stage = clutter_embed.get_stage()
    stage.set_color(Clutter.Color.new(0, 0, 0, 255))
    hidey = ConstrainedControlHider(stage=stage, loop=loop)

    # hit q or escape to quit
    stage.connect('key-press-event', maybe_stop_helper(loop))

    window.connect('destroy', lambda *a: loop.stop())
    window.show_all()

    # Make ctrl+c work, otherwise it gets swallowed somewhere
    loop.add_signal_handler(signal.SIGINT, loop.stop)

    # gogo gadget event loop
    loop.run_forever()
