#! /usr/bin/python

from fabric.api import settings
from fabric.colors import blue, magenta
from fabric.context_managers import char_buffered, hide, lcd
from fabric.contrib import files
from fabric.operations import local, put, run, sudo
import os
import sys

from bismarck_cli.utils import term
from bismarck_cli.utils.storage import Storage
from bismarck_cli.utils.ui_utils import cli_sudo_run, cli_run


#----------------------------------------------------------------------
class Installer( object ):
    tag = 'installer'
    installer_name = None
    #----------------------------------------------------------------------
    def __init__( self, srv_ctx, ):
        self.srv_ctx = srv_ctx
#         term.printDebug( 'srv_ctx: %s' % repr( self.srv_ctx ) )

    #----------------------------------------------------------------------
    def get_server_context( self ):
        return self.srv_ctx

    #----------------------------------------------------------------------
    def get_server( self ):
        srv_ctx = self.get_server_context()
        return srv_ctx.server

    #----------------------------------------------------------------------
    def apache_a2enmod( self ):
        server = self.get_server()
        apache_mod = [ 'ssl',
                       'proxy',
                       'headers',
                       'expires',
                       'wsgi' ]
        with settings( host_string=server.get_user_host_string(),
                       password=server.password ):
            for m in apache_mod:
                cli_sudo_run( 'a2enmod %s' % m,
                              password=server.password )

    #------------------------------------------------------------------
    def purge_deps_packages( self ):
        server = self.get_server()
        pkg_list = [ 'apache2*',
                     'default-jdk',
                     'openjdk-6-jdk*',
                     'ipython',
                     'libapache2-mod-wsgi',
                     'libpostgresql-jdbc-java',
                     'mercurial*',
                     'postgresql*',
                     'pylint',
                     'python-crypto',
                     'python-dateutil',
                     'python-docutils',
                     'python-fixtures',
                     'python-httplib2',
                     'python-imaging',
                     'python-lxml',
                     'python-m2crypto',
                     'python-magic',
                     'python-matplotlib',
                     'python-reportlab',
                     'python-pip',
                     'python-psycopg2',
                     'python-setuptools',
                     'python-simplejson',
                     'python-xlwt'
                     ]
        term.printDebug( 'user_host_string: %s' % server.get_user_host_string() )
        with settings( host_string=server.get_user_host_string(),
                       password=server.password ):
            self.do_server_upgrade()
    #         cli_sudo_run( 'apt-get update && apt-get upgrade -y',
    #                       password=_server.password )
            purge = ' '.join( pkg_list )
            term.printDebug( 'purge: %s' % repr( purge ) )
            cli_sudo_run( 'apt-get remove --purge %s' % purge,
                          password=server.password )
            cli_sudo_run( 'apt-get autoremove',
                          password=server.password )


    #------------------------------------------------------------------
    def install_deps( self ):
        server = self.get_server()
        pkg_list = [ 'apache2',
                     'default-jdk',
                     'ipython',
                     'libapache2-mod-wsgi',
                     'libpostgresql-jdbc-java',
                     'mercurial',
                     'ntp',
                     'postgresql',
                     'postgresql-plpython-9.1 ',
                     'pylint',
                     'python-crypto',
                     'python-dateutil',
                     'python-docutils',
                     'python-fixtures',
                     'python-httplib2',
                     'python-imaging',
                     'python-lxml',
                     'python-m2crypto',
                     'python-magic',
                     'python-matplotlib',
                     'python-reportlab',
                     'python-pip',
                     'python-psycopg2',
                     'python-setuptools',
                     'python-simplejson',
                     'python-xlrd',
                     'python-xlwt',
                     'tree',
                     'unzip',
                     'vim',
                     'wget',
                     'zip'
                     ]
        term.printDebug( 'user_host_string: %s' % server.get_user_host_string() )
        with settings( host_string=server.get_user_host_string(),
                       password=server.password ):
            self.do_server_upgrade()
    #         cli_sudo_run( 'apt-get update && apt-get upgrade -y',
    #                       password=_server.password )
            install = ' '.join( pkg_list )
            term.printDebug( 'install: %s' % repr( install ) )
            cli_sudo_run( 'apt-get install %s' % install,
                          password=server.password )

    #----------------------------------------------------------------------
    def do_server_upgrade( self, dist_upgrade=False ):
        server = self.get_server()
        term.printDebug( 'server: %s' % repr( server ) )
        with settings( host_string=server.get_user_host_string(),
                       password=server.password ):
            cli_sudo_run( 'apt-get update && apt-get upgrade -y',
                          password=server.password )
            if dist_upgrade:
                cli_sudo_run( 'apt-get dist-upgrade',
                              password=server.password )
                return True
        return False

    #----------------------------------------------------------------------
    def create_certificate( self):
        server = self.get_server()
        cmd_list = [ 'mkdir -p /etc/apache2/ssl',
                     'openssl genrsa 1024 > /etc/apache2/ssl/self_signed.key',
                     'chmod 400 /etc/apache2/ssl/self_signed.key',
                     'openssl req -new -x509 -nodes -sha1 -days 365 -key /etc/apache2/ssl/self_signed.key > /etc/apache2/ssl/self_signed.cert',
                     'openssl x509 -noout -fingerprint -text < /etc/apache2/ssl/self_signed.cert > /etc/apache2/ssl/self_signed.info'
                     ]

        with settings( host_string=server.get_user_host_string(),
                       password=server.password ):
            if files.exists( '/etc/apache2/ssl',
                             use_sudo=True ):
                return 'Folder exists: /etc/apache2/ssl/'
            with char_buffered( sys.stdin ):
                for cmd in cmd_list:
                    cli_sudo_run( cmd,
                                  password=server.password )
        return ''

    #----------------------------------------------------------------------
    def deploy_jprinter( self ):
        srv_ctx = self.get_server_context()
        server = self.get_server()
        with settings( host_string=server.get_user_host_string(),
                       password=server.password ):
            with lcd( os.path.expanduser( '~' ) ):
                local( 'tar jcvf tmp/jprinter.bz2 bin/jprinter' )
                put( 'tmp/jprinter.bz2', 'tmp' )
            home_folder = '/home/%s' % server.w3_user
            cli_sudo_run( 'mkdir -p %s/bin' % home_folder,
                          password=server.password )
            run( 'tar jxvf tmp/jprinter.bz2' )
            cli_sudo_run( 'cp -R bin/jprinter %s/bin' % ( home_folder ),
                          password=server.password )
            sudo( 'chown -R %s. %s/bin' % ( server.w3_user, home_folder ) )

    #----------------------------------------------------------------------
    def pg_config( self ):
        server = self.get_server()
        with settings( host_string=server.get_user_host_string(),
                       password=server.password ):
            ret = cli_sudo_run( 'sudo -u postgres psql -l',
                                password=server.password )
            if server.user in ret:
                return 'User DB already exists: %s' % server.user

            cli_sudo_run( 'sudo -u postgres createuser -s %(user)s' %
                          { 'user': server.user },
                          password=server.password )
            cli_sudo_run( 'sudo -u postgres createuser -s %(db_user)s' %
                          { 'db_user': server.db_user },
                          password=server.password )
            cli_run( 'createdb %(user)s' %
                          { 'user': server.user } )
            cli_run( 'createdb -O %(db_user)s %(db_user)s' %
                          { 'db_user': server.db_user } )
        return ''

    #----------------------------------------------------------------------
    def pg_define_password( self ):
        server = self.get_server()
        with settings( host_string=server.get_user_host_string(),
                       password=server.password ):
            ret = cli_sudo_run( 'sudo -u postgres psql -l',
                                password=server.password )
            if not server.user in ret:
                return 'User DB does not exist: %s' % server.user

            cli_run( '''psql -c "alter user %(user)s password '%(password)s'" ''' %
                          { 'user': server.user,
                            'password': server.password } )
            cli_run( '''psql -c "alter user %(user)s password '%(password)s'" ''' %
                          { 'user': server.db_user,
                            'password': server.password } )
        return ''

    #----------------------------------------------------------------------
    def do_setup_scheduler( self ):
        sch_cfg = '''#!/bin/sh
DAEMON=/opt/bin/python2.7
PARAMETERS="/opt/web-apps/web2py/web2py.py -K cpfecys"
LOGFILE=/var/log/web2py-scheduler-cpfecys.log

start() {
    echo -n "starting up $DAEMON"
    RUN=`$DAEMON $PARAMETERS > $LOGFILE 2>&1`
    if [ "$?" -eq 0 ]; then
        echo " Done."
    else
        echo " FAILED."
    fi
}
stop() {
    killall $DAEMON
}
status() {
    killall -0 $DAEMON
    if [ "$?" -eq 0 ]; then
        echo "Running."
    else
        echo "Not Running."
    fi
}
case "$1" in
    start)
        start
        ;;
    restart)
        stop
        sleep 2
        start
        ;;
    stop)
        stop
        ;;
    status)
        status
        ;;
    *)
        echo "usage : $0 start|restart|stop|status"
    ;;
esac
exit 0
'''

    #------------------------------------------------------------------
#----------------------------------------------------------------------
def get_installer( srv_ctx, installer_name ):
    from bismarck_cli.installers.belmiro import BelmiroInstaller
    from bismarck_cli.installers.take5 import Take5Installer
    if installer_name == BelmiroInstaller.installer_name:
        return BelmiroInstaller( srv_ctx )
    if installer_name == Take5Installer.installer_name:
        return Take5Installer( srv_ctx )

    raise Exception( 'Unknown installer: %s' % installer_name )

#----------------------------------------------------------------------
