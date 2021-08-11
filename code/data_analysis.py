import csv

# we investigate 20 continous blocks from ETH
BLOCK_NUM = 20


def read_file(filenames):
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
    return dict, tx_num


def gen_stats(data, num):
    data_sorted = sorted(data.items(), key=lambda x: x[1], reverse=True)
    # traverse sorted transaction data
    cur_num = 0
    cur_acounts = 0
    print_1 = False
    print_5 = False
    print_20 = False
    for account in data_sorted:
        cur_num += account[1]
        cur_acounts += 1
        if cur_acounts >= len(data)*0.01 and print_1 == False:
            print('1% most used accounts countains ' +
                  str(50*cur_num/num)+'% of total transactions.')
            print_1 = True
        elif cur_acounts >= len(data)*0.05 and print_5 == False:
            print('5% most used accounts countains ' +
                  str(50*cur_num/num)+'% of total transactions.')
            print_5 = True
        elif cur_acounts >= len(data)*0.5 and print_20 == False:
            print('20% most used accounts countains ' +
                  str(50*cur_num/num)+'% of total transactions.')
            print_20 = True
            break


if __name__ == "__main__":

    print('%d blocks in total from Ethereum:' % BLOCK_NUM)
    # read blocks from dataset
    filename = []
    for i in range(BLOCK_NUM):
        filename.append('../data/data/txs%d.csv' % (i+1))
    tx_data, total_txs = read_file(filename)
    print(str(len(tx_data)) + ' acounts in total ' +
          str(total_txs) + ' transactions.\n')
    # get account usage ststs
    gen_stats(tx_data, total_txs)
