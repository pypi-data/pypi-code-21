#
#
# hg19_chrlen = {'chr1': 249250621,
#                'chr2': 243199373,
#                'chr3': 198022430,
#                'chr4': 191154276,
#                'chr5': 180915260,
#                'chr6': 171115067,
#                'chr7': 159138663,
#                'chr8': 146364022,
#                'chr9': 141213431,
#                'chr10': 135534747,
#                'chr11': 135006516,
#                'chr12': 133851895,
#                'chr13': 115169878,
#                'chr14': 107349540,
#                'chr15': 102531392,
#                'chr16': 90354753,
#                'chr17': 81195210,
#                'chr18': 78077248,
#                'chr19': 59128983,
#                'chr20': 63025520,
#                'chr21': 48129895,
#                'chr22': 51304566,
#                'chrx': 155270560,
#                'chry': 59373566}
#
#
# def generate_a_random_seq(seq, genome='hg19'):
#     """
#     给定一条序列，在此序列同一染色体上随机生成一条等长的序列
#     @param genome: 序列属于哪个基因组，可以是hg19, mm9 ... 默认是hg19
#     @param seq: 是Sequence这个类的一个实例,查看sequence.py中的Sequence类
#     """
#     if genome == 'hg19':
#         chrlen = hg19_chrlen[seq.chrm]
#         random_start = random.randint(0, chrlen)
#         random_end = random_start + seq.length
#         random_seq = Sequence(seq.chrm, random_start, random_end)
#         return random_seq
#     else:
#         print 'sorry, 暂时还只支持hg19的基因组序列。'
#
#
# def generate_a_chromosome_seqs(seqs_chrm, chrm, genome='hg19'):
#     """
#     如果给定的序列都来自同一条染色体调用这个方法来生成对应的随机序列
#     """
#     if genome != 'hg19':
#         exit()
#     chrlen = hg19_chrlen[chrm]
#     seqs_chrm_length = np.array([seq.length for seq in seqs_chrm])
#     random_starts = np.random.randint(0, chrlen, len(seqs_chrm))
#     random_ends = random_starts + seqs_chrm_length
#     random_seqs_chrm = []
#     for start, end in zip(random_starts, random_ends):
#         random_seqs_chrm.append(Sequence(chrm, start, end))
#     return random_seqs_chrm
#
#
# def generate_a_group_random_seqs(seqs, genome='hg19'):
#     """
#     给定一组序列，随机生成一组等长的随机序列，生成的这组序列在不同染色体上的数目和给定的那组序列一样
#     @param seqs: 给定的一组序列
#     @param genome:序列的基因组来源
#     @return: 随机生成的序列组
#     """
#     if genome != 'hg19':
#         print 'sorry, 暂时还只支持hg19的基因组序列。'
#         exit()
#     # random_seqs = [generate_a_random_seq(seq) for seq in seqs]  # 通过调用generate_a_random_seq一条条生成随机序列
#     # 用Sequences封装seqs列表，然后按照染色体进行分组
#     random_seqs = []
#     sqs = Sequences()
#     sqs.set_sequences(seqs)
#     group_seqs = sqs.group_by_chromosomes()
#     for chrm in group_seqs.keys():
#         chrlen = hg19_chrlen[chrm]
#         seqs_chrm = group_seqs[chrm]  # 这组序列中在同一染色体上的所有序列
#         seqs_chrm_length = np.array([seq.length for seq in seqs_chrm])
#
#         random_starts = np.random.randint(0, chrlen, len(seqs_chrm))
#         random_ends = random_starts + seqs_chrm_length
#         random_seqs_chrm = []
#         for start, end in zip(random_starts, random_ends):
#             random_seqs_chrm.append(Sequence(chrm, start, end))
#         random_seqs += random_seqs_chrm
#     return random_seqs
#
