#! /usr/bin/python


from bismarck_cli.servers.defs.abstract_repo import AbstractRepo
from bismarck_cli.servers.defs.app_repos_def import AppReposDef
from bismarck_cli.utils.storage import Storage


#----------------------------------------------------------------------
class LocalRepoDef( AbstractRepo ):
    '''
    ('repos': { 'local':
    { 'base_folder': 'development/m16e/apps',
      'home_folder': '/home/carlos',
      'app_repos': { '_default': { <AppReposDef> }, },
    }
    '''
    tag = 'local'

    #----------------------------------------------------------------------
    def __init__( self, repos_def, data ):
        super( LocalRepoDef, self ).__init__( repos_def, data )
        self.status = None

    #------------------------------------------------------------------
    def get_home_folder( self ):
        srv_ctx = self.repos_def.srv_ctx
        data = { 'user': srv_ctx.local_server.user }
        return srv_ctx.local_server.home_folder % data

    #----------------------------------------------------------------------
    def load_data( self, data ):
#         term.printDebug( 'data:\n%s' % repr( data ) )
        data = super( LocalRepoDef, self ).load_data( data )
#         term.printDebug( 'data:\n%s' % repr( data ) )

        self.app_repos = Storage()
        a_data = data[ AppReposDef.tag ]
#         term.printDebug( 'a_data:\n%s' % repr( a_data ) )
        for app in a_data:
            r_data = a_data[ app ]
#             term.printDebug( 'r_data:\n%s' % repr( r_data ) )
            self.app_repos[ app ] = AppReposDef( self, r_data, app )

#     #------------------------------------------------------------------
#     def get_vcs_status( self, app_name ):
#         srv_ctx = self.get_parent( self.T_ROOT )
#         cluster = srv_ctx.clusters.get_cluster( app_name=app_name )
#         vcs_server = cluster.vcs_server
#         cmd = vcs_server.get_status_cmd()
#         abs_local_path = self.get_abs_path( app_name )
#         with lcd( abs_local_path ):
#             ret = cli_execute( cmd,
#                                exec_type=EX_LOCAL,
#                                quiet=True )
#             if not ret.stderr:
#                 if vcs_server.vcs_app_name == 'hg':
#                     self.status = HgRepoStatus( ret.stdout )
# #             term.printDebug( 'status: %s' % ret )
#             return ret

    #------------------------------------------------------------------
    def __repr__( self ):
        s = '(%s) {' % self.tag
        s += '\n    home_folder: %s' % self.home_folder
        s += '\n    base_folder: %s' % self.base_folder
        s += '\n    %s: {' % AppReposDef.tag
        for app in self.app_repos:
            ar = self.app_repos[ app ].repos
#             term.printDebug( 'ar:\n%s' % repr( ar ) )
            s += '\n        %s: {' % app
            s += '\n            folder: %s' % repr( ar.folder )
            s += '\n            git_folder: %s' % repr( ar.git_folder )
            s += '\n            hg_folder: %s' % repr( ar.hg_folder )
            s += '\n        }'
        s += '\n    }'
        return s

    #----------------------------------------------------------------------

#----------------------------------------------------------------------
