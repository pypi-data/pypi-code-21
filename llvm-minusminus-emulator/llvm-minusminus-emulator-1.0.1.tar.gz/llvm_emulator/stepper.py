from enum import Enum

from llvm_emulator import ll


def TODO(msg):
    print('TODO: not implemented yet at {}'
          .format(msg))


def err(msg):
    print('ERROR: {}'
          .format(msg))


def warn(msg):
    print('WARNING: {}'
          .format(msg))


class Garbage(Enum):
    GARBAGE = '<<Unitialized memory>>'

    def __repr__(self):
        return '<<Garbage>>'


builtins = ['allocRecord', 'initArray', 'stringEqual', 'stringNotEq', 'stringLess',
            'stringLessEq', 'stringGreater', 'stringGreaterEq', 'exponent', 'print',
            'flush', 'getChar', 'ord', 'chr', 'size', 'substring', 'concat', 'not',
            'exit_tig']


def step(insns, terminator, blocks, stack_frames, ssa_env, global_env, heap,
         tdecs, fdecs, call_res):
    if len(insns) == 0:
        return terminate(terminator, blocks, stack_frames, ssa_env, global_env, heap,
                         call_res)
    ssa_target, next_insn = insns[0]
    insns_rest = insns[1:]

    def store_in_ssa(res, insns_rest, terminator, blocks, stack_frames, ssa_env, heap,
                     call_res):
        if ssa_target is not None:
            if ssa_target in ssa_env:
                err('Cannot assign to variable twice: {}'
                    .format(ssa_target))
            elif res is None:
                err('Cannot assign empty value to %{}'
                    .format(ssa_target))
            else:
                # TODO
                print('%{} <- {}'
                      .format(ssa_target, res))
                ssa_env[ssa_target] = res

        return insns_rest, terminator, blocks, stack_frames, ssa_env, heap, call_res

    # TODO
    print('Evaluating {}'
          .format(ll.insn2s(next_insn)))

    res = None
    if isinstance(next_insn, ll.Binop):
        bop = next_insn.bop
        left = next_insn.left
        right = next_insn.right
        left_v = eval_oper(left, ssa_env, global_env)
        right_v = eval_oper(right, ssa_env, global_env)
        res = eval_binop(bop, left_v, right_v)

        # TODO
        print('{} {}, {}'
              .format(bop, left_v, right_v))
    elif isinstance(next_insn, ll.Alloca):
        ty = next_insn.ty
        base_ty = ty2base_ty(ty, tdecs)
        size = base_ty2size(base_ty)

        # TODO
        print('alloca {}  -->  allocating {} cells'
              .format(ll.ty2s(base_ty), size))

        ptr = len(heap)
        for i in range(max(size, 1)):
            heap.append(Garbage.GARBAGE)

        res = ptr
    elif isinstance(next_insn, ll.Load):
        ty = next_insn.ty
        base_ty = ty2base_ty(ty, tdecs)
        size = base_ty2size(base_ty)
        location = next_insn.location
        location_v = eval_oper(location, ssa_env, global_env)

        # TODO
        print('load heap[{}]'
              .format(location_v))

        if size != 1:
            err(('This emulator cannot load objects larger than 1 cell.'
                 ' Current size is {}')
                .format(size))

        if location_v == 0:
            err('You are not allowed to read from location 0')
            res = 0
        else:
            res = heap[location_v]
    elif isinstance(next_insn, ll.Store):
        ty = next_insn.ty
        base_ty = ty2base_ty(ty, tdecs)
        size = base_ty2size(base_ty)
        value = next_insn.value
        location = next_insn.location

        value_v = eval_oper(value, ssa_env, global_env)
        location_v = eval_oper(location, ssa_env, global_env)

        # TODO
        print('heap[{}] <- {}'
              .format(location_v, value_v))
        if location_v == 0:
            err('You are not allowed to store at location 0 (Null)')
        elif size == 1:
            heap[location_v] = value_v
        else:
            err(('This emulator cannot store objects larger than 1 cell.'
                 ' Current size is {}')
                .format(size))
    elif isinstance(next_insn, ll.Icmp):
        cnd = next_insn.cnd
        left = next_insn.left
        right = next_insn.right
        left_v = eval_oper(left, ssa_env, global_env)
        right_v = eval_oper(right, ssa_env, global_env)
        res = eval_icmp(cnd, left_v, right_v)

        # TODO
        print('icmp {} {}, {}'
              .format(cnd,  left_v, right_v))
    elif isinstance(next_insn, ll.Call):
        callee = next_insn.callee
        arguments = next_insn.arguments

        if not isinstance(callee, ll.Gid):
            err('Cannot call anything but global identifiers: {}'
                .format(ll.oper2s(callee)))
            return insns_rest, terminator, blocks, stack_frames, ssa_env, heap, call_res

        arguments_v = [eval_oper(oper, ssa_env, global_env)
                       for ty, oper in arguments]

        if callee.val in fdecs:
            function = fdecs[callee.val]
        elif callee.val in builtins:
            res, new_heap, should_exit = emulate_builtin(callee.val, arguments_v, ssa_env,
                                                         heap)
            if should_exit:
                new_insns = [(None, ll.CallResult(res))]
                new_terminator = None
                new_blocks = {}
                new_ssa_env = ssa_env
                new_stack_frames = []
                new_call_res = []
                return (new_insns, new_terminator, new_blocks, new_stack_frames,
                        new_ssa_env, heap, new_call_res)
            else:
                return store_in_ssa(res, insns_rest, terminator, blocks, stack_frames,
                                    ssa_env, new_heap, call_res)
        else:
            err('Could not find function {} in environment:\n{}'
                .format(callee.val, list(fdecs.keys()) + builtins))
            return insns_rest, terminator, blocks, stack_frames, ssa_env, heap, call_res

        parameters = function.parameters
        print('call @{} ({})'
              .format(callee.val,
                      ', '.join('%{} <- {}'.format(par[1], arg)
                                for par, arg in zip(parameters, arguments_v))))
        child_insns = function.body.first_block.insns
        child_terminator = function.body.first_block.terminator
        child_blocks = function.body.named_blocks
        child_stack_frames = [(insns_rest, terminator, blocks, ssa_env)] + stack_frames
        child_ssa_env = {par[1]: arg for par, arg in zip(parameters, arguments_v)}
        child_heap = heap
        child_call_res = [ssa_target] + call_res
        return (child_insns, child_terminator, child_blocks, child_stack_frames,
                child_ssa_env, child_heap, child_call_res)

    elif isinstance(next_insn, ll.Bitcast):
        oper = next_insn.oper
        from_ty = next_insn.from_ty
        to_ty = next_insn.to_ty
        oper_v = eval_oper(oper, ssa_env, global_env)
        res = oper_v

        # TODO
        print('bitcast {} {} to {}'
              .format(ll.ty2s(from_ty), oper_v, ll.ty2s(to_ty)))
    elif isinstance(next_insn, ll.Gep):
        res = 0
        base_ty = next_insn.base_ty
        oper_ty = next_insn.oper_ty
        oper = next_insn.oper
        steps = next_insn.steps

        actual_base_ty = ty2base_ty(base_ty, tdecs)
        actual_oper_ty = ty2base_ty(oper_ty, tdecs)

        if not isinstance(actual_oper_ty, ll.PointerType):
            err('Type of main operand to getelementptr must be a pointer type. It was {}'
                .format(ll.ty2s(actual_oper_ty)))
        elif actual_base_ty != actual_oper_ty.inner_ty:
            err(('Type of the main operand does not match the type getelementptr'
                 ' navigates through.\n'
                 '  Getelementptr type: {}\n'
                 '  Operand type:       {}')
                .format(ll.ty2s(actual_base_ty), ll.ty2s(actual_oper_ty.inner_ty)))
        else:
            oper_v = eval_oper(oper, ssa_env, global_env)
            gep_res, formula = handle_gep(oper_v, actual_base_ty, steps, ssa_env,
                                          global_env)
            res = gep_res

            # TODO
            print('Gep formula: {}'
                  .format(formula))
    elif isinstance(next_insn, ll.Zext):
        oper = next_insn.oper
        from_ty = next_insn.from_ty
        to_ty = next_insn.to_ty
        oper_v = eval_oper(oper, ssa_env, global_env)
        res = oper_v

        # TODO
        print('zext {} {} to {}'
              .format(ll.ty2s(from_ty), oper_v, ll.ty2s(to_ty)))
    elif isinstance(next_insn, ll.Ptrtoint):
        oper = next_insn.oper
        pointer_ty = next_insn.pointer_ty
        to_ty = next_insn.to_ty
        oper_v = eval_oper(oper, ssa_env, global_env)
        res = oper_v

        # TODO
        print('ptrtoint {}* {} to {}'
              .format(ll.ty2s(pointer_ty), oper_v, ll.ty2s(to_ty)))
    elif isinstance(next_insn, ll.CallResult):
        res = next_insn.val
    else:
        err('Unknown LLVM instruction: {}'
            .format(next_insn))

    return store_in_ssa(res, insns_rest, terminator, blocks, stack_frames, ssa_env, heap,
                        call_res)


