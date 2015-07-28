#! /usr/bin/python

from bismarck_cli.servers.defs.app_repo_data import AppRepo
from bismarck_cli.utils import term
from bismarck_cli.utils.storage import Storage, storagize


RT_GIT_FOLDER = 'git_folder'
RT_HG_FOLDER = 'hg_folder'
RT_FOLDER = 'folder'

RT_TYPES = [ RT_GIT_FOLDER,
             RT_HG_FOLDER,
             RT_FOLDER ]

DEFAULT_RT_TYPE = RT_HG_FOLDER

#----------------------------------------------------------------------
class AppReposDef( object ):
    '''
    ('repos': { 'local': { 'app_repos': { '_default':)
    { 'git_folder': 'repos/git/dev/%(app_name)s',
      'hg_folder': 'projects/w2p_%(app_name)s/src/applications/%(app_name)s'
    },

    '''
    tag = 'app_repos'

    #----------------------------------------------------------------------
    def __init__( self, repo_def, data, app_name ):
        self.repo_def = repo_def
        self.app_name = app_name
        self.load_data( data )

    #----------------------------------------------------------------------
    def load_data( self, data ):
        self.repos = Storage()
        self.repos[ RT_GIT_FOLDER ] = AppRepo( self,
                                               RT_GIT_FOLDER,
                                               data.get( RT_GIT_FOLDER ) )
        self.repos[ RT_HG_FOLDER ] = AppRepo( self,
                                              RT_HG_FOLDER,
                                              data.get( RT_HG_FOLDER ) )
        self.repos[ RT_FOLDER ] = AppRepo( self,
                                           RT_FOLDER,
                                           data.get( RT_FOLDER ) )

    #----------------------------------------------------------------------
    def refresh_status( self,
                        folder_type=None,
                        app_name=None ):
        app_repo = self.get_app_repo( folder_type, strict=False )
        term.printDebug( 'app_repo: %s' % repr( app_repo ) )
        if app_repo.status:
            app_repo.status.refresh()
        term.printDebug( 'app_repo: %s' % repr( app_repo ) )

    #----------------------------------------------------------------------
    def get_status( self, folder_type=None ):
        app_repo = self.get_app_repo( folder_type, strict=False )
        return app_repo.status

    #----------------------------------------------------------------------
    def get_app_repo( self, folder_type=None, strict=True ):
#         term.printDebug( 'folder_type: %s' % repr( folder_type ) )
        if not folder_type:
            strict = False
            folder_type = DEFAULT_RT_TYPE
#         term.printDebug( 'folder_type: %s' % repr( folder_type ) )
        if folder_type:
            if not folder_type in RT_TYPES:
                raise Exception( 'Unkown FOLDER TYPE: %s' % folder_type )
            f = self.repos.get( folder_type )
            if f.repo_folder:
                return f

            if not strict:
                # try default
                f = self.repos.get( RT_FOLDER )
                if f.repo_folder:
                    return f

            term.printLog( 'repo (%s) NOT FOUND' % repr( folder_type ) )
        if not strict:
            for ft in RT_TYPES:
                f = self.repos.get( ft )
                if f.repo_folder:
#                     term.printDebug( 'f: %s' % repr( f ) )
                    return f

        if strict:
            term.printLog( 'repo (%s) NOT FOUND' % repr( folder_type ) )

        return None


    #----------------------------------------------------------------------
    def get_app_repo_folder( self, folder_type=None, strict=True ):
        if not folder_type:
            strict = False
#         term.printDebug( 'folder_type: %s' % repr( folder_type ) )
        app_repo = self.get_app_repo( folder_type, strict )
#         term.printDebug( 'app_repo: %s' % repr( app_repo ) )

        if app_repo:
            return  app_repo.repo_folder
        if strict:
            term.printLog( 'repo (%s) NOT FOUND' % repr( folder_type ) )

        return None


    #------------------------------------------------------------------
    def __repr__( self ):
        s = 'AppReposDef: {'
        for a in self.__dict__:
            if a == 'parent':
                continue
            s += '\n    %s: %s' % (repr( a ), repr( self.__dict__[a] ) )
        s += '\n  }'
        return s

    #------------------------------------------------------------------
