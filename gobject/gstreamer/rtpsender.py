'''

Construct a pipeline to send some test video to an RTP receiver, with an RTCP
stream as well.


                                                   +-- (rtp) --> 9998/udp
    src --> encoder --> payloader --> rtpsession --|
                                                   +-- (rtcp) -> 9999/udp

'''
import time
from gi.repository import Gst


Gst.init(None)

pipeline = Gst.Pipeline()

src = Gst.ElementFactory.make('videotestsrc', 'src')
pipeline.add(src)

enc = Gst.ElementFactory.make('theoraenc', 'enc')
pipeline.add(enc)

payloader = Gst.ElementFactory.make('rtptheorapay', 'payloader')
pipeline.add(payloader)

src.link(enc)
enc.link(payloader)

rtp = Gst.ElementFactory.make('rtpsession', 'rtp')
pipeline.add(rtp)

# This is where the RTP stream will go
udp_send_rtp = Gst.ElementFactory.make('udpsink', 'udp_send_rtp')
pipeline.add(udp_send_rtp)
udp_send_rtp.set_property('host', '127.0.0.1')
udp_send_rtp.set_property('port', 9998)

# RTCP is a control protocol, signalling info about the RTP stream (send/
# receive stats like bitrates, jitter, etc)
udp_send_rtcp = Gst.ElementFactory.make('udpsink', 'udp_send_rtcp')
pipeline.add(udp_send_rtcp)
udp_send_rtcp.set_property('host', '127.0.0.1')
udp_send_rtcp.set_property('port', 9999)
# setting these as recommended by rtpsession docs
udp_send_rtcp.set_state(Gst.State.PLAYING)
udp_send_rtcp.set_locked_state(True)

# requesting the sink pad (pad_into_rtpsession) causes a corresponding source
# pad to be created (pad_out_of_rtpsession)
pad_into_rtpsession = rtp.get_request_pad('send_rtp_sink')
payloader.link(rtp)

pad_out_of_rtpsession = rtp.srcpads[0]
# note: we need to link pad to pad, not pad to element, else it will blow up
pad_out_of_rtpsession.link(udp_send_rtp.sinkpads[0])

rtcp_src_pad = rtp.get_request_pad('send_rtcp_src')
rtcp_src_pad.link(udp_send_rtcp.sinkpads[0])


pipeline.set_state(Gst.State.PLAYING)

try:
    while True:
        time.sleep(0.5)
except KeyboardInterrupt:
    pipeline.set_state(Gst.State.NULL)
    print('fin')
