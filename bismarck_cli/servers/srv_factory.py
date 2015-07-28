'''
Created on 16/10/2014

@author: carlos
'''

import ast
import os

from bismarck_cli.servers.server_context import ServerContext
from bismarck_cli.utils import term
from bismarck_cli.utils.storage import storagize


#------------------------------------------------------------------
def get_server_def( server_name ):
    sf = ServerFactory( server_name )
    return sf.get_srv_def()

#------------------------------------------------------------------
class ServerFactory( object ):
    #------------------------------------------------------------------
    def __init__( self, server_name ):
        self.server_name = server_name
    #------------------------------------------------------------------
    def get_srv_def( self ):
        srv_file = os.path.expanduser( '~/.m16e/servers/%s.py'
                                       % self.server_name )
        f = open( srv_file )
        text = f.read()
        f.close()
        data = ast.literal_eval( text )
#         term.printDebug( 'data:\n%s' % repr( data ) )
        srv_def = ServerContext( data=storagize( data ) )
        return srv_def

    #------------------------------------------------------------------

#------------------------------------------------------------------


