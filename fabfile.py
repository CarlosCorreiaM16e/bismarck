# -*- coding: utf-8 -*-

# template fabfile

import datetime
from fabric.colors import blue, magenta, green, cyan, red
from fabric.context_managers import settings, cd, lcd
from fabric.contrib import console
from fabric.operations import local, prompt, run, sudo
import sys

from bismarck_cli.installers.installer import Installer
from bismarck_cli.servers import srv_factory
from bismarck_cli.servers.current_server import CurrentServer
from bismarck_cli.utils import term
from bismarck_cli.utils.misc import get_top_du
from bismarck_cli.vcs.vcs import VcsServer
from bismarck_cli.installers.apps import belmiro_app


DT = datetime.datetime

#------------------------------------------------------------------
def _get_server( server_name ):
    sf = srv_factory.get_server_def( server_name )
    return sf

#------------------------------------------------------------------
def echo_vars( server_name, cluster_name, app_name ):
    '''
    echo_vars( server_name, app_name ): display vars
    '''
    curr_app = _get_current_app( server_name, cluster_name, app_name )
    db_name = curr_app.get_app_db_name()
#     srv_def = _get_server( server_name )
    srv_def = curr_app.srv_ctx

    echo = '''
    LOCAL:
        home_folder: %(home_folder)s
        base_folder: %(base_folder)s
        rel_app_folder:  %(rel_app_folder)s
        abs_app_folder:  %(abs_app_folder)s
        database: %(db_name)s
    ''' % { 'home_folder': srv_def.get_local_home_folder(),
            'base_folder': srv_def.get_local_base_folder( cluster_name ),
            'rel_app_folder': srv_def.get_rel_local_folder( cluster_name, app_name ),
            'abs_app_folder': srv_def.get_abs_local_folder( cluster_name, app_name ),
            'db_name': db_name
           }
    print( blue( echo ) )

    echo = '''
    REPO:
        home_folder: %(home_folder)s
        base_folder: %(base_folder)s
        rel_app_folder:  %(rel_app_folder)s
        abs_app_folder:  %(abs_app_folder)s
    ''' % { 'home_folder': srv_def.get_remote_home_folder(),
            'base_folder': srv_def.get_remote_base_folder( cluster_name ),
            'rel_app_folder': srv_def.get_rel_remote_folder( cluster_name, app_name ),
            'abs_app_folder': srv_def.get_abs_remote_folder( cluster_name, app_name ),
           }
    print( blue( echo ) )

    echo = '''
    WEB:
        home_folder: %(home_folder)s
        base_folder: %(base_folder)s
        rel_app_folder:  %(rel_app_folder)s
        abs_app_folder:  %(abs_app_folder)s
    ''' % { 'home_folder': srv_def.get_web_home_folder(),
            'base_folder': srv_def.get_web_base_folder( cluster_name ),
            'rel_app_folder': srv_def.get_rel_web_folder( cluster_name, app_name ),
            'abs_app_folder': srv_def.get_abs_web_folder( cluster_name, app_name ),
           }
    print( blue( echo ) )

#------------------------------------------------------------------
def list_apps( server_name ):
    '''
    list_apps( server_name )
    '''
    from bismarck_cli.utils.misc import get_padded_str

    srv_def = _get_server( server_name )
    len_app_name = 16
    len_cluster_name = 12
    len_db_name = 16
    l = get_padded_str( 'App.', len_app_name )
    l += ' ' + get_padded_str( 'Cluster', len_cluster_name )
    l += ' ' + get_padded_str( 'Database', len_db_name )
    print( blue( l ) )
    for app_name in srv_def.app_dict:
        cluster = srv_def.get_cluster( app_name=app_name )
        cluster_name = '?'
        if cluster:
            cluster_name = cluster.cluster_name
        db_name = srv_def.databases.get( app_name ) or '?'
        l = get_padded_str( app_name, len_app_name )
        l += ' ' + get_padded_str( cluster_name, len_cluster_name )
        l += ' ' + get_padded_str( db_name, len_db_name )
        print( blue( l ) )


