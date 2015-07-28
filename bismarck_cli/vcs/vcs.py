# -*- coding: utf-8 -*-

from fabric.context_managers import settings

from bismarck_cli.utils import term
from bismarck_cli.utils.ui_utils import cli_sudo_run
import fabric.contrib.files as fabfiles


#----------------------------------------------------------------------
class VcsServer( object ):
    tag = 'vcs'
    vcs_app_name = None

    #----------------------------------------------------------------------
    def __init__( self, srv_ctx ):
        self.srv_ctx = srv_ctx

    #----------------------------------------------------------------------
    def get_vcs_app_name( self ):
        return self.vcs_app_name

    #----------------------------------------------------------------------
    def config( self ):
        server = self.srv_ctx.server
        bash_file = '.bashrc'
        bash_text_list = [ "alias l='ls -l'",
                           "alias la='ls -al'",
                           "alias lh='ls -lh'" ]

        with settings( host_string=server.get_user_host_string(),
                       password=server.password ):
            for bash_text in bash_text_list:
                fabfiles.append( bash_file, bash_text )

        bash_file = '/root/.bashrc'

        with settings( host_string=server.get_user_host_string(),
                       password=server.password ):
            for bash_text in bash_text_list:
                fabfiles.append( bash_file, bash_text, use_sudo=True )

            dest = '/home/%s' % server.w3_user
            cli_sudo_run( 'mkdir -p %s' % dest,
                          password=server.password )
            cli_sudo_run( 'chown %s. %s' % (server.w3_user,
                                            dest ),
                          password=server.password )

    #----------------------------------------------------------------------
    def get_status_cmd( self ):
        raise Exception( 'Abstract method' )

    #----------------------------------------------------------------------

#----------------------------------------------------------------------
def get_vcs_server( srv_ctx, vcs_app_name ):
    from bismarck_cli.servers.server_context import ServerContext
    if not isinstance( srv_ctx, ServerContext ):
        raise Exception( 'Bad instance type: %s' % type( srv_ctx ) )

    from bismarck_cli.vcs.git import GitServer
    from bismarck_cli.vcs.hg import HgServer
    if vcs_app_name == GitServer.vcs_app_name:
        return GitServer( srv_ctx )
    if vcs_app_name == HgServer.vcs_app_name:
        return HgServer( srv_ctx )
    raise Exception( 'Unknown VCS: %s' % vcs_app_name )

#----------------------------------------------------------------------
