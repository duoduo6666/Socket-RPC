import socket

def crc8(data):
    crc = 0x00
    
    # CRC-8/ATM polynomial: x^8 + x^2 + x + 1 (0x07)
    poly = 0x07
    
    for byte in data:
        crc ^= byte
        for _ in range(8):
            if crc & 0x80:
                crc = (crc << 1) ^ poly
            else:
                crc <<= 1
            crc &= 0xFF
    
    return crc.to_bytes(1, 'big')

def recv(): 
    data = b""
    
    data_len = conn.recv(5)
    print(f"{crc8(data_len[0:4]).hex()}: {data_len.hex()[8:]}")
    data_len = int.from_bytes(data_len[0:4], "big")

    while len(data) < data_len:
        r = conn.recv(256)
        data += r
    return data

def send(data:bytes):
    data_len = len(data).to_bytes(4, "big")
    conn.sendall(data_len+crc8(data_len))

    conn.sendall(data)

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.bind(("", 8089))
    s.listen(1)
    conn, addr = s.accept()
    with conn:
        print('Connected by', addr)
        data = recv()
        send(data)