#------------------------------------------------------------------
def list_clusters( server_name ):
    '''
    list_clusters( server_name )
    '''
    from bismarck_cli.utils.misc import get_padded_str

    srv_def = _get_server( server_name )
    len_cluster_name = 12
    len_installer_name = 10
    len_vcs_name = 6
    l = get_padded_str( 'Cluster', len_cluster_name )
    l += ' ' + get_padded_str( 'Installer', len_installer_name )
    l += ' ' + get_padded_str( 'VCS', len_vcs_name )
    l += ' App. list'
    print( blue( l ) )
    for cluster_name in srv_def.clusters.clusters:
        cluster = srv_def.clusters.clusters[ cluster_name ]
        installer_name = cluster.installer.installer_name
        vcs_name = cluster.vcs_server.vcs_app_name
        app_list = ', '.join( cluster.apps )
        l = get_padded_str( cluster_name, len_cluster_name )
        l += ' ' + get_padded_str( installer_name, len_installer_name )
        l += ' ' + get_padded_str( vcs_name, len_vcs_name )
        l += ' ' + app_list
        print( blue( l ) )

#------------------------------------------------------------------
def _get_current_app( server_name, cluster_name, app_name ):
    '''
    _get_current_app( server_name, cluster_name, app_name ):
    '''
    from bismarck_cli.servers.current_app import CurrentApp
    srv_ctx = _get_server( server_name )
    cur_app = CurrentApp( srv_ctx, cluster_name, app_name )
    return cur_app

#------------------------------------------------------------------
def get_local_status( server_name, cluster_name, app_name ):
    '''
    get_local_status( server_name, cluster_name, app_name ):
    '''
    curr_app = _get_current_app( server_name, cluster_name, app_name )
    status = curr_app.get_status( 'local' )
    term.printDebug( 'status: %s' % status )
    print( blue( status ) )

#------------------------------------------------------------------
def get_remote_status( server_name, cluster_name, app_name ):
    '''
    get_remote_status( server_name, cluster_name, app_name ):
    '''
    curr_app = _get_current_app( server_name, cluster_name, app_name )
    status = curr_app.get_status( 'remote' )
    print( blue( status ) )

#------------------------------------------------------------------
def get_web_status( server_name, cluster_name, app_name ):
    '''
    get_web_status( server_name, cluster_name, app_name ):
    '''
    curr_app = _get_current_app( server_name, cluster_name, app_name )
    status = curr_app.get_status( 'web' )
    print( blue( status ) )

#------------------------------------------------------------------
def list_outgoing( server_name, app_name ):
    '''
    list_outgoing( server_name, app_name ):
    '''
    srv_def = _get_server( server_name )

#------------------------------------------------------------------
# SERVER APPS MANAGEMENT
#------------------------------------------------------------------
def list_disk_usage( server_name ):
    '''
    list_disk_usage( server_name )
    '''
    srv_ctx = _get_server( server_name )
    curr_srv = CurrentServer( srv_ctx )
    usage = curr_srv.get_disk_usage()
#     term.printDebug( 'usage.keys: %s' % ( usage.keys() ) )
    print( blue( 'free space:' ) )
#     ret = cli_run( template % 'df -h' )
    term.printDebug( 'usage.total: %s' % ( usage.total ) )
    print( blue( usage.total ) )
    print( '' )
    print( magenta( 'used in ~/tmp:' ) )
#     ret = cli_run( template % 'du -h /home/carlos/tmp' )
    print( magenta( get_top_du( usage.user_tmp ) ) )

    print( magenta( 'used in /tmp:' ) )
#     ret = cli_run( template % 'du -h /tmp' )
    print( magenta( get_top_du( usage.root_tmp ) ) )

    print()
    print( 'web:' )
    print( magenta( 'used in ~web/tmp:' ) )
#     ret = cli_run( template % 'du -h tmp' )
    print( magenta( get_top_du( usage.web_tmp ) ) )

