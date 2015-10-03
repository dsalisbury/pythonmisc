import signal

import asyncio
import gbulb

from gi.repository import Clutter
from gi.repository import GtkClutter
from gi.repository import Gtk

from helpers import maybe_stop_helper


class ControlHider:
    def __init__(self, stage, loop=None):
        self.stage = stage
        self.loop = loop or asyncio.get_event_loop()
        self.timer = None
        self.build_controls()

    def build_controls(self):
        self._button = Gtk.Button(label='stage_button')
        self._button.connect('clicked', lambda _: self.loop.stop())
        self.actor = GtkClutter.Actor(contents=self._button)
        self.stage.add_actor(self.actor)
        # FIXME: needed?
        self.actor.save_easing_state()
        # when we waggle the mouse about we should go do stuff
        self.stage.connect('motion-event', self.mouse_activity)
        self.hide()

    def show(self):
        self.actor.set_opacity(255)

    def hide(self):
        self.actor.set_opacity(0)

    def mouse_activity(self, actor, event):
        ''' Show the control if not visible, refresh hide timer if it is '''
        self.show()
        if self.timer:
            # FIXME: is there a way to reschedule a call_later without just
            # destroying it and making a new one?
            self.timer.cancel()
            self.timer = None
        self.timer = self.loop.call_later(2, self.hide)


if __name__ == '__main__':
    asyncio.set_event_loop_policy(gbulb.GtkEventLoopPolicy())
    GtkClutter.init([])
    loop = asyncio.get_event_loop()

    window = Gtk.Window()

    clutter_embed = GtkClutter.Embed()
    window.add(clutter_embed)

    stage = clutter_embed.get_stage()
    stage.set_color(Clutter.Color.new(0, 0, 0, 255))
    hidey = ControlHider(stage=stage, loop=loop)

    # hit q or escape to quit
    stage.connect('key-press-event', maybe_stop_helper(loop))

    window.connect('destroy', lambda *a: loop.stop())
    window.show_all()

    # Make ctrl+c work, otherwise it gets swallowed somewhere
    loop.add_signal_handler(signal.SIGINT, loop.stop)

    # gogo gadget event loop
    loop.run_forever()
