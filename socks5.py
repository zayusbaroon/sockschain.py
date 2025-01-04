import socket
import struct
import select

class Client:
    def __init__(self, links=[{'address': '127.0.0.1', 'port': 9050}], sock=socket.socket(socket.AF_INET, socket.SOCK_STREAM)):
        self.chain = links #last link in the "chain" will be the final proxy
        self.sock = sock #can be chained now :D



    def proxy_init(self, trg_addr, trg_port, timeout):
        c = self.sock
        for link in range(len(self.chain)):
            if link == len(self.chain) - 1:
                host_adr = trg_addr
                host_port = trg_port
            else:
                host_adr = self.chain[link]['address']
                host_port = self.chain[link]['port']
            if link == 0:
                c.connect((self.chain[link]['address'], self.chain[link]['port']))
            req_init = bytearray([0x5,0x1,0x00])
            c.send(req_init)
            res_init = c.recv(1024)
            if res_init[1] == 0xff:
                c.close()
                return(f'Proxy #{link+1}: "NO ACCEPTABLE METHODS"')
            adr = list(map(int, host_adr.split('.')))
            host_port = struct.pack('!H', host_port)
            req_base = bytearray([0x5, 0x1, 0x00, 0x01]) #VER + CMD + RSV + ATYP
            req = req_base
            for q in adr:
                #print(f"ADR: {q}")
                req.append(q)
            for r in host_port:
                #print(f"PORT: {r}")
                req.append(r)
           # print(req)
            #input("DEBUG")
            c.send(req)
           # print(socket.gettimeout())
            wait = select.select([c], [], [], timeout)[0]
            if len(wait) < 1:
                return([0, 0, link+1])
            res = c.recv(1024)
            #print(f'RES: {res}')
            if res[1] != 0x00: #REP FIELD
                if res[1] == 0x01:
                   # print(res)
                    return([res, res[1], link+1]) #proxy_init will always either return a socket or a 3-width list
            #IPV4 is assumed and its address length known; no need for check

        return(c)

    def proxy_send(self, data, t=10.3):
        self.sock.send(data)
        wait = select.select([self.sock], [], [], t)[0]
        if len(wait) < 1:
            print("ERR. Exiting...")
            sys.exit()
        return(self.sock.recv(1024))