#------------------------------------------------------------------
# SERVER MANAGEMENT
#------------------------------------------------------------------
def update_app( server_name, cluster_name, app_name, auto_start=False ):
    '''
    update_app( server_name, cluster_name, app_name, auto_start=False )
    '''
    print( 'deploying %s' % ( app_name ) )

    curr_app = _get_current_app( server_name, cluster_name, app_name )
    local_status = curr_app.get_status( 'local' )
    print( blue( '\nLocal status:' ) )
    print( blue( local_status ) )

    srv_ctx = curr_app.srv_ctx
    curr_srv = CurrentServer( srv_ctx )
    master_status = curr_app.get_master_status( 'local' )
    if master_status:
        print( green( '\nMaster status:' ) )
        print( green( master_status ) )
        if console.confirm( 'Pull from master?', default=True ):
            abs_local_folder = srv_ctx.get_abs_local_folder( app_name )
            term.printDebug( 'abs_local_folder: %s' % repr( abs_local_folder ) )
            with lcd( abs_local_folder ):
                local( 'hgfarmer pull' )

            local_status = curr_app.get_status( 'local' )
            print( blue( '\nLocal status:' ) )
            print( blue( local_status ) )

    remote_status = curr_app.get_status( 'remote' )
    print( cyan( '\nRemote status:' ) )
    print( cyan( remote_status ) )

    web_status = curr_app.get_status( 'web' )
    print( magenta( '\nWeb status:' ) )
    print( magenta( web_status ) )

    cmd = prompt( '[P]ush [d]etails [c]ancel', default='p' )
    if cmd == 'd':
        for sd in curr_app.repo_list.web.status_detailed:
            print( magenta( str( sd ) ) )
        if console.confirm( 'Show diff?' ):
            ret = curr_app.repo_list.web.exec_single( 'hg diff' )
            print( ret )
            if console.confirm( 'Revert?', default=False ):
                ret = curr_app.repo_list.web.exec_single( 'hg revert -a' )
                print( ret )
        web_status = curr_app.get_status( 'web' )
        print( magenta( '\nWeb status:' ) )
        print( magenta( web_status ) )
        if console.confirm( 'Proceed to push?', default=True ):
            cmd = 'p'
    if cmd == 'p':
        DT = datetime.datetime
        ts = DT.now().strftime( '%Y-%m-%d-%H-%M' )
        (result, errors) = curr_app.push_to_remote( ts )
        if errors:
            print( red( errors ) )
            return
        curr_srv.apache_ctl( 'stop' )

        disabled = False
        if auto_start:
            curr_app.disable_app( ts )
        elif console.confirm( 'Disable app?', default=True ):
            disabled = True
            curr_app.disable_app( ts )
        curr_app.push_to_remote( ts )
        term.printDebug( 'pushed to remote' )
        curr_app.push_to_web( ts )

        curr_srv.apache_ctl( 'start' )
        if auto_start \
        or (disabled and console.confirm( 'Enable app?', default=True )):
            curr_app.enable_app()
#         deploy_and_compile_reports( server_name, app_name, w_type )

#
#     srv_ctx = _get_server( server_name )
#
#     status = _get_status( server_name, app_name, repo_type='local' )
# #     term.printDebug( 'status: %s' % status )
#     print( blue( 'Local status:' ) )
#     print( blue( status ) )
#
#     if app_name.startswith( 'blm_' ):
#         local_status = s_handler.hg_get_local_status( srv_def, 'belmiro' )
#         print( green( 'BELMIRO status:' ) )
#         print( green( local_status ) )
#         if fabconsole.confirm( 'Pull from master?', default=True ):
#             abs_local_folder = srv_def.get_abs_local_folder( app_name )
#             term.printDebug( 'abs_local_folder: %s' % repr( abs_local_folder ) )
#             with lcd( abs_local_folder ):
#                 local( 'hgfarmer pull' )
#
#
#     dev_status = s_handler.hg_get_dev_status( srv_def, app_name )
#     print( cyan( 'Development status:' ) )
#     print( cyan( dev_status ) )
#     web_status = s_handler.hg_get_web_status( srv_def, app_name, w_type )
#     print( magenta( 'Webserver status:' ) )
#     print( magenta( web_status ) )
#
# #     if fabconsole.confirm( 'Proceed to push?', default=True ):
#     cmd = prompt( '[P]ush [d]etails [d]ancel', default='p' )
#     if cmd == 'd':
#         ret = s_handler.do_show_hg_app_status( srv_def, app_name, w_type )
#         print( magenta( ret ) )
#         if console.confirm( 'Show diff?' ):
#             ret = s_handler.do_show_hg_app_diff( srv_def, app_name, w_type )
#             print( ret )
#             if console.confirm( 'Revert?', default=False ):
#                 ret = s_handler.do_revert_app_changes( srv_def, app_name, w_type )
#                 print( ret )
#         web_status = s_handler.hg_get_web_status( srv_def, app_name, w_type )
#         print( magenta( 'Webserver status:' ) )
#         print( magenta( web_status ) )
#         if fabconsole.confirm( 'Proceed to push?', default=True ):
#             cmd = 'p'
#     if cmd == 'p':
#         s_handler.hg_push_app_to_dev( srv_def, app_name )
#         s_handler.do_apache_srv( srv_def, 'stop' )
#         DT = datetime.datetime
#         ts = DT.now().strftime( '%Y-%m-%d-%H-%M' )
#         disabled = False
#         if auto_start:
#             s_handler.w2p_disable_app( srv_def, app_name, w_type, ts )
#         elif fabconsole.confirm( 'Disable app?', default=True ):
#             disabled = True
#             s_handler.w2p_disable_app( srv_def, app_name, w_type, ts )
#
#         s_handler.hg_push_app_to_web( srv_def, app_name, w_type, ts )
#         s_handler.do_apache_srv( srv_def, 'start' )
#         if auto_start \
#         or (disabled and fabconsole.confirm( 'Enable app?', default=True )):
#             s_handler.w2p_enable_app( srv_def, app_name, w_type )
#         deploy_and_compile_reports( server_name, app_name, w_type )

