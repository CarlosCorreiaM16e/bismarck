#! /usr/bin/python


import datetime
from fabric.colors import magenta
from fabric.context_managers import settings, hide, cd, lcd, char_buffered
from fabric.contrib import files
from fabric.operations import run, sudo, local, put
import os
import sys

from bismarck_cli.utils import term
from bismarck_cli.utils.storage import Storage
from bismarck_cli.utils.ui_utils import cli_run, cli_sudo_run, cli_local
from bismarck_cli.vcs.hg import HgServer
from bismarck_cli.vcs.vcs import get_vcs_server


DATE = datetime.date

#----------------------------------------------------------------------
class CurrentServer( object ):
    #----------------------------------------------------------------------
    def __init__( self, srv_ctx ):
        self.srv_ctx = srv_ctx

#     #----------------------------------------------------------------------
#     def apache_config( self ):
#         server = self.srv_ctx.server
#         apache_mod = [ 'ssl',
#                        'proxy',
#                        'headers',
#                        'expires',
#                        'wsgi' ]
#         with settings( host_string=server.get_user_host_string(),
#                        password=server.password ):
#             for m in apache_mod:
#                 cli_sudo_run( 'a2enmod %s' % m,
#                               password=server.password )
#
#     #----------------------------------------------------------------------
#     def create_certificate( self ):
#         server = self.srv_ctx.server
#         cmd_list = [ 'mkdir -p /etc/apache2/ssl',
#                      'openssl genrsa 1024 > /etc/apache2/ssl/self_signed.key',
#                      'chmod 400 /etc/apache2/ssl/self_signed.key',
#                      'openssl req -new -x509 -nodes -sha1 -days 365 -key /etc/apache2/ssl/self_signed.key > /etc/apache2/ssl/self_signed.cert',
#                      'openssl x509 -noout -fingerprint -text < /etc/apache2/ssl/self_signed.cert > /etc/apache2/ssl/self_signed.info'
#                      ]
#
#         with settings( host_string=server.get_user_host_string(),
#                        password=server.password ):
#             with char_buffered( sys.stdin ):
#                 for cmd in cmd_list:
#                     cli_sudo_run( cmd,
#                                   password=server.password )
#
#     #----------------------------------------------------------------------
#     def postgres_config( self ):
#         server = self.srv_ctx.server
#         with settings( host_string=server.get_user_host_string(),
#                        password=server.password ):
#             cli_sudo_run( 'sudo -u postgres createuser -s %(user)s' %
#                           { 'user': server.user },
#                           password=server.password )
#             cli_sudo_run( 'sudo -u postgres createuser -s %(db_user)s' %
#                           { 'db_user': server.db_user },
#                           password=server.password )
#             cli_run( 'createdb %(user)s' %
#                           { 'user': server.user } )
#             cli_run( 'createdb -O %(db_user)s %(db_user)s' %
#                           { 'db_user': server.db_user } )
#             cli_run( '''psql -c "alter user %(user)s password '%(password)s'" ''' %
#                           { 'user': server.user,
#                             'password': server.password } )
#
#     #----------------------------------------------------------------------
#     def mercurial_config( self ):
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
#                 files.append( hg_file, hg_text, use_sudo=True )
#
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
#                 if not files.exists( '/var/www/.hgignore',
#                                         use_sudo=True ):
#                     cli_sudo_run( 'ln -s /home/%(w3_user)s/.hgignore .hgignore' % d,
#                                   password=server.password )
#
#     #----------------------------------------------------------------------
#     def init_server_folders( self ):
#         server = self.srv_ctx.server
#         bash_file = '.bashrc'
#         bash_text_list = [ "alias l='ls -l'",
#                            "alias la='ls -al'",
#                            "alias lh='ls -lh'" ]
#         with settings( host_string=server.get_user_host_string() ):
#             for bash_text in bash_text_list:
#                 files.append( bash_file, bash_text )
#         bash_file = '/root/.bashrc'
#         with settings( host_string=server.get_user_host_string(),
#                        password=server.password ):
#             for bash_text in bash_text_list:
#                 files.append( bash_file, bash_text, use_sudo=True )
#
# # #             term.printDebug( 'repo: %s' % repr( srv_def.repo ) )
#             d = { 'w3_user': server.w3_user,
#                   'dest': '/home/%s' % server.w3_user }
#             term.printDebug( 'd: %s' % repr( d ) )
#
#             cli_sudo_run( 'mkdir -p %(dest)s/bin' % d,
#                           password=server.password )
#             cli_sudo_run( 'mkdir -p %(dest)s/tmp' % d,
#                           password=server.password )
#             cli_sudo_run( 'chown -R %(w3_user)s.  %(dest)s' % d,
#                           password=server.password )


