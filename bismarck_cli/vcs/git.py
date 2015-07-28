'''
Created on 17/10/2014

@author: carlos
'''
from fabric.context_managers import settings, cd
from fabric.operations import put

from bismarck_cli.utils import term
from bismarck_cli.utils.ui_utils import cli_sudo_run
from bismarck_cli.vcs.vcs import VcsServer

import fabric.contrib.files as fabfiles

#----------------------------------------------------------------------
class GitServer( VcsServer ):
    vcs_app_name = 'git'
    #----------------------------------------------------------------------
    def __init__( self, parent ):
        super( GitServer, self ).__init__( parent )

    #----------------------------------------------------------------------
    def do_config( self ):
        super( GitServer, self ).do_config()
        server = self.parent
        with settings( host_string=server.get_user_host_string() ):
            put( '~/.gitignore' )


        with settings( host_string=server.get_user_host_string(),
                       password=server.password ):

# #             term.printDebug( 'repo: %s' % repr( srv_def.repo ) )
            d = { 'w3_user': server.w3_user,
                  'src': '/home/%(user)s' % server.user,
                  'dest': '/home/%(w3_user)s' % server.w3_user }
            term.printDebug( 'd: %s' % repr( d ) )

            cli_sudo_run( 'mkdir -p %(dest)s' % d,
                          password=server.password )

            cli_sudo_run( 'cp %(src)s/.gitignore %(dest)s' % d,
                          password=server.password )
            cli_sudo_run( 'chown -R %(w3_user)s.  %(dest)s' % d,
                          password=server.password )
            with cd( '/var/www' ):
                cli_sudo_run( 'ln -s /home/%(w3_user)s/.gitignore .gitignore' % d,
                              password=server.password )

    #----------------------------------------------------------------------

#----------------------------------------------------------------------
