import copy


def parse_keywords(keywords):
    modifiers = []
    for key in keywords:
        key_lower = key.lower()
        if key_lower == 'pointer':
            modifiers.append(1)
        elif key_lower == 'allocatable':
            modifiers.append(2)
        elif key_lower == 'optional':
            modifiers.append(3)
        elif key_lower == 'public':
            modifiers.append(4)
        elif key_lower == 'private':
            modifiers.append(5)
        elif key_lower == 'nopass':
            modifiers.append(6)
        elif key_lower == 'intent(in)':
            modifiers.append(7)
        elif key_lower == 'intent(out)':
            modifiers.append(8)
        elif key_lower == 'intent(inout)':
            modifiers.append(9)
        elif key_lower.startswith('dimension'):
            ndims = key_lower.count(':')
            modifiers.append(20+ndims)
    modifiers.sort()
    return modifiers


def get_keywords(modifiers):
    mod_strings = []
    for modifier in modifiers:
        if modifier == 1:
            mod_strings.append('POINTER')
        elif modifier == 2:
            mod_strings.append('ALLOCATABLE')
        elif modifier == 3:
            mod_strings.append('OPTIONAL')
        elif modifier == 4:
            mod_strings.append('PUBLIC')
        elif modifier == 5:
            mod_strings.append('PRIVATE')
        elif modifier == 6:
            mod_strings.append('NOPASS')
        elif modifier == 7:
            mod_strings.append('INTENT(IN)')
        elif modifier == 8:
            mod_strings.append('INTENT(OUT)')
        elif modifier == 9:
            mod_strings.append('INTENT(INOUT)')
        elif modifier > 20:
            dim_str = ":"
            for i in range(modifier-21):
                dim_str += ",:"
            mod_strings.append('DIMENSION({0})'.format(dim_str))
    return mod_strings


def find_in_scope(scope, var_name, obj_tree):
    var_name_lower = var_name.lower()
    # Check local scope
    for child in scope.get_children():
        if child.name.lower() == var_name_lower:
            return child, scope
    # Setup USE search
    use_list = {}
    for use_stmnt in scope.use:
        use_mod = use_stmnt[0]
        if use_mod not in obj_tree:
            continue
        # Module name is request
        if use_mod.lower() == var_name_lower:
            return obj_tree[use_mod][0], None
        only_list = use_stmnt[1]
        if len(only_list) > 0:
            if var_name not in only_list:
                continue
        use_list[use_mod] = 1
    # Look in use stmnts
    for use_mod in use_list:
        # poss_members = []
        # Check module
        if use_mod in obj_tree:
            curr_scope = obj_tree[use_mod][0]
            tmp_var, tmp_scope = find_in_scope(curr_scope, var_name, obj_tree)
            if tmp_var is not None:
                if tmp_scope is not None:
                    curr_scope = tmp_scope
                return tmp_var, curr_scope
    # Check parent scopes
    if scope.parent is not None:
        curr_scope = scope.parent
        tmp_var, tmp_scope = find_in_scope(curr_scope, var_name, obj_tree)
        if tmp_var is not None:
            return tmp_var, tmp_scope
    return None, None


class fortran_scope:
    def __init__(self, line_number, name, enc_scope=None):
        self.base_setup(line_number, name, enc_scope)

    def base_setup(self, sline, name, enc_scope=None):
        self.sline = sline
        self.eline = None
        self.name = name
        self.children = []
        self.members = []
        self.use = []
        self.inherit = None
        self.parent = None
        self.vis = 0
        self.def_vis = 0
        if enc_scope is not None:
            self.FQSN = enc_scope.lower() + "::" + self.name.lower()
        else:
            self.FQSN = self.name.lower()

    def set_default_vis(self, new_vis):
        self.def_vis = new_vis

    def set_visibility(self, new_vis):
        self.vis = new_vis

    def add_use(self, use_mod, only_list=[]):
        lower_only = []
        for only in only_list:
            lower_only.append(only.lower())
        self.use.append([use_mod.lower(), lower_only])

    def set_inherit(self, inherit_type):
        self.inherit = inherit_type

    def resolve_inherit(self, obj_tree):
        for child in self.children:
            child.resolve_inherit(obj_tree)

    def resolve_link(self):
        for child in self.children:
            child.resolve_link()

    def add_parent(self, parent_obj):
        self.parent = parent_obj

    def add_child(self, child):
        self.children.append(child)

    def add_member(self, member):
        self.members.append(member)

    def get_type(self):
        return -1

    def get_desc(self):
        return 'unknown'

    def get_snippet(self, name_replace=None, drop_arg=None):
        if name_replace is not None:
            return name_replace
        return self.name

    def get_documentation(self):
        return None

    def get_children(self):
        return self.children

    def is_optional(self):
        return False

    def end(self, line_number):
        self.eline = line_number