#------------------------------------------------------------------
def upgrade_app( server_name,
                 cluster_name,
                 app_name,
                 from_version,
                 to_version ):
    '''
    upgrade_app( server_name, cluster_name, app_name, from_version, to_version )
    '''
    from bismarck_cli.utils.ui_utils import set_prompt_continue, cli_sudo_run

    srv_ctx = _get_server( server_name )
    server = srv_ctx.server

    set_prompt_continue( False )
    d = { 'app_name': app_name,
          'from_version': from_version,
          'to_version': to_version }
    cmd = 'python web2py.py -i 127.0.0.1 -M -S '
    cmd += '%(app_name)s -R applications/%(app_name)s/private/resources/upgrades/' % d
    cmd += '%(to_version)s/upd_FROM_%(from_version)s.py' % d
    term.printDebug( 'cmd: %s' % repr( cmd ) )
    with settings( host_string=server.get_user_host_string(),
                   password=server.password ):
        abs_w2p_folder = srv_ctx.get_abs_w2p_folder( cluster_name )
        with cd( '%s/web2py/current' % abs_w2p_folder ):
            cli_sudo_run( 'pwd' )
            cli_sudo_run( cmd,
                          user=server.w3_user,
                          password=server.password )


#------------------------------------------------------------------
# DATABASES
#------------------------------------------------------------------
def pull_db( server_name,
             cluster_name,
             app_name,
             restore=True,
             folder='~/tmp/downloads',
             silently=False ):
    '''
    pull_db( server_name, cluster_name, app_name, restore=True, folder='~/tmp/downloads', silently=False )
    '''
    from bismarck_cli.databases import do_download_db
    srv_ctx = _get_server( server_name )
    do_download_db( srv_ctx,
                    cluster_name,
                    app_name,
                    folder,
                    restore=restore,
                    silently=False )

#------------------------------------------------------------------
def push_db( server_name,
             cluster_name,
             app_name,
             dump=True,
             folder='~/tmp/downloads',
             silently=False ):
    '''
        push_db( server_name, cluster_name, app_name, dump=True, folder='~/tmp/downloads', silently=False )
    '''
    from bismarck_cli.databases import do_upload_db
    srv_ctx = _get_server( server_name )
    do_upload_db( srv_ctx,
                  cluster_name,
                  app_name,
                  folder,
                  dump=dump,
                  silently=False )

#------------------------------------------------------------------
def reset_db_passwords( server_name ):
    srv_ctx = _get_server( server_name )
#     cluster = srv_ctx.get_cluster( cluster_name=cluster_name )
#     installer = cluster.installer
    installer = Installer( srv_ctx )
    msg = installer.pg_define_password()
    if msg:
        print( magenta( msg ) )

#------------------------------------------------------------------
# SERVER INIT/CONFIG
#------------------------------------------------------------------
def server_apache_a2enmod( server_name ):
    '''
    server_apache_a2enmod( server_name ): init app repo (dev)
    '''
    srv_ctx = _get_server( server_name )
#     installer = srv_ctx.server.get_installer()
    installer = srv_ctx.get_installer()
    installer.apache_a2enmode()

#------------------------------------------------------------------
def upd_server_packages( server_name ):
    '''
    init_server( server_name )
    '''
    srv_ctx = _get_server( server_name )
#     cluster = srv_ctx.get_cluster( cluster_name=cluster_name )
#     installer = cluster.installer
    installer = Installer( srv_ctx )
    installer.install_deps()

