#! /usr/bin/python
from bismarck_cli.utils import term


#----------------------------------------------------------------------
class ReposDef( object ):
    '''
    'repos': { 'local': { <LocalRepoDef },
               'remote': { <RemoteRepoDef> },
               'web': { <WebRepoDef> },
              },
    '''
    tag = 'repos'
    #----------------------------------------------------------------------
    def __init__( self, srv_ctx, cluster, data ):
        self.srv_ctx = srv_ctx
        self.cluster = cluster
        self.local = None
        self.remote = None
        self.web = None
        self.load_data( data )
#         term.printDebug( 'self.local:\n%s' % repr( self.local ) )
#         term.printDebug( 'self.remote:\n%s' % repr( self.remote ) )
#         term.printDebug( 'self.web:\n%s' % repr( self.web ) )

    #----------------------------------------------------------------------
    def load_data( self, data ):
        from bismarck_cli.servers.defs.repos_local_def import LocalRepoDef
        from bismarck_cli.servers.defs.repos_remote_def import RemoteRepoDef
        from bismarck_cli.servers.defs.repos_web_def import WebRepoDef
#         term.printDebug( 'data.keys():\n%s' % repr( data.keys() ) )
#         term.printDebug( 'self:\n%s' % repr( self ) )
        if self.tag in data:
            data = data[ self.tag ]
#         term.printDebug( 'data.keys():\n%s' % repr( data.keys() ) )
#         term.printDebug( 'data:\n%s' % repr( data ) )
        l_data = data.get( LocalRepoDef.tag )
#         term.printDebug( 'l_data.keys():\n%s' % repr( l_data.keys() ) )
#         term.printDebug( 'l_data:\n%s' % repr( l_data ) )
        if l_data:
            self.local = LocalRepoDef( self, l_data )
#             term.printDebug( 'local:\n%s' % repr( self.local ) )

        r_data = data.get( RemoteRepoDef.tag )
#         term.printDebug( 'r_data.keys():\n%s' % repr( r_data.keys() ) )
#         term.printDebug( 'r_data:\n%s' % repr( r_data ) )
        if r_data:
            self.remote = RemoteRepoDef( self, r_data )
#             term.printDebug( 'remote:\n%s' % repr( self.remote ) )

        w_data = data.get( WebRepoDef.tag )
#         term.printDebug( 'w_data.keys():\n%s' % repr( w_data.keys() ) )
#         term.printDebug( 'w_data:\n%s' % repr( w_data ) )
        if w_data:
            self.web = WebRepoDef( self, w_data )
#             term.printDebug( 'web:\n%s' % repr( self.web ) )

#         term.printDebug( 'self.local:\n%s' % repr( self.local ) )
#         term.printDebug( 'self.remote:\n%s' % repr( self.remote ) )
#         term.printDebug( 'self.web:\n%s' % repr( self.web ) )

    #------------------------------------------------------------------
    def get_repo( self, repo_type ):
        from bismarck_cli.servers.defs.repos_local_def import LocalRepoDef
        from bismarck_cli.servers.defs.repos_remote_def import RemoteRepoDef
        from bismarck_cli.servers.defs.repos_web_def import WebRepoDef
        if repo_type == LocalRepoDef.tag:
            return self.get_local_repo()
        elif repo_type == RemoteRepoDef.tag:
            return self.get_remote_repo()
        elif repo_type == WebRepoDef.tag:
            return self.get_web_repo()
        raise Exception( 'UNKNOWN REPO TYPE: %s' % repr( repo_type ) )

    #------------------------------------------------------------------
    def get_local_repo( self ):
        return self.local

    #------------------------------------------------------------------
    def get_remote_repo( self ):
        return self.remote

    #------------------------------------------------------------------
    def get_web_repo( self ):
#         term.printDebug( 'repo_name: %s' % repo_name )
#         term.printDebug( 'web_repos.keys: %s' % repr( self.web.w_repos.keys() ) )
        return self.web

    #------------------------------------------------------------------
    def get_def_repos( self,
                       repo_type='local' ):
        if repo_type == 'local':
            return self.local
        if repo_type == 'remote':
            return self.remote
        if repo_type == 'web':
            return self.web
        return None

    #------------------------------------------------------------------
    def __repr__( self ):
        s = '(%s) {' % self.tag
        s += '\n    local: %s' % repr( self.local )
        s += '\n    remote: %s' % repr( self.remote )
        s += '\n    web: %s' % repr( self.web )
        s += '\n    }'
        return s
    #----------------------------------------------------------------------

#----------------------------------------------------------------------
