# -*- coding: utf-8 -*-

from bismarck_cli.installers.installer import Installer

#----------------------------------------------------------------------
class BelmiroInstaller( Installer ):
    installer_name = 'belmiro'
    #----------------------------------------------------------------------
    def __init__( self, srv_ctx ):
        super( BelmiroInstaller, self ).__init__( srv_ctx )

    #----------------------------------------------------------------------

#----------------------------------------------------------------------
