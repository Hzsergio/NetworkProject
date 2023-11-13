from socket import *
from methods import *

# TESTING
data = ['Name', 'Type', 'Value', 'TTL', 'Static']
client_rr_table = pd.DataFrame(columns=data)
# print(client_rr_table)

serverName = 'localhost'
serverPort = 15000
clientSocket = socket(AF_INET, SOCK_DGRAM)
transaction_id = 0
while 1:

    host_name = get_valid_input("Enter the host name/domain name: ", VALID_DOMAIN)
    dns_type = get_valid_input("Enter the type of query (0. A, 1. AAAA, 2. CNAME, 3. NS): ", VALID_TYPE)
    converted_flag = type_flag_to_letter(int(dns_type))

    found = client_rr_table[(client_rr_table['Name'] == host_name) & (client_rr_table['Type'] == converted_flag)]

    if found.empty:
        query = create_dns_request(host_name, dns_type, transaction_id)
        json_query = query.to_json()

        clientSocket.sendto(json_query.encode(), (serverName, serverPort))
        modifiedMessage, serverAddress = clientSocket.recvfrom(2048)

        received_answer = modifiedMessage.decode()
        received_answer = json.loads(received_answer)

        if received_answer["transaction_id"] != transaction_id:
            print("Transaction ID does not match.")
        else:
            transaction_id += 1
            add_to_rr_table(received_answer, client_rr_table)
            value = client_rr_table[
                (client_rr_table['Name'] == host_name) & (client_rr_table['Type'] == converted_flag)]
            print("The value is: " + value["Value"].iloc[0])

    else:
        print("The value is: " + found["Value"].iloc[0])
        client_rr_table["TTL"] = time.time() + 60

    print("Client RR Table")
    print(client_rr_table)
clientSocket.close()
