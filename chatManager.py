from itertools import izip_longest
import curses
from log import log

class ChatManager():
    def __init__(self, chatDisplayWindow, chatEntryLine, colorDict):
        self.chatEntryLine = chatEntryLine
        self.chatDisplayWindow = chatDisplayWindow
        self.COLOR = curses.color_pair(colorDict[(curses.COLOR_WHITE, curses.COLOR_MAGENTA)])
        self.chatDisplayLines, self.width = chatDisplayWindow.getmaxyx()
        self.chatMessages = []
        self.updateChatDisplay()
        self.chatCompose = []
        self.ESCAPE_KEY = 27
        self.RETURN_KEY = 10
        self.PRINTABLE_MIN = 32
        self.PRINTABLE_MAX = 127

    def updateChatDisplay(self):
        self.chatDisplayWindow.erase()
        for y, msg in izip_longest(range(self.chatDisplayLines), self.chatMessages[-self.chatDisplayLines:], fillvalue=""):
            try:
                self.chatDisplayWindow.addstr(y, 0, msg + " " * (self.width - len(msg)), self.COLOR)
            except curses.error:
                pass
        self.chatDisplayWindow.refresh()

    def newChatMessage(self, msg):
        #todo provide way to view old messages, or trim array
        self.chatMessages.append(msg)
        self.updateChatDisplay()


    def _displayChatCursor(self):
        try:
            # erase old char after backspace
            self.chatEntryLine.addch(0, len(self.chatCompose)+1, " ")
        except curses.error:
            pass
        try:
            self.chatEntryLine.addch(0, len(self.chatCompose), "_", curses.A_BLINK | curses.A_REVERSE)
        except curses.error:
            pass

    # retunrs (chat still in progress T/F, msg)
    def newChatCharInput(self, char_in_num):

        log("(CHAT IN) %d\n"%char_in_num)

        if char_in_num == self.ESCAPE_KEY:
            self.chatCompose = []
            self.chatEntryLine.erase()
            self.chatEntryLine.refresh()
            return False, None

        if char_in_num == curses.KEY_ENTER or char_in_num == self.RETURN_KEY:
            self.chatCompose.append("\n")
            msg = "".join(self.chatCompose)
            self.chatCompose = []
            self.chatEntryLine.erase()
            self.chatEntryLine.refresh()
            return False, (msg if len(msg) > 2 else None)

        if char_in_num == curses.KEY_BACKSPACE:
            self.chatCompose.pop()
            if len(self.chatCompose):
                self._displayChatCursor()
            else:
                self.chatEntryLine.erase()
            self.chatEntryLine.refresh()
            #exit chat if all characters deleted
            return len(self.chatCompose) > 0, None

        if self.PRINTABLE_MIN <= char_in_num <= self.PRINTABLE_MAX and len(self.chatCompose) < self.width-1:
            self.chatCompose.append(chr(char_in_num))
            try:
                self.chatEntryLine.addch(0, len(self.chatCompose)-1, chr(char_in_num))
                self._displayChatCursor()
            except curses.error:
                pass
            self.chatEntryLine.refresh()

        return True, None
