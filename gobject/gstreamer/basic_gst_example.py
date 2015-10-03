import time

import gi
gi.require_version('Gst', '1.0')
from gi.repository import GObject
from gi.repository import Gst

GObject.threads_init()
Gst.init(None)

pipeline = Gst.Pipeline()

video_in = Gst.ElementFactory.make('videotestsrc', 'testvid')
video_in.set_property('pattern', 'ball')
pipeline.add(video_in)

caps = Gst.Caps.from_string('video/x-raw, width=1280, height=720')
capsfilter = Gst.ElementFactory.make("capsfilter", "filter1")
capsfilter.set_property('caps', caps)
pipeline.add(capsfilter)

video_out = Gst.ElementFactory.make('xvimagesink', 'vid_display')
pipeline.add(video_out)

video_in.link(capsfilter)
capsfilter.link(video_out)

pipeline.set_state(Gst.State.PLAYING)

try:
    while True:
            time.sleep(1)
except KeyboardInterrupt:
    pipeline.set_state(Gst.State.NULL)
    print('fin')
