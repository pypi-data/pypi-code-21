import yaml, re, os.path
from lxml.etree import Element, ElementTree, SubElement, tostring

from functools import reduce

class GroupTree:
    def __init__(self, datafile=False):
        if not datafile:
            self._datafile = "RDCMan_custom.rdg"
        else:
            self._datafile = datafile

        if not os.path.isfile(self._datafile):
            print("{} not found. It will be created on save.".format(self._datafile))
            
        self._datatree = {}

    def name(self):
        base = os.path.basename(self._datafile)
        return os.path.splitext(base)[0]
    
    def to_xml(self):
        def recursive_build(path, root):
            for key in self.keys_from_path(path):
                sub_path = path + [key]
                branch = self.branch_from_path(sub_path)
                
                node = SubElement(root, 'group')
                props = SubElement(node, 'properties')
                SubElement(props, 'name').text = key

                for k, v in branch['_servers'].items():
                    server = SubElement(node, 'server')
                    sprops = SubElement(server, 'properties')
                    SubElement(sprops, 'name').text = k

                sub_keys = self.keys_from_path(sub_path)
                if len(sub_keys) > 0:
                    recursive_build(sub_path, node)
            
        root = Element('RDCMan', programVersion='2.7', schemaVersion='3')
        file_node = SubElement(root, 'file')
        file_props = SubElement(file_node, 'properties')
        SubElement(file_props, 'expanded').text = 'True'
        SubElement(file_props, 'name').text = self.name()
        recursive_build([], file_node)
        return root
        
    def dump_dict(d):
        return yaml.dump(d, default_flow_style=False)
           
    def save(self):
        root = self.to_xml()
        ElementTree(root).write(
            self._datafile,
            pretty_print=True,
            xml_declaration=True,
            encoding='utf-8',
        )
        print("Success?")

    def __str__(self):
        return GroupTree.dump_dict(self._datatree)

    def keys_from_path(self, path):
        return [k for k in self.branch_from_path(path).keys() if not re.match('^_.*', str(k))]
                    
    def merge_server(self, path, server_name, server_data):
        node = self.branch_from_path(path)
        node['_servers'].update({server_name: server_data})

    def delete_branch(self, path):
        node = self.branch_from_path(path[:-1])
        if len(path) >= 1:
            delete_key = path[-1]
            if delete_key in node:
                del node[delete_key]
            else:
                print("{} not found in tree:".format(' > '.join(map(str, path))))
                print(str(self))

    def branch_from_path(self, path):
        node = self._datatree
        for p in path:
            if p not in node:
                node[p] = {'_servers': {}}

            node = node[p]

        return node
