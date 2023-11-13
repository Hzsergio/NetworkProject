from socket import *
from methods import *


serverPort = 22000
serverSocket = socket(AF_INET, SOCK_DGRAM)
serverSocket.bind(('', serverPort))
print('The Viasat server is ready to receive')

data = {'Name': "www.viasat.com",
        'Type': "A",
        'Value': "8.37.96.179",
        'TTL': "",
        'Static': "1"}
df = pd.DataFrame(data, index=range(1, 2))
print(df)
while 1:
    message, clientAddress = serverSocket.recvfrom(2048)
    modifiedMessage = message.decode()
    print(modifiedMessage)
    print("Viasat Here")
    received_query = json.loads(modifiedMessage)

    ans_name = received_query["name"]
    ans_type = received_query["type_flags"]
    ans_transaction_id = received_query["transaction_id"]

    found = df[(df["Name"] == ans_name) & (df["Type"] == ans_type)]
    if found.empty:
        print("That is not a valid request")

    else:
        return_value = found["Value"].iloc[0]
        response = DNSMessage(transaction_id=ans_transaction_id, qr=1, type_flags=ans_type, name_length=len(ans_name),
                              value_length=len(return_value),
                              name=ans_name, value=return_value)
        print(response)
        response_json = response.to_json()
        serverSocket.sendto(response_json.encode(), clientAddress)