import os
from inspect import FrameInfo

from hues import huestr

from amino import Boolean, IO, List, Try, __, Lists, _, Path, L
from amino.boolean import false, true

from kallikrein.match_result import SuccessMatchResult
from kallikrein.util.string import indent
from kallikrein.run.line import SpecLine
from kallikrein.expectation import (ExpectationResult, ExpectationFailed, SingleExpectation, SingleExpectationResult,
                                    Expectation)


def location_info(file: Path, func: str, stack: List[FrameInfo]) -> List[str]:
    fname = str(file)
    def failure_location(frame: FrameInfo) -> bool:
        return frame.filename == fname and frame.function == func
    def failure_location_file(frame: FrameInfo) -> bool:
        return frame.filename == fname
    def format_code(code: str) -> str:
        return f' {huestr(code.strip()).blue.colorized}'
    def format_location(frame: FrameInfo) -> List[str]:
        path = Try(file.relative_to, os.getcwd()) | file
        col_path = huestr(str(path)).magenta.colorized
        lnum = huestr(str(frame.lineno)).magenta.colorized
        code = Lists.wrap(frame.code_context).head / format_code
        return List(f'{col_path}:{lnum}').cat_m(code)
    return stack.find(failure_location).o(lambda: stack.find(failure_location_file)) / format_location | List()


class FailedUnsafeSpecResult(ExpectationResult):

    def __init__(self, line: SpecLine, error: ExpectationFailed) -> None:
        self.line = line
        self.error = error

    @property
    def success(self) -> Boolean:
        return false

    @property
    def report_lines(self) -> List[str]:
        loc = self.line.location.file / L(location_info)(_, self.line.name, self.error.stack) | List()
        return indent(loc + self.error.report).cons('unsafe spec failed:')


class UnsafeExpectationResult(ExpectationResult):

    @property
    def success(self) -> Boolean:
        return true

    @property
    def report_lines(self) -> List[str]:
        return List('unsafe spec succeeded')


unsafe_expectation_result = UnsafeExpectationResult()


class UnsafeExpectation(SingleExpectation):

    @property
    def evaluate(self) -> IO[ExpectationResult]:
        return IO.now(SingleExpectationResult(self, SuccessMatchResult()))


class FailedUnsafeSpec(Expectation):

    def __init__(self, line: SpecLine, error: ExpectationFailed) -> None:
        self.line = line
        self.error = error

    @property
    def evaluate(self) -> IO[ExpectationResult]:
        return IO.now(FailedUnsafeSpecResult(self.line, self.error))


__all__ = ('FailedUnsafeSpecResult', 'UnsafeExpectation', 'FailedUnsafeSpec', 'unsafe_expectation_result')