#------------------------------------------------------------------
def install_deps( server_name ):
    '''
    install_deps( server_name )
    '''
    srv_ctx = _get_server( server_name )
    installer = Installer( srv_ctx )
    installer.install_deps()

#------------------------------------------------------------------
def init_server( server_name ):
    '''
    init_server( server_name )
    '''
    srv_ctx = _get_server( server_name )
#     cluster = srv_ctx.get_cluster( cluster_name=cluster_name )
#     installer = cluster.installer
    installer = Installer( srv_ctx )
    installer.install_deps()
    installer.apache_a2enmod()
    msg = installer.pg_config()
    if msg:
        print( magenta( msg ) )
    msg = installer.pg_define_password()
    if msg:
        print( magenta( msg ) )
    msg = installer.create_certificate()
    if msg:
        print( magenta( msg ) )
    installer.deploy_jprinter()
    vcs_server = VcsServer( srv_ctx )
    vcs_server.config()

#------------------------------------------------------------------
def init_cluster( server_name, cluster_name ):
    '''
    init_cluster( server_name, cluster_name )
    '''
    srv_ctx = _get_server( server_name )
    curr_srv = CurrentServer( srv_ctx )
    cluster = srv_ctx.get_cluster( cluster_name=cluster_name )
#     installer = cluster.installer
    vcs_server = cluster.vcs_server
    vcs_server.config()
    msg = cluster.init_web2py()
    if msg:
        print( magenta( msg ) )
        if console.confirm( 'Abort?', default=False ):
            return

    cluster.define_web2py_admin_password()
    cluster.create_site_available()
    curr_srv.apache_ctl( 'stop' )
    curr_srv.apache_ctl( 'start' )

#------------------------------------------------------------------
def drop_cluster( server_name, cluster_name ):
    '''
    drop_cluster( server_name, cluster_name )
    '''
    srv_ctx = _get_server( server_name )
    curr_srv = CurrentServer( srv_ctx )
    cluster = srv_ctx.get_cluster( cluster_name=cluster_name )
    cluster.drop_web2py()

    cluster.drop_site_available()
    curr_srv.apache_ctl( 'stop' )
    curr_srv.apache_ctl( 'start' )

#------------------------------------------------------------------
def init_belmiro_customer( server_name,
                           cluster_name,
                           customer_name ):
    '''
    init_belmiro_customer( server_name, cluster_name, customer_name )
    '''
    curr_app = _get_current_app( server_name, cluster_name, 'belmiro' )
    belmiro_app.create_local_instance( curr_app, customer_name )

#------------------------------------------------------------------
def init_belmiro_customer_db( server_name,
                              cluster_name,
                              customer_name ):
    '''
    init_belmiro_customer_db( server_name, cluster_name, customer_name )
    '''
    curr_app = _get_current_app( server_name, cluster_name, 'belmiro' )
    db_name = curr_app.get_app_db_name()
    if console.confirm( 'Drop DATABASE "%s"' % customer_name, default=False ):
        local( 'dropdb %s' % db_name )
    belmiro_app.create_local_db( curr_app, customer_name )

#------------------------------------------------------------------
def init_belmiro_local_customer( server_name,
                                 cluster_name,
                                 customer_name,
                                 yes_to_all='f',
                                 init_db='t',
                                 test_docs='f',
                                 prompt='t' ):
    '''
    init_belmiro_local_customer( server_name, cluster_name, customer_name )
    '''
    master_app = _get_current_app( server_name, cluster_name, 'belmiro' )
    term.printLog( repr( 'clear_local_instance' ) )
    belmiro_app.clear_local_instance( master_app, customer_name )
    term.printLog( repr( 'create_local_instance' ) )
    belmiro_app.create_local_instance( master_app, customer_name )
    curr_app = _get_current_app( server_name, cluster_name, customer_name )
    if prompt[0].lower() == 't' \
    or yes_to_all[0].lower() == 't':
        if yes_to_all[0].lower() == 't' \
        or console.confirm( 'Initialize DB?', default=True ):
            belmiro_app.drop_local_db( curr_app )
            belmiro_app.create_local_db( curr_app, customer_name )
            term.printLog( repr( 'initialize_local_app' ) )
            belmiro_app.initialize_local_app( curr_app )
        if yes_to_all[0].lower() == 't' \
        or console.confirm( 'Test docs?', default=True ):
            belmiro_app.local_test_docs( curr_app )