#     #----------------------------------------------------------------------
#     def init_web2py( self, cluster_name ):
#         term.printDebug( 'cluster_name: %s' % cluster_name )
#         web_repo = self.srv_ctx.get_web_repo( cluster_name=cluster_name )
#         home_folder = web_repo.get_home_folder()
#         base_folder = web_repo.get_base_folder()
#         w2p_folder = '%s/%s/web2py' % ( home_folder, base_folder )
#         server = self.srv_ctx.server
#         with settings( host_string=server.get_user_host_string(),
#                        password=server.password ):
#             release_folder = '%s/releases' % w2p_folder
#             sudo( 'mkdir -p %s' % release_folder )
#             sudo( 'chown -R %s. %s' % ( server.w3_user, w2p_folder ) )
#             w2p_repo = self.srv_ctx.web2py.repo
#             w2p_rel = self.srv_ctx.web2py.release
#             with cd( w2p_folder ):
#                 with cd( 'releases' ):
#                     sudo( 'hg clone -r %(release)s %(w2p_repo)s %(release)s' %
#                           { 'w2p_repo': w2p_repo,
#                             'release': w2p_rel },
#                           user=server.w3_user )
#                     with cd( w2p_rel ):
#                         sudo( 'cp %s/.hgignore .' % home_folder,
#                               user=server.w3_user )
#                         sudo( 'cat %s/.hgrc_hooks >> .hg/hgrc' % home_folder,
#                               user=server.w3_user )
#                         sudo( 'cp handlers/wsgihandler.py .',
#                               user=server.w3_user )
#                         sudo( 'python -c "from gluon.widget import console; console();"',
#                               user=server.w3_user )
#                         sudo( '''python -c "from gluon.main import save_password; save_password(raw_input('admin password: '),443)" ''',
#                               user=server.w3_user )
#
#                 sudo( 'rm -f current' )
#                 sudo( 'ln -s releases/%s current' % w2p_rel,
#                       user=server.w3_user )
#
#     #----------------------------------------------------------------------
#     def install_deps( self ):
#         server = self.srv_ctx.server
#         pkg_list = [ 'apache2',
#                      'default-jdk',
#                      'ipython',
#                      'libapache2-mod-wsgi',
#                      'libpostgresql-jdbc-java',
#                      'mercurial',
#                      'postgresql',
#                      'postgresql-plpython-9.1 ',
#                      'pylint',
#                      'python-crypto',
#                      'python-dateutil',
#                      'python-docutils',
#                      'python-fixtures',
#                      'python-httplib2',
#                      'python-imaging',
#                      'python-lxml',
#                      'python-m2crypto',
#                      'python-magic',
#                      'python-matplotlib',
#                      'python-reportlab',
#                      'python-pip',
#                      'python-psycopg2',
#                      'python-setuptools',
#                      'python-simplejson',
#                      'python-xlwt',
#                      'tree',
#                      'unzip',
#                      'vim',
#                      'wget',
#                      'zip'
#                      ]
#         term.printDebug( 'user_host_string: %s' % server.get_user_host_string() )
#         with settings( host_string=server.get_user_host_string(),
#                        password=server.password ):
#             self.do_server_upgrade()
#     #         cli_sudo_run( 'apt-get update && apt-get upgrade -y',
#     #                       password=_server.password )
#             install = ' '.join( pkg_list )
#             term.printDebug( 'install: %s' % repr( install ) )
#             cli_sudo_run( 'apt-get install -y %s' % install,
#                           password=server.password )

    #----------------------------------------------------------------------
    def do_server_upgrade( self, dist_upgrade=False ):
        server = self.srv_ctx.server
        term.printDebug( 'server: %s' % repr( server ) )
        with settings( host_string=server.get_user_host_string(),
                       password=server.password ):
            cli_sudo_run( 'apt-get update && apt-get upgrade',
                          password=server.password )
            if dist_upgrade:
                cli_sudo_run( 'apt-get dist-upgrade',
                              password=server.password )
                return True
        return False

