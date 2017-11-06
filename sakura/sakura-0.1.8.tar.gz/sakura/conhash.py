# coding: utf-8

# import platform

# if platform.system().lower() == 'darwin':
#     from sakura.cpplib_osx import ConHash
# else:
#     from sakura.cpplib import ConHash
import sys
from hashlib import md5

_PY2 = sys.version_info[0] == 2


if _PY2:
    pass
else:
    long = int
    xrange = range


class ConHash(object):

    def __init__(self, nodes=None, replicas=3):
        """ nodes 是字符串的列表
            replicas 表示有多少个虚拟节点
        """
        self.replicas = replicas
        self.ring = dict()
        self._sorted_keys = []  # 有序的 hash node 队列
        self.lookup = self.get_node
        if nodes:
            for node in nodes:
                self.add_node(node)

    def add_node(self, node, *args):
        """将 node 节点加入到哈希环中
        """
        for i in xrange(0, self.replicas):
            key = self.gen_key('%s:%s' % (node, i))
            self.ring[key] = node
            self._sorted_keys.append(key)
        self._sorted_keys.sort()

    def remove_node(self, node):
        for i in xrange(0, self.replicas):
            key = self.gen_key('%s:%s' % (node, i))
            del self.ring[key]
            self._sorted_keys.remove(key)

    def get_node(self, string_key):
        """根据 string_key 找到相应的 node 节点
        """
        return self.get_node_pos(string_key)[0]

    def get_node_pos(self, string_key):
        """根据 string key 找到 node ,如果没找到，则返回第一个节点
        """
        if not self.ring:
            return None, None
        key = self.gen_key(string_key)
        nodes = self._sorted_keys
        for i in xrange(0, len(nodes)):
            node = nodes[i]
            if key <= node:
                return self.ring[node], i
        return self.ring[nodes[0]], 0

    def get_nodes(self, string_key):
        """ 获取 所有可用的 nodes 节点
        """
        if not self.ring:
            yield None, None
        node, pos = self.get_node_pos(string_key)
        # 先返回 string_key pos 节点后的 nodes
        for key in self._sorted_keys[pos:]:
            yield self.ring[key]
        # 然后循环返回整个列表
        while True:
            for key in self._sorted_keys:
                yield self.ring[key]

    def gen_key(self, key):
        """生成 key
        """
        m = md5.new()
        m.update(key)
        return long(m.hexdigest(), 16)