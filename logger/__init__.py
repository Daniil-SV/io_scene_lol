from enum import IntEnum
import sys

class MessageLevel(IntEnum):
    Default = 0
    FatalError = 1


class Logger:
    @staticmethod
    def execute(name: str):
        print("\n\n---------------------- LoL Formats Addon Log ----------------------")
        print(f"Execute target: {name}")

    @staticmethod
    def final():
        print("\n---------------------- End ----------------------")

    @staticmethod
    def info(txt: str, level: MessageLevel = MessageLevel.Default):
        typename = "LOG"
        if (level == MessageLevel.FatalError):
            typename = "ERROR"

        print(f"[{typename}] {txt}")

    @staticmethod
    def progress(message: str, value: any, is_final: bool = False):
        sys.stdout.write('\r')
        delim = '\n' if is_final else ''
        sys.stdout.write(f"[PROGRESS] {message}: {value} {delim}")
        sys.stdout.flush()