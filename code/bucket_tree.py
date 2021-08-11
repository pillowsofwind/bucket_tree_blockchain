import csv
import hashlib
import json


# we investigate 20 continous blocks from ETH
BLOCK_NUM = 20

# according to the defination, the bucket num is fixed
BUCKET_NUM = 512


class BucketTree(object):
    def __init__(self, bucket_num=BUCKET_NUM):
        self.type = 'BT'
        self.bucket_num = bucket_num
        self.reset_tree()

    def reset_tree(self):
        self.leaves = list()
        self.buckets = list()
        self.levels = None
        self.is_ready = False
        self.merkle_root_hash = None
        self.total_hash_times = 0

    def do_hash(self, input):
        # use sha256 as hash func
        # output hex value
        self.total_hash_times += 1
        return hashlib.sha256(input.encode('utf8')).hexdigest()

    '''Buckets functions'''

    def initiate_buckets(self):
        for i in range(self.bucket_num):
            # suppose we only write down balance of a account
            default = 'default%d' % i
            self.buckets.append({default: 0})

    def hash_bucket(self, index):
        return self.do_hash(json.dumps(self.buckets[index]))

    def get_bucktes_data(self):
        return self.leaves

    def get_bucket_data(self, index):
        return self.leaves[index]

    '''Merkle tree functions'''

    def get_leaf_count(self):
        return len(self.leaves)

    def up_float_level(self):
        solo_leave = None
        # calculate the tree by level, from the bottom
        N = len(self.levels[0])  # number of leaves on the level
        if N % 2 == 1:  # if odd number of leaves on the level
            solo_leave = self.levels[0][-1]
            N -= 1
        new_level = []
        for l, r in zip(self.levels[0][0:N:2], self.levels[0][1:N:2]):
            new_level.append(self.do_hash(l+r))
        if solo_leave is not None:
            new_level.append(solo_leave)
        self.levels = [new_level, ] + self.levels  # prepend new level

    def initiate(self):
        self.is_ready = False
        # initiate buckets as default
        self.initiate_buckets()
        # hash buckets for leaves
        for i in range(self.bucket_num):
            self.leaves.append(self.hash_bucket(i))
        if self.get_leaf_count() > 0:
            self.levels = [self.leaves, ]
            # compute till the root node
            while len(self.levels[0]) > 1:
                self.up_float_level()
        # compute merkle root hash
        self.is_ready = True
        self.gen_merkle_root_hash()
        # print('Bucket tree initiated.')

    def gen_merkle_root_hash(self):
        # called if the whole block is ready
        if self.is_ready:
            if self.levels is not None:
                self.merkle_root_hash = self.do_hash(self.levels[0][0])

    def get_merkle_root_hash(self):
        return self.merkle_root_hash

    '''Transaction functions'''

    def deal_transaction(self, from_whom, to_whom, value):
        self.update(from_whom, -value)
        self.update(to_whom, value)

    def get_bucket_index(self, account):
        # each acount is hashed to a certain bucket
        return int(self.do_hash(account), 16) % self.bucket_num

    def update(self, account, balance_changed):
        self.is_ready = False
        # modify the bucket balance info
        index = self.get_bucket_index(account)
        if account in self.buckets[index]:
            self.buckets[index][account] += balance_changed
        else:
            # suppose we assign a new account with balance 10ETH
            self.buckets[index][account] = 10
            self.buckets[index][account] += balance_changed

        # update the tree from the leaf node
        self.leaves[index] = self.hash_bucket(index)
        for x in range(len(self.levels) - 1, 0, -1):
            level_len = len(self.levels[x])
            if (index == level_len - 1) and (level_len % 2 == 1):  # skip if this is an odd end node
                index = int(index / 2.)
                continue
            is_right_node = index % 2
            sibling_index = index - 1 if is_right_node else index + 1
            sibling_value = self.levels[x][sibling_index]
            self_value = self.levels[x][index]
            self.levels[x - 1][int(index / 2.)] = self.do_hash(
                sibling_value+self_value) if is_right_node else self.do_hash(self_value+sibling_value)
            index = int(index / 2.)
        self.is_ready = True
