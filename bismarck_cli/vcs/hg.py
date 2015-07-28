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
from fabric.contrib import files

#----------------------------------------------------------------------
class HgServer( VcsServer ):
    vcs_app_name = 'hg'
    #----------------------------------------------------------------------
    def __init__( self, srv_ctx ):
        super( HgServer, self ).__init__( srv_ctx )

    #----------------------------------------------------------------------
    def get_status_cmd( self ):
        return 'hg status'

    #----------------------------------------------------------------------
    def parse_status_cmd( self, status_str ):
        lines = status_str.splitlines()

    #----------------------------------------------------------------------
    def config( self ):
        super( HgServer, self ).config()
        server = self.srv_ctx.server
        with settings( host_string=server.get_user_host_string() ):
            put( '~/.hgignore' )
            put( '~/.hgrc_hooks' )

        hg_file = '/etc/mercurial/hgrc'
        hg_text_list = [ '[trusted]',
                         'users = %s, www-data' % server.user ]

        with settings( host_string=server.get_user_host_string(),
                       password=server.password ):
            for hg_text in hg_text_list:
                fabfiles.append( hg_file, hg_text, use_sudo=True )

# #             term.printDebug( 'repo: %s' % repr( srv_def.repo ) )
            d = { 'w3_user': server.w3_user,
                  'src': '/home/%s' % server.user,
                  'dest': '/home/%s' % server.w3_user }
            term.printDebug( 'd: %s' % repr( d ) )

            cli_sudo_run( 'cp %(src)s/.hgignore %(dest)s' % d,
                          password=server.password )
            cli_sudo_run( 'cp %(src)s/.hgrc_hooks %(dest)s' % d,
                          password=server.password )
            cli_sudo_run( 'chown  %(w3_user)s.  %(dest)s/.hg*' % d,
                          password=server.password )
            with cd( '/var/www' ):
                if not files.exists( '.hgignore',
                                     use_sudo=True ):
                    cli_sudo_run( 'ln -s /home/%(w3_user)s/.hgignore .hgignore' % d,
                                  password=server.password )


#     #----------------------------------------------------------------------
#     def do_config( self ):
#         super( HgServer, self ).do_config()
#         server = self.srv_ctx.server
#         with settings( host_string=server.get_user_host_string() ):
#             put( '~/.hgignore' )
#             put( '~/.hgrc_hooks' )
#
#         hg_file = '/etc/mercurial/hgrc'
#         hg_text_list = [ '[trusted]',
#                          'users = %s, www-data' % server.user ]
#
#         with settings( host_string=server.get_user_host_string(),
#                        password=server.password ):
#             for hg_text in hg_text_list:
#                 fabfiles.append( hg_file, hg_text, use_sudo=True )
#
# # #             term.printDebug( 'repo: %s' % repr( srv_def.repo ) )
#             d = { 'w3_user': server.w3_user,
#                   'src': '/home/%s' % server.user,
#                   'dest': '/home/%s' % server.w3_user }
#             term.printDebug( 'd: %s' % repr( d ) )
#
#             cli_sudo_run( 'cp %(src)s/.hgignore %(dest)s' % d,
#                           password=server.password )
#             cli_sudo_run( 'cp %(src)s/.hgrc_hooks %(dest)s' % d,
#                           password=server.password )
#             cli_sudo_run( 'chown -R %(w3_user)s.  %(dest)s' % d,
#                           password=server.password )
#             with cd( '/var/www' ):
#                 if not fabfiles.exists( '/var/www/.hgignore',
#                                         use_sudo=True ):
#                     cli_sudo_run( 'ln -s /home/%(w3_user)s/.hgignore .hgignore' % d,
#                                   password=server.password )


# #----------------------------------------------------------------------
# def hg_config( srv_def ):
#     _server = srv_def.server
#     bash_file = '.bashrc'
#     bash_text_list = [ "alias l='ls -l'",
#                        "alias la='ls -al'",
#                        "alias lh='ls -lh'" ]
#     with settings( host_string=_server.get_user_host_string() ):
#         for bash_text in bash_text_list:
#             fabfiles.append( bash_file, bash_text )
#         put( '~/.hgignore' )
#
#
#     hg_file = '/etc/mercurial/hgrc'
#     hg_text_list = [ '[trusted]',
#                      'users = %s, www-data' % _server.user ]
#
#     bash_file = '/root/.bashrc'
#     with settings( host_string=_server.get_user_host_string(),
#                    password=_server.password ):
#         for hg_text in hg_text_list:
#             fabfiles.append( hg_file, hg_text, use_sudo=True )
#         for bash_text in bash_text_list:
#             fabfiles.append( bash_file, bash_text, use_sudo=True )
#
#         term.printDebug( 'repo: %s' % repr( srv_def.repo ) )
#         d = { 'src': srv_def.repo.home_folder,
#               'dest': srv_def.web.get_repo( 'p' ).home_folder }
#         term.printDebug( 'd: %s' % repr( d ) )
#
#         cli_sudo_run( 'mkdir -p %(dest)s' % d,
#                       password=_server.password )
#
#         cli_sudo_run( 'cp %(src)s/.hgignore %(dest)s' % d,
#                       password=_server.password )
#         cli_sudo_run( 'chown -R %(w3_user)s.  %(dest)s' %
#                       { 'w3_user': _server.w3_user,
#                         'dest': srv_def.web.get_repo( 'p' ).home_folder },
#                       password=_server.password )
#         with cd( '/var/www' ):
#             cli_sudo_run( 'ln -s %(dest)s/.hgignore .hgignore' % d,
#                           password=_server.password )

