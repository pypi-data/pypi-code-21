import jieba
import os

script_path = os.path.realpath(__file__)
script_dir = os.path.dirname(script_path)
jieba.load_userdict(os.path.join(script_dir, 'word.txt'))
