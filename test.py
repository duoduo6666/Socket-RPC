import krpc
conn = krpc.connect(
    name='My Example Program',
    address='192.168.1.128',
    rpc_port=50000, stream_port=50001)
print(conn.krpc.get_status().version)
print(conn.space_center.ut)