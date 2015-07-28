#! /usr/bin/python
from fabric.context_managers import settings, cd

from bismarck_cli.servers.defs.abstract_repo import AbstractRepo
from bismarck_cli.servers.defs.app_repos_def import AppReposDef, RT_FOLDER, \
    RT_GIT_FOLDER, RT_HG_FOLDER
from bismarck_cli.utils import term
from bismarck_cli.utils.storage import Storage
from bismarck_cli.utils.ui_utils import cli_execute, EX_SUDO


#----------------------------------------------------------------------
class WebRepoDef( AbstractRepo ):
    tag = 'web_repo'
    '''
    ('repos': { 'web':)
    { 'belmiro': { 'home_folder': '/home/www-data',
                   'base_folder': 'sites/belmiro',
                   'app_repos': { '_default': { <AppReposDef> }, },
                  },
      'take5': { 'home_folder': '/home/www-data',
                 'base_folder': 'sites/take5',
                   'app_repos': { '_default': { <AppReposDef> }, },
                },
      'www': { 'home_folder': '/home/www-data',
               'base_folder': 'sites/www',
                   'app_repos': { '_default': { <AppReposDef> }, },
                },
    },

    '''
    tag = 'web'

    def __init__( self, repos_def, data ):
        super( WebRepoDef, self ).__init__( repos_def, data )
        self.load_data( data )

    #------------------------------------------------------------------
    def get_home_folder( self ):
        srv_ctx = self.repos_def.srv_ctx
        data = { 'user': srv_ctx.server.user,
                 'w3_user': srv_ctx.server.w3_user,
                 }
        return srv_ctx.server.web_home_folder % data

    #----------------------------------------------------------------------
    def load_data( self, data ):
        data = super( WebRepoDef, self ).load_data( data )
        a_data = data[ AppReposDef.tag ]
        self.app_repos = Storage()
#         term.printDebug( 'a_data (%s):\n%s'
#                          % (self.subdomain, repr( a_data )) )
        for app in a_data:
            r_data = a_data[ app ]
#             term.printDebug( 'r_data:\n%s' % repr( r_data ) )
            self.app_repos[ app ] = AppReposDef( self, r_data, app )

#         term.printDebug( 'self:\n%s' % repr( self ) )

    #----------------------------------------------------------------------
    def get_app_folder( self, app_name, folder_type=None ):
        ap_name = app_name
        if not ap_name in self.app_repos:
            ap_name = '_default'
        app_repos = self.app_repos[ ap_name ]
        app_folder = app_repos.get_app_repo_folder( folder_type )
        return app_folder

    #------------------------------------------------------------------
    def get_vcs_status( self, app_name ):
        srv_def = self.get_parent( self.T_ROOT )
        cluster = srv_def.clusters.get_cluster( app_name=app_name )
        vcs_server = cluster.vcs_server
        cmd = vcs_server.get_status_cmd()
        abs_web_path = self.get_abs_path( app_name )
        with settings( host_string=srv_def.server.get_user_host_string() ):
            with cd( abs_web_path ):
                ret = cli_execute( cmd,
                                   user=srv_def.server.w3_user,
                                   password=srv_def.server.password,
                                   exec_type=EX_SUDO,
                                   quiet=True )
#             term.printDebug( 'status: %s' % ret )
            return ret

    #------------------------------------------------------------------
    def __repr__( self ):
        s = '%s: {' % self.get_tagname()
        s += '\n        home_folder: %s' % self.get_home_folder()
        s += '\n        base_folder: %s' % self.get_base_folder()
        s += '\n    app_repos: {'
        for ar in self.app_repos:
            s += '\n        %s: {' % ar
            arr = self.app_repos[ ar ]
            folder = arr.get_app_repo_folder( RT_FOLDER )
            hg_folder = arr.get_app_repo_folder( RT_HG_FOLDER )
            git_folder = arr.get_app_repo_folder( RT_GIT_FOLDER )
            s += '\n            folder: %s' % arr.get_app_repo_folder( RT_FOLDER )
            s += '\n            git_folder: %s' % arr.get_app_repo_folder( RT_GIT_FOLDER )
            s += '\n            hg_folder: %s' % arr.get_app_repo_folder( RT_HG_FOLDER )
            s += '\n      }'

        s += '\n  }'
        return s

#     #------------------------------------------------------------------
#     def get_web_cluster( self, app_name ):
#         srv_def = self.repos_def.srv_ctx
# #         term.printDebug( 'app_name: %s' % repr( app_name ) )
#         cluster_name = srv_def.clusters.get_cluster_name( app_name=app_name )
# #         term.printDebug( 'cluster_name: %s' % repr( cluster_name ) )
#         cluster = self.w_repos.get( cluster_name )
# #         term.printDebug( 'cluster: %s' % repr( cluster ) )
#         return cluster

#     #------------------------------------------------------------------
#     def get_repo( self, app_name ):
#         srv_def = self.get_parent( self.T_ROOT )
#         cluster_name = srv_def.clusters.get_cluster_name( app_name=app_name )
#         return self.w_repos.get( cluster_name )
#
#         if cluster_name in self.w_repos:
#             return self.w_repos[ cluster_name ]
#         return None


#----------------------------------------------------------------------
