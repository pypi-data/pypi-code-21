import os

from wpiformat.config import Config
from wpiformat.cidentlist import CIdentList


def test_cidentlist():
    task = CIdentList()

    inputs = []
    outputs = []

    # Main.cpp: signature for C++ function
    inputs.append(("./Main.cpp",
        "int main() {" + os.linesep + \
        "  return 0;" + os.linesep + \
        "}" + os.linesep))
    outputs.append((inputs[len(inputs) - 1][1], False, True))

    # Main.cpp: signature for C function in extern "C" block
    inputs.append(("./Main.cpp",
        "extern \"C\" {" + os.linesep + \
        "int main() {" + os.linesep + \
        "  return 0;" + os.linesep + \
        "}" + os.linesep + \
        "}" + os.linesep))
    outputs.append((
        "extern \"C\" {" + os.linesep + \
        "int main(void) {" + os.linesep + \
        "  return 0;" + os.linesep + \
        "}" + os.linesep + \
        "}" + os.linesep, True, True))

    # Main.cpp: signature for C function marked extern "C"
    inputs.append(("./Main.cpp",
        "extern \"C\" int main() {" + os.linesep + \
        "  return 0;" + os.linesep + \
        "}" + os.linesep))
    outputs.append((
        "extern \"C\" int main(void) {" + os.linesep + \
        "  return 0;" + os.linesep + \
        "}" + os.linesep, True, True))

    # Main.cpp: extern "C++" function nested in extern "C" block
    inputs.append(("./Main.cpp",
        "extern \"C\" {" + os.linesep + \
        "extern \"C++\" int main() {" + os.linesep + \
        "  return 0;" + os.linesep + \
        "}" + os.linesep + \
        "}" + os.linesep))
    outputs.append((inputs[len(inputs) - 1][1], False, True))

    # Main.c: signature for C function
    inputs.append(("./Main.c",
        "int main() {" + os.linesep + \
        "  return 0;" + os.linesep + \
        "}" + os.linesep))
    outputs.append((
        "int main(void) {" + os.linesep + \
        "  return 0;" + os.linesep + \
        "}" + os.linesep, True, True))

    # Main.c: signature for C++ function in extern "C++" block
    inputs.append(("./Main.c",
        "extern \"C++\" {" + os.linesep + \
        "int main() {" + os.linesep + \
        "  return 0;" + os.linesep + \
        "}" + os.linesep + \
        "}" + os.linesep))
    outputs.append((inputs[len(inputs) - 1][1], False, True))

    # Main.c: signature for C++ function marked extern "C++"
    inputs.append(("./Main.c",
        "extern \"C++\" int main() {" + os.linesep + \
        "  return 0;" + os.linesep + \
        "}" + os.linesep))
    outputs.append((inputs[len(inputs) - 1][1], False, True))

    # Main.c: extern "C" function nested in extern "C++" block
    inputs.append(("./Main.c",
        "extern \"C++\" {" + os.linesep + \
        "extern \"C\" int main() {" + os.linesep + \
        "  return 0;" + os.linesep + \
        "}" + os.linesep + \
        "}" + os.linesep))
    outputs.append((
        "extern \"C++\" {" + os.linesep + \
        "extern \"C\" int main(void) {" + os.linesep + \
        "  return 0;" + os.linesep + \
        "}" + os.linesep + \
        "}" + os.linesep, True, True))

    # Don't match function calls
    inputs.append(("./Main.c",
        "int main() {" + os.linesep + \
        "  foo();" + os.linesep + \
        "  return 0;" + os.linesep + \
        "}" + os.linesep))
    outputs.append((
        "int main(void) {" + os.linesep + \
        "  foo();" + os.linesep + \
        "  return 0;" + os.linesep + \
        "}" + os.linesep, True, True))

    # Make sure leaving extern block resets extern language type of
    # parent block
    inputs.append(("./Main.c",
        "extern \"C++\" {" + os.linesep + \
        "extern \"C\" int main() {" + os.linesep + \
        "  return 0;" + os.linesep + \
        "}" + os.linesep + \
        "int func() {" + os.linesep + \
        "  return 0;" + os.linesep + \
        "}" + os.linesep + \
        "}" + os.linesep))
    outputs.append((
        "extern \"C++\" {" + os.linesep + \
        "extern \"C\" int main(void) {" + os.linesep + \
        "  return 0;" + os.linesep + \
        "}" + os.linesep + \
        "int func() {" + os.linesep + \
        "  return 0;" + os.linesep + \
        "}" + os.linesep + \
        "}" + os.linesep, True, True))

    assert len(inputs) == len(outputs)

    config_file = Config(os.path.abspath(os.getcwd()), ".styleguide")
    for i in range(len(inputs)):
        output, file_changed, success = task.run_pipeline(
            config_file, inputs[i][0], inputs[i][1])
        assert output == outputs[i][0]
        assert file_changed == outputs[i][1]
        assert success == outputs[i][2]
