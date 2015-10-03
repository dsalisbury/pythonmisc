# Unicode literal ESCAPE
ESCAPE = '\N{ESCAPE}'


def maybe_stop_helper(loop, stop_keys={ESCAPE, 'q'}):
    def maybe_stop(actor, event):
        if event.unicode_value in stop_keys:
            loop.stop()
    return maybe_stop
