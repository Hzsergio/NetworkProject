import json
from socket import *
from methods import *

serverPort = 15000
serverSocket = socket(AF_INET, SOCK_DGRAM)
serverSocket.bind(('', serverPort))
print('The server is ready to receive')
local_transaction_id = 5

data = {'Name': ["www.csusm.edu", "cc.csusm.edu", "cc1.csusm.edu", "cc1.csusm.edu", "my.csusm.edu", "qualcomm.com",
                 "viasat.com"],
        'Type': ["A", "A", "CNAME", "A", "A", "NS", "NS"],
        'Value': ["144.37.5.45", "144.37.5.117", "cc.csusm.edu", "144.37.5.118", "144.37.5.150", "dns.qualcomm.com",
                  "dns.viasat.com"],
        'TTL': ["", "", "", "", "", "", ""],
        'Static': ["1", "1", "1", "1", "1", "1", "1"]}

local_server_rr_table = pd.DataFrame(data, index=range(1, 8))
print(local_server_rr_table)


def request_qualcomm_server(name, type_flag, t_id):
    server_name = 'localhost'
    server_port = 21000
    client_socket = socket(AF_INET, SOCK_DGRAM)
    query = create_dns_request(name, type_flag, t_id)
    json_message = query.to_json()
    client_socket.sendto(json_message.encode(), (server_name, server_port))
    modified_message, server_address = client_socket.recvfrom(2048)
    return modified_message.decode()


def request_viasat_server(name, type_flag, t_id):
    server_name = 'localhost'
    server_port = 22000
    client_socket = socket(AF_INET, SOCK_DGRAM)
    query = create_dns_request(name, type_flag, t_id)
    json_message = query.to_json()
    client_socket.sendto(json_message.encode(), (server_name, server_port))
    modified_message, server_address = client_socket.recvfrom(2048)
    return modified_message.decode()


while 1:
    message, clientAddress = serverSocket.recvfrom(2048)
    modifiedMessage = message.decode()

    received_query = json.loads(modifiedMessage)

    ans_name = received_query["name"]
    ans_type = int(received_query["type_flags"])
    ans_transaction_id = received_query["transaction_id"]
    converted_flag = type_flag_to_letter(ans_type)

    found = local_server_rr_table[(local_server_rr_table["Name"] == ans_name) & (local_server_rr_table["Type"] == converted_flag)]

    if found.empty:
        if "qualcomm" in ans_name:
            print("This is a qualcomm request")
            response = request_qualcomm_server(ans_name, converted_flag, local_transaction_id)
            new_entry = json.loads(response)
            if new_entry["transaction_id"] == local_transaction_id:
                print("IDS MATCH")
            local_transaction_id += 1
            new_entry["transaction_id"] = ans_transaction_id
            print(response)
            add_to_rr_table(new_entry, local_server_rr_table)
            print(local_server_rr_table)
            host_return_message = json.dumps(new_entry)
            serverSocket.sendto(host_return_message.encode(), clientAddress)
        elif "viasat" in ans_name:
            print("This is a viasat request")
            response = request_viasat_server(ans_name, converted_flag, local_transaction_id)
            new_entry = json.loads(response)
            if new_entry["transaction_id"] == local_transaction_id:
                print("IDS MATCH")
            local_transaction_id += 1
            new_entry["transaction_id"] = ans_transaction_id
            print(response)
            add_to_rr_table(new_entry, local_server_rr_table)
            print(local_server_rr_table)
            host_return_message = json.dumps(new_entry)
            serverSocket.sendto(host_return_message.encode(), clientAddress)
    else:
        return_value = found["Value"].iloc[0]
        response = DNSMessage(transaction_id=ans_transaction_id, qr=1, type_flags=converted_flag, name_length=len(ans_name),
                              value_length=len(return_value),
                              name=ans_name, value=return_value)
        print(response)
        response_json = response.to_json()
        serverSocket.sendto(response_json.encode(), clientAddress)