def terminate(terminator, blocks, stack_frames, ssa_env, global_env, heap, call_res):
    def clear_block_from_ssa_env(insns, ssa_env):
        for (id, insn) in insns:
            if id is not None and id in ssa_env:
                del ssa_env[id]

    print('Evaluating {}'
          .format(ll.terminator2s(terminator)))

    if isinstance(terminator, ll.Ret):
        oper = terminator.oper
        if oper is None:
            oper_v = None
        else:
            oper_v = eval_oper(oper, ssa_env, global_env)

        # TODO
        print('Returning {}'
              .format(oper_v))

        if len(stack_frames) == 0:
            new_insns = [(None, ll.CallResult(oper_v))]
            new_terminator = None
            new_blocks = {}
            new_ssa_env = ssa_env
            new_stack_frames = []
            new_call_res = []
        else:
            new_insns, new_terminator, new_blocks, new_ssa_env = stack_frames[0]
            new_insns = [(call_res[0], ll.CallResult(oper_v))] + new_insns
            new_stack_frames = stack_frames[1:]
            new_call_res = call_res[1:]
        return (new_insns, new_terminator, new_blocks, new_stack_frames,
                new_ssa_env, heap, new_call_res)
    elif isinstance(terminator, ll.Br):
        label = terminator.label
        next_block = blocks[label]
        new_insns = next_block.insns
        new_terminator = next_block.terminator

        # TODO: Might need to find a better solution as we will ignore
        # multiple assignments, if they are spread over multiple
        # blocks.
        clear_block_from_ssa_env(new_insns, ssa_env)

        # TODO
        print('Jumping unconditionally to {}'
              .format(label))

        return (new_insns, new_terminator, blocks, stack_frames,
                ssa_env, heap, call_res)
    elif isinstance(terminator, ll.Cbr):
        ty = terminator.ty
        if ty != ll.SimpleType.I1:
            warn('Branching based on value of type {}. You ought to branch on {}'
                 .format(ll.ty2s(ty), ll.ty2s(ll.SimpleType.I1)))
        operand = terminator.oper
        operand_v = eval_oper(operand, ssa_env, global_env)

        if operand_v:
            label = terminator.then_label
        else:
            label = terminator.else_label

        next_block = blocks[label]
        new_insns = next_block.insns
        new_terminator = next_block.terminator
        clear_block_from_ssa_env(new_insns, ssa_env)

        # TODO
        print('Operand was {}. Branching to {}'
              .format(operand_v, label))

        return (new_insns, new_terminator, blocks, stack_frames,
                ssa_env, heap, call_res)
    else:
        err('Unknown LLVM terminator: {}'
            .format(terminator))


