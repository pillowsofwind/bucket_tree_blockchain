from bucket_tree import BucketTree
from mod_bucket_tree import ModBucketTree
import csv
import matplotlib.pyplot as plt


# we investigate 20 continous blocks from ETH
BLOCK_NUM = 20

transactions = [0, ]
transaction_get = False
bucket_tree_hashes = [0, ]
mod_bucket_tree_hashes = [0, ]


def test_tree(filenames, bucket_tree):
    index = 1
    tx_num = 0
    for filename in filenames:
        with open(filename, 'r') as file:
            reader = csv.reader(file)
            for line in reader:
                if line == []:
                    continue
                if line[0] != 'tx':
                    continue
                tx_num += 1
                bucket_tree.deal_transaction(
                    line[10], line[11], float(line[16]))
            bucket_tree.gen_merkle_root_hash()
            print("Block %d:" % index)
            print("Merkle root hash: "+bucket_tree.get_merkle_root_hash())
            print("Total transactions(til now): %d" % tx_num)
            print("Total hash times(til now): %d" %
                  bucket_tree.total_hash_times)
            index += 1
            # collect data for graph
            global transactions
            global transaction_get
            global bucket_tree_hashes
            global mod_bucket_tree_hashes
            if len(transactions) == BLOCK_NUM+1:
                transaction_get = True
            if transaction_get is not True:
                transactions.append(tx_num)
            if bucket_tree.type == 'BT':
                bucket_tree_hashes.append(bucket_tree.total_hash_times)
            else:
                mod_bucket_tree_hashes.append(bucket_tree.total_hash_times)


if __name__ == "__main__":

    print('\n-------------testing bucket tree-------------\n')
    bucket_tree = BucketTree()
    bucket_tree.initiate()

    print('%d blocks in total from Ethereum:' % BLOCK_NUM)
    # read blocks from dataset
    filename = []
    for i in range(BLOCK_NUM):
        filename.append('../data/data/txs%d.csv' % (i+1))
    test_tree(filename, bucket_tree)

    print('\n-------------testing mod bucket tree-------------\n')
    mod_bucket_tree = ModBucketTree()
    mod_bucket_tree.initiate()

    print('%d blocks in total from Ethereum:' % BLOCK_NUM)
    # read blocks from dataset
    filename = []
    for i in range(BLOCK_NUM):
        filename.append('../data/data/txs%d.csv' % (i+1))
    test_tree(filename, mod_bucket_tree)

    # generate graph
    plt.plot(transactions, bucket_tree_hashes, marker='o', label='BT')
    plt.plot(transactions, mod_bucket_tree_hashes, marker='*', label='MBT')
    plt.legend()
    plt.xlabel('number of transactions')
    plt.ylabel('total hash times')
    plt.title('Comparision of Data Structures on ETH Transactions')

    plt.show()
