# -*- coding: utf-8 -*-
from fabric.colors import magenta
from fabric.context_managers import settings, cd, lcd
from fabric.contrib import files
from fabric.operations import sudo, put, local
import os

from bismarck_cli.installers.installer import get_installer
from bismarck_cli.servers.defs.repos_def import ReposDef
from bismarck_cli.utils import term
from bismarck_cli.utils.storage import Storage
from bismarck_cli.utils.ui_utils import cli_run, cli_sudo_run, cli_continue
from bismarck_cli.vcs.vcs import get_vcs_server
from datetime import datetime


#----------------------------------------------------------------------
class Cluster( object ):
    '''
    { 'installer': 'belmiro',
      'vcs': 'git',
      'apps': [ 'doors', 'gps', ],
    }
    '''

    #----------------------------------------------------------------------
    def __init__( self, srv_ctx, data, cluster_name ):
        self.srv_ctx = srv_ctx
        self.cluster_name = cluster_name
        self.load_data( data )

    #----------------------------------------------------------------------
    def load_data( self, data ):
        from bismarck_cli.servers.defs.clusters_def import ClustersDef
#         term.printDebug( 'data: %s' % repr( data ) )
        cluster_def = data[ self.cluster_name ]
        repos_def = cluster_def[ ReposDef.tag ]
        self.repos = ReposDef( self.srv_ctx, self, repos_def )
        self.installer = get_installer( self.srv_ctx,
                                        cluster_def.installer )
        self.vcs_server = get_vcs_server( self.srv_ctx,
                                          cluster_def.vcs )
        self.apps = cluster_def.apps
        self.server_name = cluster_def.server_name
        self.self_signed_cert = cluster_def.get( 'self_signed_cert' ) or False

    #----------------------------------------------------------------------
    def get_app_db_name( self, app_name ):
        for app in self.apps:
            if app.name == app_name:
                return app.database

        for app in self.apps:
            if app.name == '_default':
                return app[ 'database' ] % { 'app_name': app_name }

        return None

    #----------------------------------------------------------------------
    def drop_remote_app_db( self, app_name ):
        server = self.srv_ctx.server
        db_name = self.get_app_db_name( app_name )
        if not db_name:
            raise Exception( 'app (%s) db not in cluster (%s)'
                             % ( app_name, self.cluster_name ) )
        term.printDebug( 'dropdb' )
        with settings( host_string=server.get_user_host_string(),
                       warn_only = True ):
            result = cli_run( '''psql -tAc "select 1 from pg_database where datname='%s'"''' %
                              db_name )
            term.printDebug( 'result: %s' % repr( result ) )
            if result:
                with cd( server.backup_remote ):
                    ts = datetime.now()
                    s_ts = ts.strftime( '%Y-%m-%d-%H-%M-%s' )
                    filename = 'dump-%s-%s-dropped.sql' % (db_name, s_ts)
                    cli_run( 'pg_dump -C %s -f %s' % (db_name, filename) )

                cli_run( 'dropdb %s' % db_name,
                         prompt=True )

    #----------------------------------------------------------------------
    def upload_app_db( self, app_name ):
        server = self.srv_ctx.server
        db_name = self.get_app_db_name( app_name )
        if not db_name:
            raise Exception( 'app (%s) db not in cluster (%s)'
                             % ( app_name, self.cluster_name ) )
        d = { 'db_name': db_name }
        folder = '~/tmp/downloads'
        sql_filename = 'dump-%(db_name)s.sql' % d
        local( 'mkdir -p %s' % folder )
        with lcd( folder ):
            tarball = '%s.tar.bz2' % sql_filename
            local( 'pg_dump -C %s -f %s' % (db_name, sql_filename) )
            local( 'tar jcvf %s %s' % (tarball, sql_filename) )

        with settings( host_string=server.get_user_host_string(),
                       password=server.password ):
            cli_run( 'mkdir -p tmp' )
            tarball = '%s.tar.bz2' % sql_filename
            put( '%s/%s' % (folder, tarball),
                 'tmp/%s' % tarball )
            with cd( 'tmp' ):
                filename = cli_run( 'tar jxvfm %s' % (tarball) )
                term.printDebug( 'filename: %s' % filename )
                cli_run( 'ls -l %s' % filename )

                cmd = '''sed -i 's/SET lock_timeout/-- SET lock_timeout/g' %s'''
                term.printDebug( 'cmd: %s' % (cmd % filename) )
                cli_run( cmd % filename )

                cmd = '''sed -i 's/OWNER TO carlos/OWNER TO %s/g' %s'''
                cli_run( cmd % (server.db_user, filename) )

                cmd = '''sed -i 's/Owner: carlos/Owner: %s/g' %s'''
                cli_run( cmd % (server.db_user, filename) )

                cli_run( 'psql -f %s -v ON_ERROR_STOP=1' % filename )

    #----------------------------------------------------------------------
    def get_repo( self, repo_type ):
        return self.repos.get_repo( repo_type )

    #----------------------------------------------------------------------
    def get_server_context( self ):
        return self.srv_ctx

    #----------------------------------------------------------------------
    def drop_web2py( self ):
        term.printDebug( 'cluster_name: %s' % self.cluster_name )
        srv_ctx = self.get_server_context()
        web_repo = srv_ctx.get_web_repo( cluster_name=self.cluster_name )
        term.printDebug( 'web_repo: %s' % repr( web_repo ) )
        if not web_repo:
            return 'No cluster defined or empty (no apps)'

        home_folder = web_repo.get_home_folder()
        base_folder = web_repo.get_base_folder()
        cluster_folder = '%s/%s' % ( home_folder, base_folder )
        server = srv_ctx.server
        with settings( host_string=server.get_user_host_string(),
                       password=server.password ):
            sudo( 'rm -rf %s' % cluster_folder,
                  user=server.w3_user )

    #----------------------------------------------------------------------
    def init_web2py( self ):
        term.printDebug( 'cluster_name: %s' % self.cluster_name )
        srv_ctx = self.get_server_context()
        web_repo = srv_ctx.get_web_repo( self.cluster_name )
        term.printDebug( 'web_repo: %s' % repr( web_repo ) )
        if not web_repo:
            return 'No cluster defined or empty (no apps)'

        home_folder = web_repo.get_home_folder()
        base_folder = web_repo.get_base_folder()
        w2p_folder = '%s/%s/web2py' % ( home_folder, base_folder )
        server = srv_ctx.server
        with settings( host_string=server.get_user_host_string(),
                       password=server.password ):
            local_repo = '%s/hg' % home_folder
            w2p_local_repo = '%s/web2py' % local_repo