#------------------------------------------------------------------
def test_docs( server_name, cluster_name, app_name ):
    '''
    test_docs( server_name, cluster_name, app_name )
    '''
    curr_app = _get_current_app( server_name, cluster_name, app_name )
    belmiro_app.local_test_docs( curr_app )

#------------------------------------------------------------------
def test_doc( server_name, cluster_name, app_name, fn ):
    '''
    test_docs( server_name, cluster_name, app_name )
    '''
    curr_app = _get_current_app( server_name, cluster_name, app_name )
    belmiro_app.local_test_docs( curr_app, fn=fn )

#------------------------------------------------------------------
def init_app( server_name, cluster_name, app_name ):
    '''
    init_app( server_name, cluster_name, app_name )
    '''
    curr_app = _get_current_app( server_name, cluster_name, app_name )
    msg = curr_app.init_remote_repo()
    if msg:
        print( magenta( msg ) )
        ret = console.prompt( 'Delete Skip Abort', default='d' )
        if ret == 'a':
            return
        curr_app.init_remote_repo( force=True )
    curr_app.init_web_repo()
    srv_ctx = _get_server( server_name )
    cluster = srv_ctx.get_cluster( cluster_name )
    if console.confirm( 'Drop DB and upload?', default=True ):
        cluster.drop_remote_app_db( app_name )
        cluster.upload_app_db( app_name )

#------------------------------------------------------------------
def drop_app( server_name, cluster_name, app_name ):
    '''
    drop_app( server_name, cluster_name, app_name )
    '''
    curr_app = _get_current_app( server_name, cluster_name, app_name )
    curr_app.purge_web_repo()
    curr_app.purge_remote_repo()

#------------------------------------------------------------------
def purge_server( server_name ):
    srv_ctx = _get_server( server_name )
    server = srv_ctx.server
    installer = Installer( srv_ctx )
    installer.purge_deps_packages()
    with settings( host_string=server.get_user_host_string(),
                   password=server.password ):
        remote_repo = srv_ctx.repos.get_remote_repo()
        cmd = 'rm -rf %s/%s' % (remote_repo.home_folder,
                                remote_repo.base_folder)
        run( cmd )
        keys = srv_ctx.repos.get_web_repos_keys()
        if keys:
            web_repo = srv_ctx.repos.get_web_repos( keys[ 0 ] )
            cmd = 'rm -rf %s' % (web_repo.home_folder)
            sudo( cmd )

#------------------------------------------------------------------
def purge_app( server_name, cluster_name, app_name ):
    curr_app = _get_current_app( server_name, cluster_name, app_name )
    if console.confirm( 'Purge app "%s"' % app_name, default=False ):
        msg = curr_app.purge_remote_repo()
        if msg:
            print( magenta( msg ) )
        curr_app.purge_web_repo()
        from bismarck_cli.databases import do_drop_db
        srv_ctx = _get_server( server_name )
        do_drop_db( srv_ctx,
                    app_name,
                    silently=False )

#------------------------------------------------------------------
def run_upgrade_script( server_name,
                        cluster_name,
                        app_name,
                        from_version,
                        to_version ):
    '''
    run_w2p_script( server_name, cluster_name, app_name, script, arg1=None, arg2=None )
    '''
    curr_app = _get_current_app( server_name, cluster_name, app_name )
    curr_app.run_upgrade_script( from_version, to_version )

#------------------------------------------------------------------
# SERVER MANAGEMENT
#------------------------------------------------------------------
def server_upgrade( server_name, dist_upgrade=False ):
    srv_ctx = _get_server( server_name )
    curr_srv = CurrentServer( srv_ctx )
    curr_srv.do_server_upgrade( dist_upgrade=dist_upgrade )

#------------------------------------------------------------------
def sync_backups( server_name, archive_local=True ):
    '''
    sync_backups( server_name, archive_local=True )
    '''
    from bismarck_cli.utils.ui_utils import cli_local

    srv_def = _get_server( server_name )
    server = srv_def.server
    bak_remote = server.backup_remote
    if not bak_remote.startswith( '/' ):
        if not bak_remote.startswith( '~/' ):
            bak_remote = '~/' + bak_remote
    data = { 'user': server.user,
             'host': server.host,
             'src': bak_remote,
             'dest': server.backup_local }
    cmd = 'rsync -avz --stats %(user)s@%(host)s:%(src)s/ %(dest)s' % data
    ret = cli_local( cmd, capture=False )
    print( blue( ret ) )
    if archive_local:
        archive_local_backups( server_name )

