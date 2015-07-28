#! /usr/bin/python

from fabric.context_managers import lcd, cd, settings
from fabric.contrib import files

from bismarck_cli.servers.defs.repos_local_def import LocalRepoDef
from bismarck_cli.servers.defs.repos_remote_def import RemoteRepoDef
from bismarck_cli.servers.defs.repos_web_def import WebRepoDef
from bismarck_cli.servers.status_detailed import HgRepoStatusDetailed
from bismarck_cli.utils import term
from bismarck_cli.utils.misc import get_padded_str
from bismarck_cli.utils.storage import Storage
from bismarck_cli.utils.ui_utils import cli_execute, EX_LOCAL, EX_RUN, EX_SUDO, \
    cli_sudo_run


#----------------------------------------------------------------------
class AbstractRepo( object ):
    #----------------------------------------------------------------------
    def __init__( self, current_app, repo_type ):
        '''
            repo_type: [ local | remote | web ]
        '''
        self.current_app = current_app
        self.repo_type = repo_type
        self.status = None
        self.status_resumed = None
        self.version = None
        self.version_date = None
        self.tip = None

#----------------------------------------------------------------------
class HgRepo( AbstractRepo ):
    #----------------------------------------------------------------------
    def __init__( self, current_app, repo_type ):
        super( HgRepo, self ).__init__( current_app, repo_type )
        self.init_ctx_args()

    #----------------------------------------------------------------------
    def init_ctx_args( self ):
        srv_ctx = self.current_app.srv_ctx
        server = srv_ctx.server
        self.ctx_args = []
        self.ctx_kwargs = {}

        self.cli_kwargs = { 'quiet': True }
#         self.cli_kwargs = { 'prompt': True,
#                             'print_output': True }
        if self.repo_type == LocalRepoDef.tag:
            self.cli_kwargs[ 'exec_type' ] = EX_LOCAL
        else:
            self.ctx_kwargs[ 'host_string' ] = server.get_user_host_string()
            self.ctx_kwargs[ 'password' ] = server.password
            if self.repo_type == RemoteRepoDef.tag:
                self.cli_kwargs[ 'exec_type' ] = EX_RUN
            elif self.repo_type == WebRepoDef.tag:
                self.cli_kwargs[ 'exec_type' ] = EX_SUDO
                self.cli_kwargs[ 'user' ] = server.w3_user

    #----------------------------------------------------------------------
    def exec_list( self, cmd_list, prefix='' ):
        srv_ctx = self.current_app.srv_ctx
        app_name = self.current_app.app_name
        cluster = srv_ctx.get_cluster( self.current_app.cluster_name )
        repo = cluster.get_repo( self.repo_type )
        result_list = []
        abs_path = repo.get_abs_path( app_name )
        cd_cmd = cd
        if self.repo_type == LocalRepoDef.tag:
            cd_cmd = lcd
        elif self.repo_type == WebRepoDef.tag:
            abs_path += '/current'
        with settings( *self.ctx_args, **self.ctx_kwargs ):
            with cd_cmd( abs_path ):
                for cmd in cmd_list:
                    cli_args = [ prefix + cmd ]
                    ret = cli_execute( *cli_args,
                                       **self.cli_kwargs )
                    result_list.append( ret )
                    if ret.stderr:
                        return (result_list, ret.stderr)
        if len( cmd_list ) == 1:
            return (result_list[0], None)
        return (result_list, None)

    #----------------------------------------------------------------------
    def exec_single( self, cmd, prefix='' ):
        result_list, errors = self.exec_list( [ cmd ], prefix=prefix )
        result = '' if not result_list else result_list[0]
        return (result, errors)

#     #----------------------------------------------------------------------
#     def disable_app( self, since ):
#         if self.repo_type != WebRepoDef.tag:
#             raise Exception( 'bad repo type: %s' % ( repr( self.repo_type ) ) )
#
#         srv_ctx = self.current_app.srv_ctx
#         server = srv_ctx.server
#         app_name = self.current_app.app_name
#         repo = srv_ctx.repos.get_repo( self.repo_type,
#                                        app_name )
#
#         abs_path = repo.get_abs_path( app_name )
#         cd_cmd = cd
#         if self.repo_type == LocalRepoDef.tag:
#             cd_cmd = lcd
#         with settings( *self.ctx_args, **self.ctx_kwargs ):
#             with cd_cmd( abs_path ):
#                 files.append( 'DISABLED',
#                               str( since ),
#                               use_sudo=True )
#                 cli_sudo_run( 'chown %s. DISABLED' % server.w3_user,
#                               password=server.password )

    #----------------------------------------------------------------------
    def refresh( self ):
        cmd_list = [ 'hg status',
                     'cat __init__.py',
                     'hg tip' ]
        result_list, errors = self.exec_list( cmd_list,
                                              prefix='LANGUAGE=C ' )
