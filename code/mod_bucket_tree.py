import csv
import hashlib
from bucket_tree import BucketTree


# we investigate 20 continous blocks from ETH
BLOCK_NUM = 20

# according to the defination, the bucket num is fixed
BUCKET_NUM_1ST = 8
BUCKET_NUM_2ND = 16
BUCKET_NUM_3RD = 128


class ModBucketTree(object):
    def __init__(self):
        self.type = 'MBT'
        self.bucket_tree_1st = BucketTree(BUCKET_NUM_1ST)
        self.bucket_tree_2nd = BucketTree(BUCKET_NUM_2ND)
        self.bucket_tree_3rd = BucketTree(BUCKET_NUM_3RD)
        self.bucket_nums = [BUCKET_NUM_1ST, BUCKET_NUM_2ND, BUCKET_NUM_3RD]
        self.reset_tree()

    def reset_tree(self):
        self.bucket_tree_1st.reset_tree()
        self.bucket_tree_2nd.reset_tree()
        self.bucket_tree_3rd.reset_tree()
        self.tree_filter = {}
        self.is_ready = False
        self.merkle_root_hash = None
        self.total_hash_times = 0

    def do_hash(self, input):
        # use sha256 as hash func
        # output hex value
        self.total_hash_times += 1
        return hashlib.sha256(input.encode('utf8')).hexdigest()

    '''Filter functions'''

    def initiate_filter(self):
        # choose upon accounts and classify to 3 level of usage
        heavy = set()  # contains 5% of the most active accounts
        mild = set()  # contains 20% of the most active accoutns
        filenames = []
        for i in range(BLOCK_NUM):
            filenames.append('../data/data/txs%d.csv' % (i+1))
        dict = {}
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
                    # both the acounts need to be updated after the transaction
                    from_whom = line[10]
                    to_whom = line[11]
                    if from_whom in dict:
                        dict[from_whom] += 1
                    else:
                        dict[from_whom] = 1
                    if to_whom in dict:
                        dict[to_whom] += 1
                    else:
                        dict[to_whom] = 1
        data_sorted = sorted(
            dict.items(), key=lambda x: x[1], reverse=True)
        # traverse sorted transaction data
        cur_num = 0
        cur_acounts = 0
        for account in data_sorted:
            cur_num += account[1]
            cur_acounts += 1
            if cur_acounts <= len(dict)*0.05:
                heavy.add(account[0])
            elif cur_acounts <= len(dict)*0.2:
                mild.add(account[0])
            else:
                break
        self.tree_filter['heavy'] = heavy
        self.tree_filter['mild'] = mild

    def account_usage(self, account):
        if account in self.tree_filter['heavy']:
            return 0
        else:
            return 1 if account in self.tree_filter['mild'] else 2

    '''Tree functions'''

    def initiate(self):
        self.is_ready = False
        # initiate filter
        self.initiate_filter()
        # initiate the son bucket trees
        self.bucket_tree_1st.initiate()
        self.bucket_tree_2nd.initiate()
        self.bucket_tree_3rd.initiate()
        # compute merkle root hash
        self.is_ready = True
        self.gen_merkle_root_hash()
        # print('H bucket tree initiated.')

    def gen_merkle_root_hash(self):
        # called if the whole block is ready
        if self.is_ready:
            self.bucket_tree_1st.gen_merkle_root_hash()
            self.bucket_tree_2nd.gen_merkle_root_hash()
            self.bucket_tree_3rd.gen_merkle_root_hash()
            if self.bucket_tree_1st.merkle_root_hash is not None and self.bucket_tree_2nd.merkle_root_hash is not None and self.bucket_tree_3rd.merkle_root_hash is not None:
                root_hash_12 = self.do_hash(
                    self.bucket_tree_1st.merkle_root_hash+self.bucket_tree_2nd.merkle_root_hash)
                self.merkle_root_hash = self.do_hash(
                    root_hash_12+self.bucket_tree_3rd.merkle_root_hash)
                self.total_hash_times = (self.bucket_tree_1st.total_hash_times +
                                         self.bucket_tree_2nd.total_hash_times +
                                         self.bucket_tree_3rd.total_hash_times)

    def get_merkle_root_hash(self):
        return self.merkle_root_hash

    '''Transaction functions'''

    def deal_transaction(self, from_whom, to_whom, value):
        self.update(from_whom, -value)
        self.update(to_whom, value)

    def update(self, account, balance_changed):
        self.is_ready = False
        index = self.account_usage(account)
        if index == 0:
            self.bucket_tree_1st.update(account, balance_changed)
        elif index == 1:
            self.bucket_tree_2nd.update(account, balance_changed)
        else:
            self.bucket_tree_3rd.update(account, balance_changed)
        self.is_ready = True