#------------------------------------------------------------------
def archive_local_backups( server_name ):
    srv_ctx = _get_server( server_name )
    server = CurrentServer( srv_ctx )
    server.archive_local_backups()

#------------------------------------------------------------------
def archive_remote_backups( server_name ):
    srv_ctx = _get_server( server_name )
    server = CurrentServer( srv_ctx )
    server.archive_remote_backups()

#------------------------------------------------------------------
def clean_old_backups( server_name, age=10 ):
    '''
    clean_old_backups( server_name, age=10 )
    '''
    srv_def = _get_server( server_name )
    server = srv_def.server
    bak_remote = server.backup_remote
    if not bak_remote.startswith( '/' ):
        if not bak_remote.startswith( '~/' ):
            bak_remote = '~/' + bak_remote
    data = { 'user': server.user,
             'host': server.host,
             'src': bak_remote,
             'dest': server.backup_local }
    preserve_since = DT.now() - datetime.timedelta( days=int( age ) )
    with settings( host_string=server.get_user_host_string(),
                   password=server.password ):
        with cd( bak_remote ):
            old_folders = []
            keep_folders = []
            cmd = 'ls'
            ret = run( cmd )
#             print( blue( '[' + ret + ']' ) )

            files = ret.split()
#             print( blue( repr( files ) ) )
            for f in files:
                if not f.startswith( server.backup_prefix ):
                    continue
                s_dt = f[ len( server.backup_prefix ) : ]
                dt = DT.strptime( s_dt, server.backup_date_mask )
                if dt < preserve_since:
                    old_folders.append( f )
                else:
                    keep_folders.append( f )
            old_folders = sorted( old_folders )
            kepp_folders = sorted( keep_folders )
            print( blue( 'keep folders:\n%s' % '\n'.join( keep_folders ) ) )
            print( magenta( 'old folders:\n%s' % '\n'.join( old_folders ) ) )
            if old_folders and console.confirm( 'Delete marked?',
                                                default=True ):
                for f in old_folders:
                    s_dt = f[ len( server.backup_prefix ) : ]
                    dt = DT.strptime( s_dt, server.backup_date_mask )
                    if dt.day == 1:
                        run( 'mv %s monthly' % f )
                    else:
                        run( 'mv %s %s' % (f, server.backup_trash) )
                with cd( server.backup_trash ):
                    cmd = 'ls'
                    ret = run( cmd )
                    files = sorted( ret.split() )
                    print( red( 'Trash:' ) )
                    print( red( '\n'.join( files ) ) )
                    if console.confirm( 'Delete TRASH?',
                                        default=True ):
                        run( 'rm -rf *' )


#------------------------------------------------------------------
# APP INIT/CONFIG
#------------------------------------------------------------------
def init_remote_repo( server_name, cluster_name, app_name ):
    curr_app = _get_current_app( server_name, cluster_name, app_name )

#------------------------------------------------------------------
def run_w2p_script( server_name,
                    cluster_name,
                    app_name,
                    script,
                    arg1=None,
                    arg2=None ):
    '''
    run_w2p_script( server_name, cluster_name, app_name, script, arg1=None, arg2=None )
    '''
    curr_app = _get_current_app( server_name, cluster_name, app_name )
    curr_app.run_w2p_script( script, arg1, arg2 )

#------------------------------------------------------------------

if __name__ == '__main__':
    print( 'args: %s' % repr( sys.argv ) )
    if len( sys.argv ) > 1:
        print( 'args: %s' % repr( sys.argv[1] ) )
        if sys.argv[1] == '-h':
            print( '''Usage: %s { -s <servername>| -h } [ -y ]
    Synchs files with extyernal disk and, optionally:
    -A: archive local
    -s : sync backup from <servername>
    -y : always assume yes, do not prompt
    -h : show this help message
            '''
                   % ( sys.argv[0] ) )
            sys.exit()
        else:
            if '-y' in sys.argv:
                use_prompt = False
            if sys.argv[1] == '-s':
                sync_backups( sys.argv[2] )
            elif sys.argv[1] == '-A':
                archive_local_backups( sys.argv[2] )

#     raw_input( 'finished! click ENTER to close...' )


