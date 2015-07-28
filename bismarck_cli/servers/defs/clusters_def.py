# -*- coding: utf-8 -*-
from bismarck_cli.servers.defs.cluster import Cluster
from bismarck_cli.utils import term
from bismarck_cli.utils.storage import Storage

#----------------------------------------------------------------------
class ClustersDef( object ):
    '''
    'clusters': { 'belmiro': { <Cluster> },
                  'www': { <Cluster> },
                  'take5': { <Cluster> },
                },

    '''
    tag = 'clusters'

    #----------------------------------------------------------------------
    def __init__( self, srv_ctx, data ):
#         term.printDebug( 'srv_ctx: %s' % type( srv_ctx ) )
        self.srv_ctx = srv_ctx
        self.load_data( data )

    #----------------------------------------------------------------------
    def load_data( self, data ):
        if self.tag in data:
            data = data[ self.tag ]
#         term.printDebug( 'data.keys: %s' % data.keys() )
        self.clusters = Storage()
        for i in data:
            self.clusters[ i ] = Cluster( self.srv_ctx, data, i )

    #----------------------------------------------------------------------
    def get_cluster( self, cluster_name ):
#         term.printDebug( 'cluster_name: %s' % repr( cluster_name ) )
#         term.printDebug( 'self: %s' % repr( self ) )
        if not cluster_name:
            cluster_name = 'www'
#         term.printDebug( 'cluster_name: %s' % repr( cluster_name ) )
        if cluster_name:
            return self.clusters.get( cluster_name )
        raise Exception( 'Unknown Cluster: %s' % cluster_name )
    #----------------------------------------------------------------------
    def get_cluster_name( self,
                          app_name=None ):
        for h in self.clusters:
            cluster = self.clusters[ h ]
            if app_name in cluster.apps:
                return h
        raise Exception( 'No Cluster for app: %s' % app_name )

    #------------------------------------------------------------------
    def __repr__( self ):
        s = '(%s) {' % self.tag
        for h in self.clusters:
            s += '\n    %s: {' % h
            cluster = self.clusters[ h ]
#             term.printDebug( 'cluster[ %s ]: %s' % ( h, repr( cluster ) ) )
            s += '\n        installer: %s' % repr( cluster.installer.installer_name )
            s += '\n        vcs_server: %s' % repr( cluster.vcs_server.vcs_app_name )
            s += '\n        apps: %s' % repr( cluster.apps )
            s += '\n    }'
        s += '\n    }'
        return s

    #----------------------------------------------------------------------

#----------------------------------------------------------------------
