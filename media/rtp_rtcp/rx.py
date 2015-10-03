import socketserver
import struct
from collections import OrderedDict
from numbers import Number
import threading
import time
import binascii
import traceback

NETWORK = '!'
RTP_FIXED_SECTION = 'BBHLL'
RTP_CSRC = '{qty}L'
RTP_EXTENSION_HEADER_META = 'HH'
RTCP_PREAMBLE = 'BBHL'


def dump_dict(d):
    for field, value in d.items():
        if isinstance(value, Number) and value >= 2**16:
            fmtd_value = '0x{:08x}'.format(value)
        else:
            fmtd_value = repr(value)
        print('{}: {}'.format(field, fmtd_value))


def parse_rtp(data):
    info = OrderedDict()
    vpxcc, mpt, seq, timestamp, ssrc = struct.unpack_from(
        NETWORK + RTP_FIXED_SECTION, data)

    info['version'] = vpxcc >> 6
    info['padding'] = bool(vpxcc >> 5 & 1)
    info['extension'] = bool(vpxcc >> 4 & 1)
    info['csrc_count'] = vpxcc & 0x0f

    info['marker'] = mpt >> 7
    info['payload_type'] = mpt & 0x7f

    info['sequence_numer'] = seq

    info['timestamp'] = timestamp
    info['ssrc'] = ssrc

    if info['csrc_count']:
        info['csrc'] = struct.unpack_from(
            NETWORK + RTP_CSRC.format(qty=info['csrc_count']), data,
            offset=struct.calcsize(RTP_FIXED_SECTION))

    if info['extension']:
        eh_id, eh_len = struct.unpack_from(
            NETWORK + RTP_EXTENSION_HEADER_META, data, offset=struct.calcsize(
                RTP_FIXED_SECTION + RTP_CSRC.format(qty=info['csrc_count'])))
        info['profile_specific_ext_header_id'] = eh_id
        info['ext_header_len'] = eh_len

    return info


def parse_rtcp_200(vpxx, pt, length, sender_ssrc, payload):
    info = OrderedDict()
    info['version'] = vpxx >> 6
    info['padding'] = bool(vpxx >> 5 & 1)
    info['reception_report_count'] = vpxx & 0x1f
    info['packet_type'] = 200
    info['length'] = length
    info['sender_ssrc'] = sender_ssrc
    return info


def parse_rtcp_unknown(vpxx, pt, length, sender_ssrc, payload):
    info = OrderedDict()
    info['version'] = vpxx >> 6
    info['padding'] = bool(vpxx >> 5 & 1)
    info['packet_type'] = pt
    info['unknown'] = True
    info['payload'] = payload
    return info


def parse_rtcp(data):
    overall_len = len(data)
    offset = 0
    packets = []
    while offset < overall_len:
        vpxx, pt, length, sender_ssrc = struct.unpack_from(
            NETWORK + RTCP_PREAMBLE, data, offset=offset)
        parser_name = 'parse_rtcp_{}'.format(pt)
        parser = globals().get(parser_name, parse_rtcp_unknown)
        packets.append(parser(
            vpxx=vpxx, pt=pt, length=length, sender_ssrc=sender_ssrc,
            payload=data[offset:offset+(length+1)*4]))
        offset += (length + 1) * 4
    return packets


class RtpHandler(socketserver.BaseRequestHandler):
    def handle(self):
        try:
            data = self.request[0]
            dump_dict(parse_rtp(data))
            print('')
            print('')
        except Exception:
            traceback.print_exc()
            print('data was: {!r}'.format(binascii.hexlify(data)))


class RtcpHandler(socketserver.BaseRequestHandler):
    def handle(self):
        try:
            data = self.request[0]
            for packet in parse_rtcp(data):
                dump_dict(packet)
                print('')
                print('')
        except Exception:
            traceback.print_exc()
            print('data was: {!r}'.format(binascii.hexlify(data)))


if __name__ == "__main__":
    rtp_server = socketserver.UDPServer(('localhost', 9998), RtpHandler)
    rtp_thread = threading.Thread(target=rtp_server.serve_forever)
    rtp_thread.daemon = True

    rtcp_server = socketserver.UDPServer(('localhost', 9999), RtcpHandler)
    rtcp_thread = threading.Thread(target=rtcp_server.serve_forever)
    rtcp_thread.daemon = True

    servers = (rtp_server, rtcp_server)
    threads = (rtp_thread, rtcp_thread)
    print('starting')
    for thread in threads:
        thread.start()

    try:
        while True:
            if not all(t.is_alive() for t in threads):
                print('a thread crashed')
                break
            time.sleep(0.5)
    except KeyboardInterrupt:
        print('stopping')
        for server in servers:
            try:
                server.server_close()
                server.shutdown()
            except Exception as e:
                print('failed stopping {!r}: {!r}'.format(server, e))

    print('fin.')
