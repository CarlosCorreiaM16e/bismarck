# -*- coding: utf-8 -*-

from bismarck_cli.installers.installer import Installer

#----------------------------------------------------------------------
class Take5Installer( Installer ):
    installer_name = 'take5'
    #----------------------------------------------------------------------
    def __init__( self, srv_ctx ):
        super( Take5Installer, self ).__init__( srv_ctx )

    #----------------------------------------------------------------------

#----------------------------------------------------------------------