class fortran_module(fortran_scope):
    def get_type(self):
        return 1

    def get_desc(self):
        return 'MODULE'


class fortran_program(fortran_module):
    def get_desc(self):
        return 'PROGRAM'


class fortran_subroutine(fortran_scope):
    def __init__(self, line_number, name, enc_scope=None, args=None):
        self.base_setup(line_number, name, enc_scope)
        self.args = args
        self.arg_objs = []

    def resolve_link(self):
        self.arg_objs = []
        arg_list = self.args.replace(' ', '').lower().split(',')
        for child in self.children:
            ind = -1
            for i, arg in enumerate(arg_list):
                if arg == child.name.lower():
                    ind = i
                    break
            if ind >= 0:
                self.arg_objs.append(child)
            child.resolve_link()

    def get_type(self):
        return 2

    def get_snippet(self, name_replace=None, drop_arg=None):
        arg_str = "({0})".format(self.args)
        if drop_arg is not None:
            first_comma = self.args.find(",")
            if first_comma > 0:
                arg_str = "({0})".format(self.args[first_comma+1:])
            else:
                arg_str = "()"
        if name_replace is not None:
            return name_replace + arg_str
        return self.name + arg_str

    def get_desc(self):
        return 'SUBROUTINE'


class fortran_function(fortran_subroutine):
    def __init__(self, line_number, name, enc_scope=None, args=None,
                 return_type=None, result_var=None):
        self.base_setup(line_number, name, enc_scope)
        self.args = args
        self.arg_objs = []
        self.result_var = result_var
        if return_type is not None:
            self.return_type = return_type[0]
            self.modifiers = parse_keywords(return_type[1])
        else:
            self.return_type = None
            self.modifiers = []

    def get_type(self):
        return 3

    def get_desc(self):
        # desc = None
        if self.result_var is not None:
            result_var_lower = self.result_var.lower()
            for child in self.children:
                if child.name == result_var_lower:
                    return child.get_desc()
        if self.return_type is not None:
            return self.return_type
        return 'FUNCTION'


class fortran_type(fortran_scope):
    def __init__(self, line_number, name, modifiers, enc_scope=None):
        self.base_setup(line_number, name, enc_scope)
        #
        self.in_children = []
        self.modifiers = modifiers
        self.inherit = None
        for modifier in self.modifiers:
            if modifier == 4:
                self.vis = 1
            elif modifier == 5:
                self.vis = -1

    def get_type(self):
        return 4

    def get_desc(self):
        return 'TYPE'

    def get_children(self):
        tmp_list = copy.copy(self.children)
        tmp_list.extend(self.in_children)
        return tmp_list

    def resolve_inherit(self, obj_tree):
        if self.inherit is None:
            return
        #
        inherit_var, inherit_scope = \
            find_in_scope(self.parent, self.inherit, obj_tree)
        if inherit_var is not None:
            inherit_var.resolve_inherit(obj_tree)
            # Get current fields
            child_names = []
            for child in self.children:
                child_names.append(child.name.lower())
                child.resolve_inherit(obj_tree)
            # Import for parent objects
            self.in_children = []
            for child in inherit_var.children:
                if child.name.lower() not in child_names:
                    self.in_children.append(child)


class fortran_int(fortran_scope):
    def __init__(self, line_number, name, enc_scope=None):
        self.base_setup(line_number, name, enc_scope)
        self.mems = []

    def get_type(self):
        return 5

    def get_desc(self):
        return 'INTERFACE'

    def resolve_link(self):
        if self.parent is None:
            return
        self.mems = []
        for member in self.members:
            for child in self.parent.children:
                if child.name.lower() == member:
                    self.mems.append(child)


