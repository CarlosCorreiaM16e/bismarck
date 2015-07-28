#! /usr/bin/python


import datetime
from fabric.colors import red, blue
from fabric.context_managers import settings, cd, hide, lcd, warn_only
from fabric.contrib import files
from fabric.operations import run, sudo, local

from bismarck_cli.servers.status_resumed import HgRepo
from bismarck_cli.utils import term
from bismarck_cli.utils.storage import Storage
from bismarck_cli.utils.ui_utils import cli_sudo_run, cli_local
from bismarck_cli.vcs.hg import HgServer


PRESERVE_DIRS = [
    'cache',
    'cron',
    'databases',
    'errors',
    'sessions',
    'uploads' ]

LINK_LIST = [ 'ABOUT',
              'config',
              'controllers',
              '__init__.py',
              'languages',
              'LICENSE',
              'models',
              'modules',
              'private',
              'static',
              'views'
              ]

W2P_FOLDER = 'w2p_master'

#----------------------------------------------------------------------
class CurrentApp( object ):
    #----------------------------------------------------------------------
    def __init__( self,
                  srv_ctx,
                  cluster_name,
                  app_name ):
        self.srv_ctx = srv_ctx
        self.cluster_name = cluster_name
        self.app_name = app_name
        vcs_server = self.srv_ctx.get_vcs_server( cluster_name )
        if vcs_server.get_vcs_app_name() == HgServer.vcs_app_name:
            repo_status = HgRepo
        else:
            repo_status = None
        if repo_status:
            self.repo_list = Storage( local=HgRepo( self, 'local' ),
                                      remote=HgRepo( self, 'remote' ),
                                      web=HgRepo( self, 'web' ) )

    #----------------------------------------------------------------------
    def get_app_name( self ):
        return self.app_name

    #----------------------------------------------------------------------
    def get_status( self, repo_type ):
        '''
            repo_type = [ 'local' | 'remote' | 'web' ]
        '''
#         term.printDebug( 'repo_type: %s' % repr( repo_type ) )
        self.repo_list[ repo_type ] = HgRepo( self, repo_type )