#     #----------------------------------------------------------------------
#     def apache_add_site_available( self, cluster_name='take5' ):
#         web_repo = self.srv_ctx.get_web_repo( cluster_name=cluster_name )
#         home_folder = web_repo.get_home_folder()
#         base_folder = web_repo.get_base_folder()
#         w2p_folder = '%s/%s/web2py' % ( home_folder, base_folder )
#         server = self.srv_ctx.server
#         d = { 'server_host': server.host,
#               'server_name': server.name,
#               'srv_base_folder': w2p_folder,
#               'w3_user': server.w3_user }
#         sub_domain_cfg = '''
#     <VirtualHost *:80>
#       ServerName %(server_host)s
#       Redirect permanent / https://%(server_host)s/
#     </VirtualHost>
#
#     <VirtualHost *:443>
#       ServerName %(server_host)s
#
#       SSLEngine on
#       SSLCertificateFile /etc/apache2/ssl/self_signed.cert
#       SSLCertificateKeyFile /etc/apache2/ssl/self_signed.key
#
#       WSGIDaemonProcess w2p_%(server_name)s user=www-data group=www-data threads=5 processes=6
#       WSGIProcessGroup w2p_%(server_name)s
#       WSGIScriptAlias / %(srv_base_folder)s/current/wsgihandler.py
#     ''' % d
#
#         sub_domain_cfg += '''
#       WSGIApplicationGroup %{GLOBAL}
#     '''
#         sub_domain_cfg += '''
#       DocumentRoot %(srv_base_folder)s/current/applications/wiki
#
#       Options +FollowSymLinks
#
#       <Directory %(srv_base_folder)s/current/>
#         AllowOverride None
#         Order Allow,Deny
#         Deny from all
#         <Files wsgihandler.py>
#           Allow from all
#         </Files>
#       </Directory>
#
#       AliasMatch ^/([^/]+)/static/(?:_[\d]+.[\d]+.[\d]+/)?(.*) \
#             %(srv_base_folder)s/current/applications/$1/static/$2
#
#       <Directory %(srv_base_folder)s/current/applications/*/static/>
#         Options -Indexes
#         ExpiresActive On
#         ExpiresDefault "access plus 1 hour"
#         Order Allow,Deny
#         Allow from all
#       </Directory>
#
#       #<LocationMatch ^/([^/]+)/appadmin>
#       #  Deny from all
#       #</LocationMatch>
#
#       CustomLog /var/log/apache2/t5-access.log common
#       ErrorLog /var/log/apache2/t5-error.log
#     </VirtualHost>
#         ''' % d
#
#         with settings( host_string=server.get_user_host_string(),
#                        password=server.password ):
#             user_home = '/home/%s/tmp' % server.user
#             cli_run( 'mkdir -p %s/tmp' % user_home )
#             with cd( '%s/tmp' % user_home ):
#                 f = open( '%s/tmp/%s' % (user_home, server.host),
#                           'w' )
#                 f.write( sub_domain_cfg )
#                 f.close()
#             sudo( 'cp %s/%s /etc/apache2/sites-available/' % (user_home, server.host) )
#             with cd( '/etc/apache2/sites-enabled' ):
#                 sudo( 'rm -f %s' % (server.host) )
#                 sudo( 'ln -s /etc/apache2/sites-available/%s %s'
#                       % (server.host, server.host) )
#
#     #----------------------------------------------------------------------
#     def do_deploy_jprinter( self ):
#         server = self.srv_ctx.server
#         user_home = '/home/%s' % server.user
#         w3_home = '/home/%s' % server.w3_user
#         with settings( host_string=server.get_user_host_string(),
#                        password=server.password ):
#             with lcd( os.path.expanduser( '~' ) ):
#                 local( 'tar jcvf tmp/jprinter.bz2 bin/jprinter' )
#                 put( 'tmp/jprinter.bz2', 'tmp' )
#
#             with cd( w3_home ):
#                 sudo( 'mkdir -p bin',
#                       user=server.w3_user )
#                 sudo( 'tar jxvf %s/tmp/jprinter.bz2' % user_home )
#                 sudo( 'chown -R %s. bin' % ( server.w3_user ) )

    #----------------------------------------------------------------------
    def get_disk_usage( self ):
        server = self.srv_ctx.server
        usage = Storage()
        template = 'export LANG=C; %s'
        with settings( host_string=server.get_user_host_string(),
                       password=server.password ):