class fortran_obj:
    def __init__(self, line_number, name, var_desc, modifiers,
                 enc_scope=None, link_obj=None):
        self.sline = line_number
        self.name = name
        self.desc = var_desc
        self.modifiers = modifiers
        self.children = []
        self.vis = 0
        self.parent = None
        self.link_obj = None
        if link_obj is not None:
            self.link_name = link_obj.lower()
        else:
            self.link_name = None
        if enc_scope is not None:
            self.FQSN = enc_scope.lower() + "::" + self.name.lower()
        else:
            self.FQSN = self.name.lower()
        for modifier in self.modifiers:
            if modifier == 4:
                self.vis = 1
            elif modifier == 5:
                self.vis = -1

    def add_parent(self, parent_obj):
        self.parent = parent_obj

    def resolve_link(self):
        if self.link_name is None:
            return
        if self.parent is not None:
            parent = self.parent
            while(parent is not None):
                for child in parent.children:
                    if child.name.lower() == self.link_name:
                        self.link_obj = child
                        return
                parent = parent.parent

    def set_visibility(self, new_vis):
        self.vis = new_vis

    def get_type(self):
        if self.link_obj is not None:
            return self.link_obj.get_type()
        # Normal variable
        return 6

    def get_desc(self):
        if self.link_obj is not None:
            return self.link_obj.get_desc()
        # Normal variable
        return self.desc

    def set_dim(self, ndim):
        for (i, modifier) in enumerate(self.modifiers):
            if modifier > 20:
                self.modifiers[i] = ndim+20
                return
        self.modifiers.append(ndim+20)

    def get_snippet(self, name_replace=None, drop_arg=None):
        name = self.name
        if name_replace is not None:
            name = name_replace
        if self.link_obj is not None:
            return self.link_obj.get_snippet(name, drop_arg)
        # Normal variable
        return name

    def get_documentation(self):
        if self.link_obj is not None:
            return self.link_obj.get_documentation()
        #
        doc_str = self.desc
        if len(self.modifiers) > 0:
            doc_str += ", "
            doc_str += ", ".join(get_keywords(self.modifiers))
        return doc_str

    def get_children(self):
        return []

    def resolve_inherit(self, obj_tree):
        return

    def is_optional(self):
        if self.modifiers.count(3) > 0:
            return True
        else:
            return False
        # try:
        #     ind = self.modifiers.index(3)
        # except:
        #     return False
        # return True


class fortran_meth(fortran_obj):
    def get_snippet(self, name_replace=None, drop_arg=None):
        if self.modifiers.count(6) > 0:
            nopass = True
        else:
            nopass = False
        # try:
        #     ind = self.modifiers.index(6)
        # except:
        #     nopass = False
        # else:
        #     nopass = True
        #
        name = self.name
        if name_replace is not None:
            name = name_replace
        if self.link_obj is not None:
            return self.link_obj.get_snippet(name, nopass)

    def get_type(self):
        if self.link_obj is not None:
            return self.link_obj.get_type()
        # Generic
        return 7


class fortran_file:
    def __init__(self):
        self.global_dict = {}
        self.scope_list = []
        self.variable_list = []
        self.public_list = []
        self.private_list = []
        self.scope_stack = []
        self.end_stack = []
        self.current_scope = None
        self.END_REGEX = None
        self.enc_scope_name = None

    def get_enc_scope_name(self):
        if self.current_scope is None:
            return None
        name_str = self.current_scope.name
        if len(self.scope_stack) > 0:
            for scope in reversed(self.scope_stack):
                name_str = scope.name + '::' + name_str
        return name_str

    def add_scope(self, new_scope, END_SCOPE_REGEX, hidden=False):
        if hidden:
            self.variable_list.append(new_scope)
        else:
            self.scope_list.append(new_scope)
        if self.current_scope is None:
            self.global_dict[new_scope.FQSN] = new_scope
        else:
            self.current_scope.add_child(new_scope)
            new_scope.add_parent(self.current_scope)
            self.scope_stack.append(self.current_scope)
        if self.END_REGEX is not None:
            self.end_stack.append(self.END_REGEX)
        self.current_scope = new_scope
        self.END_REGEX = END_SCOPE_REGEX
        self.enc_scope_name = self.get_enc_scope_name()

    def end_scope(self, line_number):
        self.current_scope.end(line_number)
        if len(self.scope_stack) > 0:
            self.current_scope = self.scope_stack.pop()
        else:
            self.current_scope = None
        if len(self.end_stack) > 0:
            self.END_REGEX = self.end_stack.pop()
        else:
            self.END_REGEX = None
        self.enc_scope_name = self.get_enc_scope_name()

    def add_variable(self, new_var):
        self.current_scope.add_child(new_var)
        new_var.add_parent(self.current_scope)
        self.variable_list.append(new_var)

    def add_int_member(self, key):
        self.current_scope.add_member(key)

    def add_private(self, name):
        self.private_list.append(self.enc_scope_name+'::'+name)

    def add_public(self, name):
        self.public_list.append(self.enc_scope_name+'::'+name)

    def add_use(self, mod_words):
        if len(mod_words) > 0:
            n = len(mod_words)
            if n > 2:
                use_list = mod_words[2:]
                self.current_scope.add_use(mod_words[0], use_list)
            else:
                self.current_scope.add_use(mod_words[0])

    def get_scopes(self, line_number=None):
        if line_number is None:
            return self.scope_list
        scope_list = []
        for scope in self.scope_list:
            if line_number >= scope.sline and line_number <= scope.eline:
                scope_list.append(scope)
        return scope_list

    def get_inner_scope(self, line_number):
        scope_sline = -1
        curr_scope = None
        for scope in self.scope_list:
            if scope.sline > scope_sline:
                if line_number >= scope.sline and line_number <= scope.eline:
                    curr_scope = scope
                    scope_sline = scope.sline
        return curr_scope
