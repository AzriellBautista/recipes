import ctypes
import enum


# https://learn.microsoft.com/en-us/windows/win32/api/winuser/nf-winuser-messageboxa


class Button(enum.IntEnum):
    OK = 0x0
    OKCANCEL = 0x1
    ABORTRETRYIGNORE = 0x2
    YESNOCANCEL = 0x3
    YESNO = 0x4
    RETRYCANCEL = 0x5
    CANCELTRYCONTINUE = 0x6
    HELP = 0x4000


class Icon(enum.IntEnum):
    STOP = 0x10
    ERROR = 0x10
    HAND = 0x10
    QUESTION = 0x20
    EXCLAMATION = 0x30
    WARNING = 0x30
    INFORMATION = 0x40
    ASTERISK = 0x40


class DefaultButton(enum.IntEnum):
    BUTTON1 = 0x0
    BUTTON2 = 0x100
    BUTTON3 = 0x200
    BUTTON4 = 0x300


class Modality(enum.IntEnum):
    APPLICATION = 0x0
    SYSTEM = 0x1000
    TASK = 0x2000


class OtherOption(enum.IntEnum):
    DEFAULTDESKTOPONLY = 0x20000
    RIGHTALIGN = 0x80000
    RTLREADING = 0x100000
    SETFOREGROUND = 0x10000
    TOPMOST = 0x40000
    SERVICENOTIFICATION = 0x20000


class ReturnValue(enum.IntEnum):
    ABORT = 3
    CANCEL = 6
    CONTINUE = 11
    IGNORE = 5
    NO = 7
    OK = 1
    RETRY = 4
    TRYAGAIN = 10
    YES = 2


def show_message_box(
    message: str = "",
    title: str = "",
    flags: int = 0,
) -> int:
    return ctypes.windll.user32.MessageBoxW(0, message, title, flags)


if __name__ == "__main__":
    # * Example Usage:
    print(show_message_box(
        r"""Your code sucks. Would you like to delete "C:\Windows\System32"?""", 
        "Visual Studio Code", 
        Icon.ERROR | Button.YESNO | DefaultButton.BUTTON2 | OtherOption.TOPMOST
    ))
