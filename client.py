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

    # host_name = get_valid_input("Enter the host name/domain name: ", VALID_DOMAIN)
    host_name = input("Enter the host name/domain name: ")
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

        if received_answer["name"] == "error":
            print(f"\nClient: The local DNS server was unable to answer the query for hostname {host_name}")
            continue

        if received_answer["transaction_id"] != transaction_id:
            print("Transaction ID does not match.")
        else:
            transaction_id += 1
            add_to_rr_table(received_answer, client_rr_table)
            value = client_rr_table[
                (client_rr_table['Name'] == host_name) & (client_rr_table['Type'] == converted_flag)]
            print(f"Client: Record received for hostname {host_name} from the local DNS server.")
            print(f"Client: The value for hostname {host_name} is " + value["Value"].iloc[0])

    else:
        print(f"Client: Record for hostname {host_name} located in client RR table.")
        print(f"Client: The value for hostname {host_name} is " + found["Value"].iloc[0])
        client_rr_table.loc[client_rr_table["Name"] == host_name, "TTL"] = round(time.time() + 60)

    print("\nClient RR Table")
    print(client_rr_table)

    if input("Make another request? (Y/N): ").lower() == "n":
        clientSocket.close()
        break
