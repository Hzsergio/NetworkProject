import json
from socket import *
from methods import *

serverPort = 15000
serverSocket = socket(AF_INET, SOCK_DGRAM)
serverSocket.bind(('', serverPort))
print('The local server is ready to receive')
local_transaction_id = 0

data = {'Name': ["www.csusm.edu", "cc.csusm.edu", "cc1.csusm.edu", "cc1.csusm.edu", "my.csusm.edu", "qualcomm.com",
                 "viasat.com"],
        'Type': ["A", "A", "CNAME", "A", "A", "NS", "NS"],
        'Value': ["144.37.5.45", "144.37.5.117", "cc.csusm.edu", "144.37.5.118", "144.37.5.150", "dns.qualcomm.com",
                  "dns.viasat.com"],
        'TTL': ["", "", "", "", "", "", ""],
        'Static': ["1", "1", "1", "1", "1", "1", "1"]}

local_server_rr_table = pd.DataFrame(data, index=range(1, 8))


# Set up connection for the Qualcomm server, send request, receive data
def request_qualcomm_server(name, type_flag, t_id):
    server_name = 'localhost'
    server_port = 21000
    client_socket = socket(AF_INET, SOCK_DGRAM)
    query = create_dns_request(name, type_flag, t_id)
    json_message = query.to_json()
    client_socket.sendto(json_message.encode(), (server_name, server_port))
    modified_message, server_address = client_socket.recvfrom(2048)
    return modified_message.decode()


# Set up connection for the Viasat server, send request, receive data
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
    # Receive request from the host
    message, clientAddress = serverSocket.recvfrom(2048)
    modifiedMessage = message.decode()
    received_query = json.loads(modifiedMessage)
    if received_query["transaction_id"] == "admin":
        print("Local DNS Server: Received a request for RR table from Admin.")
        response_to_admin = local_server_rr_table.to_dict()
        response_to_admin = json.dumps(response_to_admin)
        serverSocket.sendto(response_to_admin.encode(), clientAddress)
        continue

    # Information about the request
    ans_name = received_query["name"]
    ans_type = int(received_query["type_flags"])
    ans_transaction_id = received_query["transaction_id"]
    converted_flag = type_flag_to_letter(ans_type)

    print(f"\nLocal DNS Server: The client with IP address {clientAddress} sent an {converted_flag} request for "
          f"hostname {ans_name}")

    # Check if the requested entry is in the rr table
    found_entry = local_server_rr_table[
        (local_server_rr_table["Name"] == ans_name) & (local_server_rr_table["Type"] == converted_flag)]

    # If not found, request data from the corresponding server
    if found_entry.empty:
        print(f"Local DNS Server: An {converted_flag} record for hostname {ans_name} was not found.")
        # Qualcomm request
        if "qualcomm" in ans_name:
            print(
                f"Local DNS Server: Sending an {converted_flag} request to the Qualcomm DNS Server for the hostname {ans_name}")
            response = request_qualcomm_server(ans_name, converted_flag, local_transaction_id)
            new_entry = json.loads(response)
            # Checking if the transaction IDs match
            if new_entry["transaction_id"] == local_transaction_id:
                print(f"Local DNS Server: Obtained the {converted_flag} record for hostname {ans_name} ")
            local_transaction_id += 1
            # Checking the name of the message, if it is called error the entry is not added to the RR table
            new_entry["transaction_id"] = ans_transaction_id
            if new_entry['name'] != "error":
                add_to_rr_table(new_entry, local_server_rr_table)

            host_return_message = json.dumps(new_entry)
            serverSocket.sendto(host_return_message.encode(), clientAddress)
            print(local_server_rr_table)

        # Viasat Request
        elif "viasat" in ans_name:
            print(
                f"Local DNS Server: Sending an {converted_flag} request to the Viasat DNS Server for the hostname {ans_name}")
            response = request_viasat_server(ans_name, converted_flag, local_transaction_id)
            new_entry = json.loads(response)
            # Checking if the transaction IDs match
            if new_entry["transaction_id"] == local_transaction_id:
                print(f"Local DNS Server: Obtained the {converted_flag} record for hostname {ans_name} ")
            local_transaction_id += 1
            # Checking the name of the message, if it is called error the entry is not added to the RR table
            new_entry["transaction_id"] = ans_transaction_id
            if new_entry['name'] != "error":
                add_to_rr_table(new_entry, local_server_rr_table)
            host_return_message = json.dumps(new_entry)
            serverSocket.sendto(host_return_message.encode(), clientAddress)

            print(local_server_rr_table)
        # If the host name is not found an error message will be sent to the client
        else:
            print(f'Local DNS Server: Unable to answer query for host name {ans_name}')
            error_message = create_error_message(ans_transaction_id)
            serverSocket.sendto(error_message.encode(), clientAddress)

    # Entry found in local RR table
    elif not found_entry.empty:
        print(f"Local DNS Server: The {converted_flag} record for the hostname {ans_name} was found in the local RR "
              f"table.")

        matching_row = found_entry.iloc[0]
        if matching_row["Static"] == 0:
            local_server_rr_table.loc[local_server_rr_table["Name"] == ans_name, "TTL"] = round(time.time() + 60)

        return_value = found_entry["Value"].iloc[0]
        response = DNSMessage(transaction_id=ans_transaction_id, qr=1, type_flags=converted_flag,
                              name_length=len(ans_name),
                              value_length=len(return_value),
                              name=ans_name, value=return_value)

        print(local_server_rr_table)
        response_json = response.to_json()
        serverSocket.sendto(response_json.encode(), clientAddress)
