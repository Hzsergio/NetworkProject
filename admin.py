from socket import *
from methods import *

serverName = 'localhost'
serverPort = 15000
clientSocket = socket(AF_INET, SOCK_DGRAM)
transaction_id = "admin"

print("Obtaining Local DNS Server RR Table...")
admin_request = create_dns_request("admin", "A", transaction_id)
json_admin = admin_request.to_json()
clientSocket.sendto(json_admin.encode(), (serverName, serverPort))
modifiedMessage, serverAddress = clientSocket.recvfrom(2048)
rr_table = json.loads(modifiedMessage.decode())
rr_table = pd.DataFrame(rr_table)
print(rr_table)
