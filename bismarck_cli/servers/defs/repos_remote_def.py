#! /usr/bin/python

from fabric.context_managers import cd, settings

from bismarck_cli.servers.defs.abstract_repo import AbstractRepo
from bismarck_cli.servers.defs.app_repos_def import AppReposDef
from bismarck_cli.utils import term
from bismarck_cli.utils.storage import Storage
from bismarck_cli.utils.ui_utils import cli_run, cli_execute, EX_RUN

#----------------------------------------------------------------------
class RemoteRepoDef( AbstractRepo ):
    '''
    ('repos': { 'remote':)
    { 'base_folder': 'git/apps/www',
      'home_folder': '/home/carlos',
      'app_repos': { '_default': { <AppReposDef> },
                    },
    }
    '''
    tag = 'remote'

    #----------------------------------------------------------------------
    def __init__( self, repos_def, data ):
        super( RemoteRepoDef, self ).__init__( repos_def, data )
        self.status = None

    #------------------------------------------------------------------
    def get_home_folder( self ):
        srv_ctx = self.repos_def.srv_ctx
        data = { 'user': srv_ctx.server.user,
                 'w3_user': srv_ctx.server.w3_user,
                 }
        return srv_ctx.server.remote_home_folder % data

    #----------------------------------------------------------------------
    def load_data( self, data ):
#         term.printDebug( data.keys() )
        data = super( RemoteRepoDef, self ).load_data( data )
#         term.printDebug( data.keys() )
        self.app_repos = Storage()
        a_data = data[ AppReposDef.tag ]
#         term.printDebug( 'a_data:\n%s' % repr( a_data ) )
        for app in a_data:
            r_data = a_data[ app ]
#             term.printDebug( 'r_data:\n%s' % repr( r_data ) )
            self.app_repos[ app ] = AppReposDef( self, r_data, app )

    #------------------------------------------------------------------
    def get_vcs_status( self, app_name ):
        srv_def = self.get_parent( self.T_ROOT )
        cluster = srv_def.clusters.get_cluster( app_name=app_name )
        vcs_server = cluster.vcs_server
        cmd = vcs_server.get_status_cmd()
        abs_remote_path = self.get_abs_path( app_name )
        with settings( host_string=srv_def.server.get_user_host_string() ):
            with cd( abs_remote_path ):
                ret = cli_execute( cmd,
                                   exec_type=EX_RUN,
                                   quiet=True )
                return ret

    #------------------------------------------------------------------
    def __repr__( self ):
        s = '%s: {' % self.tag
        s += '\n    home_folder: %s' % self.home_folder
        s += '\n    base_folder: %s' % self.base_folder
        s += '\n    %s: {' % AppReposDef.tag
        for app in self.app_repos:
            ar = self.app_repos[ app ].repos
            s += '\n        %s: {' % app
            s += '\n            folder: %s' % repr( ar.folder )
            s += '\n            git_folder: %s' % repr( ar.git_folder )
            s += '\n            hg_folder: %s' % repr( ar.hg_folder )
            s += '\n        }'
        s += '\n    }'
        return s

    #----------------------------------------------------------------------

#----------------------------------------------------------------------