#         term.printDebug( 'errors: %s' % repr( errors ) )
#         term.printDebug( 'result_list: %s' % '\n'.join( result_list ) )
        if errors:
            term.printLog( 'errors: %s' % repr( errors ) )
            return result_list[ -1 ]
        for r in result_list:
            if r.startswith( 'abort: ' ):
                term.printDebug( 'result_list: %s' % '\n'.join( result_list ) )
                return result_list

        self._parse_status( result_list[ 0 ].stdout )
        self._parse_init_file( result_list[ 1 ].stdout )
        self._parse_tip( result_list[ 2 ].stdout )

        return None

    #----------------------------------------------------------------------
    def _parse_tip( self, tip_output ):
        self.tip = Storage()
        for l in tip_output.splitlines():
            parts = [ p.strip() for p in l.split( ':', 1 ) ]
            if parts[0] == 'changeset':
                cs_parts = parts[1].split( ':', 1 )
                self.tip.changeset_number = int( cs_parts[0] )
                self.tip.changeset_id = cs_parts[1]
            elif parts[0] == 'user':
                self.tip.user = parts[1]
            elif parts[0] == 'date':
                self.tip.date = parts[1]
            elif parts[0] == 'summary':
                self.tip.summary = parts[1]

    #----------------------------------------------------------------------
    def _parse_init_file( self, init_file ):
        for l in init_file.splitlines():
            if l.startswith( '#' ) or len( l.strip() ) == 0:
                continue
            parts = [ p.strip() for p in l.split( '=' ) ]
            if parts[0] == '__version__':
                self.version = parts[1].replace( '"', '' ).replace( "'", "" ).strip()
            elif parts[0] == '__version_date__':
                self.version_date = parts[1].replace( '"', '' ).replace( "'", "" ).strip()

    #----------------------------------------------------------------------
    def _parse_status( self, status_str ):
#         term.printDebug( 'status_str: [%s]' % status_str )
        lines = status_str.splitlines()
        self.status_resumed = ''
        self.status_detailed = []
        for l in lines:
            parts = l.split( ' ' )
            if not parts[0] in self.status_resumed:
                self.status_resumed += parts[0]
            self.status_detailed.append( HgRepoStatusDetailed( parts ))
#         term.printDebug( 'self.status_detailed:\n[%s]' % self.status_detailed )

    #----------------------------------------------------------------------
    # line format (LF_) lengths
    LF_VER_LEN = 12
    LF_DATE_LEN = 14
    LF_STATUS_LEN = 7
    LF_TIP_LEN = 6

    #----------------------------------------------------------------------
    def get_format_status_header( self, style='line' ):
        l = get_padded_str( 'Version', self.LF_VER_LEN )
        l += ' ' + get_padded_str( 'Date', self.LF_DATE_LEN )
        l += ' ' + get_padded_str( 'Status', self.LF_STATUS_LEN )
        l += ' ' + get_padded_str( 'Tip', self.LF_TIP_LEN )
#         term.printDebug( 'l: [%s]' % repr( l ) )
        return l

    #----------------------------------------------------------------------
    def format_status( self, style='line' ):
#         term.printDebug( 'self: %s' % repr( self ) )
        v = self.version or ''
#         term.printDebug( 'v: [%s]' % repr( v ) )
        l = get_padded_str( v, self.LF_VER_LEN )
#         term.printDebug( 'l: [%s]' % repr( l ) )

        v = self.version_date or ''
#         term.printDebug( 'v: [%s]' % repr( v ) )
        l += ' ' + get_padded_str( v, self.LF_DATE_LEN )
#         term.printDebug( 'l: [%s]' % repr( l ) )

        v = str( self.status_resumed )
#         term.printDebug( 'v: [%s]' % repr( v ) )
        l += ' ' + get_padded_str( v, self.LF_STATUS_LEN )
#         term.printDebug( 'l: [%s]' % repr( l ) )

        v = self.tip.changeset_number if self.tip else ''
#         term.printDebug( 'v: [%s]' % repr( v ) )
        l += ' ' + get_padded_str( v, self.LF_TIP_LEN )
#         term.printDebug( 'l: [%s]' % repr( l ) )
        return l

    #----------------------------------------------------------------------
    def __str__(self, *args, **kwargs):
        data = { 'ver': self.version or '',
                 'ver_date': self.version_date or '',
                 'st': self.status_resumed,
                 'tip': self.tip.changeset_number if self.tip else '' }
        data[ 'date' ] = '-'
        if self.version_date:
            data[ 'date' ] = self.version_date

        s = '''version: %(ver)s; date: %(date)s; status: [%(st)s]; tip: %(tip)s''' % data
        return s

    #----------------------------------------------------------------------