#             hg_repo = '%s/hg/web2py' % home_folder
            w2p_repo = srv_ctx.web2py.repo
            w2p_rel = srv_ctx.web2py.release
            if files.exists( w2p_local_repo ):
                print( magenta( 'updating local w2p repo' ) )
                with cd( w2p_local_repo ):
                    sudo( 'hg pull && hg update',
                          user=server.w3_user )
            else:
                print( magenta( 'creating local w2p repo' ) )
                sudo( 'mkdir -p %s' % local_repo,
                      user=server.w3_user )
                with cd( local_repo ):
                    sudo( 'hg clone %(w2p_repo)s web2py' %
                          { 'w2p_repo': w2p_repo },
                          user=server.w3_user )

            release_folder = '%s/releases' % w2p_folder
            sudo( 'mkdir -p %s' % release_folder,
                  user=server.w3_user )
#             sudo( 'chown -R %s. %s' % ( server.w3_user, home_folder ) )
            with cd( w2p_folder ):
                with cd( 'releases' ):
                    sudo( 'pwd' )
                    sudo( 'ls -l' )
                    term.printDebug( 'w2p_rel: %s' % w2p_rel )
                    if files.exists( w2p_rel,
                                     use_sudo=True ):
                        return 'Repo already exists: %s' % w2p_rel

                    sudo( 'hg clone -r %(release)s %(w2p_local_repo)s %(release)s' %
                          { 'w2p_local_repo': w2p_local_repo,
                            'release': w2p_rel },
                          user=server.w3_user )
                    with cd( w2p_rel ):
                        sudo( 'cp %s/.hgignore .' % home_folder,
                              user=server.w3_user )
                        sudo( 'cat %s/.hgrc_hooks >> .hg/hgrc' % home_folder,
                              user=server.w3_user )
                        sudo( 'cp handlers/wsgihandler.py .',
                              user=server.w3_user )
