#! /usr/bin/python

from bismarck_cli.utils import term

#----------------------------------------------------------------------
class ServerContext( object ):
    '''
{
    'local_server': { 'host': 'zappa.clientes.m16e.com',
                      'port': 22016,
                      'user': 'carlos',
                      },
    'server': { <ServerDef> },
     'web2py': { 'repo': 'https://code.google.com/p/web2py',
                  'release': 'R-2.9.11',
                  },
    'clusters': { <ClustersDef>
                    'repos': { <ReposDef> },
    },

    '''
#     tag = 'root'

    #----------------------------------------------------------------------
    def __init__( self, data={} ):
        self.load_data( data )

    #----------------------------------------------------------------------
    def load_data( self, data ):
        from bismarck_cli.servers.defs.clusters_def import ClustersDef
        from bismarck_cli.servers.defs.repos_def import ReposDef
        from bismarck_cli.servers.defs.server_def import ServerDef
#         term.printDebug( 'data:\n%s' % repr( data ) )
        self.local_server = data.local_server
#         self.databases = data.databases
#         self.app_dict = data.app_dict
        self.web2py = data.web2py

        self.server = ServerDef( self, data )
#         term.printDebug( 'server:\n%s' % repr( self.server ) )
#         self.repos = ReposDef( self, data )
#         term.printDebug( 'repos:\n%s' % repr( self.repos ) )

        self.clusters = ClustersDef( self, data )
#         term.printDebug( 'hanlers:\n%s' % repr( self.clusters ) )
#         term.printDebug( 'self:\n%s' % repr( self ) )

#     #----------------------------------------------------------------------
#     def get_app_web_name( self, app_name ):
#         a_name = self.app_dict.get( app_name )
# #         term.printDebug( 'a_name: %s' % repr( a_name ) )
#         if a_name:
#             return a_name[ 'name' ]
#         return None

    #----------------------------------------------------------------------
    def get_rel_app_folder( self, repo, app_name ):
        app_web_name = self.get_app_web_name( app_name )
        return repo.local.get_rel_path( app_name, app_web_name )
#
#         data = { 'home_folder': repo.home_folder,
#                  'base_folder': repo.base_folder,
#                  'app_name': app_name }
#         _app = '_default'
# #         term.printLog( 'repo: %s' % repr( _app ) )
#         if app_name in repo.app_repos:
#             _app = app_name
# #         term.printDebug( '_app: %s' % repr( _app ) )
# #         term.printLog( 'data: %s' % repr( data ) )
# #         term.printLog( 'repo.app_repos[ _app ].folder: %s' % repr( repo.app_repos[ _app ].folder ) )
#         folder = repo.app_repos[ _app ].get_folder() % data
# #         term.printLog( 'folder: %s' % repr( folder ) )
#         return folder

#     #----------------------------------------------------------------------
#     def get_abs_repo_folder( self, app_name ):
#         if not app_name in self.app_list:
#             raise Exception( 'UNKNOWN APP: %s' % app_name )
#         data = { 'home_folder': self.repo.home_folder,
#                  'base_folder': self.get_rel_app_folder( self.repo,
#                                                          app_name ) }
#         folder = '%(home_folder)s/%(base_folder)s' % data
# #         term.printLog( 'folder: %s' % repr( folder ) )
#         return folder

    #----------------------------------------------------------------------
    # home_folder
    #----------------------------------------------------------------------
    def get_local_home_folder( self ):
        data = { 'user': self.local_server.user }
        return self.local_server.home_folder % data

    #----------------------------------------------------------------------
    def get_remote_home_folder( self ):
        data = { 'user': self.server.user,
                 'w3_user': self.server.w3_user,
                 }
        return self.server.remote_home_folder % data

    #----------------------------------------------------------------------
    def get_web_home_folder( self ):
        data = { 'user': self.server.user,
                 'w3_user': self.server.w3_user,
                 }
        return self.server.web_home_folder % data

    #----------------------------------------------------------------------
    # base_folder
    #----------------------------------------------------------------------
    def get_local_base_folder( self, cluster_name ):
        cluster = self.clusters.get_cluster( cluster_name )
        repo = cluster.repos.get_local_repo()
        folder = repo.get_base_folder()
        return folder

    #----------------------------------------------------------------------
    def get_remote_base_folder( self, cluster_name ):
        cluster = self.clusters.get_cluster( cluster_name )
        repo = cluster.repos.get_remote_repo()
        folder = repo.get_base_folder()
        return folder

    #----------------------------------------------------------------------
    def get_web_base_folder( self, cluster_name ):
        cluster = self.clusters.get_cluster( cluster_name )
        repo = cluster.repos.get_web_repo()
        folder = repo.get_base_folder()
        return folder

    #----------------------------------------------------------------------
    # rel_foldero
    #----------------------------------------------------------------------
    def get_rel_local_folder( self, cluster_name, app_name ):
#         if not app_name in self.app_dict:
#             raise Exception( 'UNKNOWN APP: %s' % app_name )
        cluster = self.clusters.get_cluster( cluster_name )
        repo = cluster.repos.get_local_repo()
        folder = repo.get_rel_path( app_name )
        return folder

    #----------------------------------------------------------------------
    def get_rel_remote_folder( self, cluster_name, app_name ):