def eval_oper(operand, ssa_env, global_env):
    if isinstance(operand, ll.Null):
        return 0
    elif isinstance(operand, ll.Const):
        return operand.val
    elif isinstance(operand, ll.Gid):
        gid = operand.val
        try:
            return global_env[gid]
        except KeyError:
            err('Unable to find @{} in environment:\n{}'
                .format(global_env))
            return 0
    elif isinstance(operand, ll.Id):
        id = operand.val
        try:
            return ssa_env[id]
        except KeyError:
            err('Unable to find %{} in environment:\n{}'
                .format(id, ssa_env))
            return 0


def eval_binop(bop, left, right):
    if bop == 'add':
        return left + right
    elif bop == 'sub':
        return left - right
    elif bop == 'mul':
        return left * right
    elif bop == 'sdiv':
        return left // right
    elif bop == 'shl':
        return left << right
    elif bop == 'ashr':
        return left >> right
    elif bop == 'lshr':
        return (left >> right) % 0x10000000000000000
    elif bop == 'and':
        return left & right
    elif bop == 'or':
        return left | right
    elif bop == 'xor':
        return left ^ right
    else:
        err('Unknown LLVM Binary operator: {}'
            .format(bop))


def eval_icmp(cnd, left, right):
    if cnd == 'eq':
        return left == right
    elif cnd == 'ne':
        return left != right
    elif cnd == 'slt':
        return left < right
    elif cnd == 'sle':
        return left <= right
    elif cnd == 'sgt':
        return left > right
    elif cnd == 'sge':
        return left >= right
    else:
        err('eval_icmp: Unknown cnd: {}'
            .format(cnd))
        return 0