#                         sudo( 'python -c "from gluon.widget import console; console();"',
#                               user=server.w3_user )
#                         sudo( '''python -c "from gluon.main import save_password; save_password(raw_input('admin password: '),443)" ''',
#                               user=server.w3_user )

                sudo( 'rm -f current' )
                sudo( 'ln -s releases/%s current' % w2p_rel,
                      user=server.w3_user )

    #----------------------------------------------------------------------
    def define_web2py_admin_password( self ):
        term.printDebug( 'cluster_name: %s' % self.cluster_name )
        srv_ctx = self.get_server_context()

        web_repo = srv_ctx.get_web_repo( cluster_name=self.cluster_name )
        term.printDebug( 'web_repo: %s' % repr( web_repo ) )
        if not web_repo:
            return 'No cluster defined or empty (no apps)'

        home_folder = web_repo.get_home_folder()
        base_folder = web_repo.get_base_folder()
        w2p_folder = '%s/%s/web2py' % ( home_folder, base_folder )
        server = srv_ctx.server
        with settings( host_string=server.get_user_host_string(),
                       password=server.password ):
            w2p_rel = srv_ctx.web2py.release
            with cd( w2p_folder ):
                with cd( 'releases' ):
                    with cd( w2p_rel ):
                        sudo( 'python -c "from gluon.widget import console; console();"',
                              user=server.w3_user )
                        sudo( '''python -c "from gluon.main import save_password; save_password(raw_input('admin password: '),443)" ''',
                              user=server.w3_user )
                        sudo( 'echo "disabled: True" >> applications/examples/DISABLED',
                              user=server.w3_user )
                        sudo( 'echo "disabled: True" >> applications/welcome/DISABLED',
                              user=server.w3_user )


    #----------------------------------------------------------------------
    def create_site_available( self ):
        srv_ctx = self.get_server_context()
        server = srv_ctx.server
        local_server = srv_ctx.local_server
        srv_name = 'w2p_%s_%s' % ( self.cluster_name,
                                   self.server_name.replace( '.', '_' ) )
        d = { 'server_host': self.server_name,
              'server_name': srv_name,
              'srv_base_folder': srv_ctx.get_abs_w2p_folder( self.cluster_name ),
              'w3_user': server.w3_user }
        sub_domain_cfg = '''
    <VirtualHost *:80>
      ServerName %(server_host)s
      Redirect permanent / https://%(server_host)s/
    </VirtualHost>

    <VirtualHost *:443>
      ServerName %(server_host)s

      SSLEngine on
    ''' % d

        if self.self_signed_cert:
            sub_domain_cfg += '''
      SSLCertificateFile /etc/apache2/ssl/self_signed.cert
      SSLCertificateKeyFile /etc/apache2/ssl/self_signed.key
    '''
        else:
            sub_domain_cfg += '''
      SSLCertificateFile /etc/apache2/ssl/multidomain.m16e.com.cert
      SSLCertificateKeyFile /etc/apache2/ssl/multidomain.m16e.com.key
      SSLCACertificateFile /etc/apache2/ssl/multidomain.m16e.com.ca-bundle
      Header always set Strict-Transport-Security "max-age=15768000;"
      SetEnvIf User-Agent ".*MSIE.*" nokeepalive ssl-unclean-shutdown

    '''

        sub_domain_cfg += '''
      WSGIDaemonProcess %(server_name)s user=www-data group=www-data threads=5 processes=6
      WSGIProcessGroup %(server_name)s
      WSGIScriptAlias / %(srv_base_folder)s/web2py/current/wsgihandler.py
    ''' % d

        sub_domain_cfg += '''
      WSGIApplicationGroup %{GLOBAL}
    '''
        sub_domain_cfg += '''
      DocumentRoot %(srv_base_folder)s/web2py/current/applications/wiki

      Options +FollowSymLinks

      <Directory %(srv_base_folder)s/web2py/current/>
        AllowOverride None
        Order Allow,Deny
        Deny from all
        <Files wsgihandler.py>
          Allow from all
        </Files>
      </Directory>

      AliasMatch ^/([^/]+)/static/(?:_[\d]+.[\d]+.[\d]+/)?(.*) \
            %(srv_base_folder)s/web2py/current/applications/$1/static/$2

      <Directory %(srv_base_folder)s/web2py/current/applications/*/static/>
        Options -Indexes
        ExpiresActive On
        ExpiresDefault "access plus 1 hour"
        Order Allow,Deny
        Allow from all
      </Directory>

      #<LocationMatch ^/([^/]+)/appadmin>
      #  Deny from all
      #</LocationMatch>

      CustomLog /var/log/apache2/%(server_name)s-access.log common
      ErrorLog /var/log/apache2/%(server_name)s-error.log
    </VirtualHost>
        ''' % d

        with settings( host_string=server.get_user_host_string(),
                       password=server.password ):
            src_cfg_folder = '/home/%s/tmp' % local_server.user
            src_cfg_file = '%s/%s' % (src_cfg_folder, self.server_name)
            term.printDebug( 'src_cfg_folder: %s' % src_cfg_folder )
            term.printDebug( 'src_cfg_file: %s' % src_cfg_file )
            with lcd( src_cfg_folder ):
                f = open( src_cfg_file, 'w' )
                f.write( sub_domain_cfg )
                f.close()
            if not files.exists( 'tmp' ):
                cli_run( 'mkdir -p tmp' )
            put( src_cfg_file, 'tmp/%s' % self.server_name )
            remote_src_cfg_file = '/home/%s/tmp/%s' % ( server.user,
                                                        self.server_name )
            term.printDebug( 'remote_src_cfg_folder: %s' % remote_src_cfg_file )
            cli_sudo_run( 'mv %s /etc/apache2/sites-available/' % remote_src_cfg_file,
                          password=server.password )
            with cd( '/etc/apache2/sites-enabled' ):
                cli_sudo_run( 'rm -f %s' % (self.server_name),
                              password=server.password )
                cli_sudo_run( 'ln -s /etc/apache2/sites-available/%s %s'
                              % (self.server_name, self.server_name),
                              password=server.password )

    #----------------------------------------------------------------------
    def drop_site_available( self ):
        srv_ctx = self.get_server_context()
        server = srv_ctx.server
        with settings( host_string=server.get_user_host_string(),
                       password=server.password ):
            with cd( '/etc/apache2/sites-enabled' ):
                cli_sudo_run( 'rm -f %s' % (self.server_name),
                              password=server.password )
            with cd( '/etc/apache2/sites-available' ):
                cli_sudo_run( 'rm -f %s' % (self.server_name),
                              password=server.password )

    #------------------------------------------------------------------
    def __repr__( self ):
        s = '%s (Cluster){\n' % repr( self.cluster_name )
        for a in self.__dict__:
            if a == 'parent':
                continue
            s += '    %s: %s\n' % (repr( a ), repr( self.__dict__[a] ) )
#             s += '    %s: %s\n' % (repr( a ), pp.pformat( self.__dict__[a] ) )
        s += '  }'
        return s
    #----------------------------------------------------------------------

#----------------------------------------------------------------------