#         if not app_name in self.app_dict:
#             raise Exception( 'UNKNOWN APP: %s' % app_name )
        cluster = self.clusters.get_cluster( cluster_name )
        repo = cluster.repos.get_remote_repo()
        folder = repo.get_rel_path( app_name )
        return folder

    #----------------------------------------------------------------------
    def get_rel_web_folder( self, cluster_name, app_name ):
#         if not app_name in self.app_dict:
#             raise Exception( 'UNKNOWN APP: %s' % app_name )
        cluster = self.clusters.get_cluster( cluster_name )
        repo = cluster.repos.get_web_repo()
        folder = repo.get_rel_path( app_name )
        return folder

    #----------------------------------------------------------------------
    # abs_foldero
    #----------------------------------------------------------------------
    def get_abs_local_folder( self, cluster_name, app_name ):
#         if not app_name in self.app_dict:
#             raise Exception( 'UNKNOWN APP: %s' % app_name )
#         term.printDebug( 'self.repos.local: %s' % repr( self.repos.local ) )
        cluster = self.clusters.get_cluster( cluster_name )
        repo = cluster.repos.get_local_repo()
        folder = repo.get_abs_path( app_name )
        return folder

    #----------------------------------------------------------------------
    def get_abs_remote_folder( self, cluster_name, app_name ):
#         if not app_name in self.app_dict:
#             raise Exception( 'UNKNOWN APP: %s' % app_name )
#         term.printDebug( 'self.repos.remote: %s' % repr( self.repos.remote ) )
        cluster = self.clusters.get_cluster( cluster_name )
        repo = cluster.repos.get_remote_repo()
        folder = repo.get_abs_path( app_name )
        return folder

    #----------------------------------------------------------------------
    def get_web_repo( self, cluster_name ):
        cluster = self.clusters.get_cluster( cluster_name )
        repo = cluster.repos.get_web_repo()
        return repo

    #----------------------------------------------------------------------
    def get_abs_web_folder( self, cluster_name, app_name ):
#         if not app_name in self.app_dict:
#             raise Exception( 'UNKNOWN APP: %s' % app_name )
#         term.printDebug( 'self.repos.web: %s' % repr( self.repos.web ) )
        cluster = self.clusters.get_cluster( cluster_name )
        repo = cluster.repos.get_web_repo()
        folder = repo.get_abs_path( app_name )
        return folder

    #----------------------------------------------------------------------
    def get_abs_w2p_folder( self, cluster_name ):
        cluster = self.clusters.get_cluster( cluster_name )
        web_repo = self.get_web_repo( cluster_name )
        term.printDebug( 'web_repo: %s' % repr( web_repo ) )
        if not web_repo:
            return 'No cluster defined or empty (no apps)'

        home_folder = web_repo.get_home_folder()
        base_folder = web_repo.get_base_folder()
        data = { 'home_folder': home_folder,
                 'base_folder': base_folder }
        folder = '%(home_folder)s/%(base_folder)s' % data
        return folder

    #----------------------------------------------------------------------
    def get_local_host_ssh_str( self ):
#         ssh_str = 'ssh://%s@%s' % ( self.local_server.user,
#                                     '85.244.63.224' )
        ssh_str = 'ssh://%s@%s' % ( self.local_server.user,
                                    self.local_server.host )
        if self.local_server.port and self.local_server.port != 22:
            ssh_str += ':%d' % self.local_server.port
        return ssh_str

    #----------------------------------------------------------------------
    def get_remote_host_ssh_str( self ):
        ssh_str = 'ssh://%s' % ( self.server.get_user_host_string() )
        if self.server.port and self.server.port != 22:
            ssh_str += ':%d' % self.server.port
        return ssh_str

    #----------------------------------------------------------------------
    def get_cluster( self, cluster_name ):
        return self.clusters.get_cluster( cluster_name )

    #----------------------------------------------------------------------
    def get_app_db_name( self, cluster_name, app_name ):
        cluster = self.clusters.get_cluster( cluster_name )
        if not cluster:
            raise Exception( 'No cluster: %s' % cluster_name )
        db_name = cluster.get_app_db_name( app_name )
        return db_name

    #----------------------------------------------------------------------
    def get_installer( self, cluster_name ):
        cluster = self.get_cluster( cluster_name )
        return cluster.installer

    #----------------------------------------------------------------------
    def get_vcs_server( self, cluster_name ):
        cluster = self.get_cluster( cluster_name )
        return cluster.vcs_server

    #------------------------------------------------------------------
    def __repr__( self ):
        s = ''
        s += 'local_server: %s\n' % (repr( self.local_server ) )
        s += 'server: %s\n' % (repr( self.server ) )
        s += 'repos: %s\n' % (repr( self.repos ) )
#         s += 'databases: %s\n' % (repr( self.databases ) )
        s += 'web2py: %s\n' % (repr( self.web2py ) )
        s += 'clusters: %s\n' % (repr( self.clusters ) )
#         s += 'app_dict: %s\n' % (repr( self.app_dict ) )
        return s

#     #----------------------------------------------------------------------
#     def get_rel_repo_folder( self, app_name ):
#         if not app_name in self.app_list:
#             raise Exception( 'UNKNOWN APP: %s' % app_name )
#         data = { 'base_folder': self.get_rel_app_folder( self.repo,
#                                                          app_name ) }
#         folder = '%(base_folder)s' % data
# #         term.printLog( 'folder: %s' % repr( folder ) )
#         return folder

    #------------------------------------------------------------------