#         term.printDebug( 'repo type: %s' % type( self.repo_list[ repo_type ] ) )
#         term.printDebug( 'repo: %s' % repr( self.repo_list[ repo_type ] ) )
        s = self.repo_list[ repo_type ].refresh()
        if s and s[0].startswith( 'abort: ' ):
            print( red( '\n'.join( s ) ) )
        s = self.repo_list[ repo_type ].get_format_status_header()
        s += '\n'
        s += self.repo_list[ repo_type ].format_status()
        return s

    #----------------------------------------------------------------------
    def get_master_status( self, repo_type ):
        '''
            repo_type = [ 'local' | 'remote' | 'web' ]
        '''
        if self.app_name.startswith( 'blm_' ):
            master_app = CurrentApp( self.srv_ctx, 'belmiro' )
            self.repo_list[ repo_type ] = HgRepo( master_app, repo_type )
            self.repo_list[ repo_type ].refresh()
            s = self.repo_list[ repo_type ].get_format_status_header()
            s += '\n'
            s += self.repo_list[ repo_type ].format_status()
            return s
        return None

    #----------------------------------------------------------------------
    def disable_app( self, since ):
        srv_ctx = self.srv_ctx
        server = srv_ctx.server
        abs_path = srv_ctx.get_abs_web_folder( self.cluster_name,
                                               self.app_name )
        with settings( host_string=server.get_user_host_string(),
                       password=server.password ):
            with cd( abs_path ):
                files.append( 'DISABLED',
                              str( since ),
                              use_sudo=True )
                cli_sudo_run( 'chown %s. DISABLED' % server.w3_user,
                              password=server.password )

    #----------------------------------------------------------------------
    def enable_app( self ):
        srv_ctx = self.srv_ctx
        server = srv_ctx.server
        abs_path = srv_ctx.get_abs_web_folder( self.cluster_name,
                                               self.app_name )
        with settings( host_string=server.get_user_host_string(),
                       password=server.password ):
            with cd( abs_path ):
                cli_sudo_run( 'rm -f DISABLED',
                              password=server.password )

    #----------------------------------------------------------------------
    def purge_remote_repo( self ):
        server = self.srv_ctx.server
        with settings( host_string=server.get_user_host_string() ):
            abs_repo_folder = self.srv_ctx.get_abs_remote_folder( self.cluster_name,
                                                                  self.app_name )
            term.printDebug( 'purging folder: %s' % abs_repo_folder )
            run( 'rm -rf %s' % abs_repo_folder )

    #----------------------------------------------------------------------
    def get_app_db_name(self ):
        db_name = self.srv_ctx.get_app_db_name( self.cluster_name,
                                                self.app_name )
        return db_name

    #----------------------------------------------------------------------
    def get_abs_local_folder( self ):
        local_folder = self.srv_ctx.get_abs_local_folder( self.cluster_name,
                                                          self.app_name )
        term.printLog( repr( local_folder ) )
        return local_folder

    #----------------------------------------------------------------------
    def get_abs_local_w2p_folder( self ):
        local_folder = self.get_abs_local_folder()
        path = local_folder.split( '/' )
        w2p_folder = '/'.join( path[:-1] ) + '/' + W2P_FOLDER
        term.printLog( repr( w2p_folder ) )
        return w2p_folder

    #----------------------------------------------------------------------
    def init_remote_repo( self, force=False ):
        server = self.srv_ctx.server
        with settings( host_string=server.get_user_host_string() ):
            abs_repo_folder = self.srv_ctx.get_abs_remote_folder( self.cluster_name,
                                                                  self.app_name )
            parent_folder, app_folder = abs_repo_folder.rsplit( '/', 1 )
            term.printDebug( 'abs_repo_folder: %s ' % abs_repo_folder )
            term.printDebug( 'parent_folder: %s ' % parent_folder )
            term.printDebug( 'app_folder: %s ' % app_folder )
            if files.exists( abs_repo_folder ):
                if force:
                    run( 'rm -r %s' % abs_repo_folder )
                else:
                    return ( 'app repo (%s) already exists' % abs_repo_folder,
                             'REPO EXISTS: %s' % abs_repo_folder )

            term.printDebug( 'mkdir -p %s' % abs_repo_folder )
            run( 'mkdir -p %s' % abs_repo_folder )
            local_folder = self.srv_ctx.get_abs_local_folder( self.cluster_name,
                                                              self.app_name )
            term.printLog( repr( local_folder ) )
            with cd( parent_folder ):
                run( 'pwd' )
                d = { 'ssh_str': self.srv_ctx.get_local_host_ssh_str(),
                      'repo': local_folder,
                      'app_name': self.app_name }
                cmd = 'LANGUAGE=C hg clone %(ssh_str)s/%(repo)s %(app_name)s' % d
                run( cmd )
                with cd( app_folder ):
                    run( 'cp ~/.hgignore .' )
                    run( 'cat ~/.hgrc_hooks >> .hg/hgrc' )

    #----------------------------------------------------------------------
    def push_to_remote( self, since ):
        server = self.srv_ctx.server
        local_path = self.srv_ctx.get_abs_local_folder( self.cluster_name,
                                                        self.app_name )
        remote_path = '%s/%s' % ( self.srv_ctx.get_remote_host_ssh_str(),
                                  self.srv_ctx.get_abs_remote_folder( self.cluster_name,
                                                                      self.app_name ) )
        with settings( host_string=server.get_user_host_string(),
                       password=server.password ):
            with lcd( local_path ), warn_only():
                local( 'pwd' )
                result = local( 'LANGUAGE=C hg push %s' % remote_path )
                errors = result.stderr
                if errors:
                    print( red( errors ) )
                    return (result, errors)
                failed = False
                for line in result.splitlines():
                    if line.startswith( 'remote: abort' ) \
                    or line.startswith( 'abort:' ):
                        failed = True
                if failed:
                    term.printDebug( 'output: %s' % result )
                    raise Exception( 'Failed' )

#         (result, errors) = self.repo_list.local.exec_single( 'hg push',
#                                                              prefix='LANGUAGE=C ' )
#         if errors:
#             print( red( errors ) )
#             return (result, errors)
#         failed = False
#         for line in result.splitlines():
#             if line.startswith( 'remote: abort' ) \
#             or line.startswith( 'abort:' ):
#                 failed = True
#         if failed:
#             term.printDebug( 'output: %s' % result )
#             raise Exception( 'Failed' )
#         term.printDebug( 'pushed to remote' )
        return (result, errors)

    #----------------------------------------------------------------------
    def init_web_repo( self ):
        srv_ctx = self.srv_ctx
        server = srv_ctx.server
        DT = datetime.datetime
        ts = DT.now().strftime( '%Y-%m-%d-%H-%M' )
        with settings( host_string=server.get_user_host_string(),
                       password=server.password ):
            app_folder = srv_ctx.get_abs_web_folder( self.cluster_name,
                                                     self.app_name )
