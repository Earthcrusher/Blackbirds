# ANSI definitions

ANSI_BEEP = "\07"
ANSI_ESCAPE = "\033"
ANSI_NORMAL = "\033[0m"

ANSI_UNDERLINE = "\033[4m"
ANSI_HILITE = "\033[1m"
ANSI_UNHILITE = "\033[22m"
ANSI_BLINK = "\033[5m"
ANSI_INVERSE = "\033[7m"
ANSI_INV_HILITE = "\033[1;7m"
ANSI_INV_BLINK = "\033[7;5m"
ANSI_BLINK_HILITE = "\033[1;5m"
ANSI_INV_BLINK_HILITE = "\033[1;5;7m"

# Foreground colors
ANSI_BLACK = "\033[30m"
ANSI_RED = "\033[31m"
ANSI_GREEN = "\033[32m"
ANSI_YELLOW = "\033[33m"
ANSI_BLUE = "\033[34m"
ANSI_MAGENTA = "\033[35m"
ANSI_CYAN = "\033[36m"
ANSI_WHITE = "\033[37m"

# Background colors
ANSI_BACK_BLACK = "\033[40m"
ANSI_BACK_RED = "\033[41m"
ANSI_BACK_GREEN = "\033[42m"
ANSI_BACK_YELLOW = "\033[43m"
ANSI_BACK_BLUE = "\033[44m"
ANSI_BACK_MAGENTA = "\033[45m"
ANSI_BACK_CYAN = "\033[46m"
ANSI_BACK_WHITE = "\033[47m"

# Formatting Characters
ANSI_RETURN = "\r\n"
ANSI_TAB = "\t"
ANSI_SPACE = " "

# Escapes
ANSI_ESCAPES = ("{{", "\\\\", "\|\|")

# Blackbirds color definitions.
A_GREY = ANSI_UNHILITE + ANSI_WHITE
A_WHITE = ANSI_HILITE + ANSI_WHITE
A_BLUE = ANSI_HILITE + ANSI_BLUE
A_CYAN = ANSI_HILITE + ANSI_CYAN
A_RED = ANSI_HILITE + ANSI_RED
A_MAGENTA = ANSI_HILITE + ANSI_MAGENTA
A_GREEN = ANSI_HILITE + ANSI_GREEN
A_YELLOW = ANSI_HILITE + ANSI_YELLOW
A_DARKGREY = ANSI_HILITE + ANSI_BLACK
A_DARKBLUE = ANSI_UNHILITE + ANSI_BLUE
A_DARKCYAN = ANSI_UNHILITE + ANSI_CYAN
A_DARKRED = ANSI_UNHILITE + ANSI_RED
A_DARKMAGENTA = ANSI_UNHILITE + ANSI_MAGENTA
A_DARKGREEN = ANSI_UNHILITE + ANSI_GREEN
A_DARKYELLOW = ANSI_UNHILITE + ANSI_YELLOW
A_BROWN = ANSI_UNHILITE + ANSI_YELLOW

# XTERM name definitions.