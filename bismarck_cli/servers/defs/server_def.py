#! /usr/bin/python

from bismarck_cli.utils.storage import Storage

#----------------------------------------------------------------------
class ServerDef( object ):
    '''
        'server': { 'name': 'take5',
                    'host': 'belmiro',
                    'port': 22,
                    'user': 'carlos',
                    'db_user': 'belmiro',
                    'w3_user': 'www-data',
                    'password': 'zecuPsalif45',
                    },
    '''

    tag = 'server'

    #----------------------------------------------------------------------
    def __init__( self, srv_ctx, data ):
        self.srv_ctx = srv_ctx
        self.load_data( data )

    #----------------------------------------------------------------------
    def load_data( self, data ):
        if self.tag in data:
            data = data[ self.tag ]
        self.name = data.get( 'name' )
        self.host = data.get( 'host' )
        self.port = int( data.get( 'port' ) or 22 )
        self.user = data.get( 'user' )
        self.db_user = data.get( 'db_user' )
        self.w3_user = data.get( 'w3_user' )
        self.password = data.get( 'password' )
        self.backup_remote = data.get( 'backup_remote' )
        self.backup_local = data.get( 'backup_local' )
        self.backup_prefix = data.get( 'backup_prefix' )
        self.remote_home_folder = data.get( 'remote_home_folder' )
        self.web_home_folder = data.get( 'web_home_folder' )

    #----------------------------------------------------------------------
    def get_user_host_string( self ):
        return '%s@%s' % ( self.user, self.host )

    #----------------------------------------------------------------------
    def get_web_host_string( self ):
        return '%s@%s' % ( self.w3_user, self.host )

#     #------------------------------------------------------------------
#     def __repr__( self ):
#         s = 'ServerDef: {'
#         for a in self.__dict__:
#             if a == 'parent':
#                 continue
#             s += '\n    %s: %s' % (repr( a ), repr( self.__dict__[a] ) )
#         s += '\n  }'
#         return s

    #------------------------------------------------------------------
