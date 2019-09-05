import binascii
import csv
import os

from iroha import IrohaCrypto
from iroha import Iroha, IrohaGrpc

class User:
    Name = ""
    PubKey = ""
    PrivKey = ""

users = list()

class TestIroha:
    def __init__(self):
        # self.IROHA_HOST_ADDR = os.getenv('IROHA_HOST_ADDR', '192.168.88.202')
        self.IROHA_HOST_ADDR = os.getenv('IROHA_HOST_ADDR', 'localhost')
        self.IROHA_PORT = os.getenv('IROHA_PORT', '50051')
        self.admin_private_key = 'f101537e319568c765b2cc89698325604991dca57b9716b58016b253506cab70'
        self.iroha = Iroha('admin@test')
        self.net = IrohaGrpc('{}:{}'.format(self.IROHA_HOST_ADDR, self.IROHA_PORT))
        self.txAmount = 0

    def SendTx(self, transaction):
        hex_hash = binascii.hexlify(IrohaCrypto.hash(transaction))
        print('Transaction hash = {}, creator = {}'.format(
            hex_hash, transaction.payload.reduced_payload.creator_account_id))
        self.net.send_tx(transaction)
        self.txAmount += 1
        for status in self.net.tx_status_stream(transaction):
            print(status)

    def SendToUser(self, fromUser, toUser):
        tx = self.iroha.transaction([
            self.iroha.command('TransferAsset', src_account_id=fromUser.Name, dest_account_id=toUser.Name,
                          asset_id='coin#domain', description='sending', amount='0.01')
        ])
        IrohaCrypto.sign_transaction(tx, fromUser.PrivKey)
        self.SendTx(tx)

def ReadCSV():
    with open("accounts.csv", "r", newline="") as file:
        reader = csv.reader(file)
        line = 0
        for row in reader:
            if line != 0:
                user = User()
                user.Name = row[0]
                user.PubKey = row[1][2:len(user.PubKey)-1]
                user.PrivKey = row[2][2:len(user.PrivKey)-1]
                users.append(user)
            line += 1

def main():
    ReadCSV()
    test = TestIroha()
    test.SendToUser(users[76], users[77])

if __name__ == "__main__":
    main()