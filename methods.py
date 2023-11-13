import json
import time
import pandas as pd

#
#

VALID_TYPE = ["0", "1", "2", "3"]
VALID_DOMAIN = ['www.csusm.edu', "cc.csusm.edu", "cc1.csusm.edu", "cc1.csusm.edu", "my.csusm.edu", "qualcomm.com",
                "viasat.com", "www.viasat.com", "www.qualcomm.com", "qtiack12.qti.qualcomm.com"]


class DNSMessage:
    def __init__(self, transaction_id, qr, type_flags, name_length, value_length, name, value):
        self.transaction_id = transaction_id
        self.qr = qr
        self.type_flags = type_flags
        self.name_length = name_length
        self.value_length = value_length
        self.name = name
        self.value = value

    def __str__(self):
        return f"Transaction ID: {self.transaction_id}\n" \
               f"QR: {self.qr}\n" \
               f"Type Flags: {self.type_flags}\n" \
               f"Name Length: {self.name_length}\n" \
               f"Value Length: {self.value_length}\n" \
               f"Name: {self.name}\n" \
               f"Value: {self.value}"

    def to_json(self):
        return json.dumps(self.__dict__)

    @classmethod
    def from_json(cls, json_string):
        data = json.loads(json_string)
        return cls(**data)


#
def type_flag_to_letter(flag):
    if flag == 0:
        return "A"
    elif flag == 1:
        return "AAAA"
    elif flag == 2:
        return "CNAME"
    elif flag == 3:
        return "NS"
    else:
        return 0


def add_to_rr_table(response, table):
    answer_name = response['name']
    answer_type = response['type_flags']
    answer_value = response['value']
    answer_ttl = time.time() + 60
    new_entry = {"Name": answer_name, "Type": answer_type, "Value": answer_value, 'TTL': answer_ttl, 'Static': 0}
    table.loc[len(table) + 1] = new_entry


def create_dns_request(name, type_flag, t_id):
    request = DNSMessage(transaction_id=t_id, qr=0,
                         type_flags=type_flag,
                         name_length=len(name),
                         value_length=0,
                         name=name, value="")
    return request


def get_valid_input(prompt, valid_options):
    while True:
        user_input = input(prompt).lower()

        try:
            if user_input in valid_options:
                return user_input
            else:
                print("Invalid input. Try again.")
        except ValueError:
            print("Invalid input. Try again.")
