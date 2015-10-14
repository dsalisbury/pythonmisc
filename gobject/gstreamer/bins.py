import time
from itertools import islice, cycle

from gi.repository import Gst


# See Python itertools recipes
# (https://docs.python.org/3.5/library/itertools.html)
def take(n, iterable):
    "Return first n items of the iterable as a list"
    return list(islice(iterable, n))


class VideoBin(Gst.Bin):
    def __init__(self):
        super().__init__()

        self.src_element = self.make_source()
        self.add(self.src_element)

        caps = Gst.Caps.from_string('video/x-raw, width=1280, height=720')
        capsfilter = Gst.ElementFactory.make('capsfilter', None)
        capsfilter.set_property('caps', caps)
        self.add(capsfilter)

        self.src_element.link(capsfilter)
        srcpad = Gst.GhostPad.new('src', capsfilter.srcpads[0])
        self.add_pad(srcpad)

    def make_source(self):
        raise NotImplementedError()


class TestSrcVideoBin(VideoBin):
    patterns = ('smpte', 'ball', 'snow')

    def make_source(self):
        return Gst.ElementFactory.make('videotestsrc', None)

    @property
    def pattern(self):
        return self.src_element.props.pattern.value_nick

    @pattern.setter
    def pattern(self, value):
        if value not in self.patterns:
            raise ValueError(value)
        self.src_element.props.pattern = value


class V4l2VideoBin(VideoBin):
    def make_source(self):
        return Gst.ElementFactory.make('v4l2src', None)


class AudioBin(Gst.Bin):
    def __init__(self):
        super().__init__()

        self.src_element = self.make_source()
        self.add(self.src_element)

        caps = Gst.Caps.from_string('audio/x-raw')
        self.cf = capsfilter = Gst.ElementFactory.make('capsfilter', None)
        capsfilter.set_property('caps', caps)
        self.add(capsfilter)

        self.vol_element = Gst.ElementFactory.make('volume', None)
        self.vol_element.props.volume = 1
        self.add(self.vol_element)

        self.src_element.link(capsfilter)
        capsfilter.link(self.vol_element)

        srcpad = Gst.GhostPad.new('src', self.vol_element.srcpads[0])
        self.add_pad(srcpad)

    def make_source(self):
        raise NotImplementedError()

    @property
    def volume(self):
        return self.vol_element.props.volume

    @volume.setter
    def volume(self, volume):
        self.vol_element.props.volume = volume


class TestSrcAudioBin(AudioBin):
    def make_source(self):
        return Gst.ElementFactory.make('audiotestsrc', None)


if __name__ == '__main__':
    Gst.init(None)
    pipeline = Gst.Pipeline()
    pipeline.set_state(Gst.State.PLAYING)

    vsrc = TestSrcVideoBin()
    # vsrc = V4l2VideoBin()
    vsink = Gst.ElementFactory.make('xvimagesink', None)
    asrc = TestSrcAudioBin()
    asink = Gst.ElementFactory.make('autoaudiosink', None)

    pipeline.add(vsrc)
    pipeline.add(vsink)
    pipeline.add(asrc)
    pipeline.add(asink)

    vsrc.link(vsink)
    vsrc.sync_state_with_parent()
    vsink.sync_state_with_parent()

    asrc.link(asink)
    # For some reason this needs to be done with the sink *before* the source.
    # TODO: why?
    asink.sync_state_with_parent()
    asrc.sync_state_with_parent()

    print('GO')
    asrc.volume = 0.0  # start silent and work up
    patterns = cycle(vsrc.patterns)
    try:
        for p in take(10, patterns):
            time.sleep(1)
            vsrc.pattern = p
            asrc.volume += 0.1
    except KeyboardInterrupt:
        pass
    finally:
        print('FIN')
