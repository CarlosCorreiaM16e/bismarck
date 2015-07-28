import inspect
import os
import sys

#----------------------------------------------------------------------
class AnsiPrint( object ):
    FG_BLACK = "\033[30m"
    FG_BLUE = "\033[34m"
    FG_GREEN = "\033[32m"
    FG_CYAN = "\033[36m"
    FG_RED = "\033[31m"
    FG_MAGENTA = "\033[35m"
    FG_YELLOW = "\033[33m"
    FG_DARK_GRAY = "\033[1;30m"

    RESET = "\033[0m"

    def __init__( self, color ):
        self.color = color

    #----------------------------------------------------------------------
    def getColoredText( self, text ):
        return self.color + text + self.RESET

#----------------------------------------------------------------------
def getTerminalSize():
    rows, columns = os.popen( 'stty size', 'r' ).read().split()
    return ( int( rows ), int( columns ) )

#----------------------------------------------------------------------
def printLine( text, color = None ):
    if color:
        text = color + text + AnsiPrint.RESET
    print text

#----------------------------------------------------------------------
def printLog( text ):
    cwd = os.getcwd()
    stack = inspect.stack()[1]
    dir = stack[1]
    if dir.startswith( os.getenv( 'HOME' ) ):
        dir = dir[ len( cwd ) + 1 : ]
    text = "*** in %s:%d:\n%s\n" % (dir, stack[2], text)
    print text

#----------------------------------------------------------------------
def printDebug( text ):
    cwd = os.getcwd()
    stack = inspect.stack()[1]
    dir = stack[1]
    if dir.startswith( os.getenv( 'HOME' ) ):
        dir = dir[ len( cwd ) + 1 : ]
    text = "*** in %s:%d:\n%s\n" % (dir, stack[2], text )
#     text = "%s*** in %s:%d:\n%s%s\n" % (
#         AnsiPrint.FG_MAGENTA, dir, stack[2], text, AnsiPrint.RESET )
    print text

#----------------------------------------------------------------------
def printWarn( text ):
    cwd = os.getcwd()
    stack = inspect.stack()[2]
    dir = stack[1]
    if dir.startswith( os.getenv( 'HOME' ) ):
        dir = dir[ len( cwd ) + 1 : ]
    text = "%s*** in %s:%d:\n%s%s" % (
        AnsiPrint.FG_RED, dir, stack[2], text, AnsiPrint.RESET )
    print text

#----------------------------------------------------------------------
def printDeprecated( text ):
    cwd = os.getcwd()
    stack = inspect.stack()[2]
    dir = stack[1]
    if dir.startswith( os.getenv( 'HOME' ) ):
        dir = dir[ len( cwd ) + 1 : ]
    text = "%s!!! DEPRECATION in %s:%d: %s%s" % (
        AnsiPrint.FG_RED, dir, stack[2], text, AnsiPrint.RESET )
    print text

#----------------------------------------------------------------------
def formatStorage( st, indent = '' ):
    if isinstance( st, dict ):
        text = indent + '{\n'
        indent += '    '
        first = True
        for k in st.keys():
            v = st[k]
#            printLog( 'v:' + repr( v ) )
            if v and repr( v ).startswith( '<' ):
                continue
            if first:
                first = False
            else:
                text += ',\n'
            text += indent + k + ': ' + formatStorage( v, indent )
        text += '\n'
        text += indent + '}\n'
        return text
    else:
        print 'not dict'
    return str( st )

#----------------------------------------------------------------------
def printLogStorage( storage ):
    text = formatStorage( storage )
    stack = inspect.stack()[1]
    text = "*** in %s:%d:\n%s" % (stack[1], stack[2], text)
    print text

#----------------------------------------------------------------------
def printLogDict( d, indent = 0, dictName = '' ):
    cwd = os.getcwd()
    stack = inspect.stack()[1]
    dir = stack[1]
    if dir.startswith( os.getenv( 'HOME' ) ):
        dir = dir[ len( cwd ) + 1 : ]
    text = "*** in %s:%d:" % (dir, stack[2] )
    print text
    print( 'dictName: %s' % dictName )
    printDict( d, indent )

#----------------------------------------------------------------------
def printDict( d, indent = 0 ):
    iStr = '    ' * indent
    kList = d.keys()
    for k in kList:
        print k
        val = d[k]
        if isinstance( val, dict ):
            print '%s%s:' % (iStr, k, )
            printDict( val, indent + 1 )
        else:
            print '%s%s: %s' % (iStr, k, repr( val ))

#----------------------------------------------------------------------
def printChars( text, color = None ):
    if color:
        text = color + text + AnsiPrint.RESET
    sys.stdout.write( text )
    sys.stdout.flush()

#----------------------------------------------------------------------
if __name__ == "__main__":
    printDebug( 'ola' )