#             with settings( hide( 'running', 'stderr', 'stdout', 'warnings' ),
#                            warn_only = True ):
#                 print( blue( 'free space:' ) )
            usage.total = run( template % 'df -h' )
#             usage.total = cli_run( template % 'df -h' )
            term.printDebug( 'usage.total: %s' % ( usage.total ) )
#             ret = run( template % 'du -h tmp/*' )
            usage.user_tmp = run( template % 'du -h /home/carlos/tmp' )
#                 print( magenta( 'used in /tmp:' ) )
            usage.root_tmp = run( template % 'du -h /tmp' )

            usage.web_tmp = sudo( template % 'du -h /home/' + server.w3_user + '/tmp' )
#         term.printDebug( 'usage.keys: %s' % ( usage.keys() ) )
        return usage

    #----------------------------------------------------------------------
    def archive_local_backups( self ):
        today = DATE.today()
        server = self.srv_ctx.server
        with lcd( server.backup_local ):
            ret = cli_local( 'ls -d %s*' % server.backup_prefix, capture=True )
            folder_list = ret.split()
            for folder in folder_list:
                fparts = folder.split( '-' )
                year = int( fparts[ 2 ] )
                month = int( fparts[ 3 ] )
                day = int( fparts[ 4 ] )
                if day in ( 1, 15 ):
                    ret = cli_local( 'mv %s monthly/' % folder, capture=False )
                else:
                    delete = False
                    if year < today.year and today.month > 1:
                        delete = True
                    elif month < today.month -1:
                        delete = True
                    print( 'deleting %s' % folder )

    #----------------------------------------------------------------------
    def archive_remote_backups( self ):
        server = self.srv_ctx.server

#         with settings( host_string=server.get_user_host_string(),
#                        password=server.password ):
#             with cd( server.backup_remote ):
#                 cli_run( 'mv t5-bak-????-??-01-* monthly' )
#                 until_day = DATE.today()
#                 until_day = DATE( until_day.year, until_day.month, 1 )
#                 with hide( 'everything' ), settings( warn_only=True ):
#                     ret = cli_run( 'ls t5-bak-*')
#                     folder_list = sorted( ret.split() )
#     #                         term.printDebug( 'folder_list: %s' % repr( rel_list ) )
#
#                     folder_count = len( folder_list )
#                     del_list = []
#                     print( magenta( '(%d folders)' % folder_count ) )
#                     for f in folder_list:
#                         if
#                         color, rel_folder, status = \
#                             _get_folder_age( r,
#                                              preserve_since,
#                                              folder_count,
#                                              int( min_left ),
#                                              i )
#                         if status == 'D':
#                             del_list.append( r )
#                         print( color( rel_folder ) )
#                     if del_list and fabconsole.confirm( 'Delete marked?',
#                                                         default=True ):
#         #                 run( 'pwd' )
#         #                 for r in del_list:
#         #                     print( r )
#                         for r in del_list:
#         #                     print( 'removing %s' % r )
#                             run( 'rm -rf %s' % r )
#
#                 cli_run( 'rm -r t5-bak-????-??-01-* monthly' )

    #----------------------------------------------------------------------
    def apache_ctl( self, action ):
        if not action in [ 'start', 'stop', 'restart' ]:
            raise Exception( 'improper action: %s' % repr( action ) )
        server = self.srv_ctx.server
        with settings( host_string=server.get_user_host_string(),
                       password=server.password ):
            cli_sudo_run( '/etc/init.d/apache2 %s' % action,
                          password=server.password )

    #----------------------------------------------------------------------

