from socket import *
from methods import *


serverPort = 21000
serverSocket = socket(AF_INET, SOCK_DGRAM)
serverSocket.bind(('', serverPort))
print('The Qualcomm server is ready to receive')

data = {'Name': ["www.qualcomm.com", "qtiack12.qti.qualcomm.com"],
        'Type': ["A", "A"],
        'Value': ["104.86.224.205", "129.46.100.21"],
        'TTL': ["", ""],
        'Static': ["1", "1"]}
qualcomm_rr_table = pd.DataFrame(data, index=range(1, 3))
print(qualcomm_rr_table)
while 1:
    message, clientAddress = serverSocket.recvfrom(2048)
    modifiedMessage = message.decode()
    received_query = json.loads(modifiedMessage)

    ans_name = received_query["name"]
    ans_type = received_query["type_flags"]
    ans_transaction_id = received_query["transaction_id"]
    print(f"Qualcomm Server: The client with IP address {clientAddress} sent an {ans_type} request for hostname {ans_name}")

    found = qualcomm_rr_table[(qualcomm_rr_table["Name"] == ans_name) & (qualcomm_rr_table["Type"] == ans_type)]
    # If the host name is not found an error message will be sent to the client
    if found.empty:
        print(f'Qualcomm Server: Unable to answer query for host name {ans_name}')
        error_message = create_error_message(ans_transaction_id)
        serverSocket.sendto(error_message.encode(), clientAddress)
    # Return value
    else:
        return_value = found["Value"].iloc[0]
        response = DNSMessage(transaction_id=ans_transaction_id, qr=1, type_flags=ans_type, name_length=len(ans_name),
                              value_length=len(return_value),
                              name=ans_name, value=return_value)
        print(response)
        response_json = response.to_json()
        serverSocket.sendto(response_json.encode(), clientAddress)