def handle_gep(starting_location, starting_type, starting_steps, ssa_env, global_env):
    def visit(current_location, current_type, current_steps, current_formula):
        if len(current_steps) == 0:
            return current_location, current_formula
        else:
            s_ty, s_oper = current_steps[0]
            s_oper_v = eval_oper(s_oper, ssa_env, global_env)
            next_steps = current_steps[1:]
            if isinstance(current_type, ll.StructType):
                if not isinstance(s_oper, ll.Const):
                    err('Index into struct must be a constant. It was: {}'
                        .format(ll.oper2s(s_oper)))
                    return current_location, current_formula + ' + ???'
                jumps = [base_ty2size(current_type.fields[i])
                         for i in range(s_oper_v)]
                next_location = current_location + sum(jumps)
                next_type = current_type.fields[s_oper_v]
                if len(jumps) > 0:
                    next_formula = ('{} + ({})'
                                    .format(current_formula,
                                            ' + '.join(map(str, jumps))))
                else:
                    next_formula = ('{} + 0'
                                    .format(current_formula))

                return visit(next_location, next_type, next_steps, next_formula)
            elif isinstance(current_type, ll.ArrayType):
                TODO('gep arrays')
                return current_location, current_formula + ' + ???'
            elif isinstance(current_type, ll.PointerType):
                err(('Cannot use getelementptr to traverse pointers.'
                     ' Use Load, and getelementptr on the result from that'
                     ' to go through a pointer.'))
                return current_location, current_formula + ' + ???'
            else:
                err('Unknown type to getelementptr on: {}'
                    .format(ll.ty2s(current_type)))
                return current_location, current_formula + ' + ???'

    if len(starting_steps) == 0:
        err('There must be at least one stepping argument to a getelementptr instruction')
        return 0, ''
    s_ty, s_oper = starting_steps[0]
    s_oper_v = eval_oper(s_oper, ssa_env, global_env)
    size = base_ty2size(starting_type)
    next_location = starting_location + s_oper_v * size
    formula = ('{} + {} * {}'
               .format(starting_location, s_oper_v, size))
    return visit(next_location, starting_type, starting_steps[1:], formula)


def ty2base_ty(ty, tdecs, seen=[]):
    if isinstance(ty, ll.SimpleType):
        return ty
    elif isinstance(ty, ll.PointerType):
        # TODO: Consider if types behind pointers should not be
        # expanded. They might be allowed for cyclic types
        return ll.PointerType(ty2base_ty(ty.inner_ty, tdecs, seen))
    if isinstance(ty, ll.StructType):
        return ll.StructType([ty2base_ty(t, tdecs, seen)
                              for t in ty.fields])
    if isinstance(ty, ll.NamedType):
        other_name = ty.other_name
        if other_name in seen:
            err('Cyclic type definition, offender: {}. Seen: {}'
                .format(other_name, seen))
        elif other_name in tdecs:
            return ty2base_ty(tdecs[other_name].body, tdecs, [other_name] + seen)
        else:
            err('Could not find type {} in global type environment:\n{}'
                .format(ll.ty2s(ty), list(tdecs.keys())))
            return ll.SimpleType.Void
    else:
        # TODO
        err('ty2base_ty: Unknown type: {}'
            .format(ll.ty2s(ty)))
        return ty


def base_ty2size(base_ty):
    if isinstance(base_ty, ll.SimpleType):
        return 1
    elif isinstance(base_ty, ll.PointerType):
        return 1
    elif isinstance(base_ty, ll.StructType):
        return max(1, sum(map(base_ty2size, base_ty.fields)))
    else:
        # TODO
        err('base_ty2size: Unknown type or illegal type: {}'
            .format(ll.ty2s(base_ty)))
        return 1


def alloc_globals(gdecls, heap):
    def alloc_global(ginit):
        next_idx = len(heap)
        if isinstance(ginit, ll.GNull):
            TODO('alloc_global: GNull')
        elif isinstance(ginit, ll.GGid):
            TODO('alloc_global: GGid')
        elif isinstance(ginit, ll.GInt):
            heap.append(ginit.val)
        elif isinstance(ginit, ll.GString):
            heap.append(ginit.val)
        elif isinstance(ginit, ll.GArray):
            TODO('alloc_global: GArray')
        elif isinstance(ginit, ll.GStruct):
            for ty, field in ginit.fields:
                alloc_global(field)
        else:
            err('alloc_global: Unknown global init value: {}'
                .format(ll.ginit2s(ginit)))
        return next_idx

    global_env = {}

    for gdecl in gdecls.values():
        location = alloc_global(gdecl.body)
        print('heap[{}] <- {}'
              .format(location, ll.gdecl2s(gdecl)))
        global_env[gdecl.name] = location

    return global_env


