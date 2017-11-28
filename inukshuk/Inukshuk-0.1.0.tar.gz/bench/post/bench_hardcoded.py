import io


def render(data, out_write):
    out_write("Lorem ipsum dolor sit amet, consectetur adipiscing elit. Vestibulum at risus convallis, ultricies justo euismod, laoreet turpis. Curabitur elit lacus, finibus in risus sed, condimentum sollicitudin nisl. Etiam fringilla, quam vitae viverra gravida, sapien risus aliquam dolor, sit amet cursus tellus mauris in urna. Vivamus sit amet metus ornare, tempor mauris eget, ultrices enim. Nam euismod felis tellus, vitae egestas ex varius nec. Nam pharetra eu orci non semper. Nullam luctus ligula quis justo convallis scelerisque. In vestibulum consectetur commodo. Proin sodales odio risus, quis imperdiet leo aliquet eu. Integer porta turpis id magna porta, facilisis consequat arcu rutrum. Suspendisse sed erat lacinia, vulputate lacus sit amet, pretium mi.\n")
    out_write("\n")
    out_write("Suspendisse blandit scelerisque nisl, a fermentum urna convallis et. Etiam a velit tortor. Sed a tortor luctus, tempor tortor ac, pretium lacus. Fusce convallis, purus vel convallis accumsan, ex neque volutpat est, sit amet pellentesque magna urna vestibulum sapien. Aliquam rutrum magna sit amet turpis ultrices cursus. Morbi ac imperdiet ex, et dignissim est. Donec posuere et urna id tincidunt. Donec tincidunt enim at ullamcorper auctor. Integer id interdum purus. Ut fermentum augue enim, ac pulvinar metus sagittis sed. Sed pulvinar neque et lorem fringilla consequat. Curabitur nec nunc quis mi efficitur commodo. Pellentesque pulvinar lacus mauris, eget accumsan nibh luctus in. Nam nibh ipsum, imperdiet ultricies accumsan sit amet, interdum sit amet diam. Mauris turpis sem, pellentesque eget venenatis eu, feugiat a metus.\n")

    out_write('![Imago](')
    out_write(data['assets']['image'])
    out_write(')\n')

    out_write('\n')
    out_write("Morbi nulla velit, cursus in urna nec, tristique vehicula ipsum. Etiam ornare, augue id luctus venenatis, nunc augue pulvinar lorem, et laoreet nisi sem quis lorem. Sed sagittis luctus ex faucibus auctor. Fusce suscipit lobortis tristique. Suspendisse rhoncus odio non libero interdum, id tincidunt elit placerat. Maecenas venenatis rutrum ante vel facilisis. Vivamus convallis justo nec nibh semper fringilla. Proin augue quam, consequat eu facilisis sit amet, viverra ut eros. Praesent dictum quis nibh lobortis ornare. Vivamus ex ipsum, maximus sed nulla nec, placerat tincidunt purus. Donec accumsan lacus eget urna laoreet, nec dapibus eros imperdiet. Proin vitae convallis nisi, eget laoreet urna. Nulla sed urna laoreet, congue velit id, elementum est. Aliquam eu turpis consequat, cursus nunc id, iaculis tortor. Vestibulum consectetur malesuada libero, sed consequat ipsum ullamcorper vitae. Nullam lectus urna, condimentum sed sapien quis, luctus consequat turpis.\n")
    out_write("\n")
    out_write("Ut lacinia augue sit amet nisl gravida volutpat. Ut imperdiet, libero in eleifend mollis, ex est convallis nisl, sed pulvinar velit urna porttitor dui. Etiam et nisi id tortor consectetur aliquam ac ac urna. Mauris et egestas est. Mauris efficitur elit a quam luctus, a pharetra magna sodales. Duis feugiat lorem ut elit sollicitudin, sed convallis neque pharetra. Nam non mauris at enim rhoncus ultricies. Aliquam erat volutpat. Phasellus nisi augue, pellentesque quis condimentum ac, eleifend non mauris. Nam mollis neque ac luctus interdum. Pellentesque quis tincidunt mauris. Nulla facilisi. Duis commodo mi et aliquam sagittis. Nulla id eleifend arcu, a viverra mi. Nunc placerat nibh mauris, sed dignissim arcu ultricies non.\n")
    out_write("\n")
    out_write("Nulla facilisi. Vestibulum blandit lobortis justo, in imperdiet leo. Cras vitae auctor sem, placerat tincidunt arcu. Maecenas ullamcorper, leo nec finibus auctor, dolor sem rutrum mauris, a volutpat mi ante quis diam. Quisque volutpat libero lectus, at iaculis neque tincidunt quis. Donec luctus congue tortor, sit amet pellentesque mauris interdum eget. Sed facilisis lacinia mattis. Aliquam pellentesque tellus id est malesuada, in tristique lectus commodo. Nulla facilisi. Cras ac dolor ullamcorper, volutpat mi in, tincidunt nunc. In hac habitasse platea dictumst. Fusce faucibus eros sed ligula congue eleifend. In aliquam justo lobortis, dapibus dui quis, interdum lacus. Mauris nisi tellus, luctus vel pretium et, egestas vitae ante. Nulla sed risus nec lectus sodales semper. Duis scelerisque viverra quam, id cursus urna maximus at.\n")


def render_io(data):
    with io.StringIO() as out:
        out.truncate(2048)
        out.seek(0)
        out_write = out.write
        render(data, out_write)
        return out.getvalue()


def render_join(data):
    out = []
    out_write = out.append
    render(data, out_write)
    return ''.join(out)