#             app_folder = app_folder.rsplit( '/', 1 )[0]
            sudo( 'mkdir -p %s/releases' % app_folder,
                  user=server.w3_user )

            sudo( 'mkdir -p %s/preserve' % ( app_folder ),
                  user=server.w3_user )
            with cd( app_folder ):
                with cd( 'preserve' ):
                    sudo( 'pwd',
                           user=server.w3_user )
                    for p in PRESERVE_DIRS:
                        sudo( 'mkdir -p %s' % ( p ),
                              user=server.w3_user )
                with cd( 'releases' ):
                    sudo( 'pwd',
                          user=server.w3_user )
                    repo_folder = srv_ctx.get_abs_remote_folder( self.cluster_name,
                                                                 self.app_name )
                    sudo( 'LANGUAGE=C hg clone %s %s' % ( repo_folder, ts ),
                          user=server.w3_user )
                    with cd( ts ):
                        for p in PRESERVE_DIRS:
                            sudo( 'ln -s %s/preserve/%s ' % ( app_folder, p ),
                                  user=server.w3_user )
                        sudo( 'mkdir -p static/tmp',
                              user=server.w3_user )

                sudo( 'ln -s releases/%s current' % ts,
                      user=server.w3_user )
                with cd( 'current' ):
                    sudo( 'cp %s/.hgignore .' % srv_ctx.get_remote_home_folder() )
                    sudo( 'cat %s/.hgrc_hooks >> .hg/hgrc' % srv_ctx.get_remote_home_folder() )
                sudo( 'chown -R %s. .' % server.w3_user )

            home_folder = srv_ctx.get_web_home_folder()
            base_folder = srv_ctx.get_web_base_folder( self.cluster_name )
#             w2p_folder = '%s/%s/web2py/current' % ( home_folder, base_folder )
#
#             web_repo = srv_ctx.get_web_repo( app_name=self.app_name )
#             home_folder = web_repo.get_home_folder()
#             base_folder = web_repo.get_base_folder( self.cluster_name )
            w2p_app_folder = '%s/%s/web2py/current/applications' % ( home_folder, base_folder )
            with cd( w2p_app_folder ):
                f_link = '%s/current' % ( app_folder )
                link_name = f_link.rsplit( '/', 2 )[-2]
                if not files.exists( link_name ):
                    cli_sudo_run( 'ln -s %s %s' % ( f_link, link_name ),
                                  user=server.w3_user,
                                  password=server.password )

#             w_repo = _web.get_repo( w_type )
#             web_folder = '%s/%s/web2py/current/applications' % ( w_repo.home_folder,
#                                                                  w_repo.base_folder )
#
#             with cd( web_folder ):
#                 cli_sudo_run( 'pwd',
#                               password=_server.password )
#                 f_link = '%s/current' % ( app_folder )
#                 if not fabfiles.exists( app_name ):
#                     cli_sudo_run( 'ln -s %s %s' % ( f_link, app_name ),
#                                   password=_server.password )
#                 cli_sudo_run( 'chown -R %s. .' % _server.w3_user,
#                               password=_server.password )
#
#             return dutils.CmdResult( 'app repo cloned', dutils.OK )
#
#         return dutils.CmdResult( 'app repo clone: UNKNOWN ERROR', dutils.ERROR )

    #----------------------------------------------------------------------
    def purge_web_repo( self ):
        srv_ctx = self.srv_ctx
        server = self.srv_ctx.server
        with settings( host_string=server.get_user_host_string(),
                       password=server.password ):
            home_folder = srv_ctx.get_web_home_folder()
            base_folder = srv_ctx.get_web_base_folder( self.cluster_name )
#             web_repo = srv_ctx.get_web_repo( app_name=self.app_name )
#             home_folder = web_repo.get_home_folder()
#             base_folder = web_repo.get_base_folder( self.cluster_name )
            w2p_app_folder = '%s/%s/web2py/current/applications' % ( home_folder, base_folder )
            with cd( w2p_app_folder ):
                if files.exists( self.app_name ):
                    cli_sudo_run( 'rm %s' % ( self.app_name ),
                                  password=server.password )
            app_folder = srv_ctx.get_abs_web_folder( self.cluster_name,
                                                     self.app_name )