def emulate_builtin(name, arguments_v, ssa_env, heap):
    new_heap = heap
    res = None
    should_exit = False
    if name == 'allocRecord':
        if len(arguments_v) != 1:
            err('Number of arguments to {} should be 1'
                .format(name))
        else:
            size = max(arguments_v[0], 1)
            print('Allocating {} cells'
                  .format(size))
            res = len(heap)
            for i in range(size):
                heap.append(Garbage.GARBAGE)
    elif name == 'initArray':
        if len(arguments_v) != 3:
            err('Number of arguments to {} should be 3'
                .format(name))
        else:
            num_elements = arguments_v[0]
            cells_per_element = arguments_v[1]
            init_ptr = arguments_v[2]
            print('Allocating {} + {} + {} (size + pointer + content) cells'
                  .format(1, 1, num_elements * cells_per_element))
            struct_begin = len(heap)
            heap.append(num_elements)
            heap.append(Garbage.GARBAGE)  # pointer to array contents
            array_begin = len(heap)
            heap[struct_begin + 1] = array_begin
            init_val = [heap[init_ptr + j]
                        for j in range(cells_per_element)]
            if len(init_val) == 1:
                init_val_s = init_val[0]
            else:
                init_val_s = '{{}}'.format(', '.join(init_val))

            for i in range(num_elements):
                array_last = len(heap)
                for j in init_val:
                    heap.append(j)

            if num_elements <= 0:
                array_init_s = 'No elements initialized for zero length array'
            else:
                array_init_s = ('heap[{}..{}] <- heap[{}] = {}'
                                .format(array_begin, array_last,
                                        init_ptr, init_val_s))
            # TODO
            print('heap[{}] <- {}, heap[{}] <- {}, --- {}'
                  .format(struct_begin, num_elements,
                          struct_begin + 1, array_begin,
                          array_init_s))
            res = struct_begin
    elif name == 'print':
        if len(arguments_v) != 2:
            err('Number of arguments to {} should be 3'
                .format(name))
        else:
            struct_begin = arguments_v[1]
            print('Printing string, heap[{}]:'
                  .format(struct_begin))
            printee = heap[struct_begin + 1]
            print(printee)
            if not isinstance(printee, str):
                warn('What was printed, was not stored as a string in the heap')
    elif name in builtins:
        TODO('Have not implemented builtin function {}, yet.'
             .format(name))
    else:
        err('Unknown builtin function {}.'
            .format(name))
        return None, heap

    return res, new_heap, should_exit


def auto_step(ast, function_name='tigermain', function_args=[1234, 5678]):
    tdecls = ast.tdecls
    fdecls = ast.fdecls
    gdecls = ast.gdecls

    function = fdecls[function_name]
    body = function.body
    first_block = body.first_block
    blocks = body.named_blocks
    insns = first_block.insns
    terminator = first_block.terminator
    stack_frames = []
    ssa_env = {par[1]: arg for par, arg in zip(function.parameters, function_args)}
    heap = [None]
    call_res = []

    global_env = alloc_globals(gdecls, heap)
    print('Heap after globals are allocated:')
    print(heap)
    print()

    step_cnt = 0
    while True:
        (insns, terminator, blocks,
         stack_frames, ssa_env, heap, call_res) = step(insns, terminator, blocks,
                                                       stack_frames, ssa_env,
                                                       global_env, heap, tdecls,
                                                       fdecls, call_res)
        print()
        step_cnt += 1
        if terminator is None:
            print('Stepping done!\nFinal ssa_env: {}'
                  .format(ssa_env))
            print('Final heap: {}'
                  .format(heap))
            print('Program resulted in {} after {} steps'.
                  format(insns[0][1].val, step_cnt))
            break

        if step_cnt % 100 == 0:
            while True:
                stop_q = input('We have now done {} steps. Continue? [Y/n]: '
                               .format(step_cnt)).lower()
                if stop_q in ['y', 'yes', 'n', 'no', '']:
                    break
            if stop_q in ['n', 'no']:
                break
