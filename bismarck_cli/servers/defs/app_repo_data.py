#! /usr/bin/python

#----------------------------------------------------------------------
class AppRepo( object ):
    #----------------------------------------------------------------------
    def __init__( self, app_repo_def, repo_type, repo_folder ):
        from bismarck_cli.servers.status_resumed import HgRepo

        self.app_repo_def = app_repo_def
        self.repo_folder = repo_folder
        self.repo_type = repo_type
#         if repo_type == RT_FOLDER:
#             repo_type = DEFAULT_RT_TYPE
#         if repo_type == RT_HG_FOLDER:
#             self.status = HgRepo( self )
#         else:
#             self.status = None

#     #----------------------------------------------------------------------
#     def refresh_status( self ):
#         if self.status:
#             self.status.refresh()

    #------------------------------------------------------------------
    def __repr__( self ):
        s = 'AppRepo: {'
        s += '\n        repo_folder: %s' % self.repo_folder
#         s += '\n        status: %s' % str( self.status )
        s += '\n  }'
        return s
    #----------------------------------------------------------------------
