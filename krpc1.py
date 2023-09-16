import socket, krpc_pb2, varint_pb2
from google.protobuf.internal.encoder import _VarintEncoder
from google.protobuf.internal.decoder import _DecodeVarint
from time import sleep

def encode_varint(value):
    """ Encode an int as a protobuf varint """
    data = []
    _VarintEncoder()(data.append, value, False)
    return b''.join(data)

def decode_varint(data):
    """ Decode a protobuf varint to an int """
    return _DecodeVarint(data, 0)[0]

def encode_double(value):
    v = varint_pb2.double()
    v.value = value
    return v.SerializeToString()[1:]

def decode_double(data):
    v = varint_pb2.double()
    v.ParseFromString(b"\x09"+data)
    return v.value

def send_msg(s, msg):
    s.send(encode_varint(len(msg.SerializeToString())))
    s.send(msg.SerializeToString())

def recv_msg(s:socket.socket, msg_type):
    def recv_len(s:socket.socket):
        data = b''
        while True:
            try:
                data += s.recv(1)
                size = decode_varint(data)
                break
            except IndexError:
                pass
        return size
    len = recv_len(s)
    data = s.recv(len)
    msg = msg_type()
    msg.ParseFromString(data)
    return msg

cr = krpc_pb2.ConnectionRequest()
cr.type = krpc_pb2.ConnectionRequest.RPC
cr.client_name = "ESP32"
cr.client_identifier = b""


with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.connect(("192.168.1.128", 50000))
    send_msg(s, cr)
    r = recv_msg(s, krpc_pb2.ConnectionResponse)
    print(r.status)

    request = krpc_pb2.Request()
    call = krpc_pb2.ProcedureCall()
    call.service = "KRPC"
    call.procedure = "GetStatus"
    request.calls.append(call)
    call1 = krpc_pb2.ProcedureCall()
    call1.service = "SpaceCenter"
    call1.procedure = "get_UT"
    request.calls.append(call1)

    send_msg(s, request)
    r = recv_msg(s, krpc_pb2.Response)
    status = krpc_pb2.Status()
    status.ParseFromString(r.results[0].value)
    ut = decode_double(r.results[1].value)

    request = krpc_pb2.Request()
    call2 = krpc_pb2.ProcedureCall()
    call2.service = "SpaceCenter"
    call2.procedure = "get_ActiveVessel"
    request.calls.append(call2)
    send_msg(s, request)
    r = recv_msg(s, krpc_pb2.Response)
    Vessel = r.results[0].value

    request = krpc_pb2.Request()
    call3 = krpc_pb2.ProcedureCall()
    call3.service = "SpaceCenter"
    call3.procedure = "Vessel_Flight"
    argv1 = krpc_pb2.Argument()
    argv1.position = 0
    argv1.value = Vessel
    call3.arguments.append(argv1)
    request.calls.append(call3)
    send_msg(s, request)
    r = recv_msg(s, krpc_pb2.Response)
    Flight = r.results[0].value

    request = krpc_pb2.Request()
    call4 = krpc_pb2.ProcedureCall()
    call4.service = "SpaceCenter"
    call4.procedure = "Flight_get_SurfaceAltitude"
    argv1 = krpc_pb2.Argument()
    argv1.position = 0
    argv1.value = Flight
    call4.arguments.append(argv1)
    request.calls.append(call4)
    send_msg(s, request)
    r = recv_msg(s, krpc_pb2.Response)
    h = decode_double(r.results[0].value)

    print(status.version)
    print(ut)
    print(Vessel)
    print(Flight)
    print(h)
