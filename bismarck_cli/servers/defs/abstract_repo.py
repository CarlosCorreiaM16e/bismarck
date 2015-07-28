#! /usr/bin/python

from fabric.context_managers import lcd

from bismarck_cli.utils import term
from bismarck_cli.utils.ui_utils import cli_execute, EX_LOCAL

#----------------------------------------------------------------------
class AbstractRepo( object ):
    tag = '?AbstractRepo?'
    #----------------------------------------------------------------------
    def __init__( self, repos_def, data ):
        self.repos_def = repos_def
#         self.subdomain = subdomain
        self.load_data( data )

    #----------------------------------------------------------------------
    def load_data( self, data ):
#         term.printDebug( data.keys() )
        self.base_folder = data.get( 'base_folder' )
        return data

#     #------------------------------------------------------------------
#     def get_subdomain( self ):
#         return self.subdomain

    #------------------------------------------------------------------
    def get_tagname( self ):
#         if self.subdomain:
#             return self.subdomain
        return self.tag

#     #------------------------------------------------------------------
#     def get_home_folder( self ):
#         srv_ctx = self.repos_def.srv_ctx
#         return self.home_folder % { 'user': srv_ctx.server.user,
#                                     'w3_user': srv_ctx.server.w3_user,
#                                     }

    #------------------------------------------------------------------
    def get_base_folder( self ):
        data = { 'cluster': self.repos_def.cluster.cluster_name }
        return self.base_folder % data

    #------------------------------------------------------------------
    def get_repo( self, app_name ):
        repo = None
        if hasattr( self, 'app_repos' ):
            repo = self.app_repos.get( app_name )
            if not repo:
                repo = self.app_repos.get( '_default' )
        return repo

    #------------------------------------------------------------------
    def get_rel_path( self, app_name ):
        data = { 'home_folder': self.get_home_folder(),
                 'base_folder': self.get_base_folder(),
                 'app_name': app_name,
                 'cluster': self.repos_def.cluster.cluster_name }
        _app = '_default'
#         term.printDebug( 'repo: %s' % repr( _app ) )
        if app_name in self.app_repos:
            _app = app_name
#         term.printDebug( '_app: %s' % repr( _app ) )
#         term.printDebug( 'data: %s' % repr( data ) )
#         term.printDebug( 'repo.app_repos[ %s ].folder: %s' %
#                        (_app, type( self.app_repos[ _app ] )) )
        folder = self.app_repos[ _app ].get_app_repo_folder()
#         term.printDebug( 'folder: %s' % repr( folder ) )
        if folder:
            folder = folder % data
#             term.printDebug( 'folder: %s' % repr( folder ) )
            return folder
        return None

    #------------------------------------------------------------------
    def get_abs_path( self, app_name ):
        home_folder = self.get_home_folder()
        base_folder = self.get_base_folder()
        rel_folder = self.get_rel_path( app_name )
#         term.printDebug( 'rel_folder: %s' % repr( rel_folder ) )
        folder = '%s/%s/%s' % ( home_folder, base_folder, rel_folder )
#         term.printDebug( 'folder: %s' % repr( folder ) )
        return folder

    #------------------------------------------------------------------
    def get_cluster( self, app_name ):
        cluster = self.repos_def.srv_ctx.clusters.get_cluster( app_name=app_name )
        return cluster

    #------------------------------------------------------------------
    def get_vcs_server( self, app_name ):
        cluster = self.repos_def.srv_ctx.clusters.get_cluster( app_name=app_name )
        vcs_server = cluster.vcs_server
        return vcs_server

    #------------------------------------------------------------------
    def refresh_status( self, app_name ):
        srv_ctx = self.get_parent( self.T_ROOT )

        repo = self.get_repo( app_name )
        repo.refresh_status( app_name )

    #------------------------------------------------------------------
    def get_vcs_status( self, app_name, refresh=True ):
        if refresh:
            self.refresh_status( app_name )
        repo = self.get_repo( app_name )
#         term.printDebug( 'repo: %s' % repr( repo ) )
        repo.get_status()

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
#                     from bismarck_cli.servers.status_resumed import HgRepoStatus
#                     self.status = HgRepoStatus( ret.stdout )
#
# #             term.printDebug( 'status: %s' % ret )
#             return ret

    #------------------------------------------------------------------

