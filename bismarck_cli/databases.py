#! /usr/bin/python
from fabric.context_managers import settings, lcd, cd
from fabric.operations import get, local, put, run

from bismarck_cli.utils import term
from bismarck_cli.utils.ui_utils import cli_run, cli_local, cli_continue


#----------------------------------------------------------------------
def do_download_db( srv_ctx,
                    cluster_name,
                    app_name,
                    folder,
                    restore=True,
                    silently=False ):
    server = srv_ctx.server
    db_name = srv_ctx.get_app_db_name( cluster_name, app_name )
    d = { 'db_name': db_name }
    sql_filename = 'dump-%(db_name)s.sql' % d
    with settings( host_string=server.get_user_host_string(),
                   password=server.password ):
        cli_run( 'mkdir -p tmp' )
        with lcd( folder ):
            with cd( 'tmp' ):
                d[ 'f' ] = sql_filename
                cli_run( 'pg_dump -C %(db_name)s -f %(f)s' % d )
                cli_run( 'tar jcvf %(f)s.tar.bz2 %(f)s' % d )
                get( '%(f)s.tar.bz2' %d, '%(f)s.tar.bz2' % d )
            if restore:
                cli_local( 'tar jxvf %(f)s.tar.bz2 %(f)s' % d )
                with settings( warn_only = True ):
                    cli_local( 'dropdb %s' % db_name )
                cli_local( 'psql -f %(f)s -v ON_ERROR_STOP=1' % d )

#----------------------------------------------------------------------
def do_upload_db( srv_ctx,
                  cluster_name,
                  app_name,
                  folder,
                  dump=True,
                  silently=False ):
    server = srv_ctx.server
    db_name = srv_ctx.get_app_db_name( cluster_name, app_name )
    d = { 'db_name': db_name }
    sql_filename = 'dump-%(db_name)s.sql' % d
    local( 'mkdir -p %s' % folder )
    if dump:
        with lcd( folder ):
            tarball = '%s.tar.bz2' % sql_filename
            local( 'pg_dump -C %s -f %s' % (db_name, sql_filename) )
            local( 'tar jcvf %s %s' % (tarball, sql_filename) )

    do_drop_db( srv_ctx, db_name, silently=silently )
    with settings( host_string=server.get_user_host_string(),
                   password=server.password ):
        cli_run( 'mkdir -p tmp' )
        tarball = '%s.tar.bz2' % sql_filename
        put( '%s/%s' % (folder, tarball),
             'tmp/%s' % tarball )
        with cd( 'tmp' ):
            filename = run( 'tar jxvfm %s' % (tarball) )
            term.printDebug( 'filename: %s' % filename )
            run( 'ls -l %s' % filename )
            cmd = '''sed -i 's/SET lock_timeout/-- SET lock_timeout/g' %s'''
            term.printDebug( 'cmd: %s' % (cmd % filename) )
            run( cmd % filename )
            cmd = '''sed -i 's/OWNER TO carlos/OWNER TO %s/g' %s'''
            run( cmd % (server.db_user, filename) )
            cmd = '''sed -i 's/Owner: carlos/Owner: %s/g' %s'''
            run( cmd % (server.db_user, filename) )
            run( 'psql -f %s -v ON_ERROR_STOP=1' % filename )

#----------------------------------------------------------------------
def do_drop_db( srv_ctx,
                db_name,
                silently=False ):
    server = srv_ctx.server
#     db_name = srv_ctx.databases[ app_name ]
    term.printDebug( 'dropdb' )
    with settings( host_string=server.get_user_host_string(),
                   warn_only = True ):
        result = cli_run( '''psql -tAc "select 1 from pg_database where datname='%s'"''' %
                          db_name,
                          prompt=True )
        term.printDebug( 'result: %s' % repr( result ) )
        cli_continue( 'Continue?' )
        if result:
            cli_run( 'dropdb %s' % db_name,
                     prompt=True )

#------------------------------------------------------------------