#             term.printDebug( 'app_folder: %s' % repr( app_folder ) )
#             app_folder = app_folder.rsplit( '/', 1 )[0]
#             term.printDebug( 'app_folder: %s' % repr( app_folder ) )
            sudo( 'rm -rf %s' % app_folder )

    #----------------------------------------------------------------------
    def push_to_web( self, ts ):
        srv_ctx = self.srv_ctx
        server = self.srv_ctx.server
        dest_folder = srv_ctx.get_abs_web_folder( self.cluster_name,
                                                  self.app_name )
        term.printDebug( 'pushed to web: %s' % dest_folder )
#         dest_folder = '%s/apps/%s' % ( self.srv_ctx.get_abs_w2p_folder( w_type ),
#                                        app_name )
        with settings( host_string=server.get_user_host_string(),
                       password=server.password ):
            with cd( dest_folder ):
                with cd ( 'current' ):
                    prev_folder = run( 'pwd -P' )
                with cd( 'releases' ):
                    cli_sudo_run( 'cp -prH ../current %s' % ts,
                                  password=server.password )
                    with cd( ts ):
                        ret = cli_sudo_run( 'pwd', password=server.password )
                        term.printDebug( ret )
                        cli_sudo_run( 'LANGUAGE=C hg pull', password=server.password )
                        cli_sudo_run( 'mkdir -p static/tmp', password=server.password )

                cli_sudo_run( 'rm -f current', password=server.password )
                cli_sudo_run( 'ln -s releases/%s current' % ts, password=server.password )
                with cd( 'releases/%s' % ts ):
                    with settings( hide( 'stderr', 'warnings' ), warn_only = True ):
                        ret = cli_sudo_run( 'rm -f cache/*', password=server.password )
                        print( blue( ret.stdout ) )
                        ret = cli_sudo_run( 'rm -rf sessions/*', password=server.password )
                        print( blue( ret.stdout ) )
                        ret = cli_sudo_run( 'find -L . -name "*.pyc" |xargs rm',
                                            password=server.password )
                        print( blue( ret.stdout ) )
                sudo( 'chown -R %s. .' % server.w3_user )
        return prev_folder

    #----------------------------------------------------------------------
    def run_w2p_script( self,
                        script,
                        arg1=None,
                        arg2=None ):
        srv_ctx = self.srv_ctx
        server = self.srv_ctx.server
        with settings( host_string=server.get_user_host_string(),
                       password=server.password ):
            home_folder = srv_ctx.get_web_home_folder()
            base_folder = srv_ctx.get_web_base_folder( self.cluster_name )
#             web_repo = srv_ctx.get_web_repo( app_name=self.app_name )
#             app_web_name = srv_ctx.get_app_web_name( self.app_name )
#             home_folder = web_repo.get_home_folder()
#             base_folder = web_repo.get_base_folder( self.cluster_name )
            w2p_folder = '%s/%s/web2py/current' % ( home_folder, base_folder )
            with cd( w2p_folder ):
                cmd = 'python web2py.py -i 127.0.0.1 -M -S '
                cmd += self.app_name
                cmd += ' -R applications/'
                cmd += self.app_name
                cmd += '/private/scripts/'
                cmd += script
                if arg1:
                    cmd += ' -A '
                    cmd += arg1
                    if arg2:
                        cmd += ' ' + arg2
                cli_sudo_run( cmd,
                              user=server.w3_user,
                              password=server.password )

    #----------------------------------------------------------------------
    def run_upgrade_script( self,
                            from_version,
                            to_version ):
        srv_ctx = self.srv_ctx
        server = self.srv_ctx.server
        with settings( host_string=server.get_user_host_string(),
                       password=server.password ):

            home_folder = srv_ctx.get_web_home_folder()
            base_folder = srv_ctx.get_web_base_folder( self.cluster_name )
            w2p_folder = '%s/%s/web2py/current' % ( home_folder, base_folder )
            with cd( w2p_folder ):
                cli_sudo_run( 'pwd' )
                cmd = 'python web2py.py -i 127.0.0.1 -M -S '
                cmd += self.app_name
                cmd += ' -R applications/'
                cmd += self.app_name
                cmd += '/private/resources/upgrades/'
                cmd += '%s/upd_FROM_%s.py' % (to_version, from_version)
                cli_sudo_run( cmd,
                              user=server.w3_user,
                              password=server.password,
                              prompt=True )

    #----------------------------------------------------------------------
    def upload_db( self ):
        cluster = self.srv_ctx.get_cluster( self.cluster_name )

    #----------------------------------------------------------------------

