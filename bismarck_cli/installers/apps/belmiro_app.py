'''
Created on 09/07/2015

@author: carlos
'''
from fabric.context_managers import lcd
from fabric.operations import local
import os.path

from bismarck_cli.servers.current_app import PRESERVE_DIRS, LINK_LIST
from bismarck_cli.utils import term


#------------------------------------------------------------------
def clear_local_instance( curr_app, new_name ):
    abs_repo_folder = curr_app.get_abs_local_folder()
    term.printLog( repr( abs_repo_folder ) )
    path = abs_repo_folder.split( '/' )
    base_folder = '/'.join( path[:-1] )
    term.printLog( 'base_folder: %s' % repr( base_folder ) )
    with lcd( base_folder ):
        local( 'rm -rf %s' % new_name )

    abs_w2p_folder = curr_app.get_abs_local_w2p_folder()
    term.printLog( repr( abs_w2p_folder ) )
    with lcd( abs_w2p_folder ):
        with lcd( 'applications' ):
            with lcd( 'belmiro/config' ):
                local( 'rm -rf %s' % new_name )
            local( 'rm -f %s' % new_name )
#------------------------------------------------------------------
def create_local_instance( curr_app, new_name ):
    abs_repo_folder = curr_app.get_abs_local_folder()
    term.printLog( repr( abs_repo_folder ) )
    path = abs_repo_folder.split( '/' )
    base_folder = '/'.join( path[:-1] )
    term.printLog( 'base_folder: %s' % repr( base_folder ) )
    with lcd( base_folder ):
        with lcd( curr_app.app_name ):
            term.printLog( local( 'pwd', capture=True ) )
            with lcd( 'config' ):
                term.printLog( local( 'pwd', capture=True ) )
                local( 'mkdir %s' % new_name )
                with lcd( new_name ):
                    term.printLog( local( 'pwd', capture=True ) )
                    local( 'mkdir -p init' )
                    local( 'mkdir -p reports' )
                term.printLog( local( 'pwd', capture=True ) )
                with lcd( new_name ):
                    term.printLog( local( 'pwd', capture=True ) )
                    local( 'cp ../belmiro/template/template.dict %(app)s.dict' %
                           { 'app': new_name } )
                    local( "sed -i 's/belmiro3/%(app)s/g' %(app)s.dict" %
                           { 'app': new_name } )

        term.printLog( local( 'pwd', capture=True ) )
        local( 'mkdir %s' % new_name )
        with lcd( new_name ):
            term.printLog( local( 'pwd', capture=True ) )
            for st in PRESERVE_DIRS:
                local( 'mkdir %s' % st )
            local( 'ln -s ../belmiro _master_app' )
            for lk in LINK_LIST:
                local( 'ln -s _master_app/%(lk)s %(lk)s' % { 'lk': lk } )

    abs_w2p_folder = curr_app.get_abs_local_w2p_folder()
    term.printLog( repr( abs_w2p_folder ) )
    with lcd( abs_w2p_folder ):
        with lcd( 'applications' ):
            term.printLog( local( 'pwd', capture=True ) )
            local( 'ln -s ../../%(app)s %(app)s' % { 'app': new_name } )

#------------------------------------------------------------------
def create_local_db( curr_app, customer_name ):
    abs_repo_folder = curr_app.get_abs_local_folder()
    term.printLog( repr( abs_repo_folder ) )
    path = abs_repo_folder.split( '/' )
    base_folder = '/'.join( path[:-1] )
    term.printLog( 'base_folder: %s' % repr( base_folder ) )
    with lcd( '%s/%s' % (base_folder, customer_name) ):
        with lcd( 'private/resources/sql/dbs' ):
            local( 'cp belmiro3-template.sql %s.sql' % customer_name )
            local( "sed -i 's/belmiro3_template/%(c)s/g' %(c)s.sql" %
                   { 'c': customer_name } )
            local( 'psql -f %(c)s.sql -v ON_ERROR_STOP=1' %
                   { 'c': customer_name } )

#------------------------------------------------------------------
def drop_local_db( curr_app ):
    db_name = curr_app.get_app_db_name()
    term.printLog( repr( db_name ) )
    local( 'dropdb %s' % db_name )

#------------------------------------------------------------------
def initialize_local_app( curr_app ):
    abs_w2p_folder = curr_app.get_abs_local_w2p_folder()
    term.printLog( repr( abs_w2p_folder ) )
    with lcd( abs_w2p_folder ):
        local( 'rm -rf applications/%s/uploads/*' % curr_app.app_name )
        local( 'find applications/%s/ -name "*.pyc" | xargs rm -f' % curr_app.app_name )
        local( 'python web2py.py -i 127.0.0.1 -M -S %(app)s -R applications/%(app)s/private/scripts/resetdb.py -A init' %
               { 'app': curr_app.app_name } )

#------------------------------------------------------------------
def local_test_docs( curr_app, fn='full_test' ):
    abs_w2p_folder = curr_app.get_abs_local_w2p_folder()
    term.printLog( repr( abs_w2p_folder ) )
    with lcd( abs_w2p_folder ):
        local( 'find applications/belmiro/ . -name "*.pyc" | xargs rm' )
        local( 'python web2py.py -i 127.0.0.1 -M -S %(app)s -R applications/%(app)s/private/scripts/test_docs.py -A %(fn)s' %
               { 'app': curr_app.app_name,
                 'fn': fn } )
