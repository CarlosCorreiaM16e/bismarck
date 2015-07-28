#! /usr/bin/python
from bismarck_cli.utils.storage import Storage


#------------------------------------------------------------------
def get_padded_str( s, pad_len, pad_left=True ):
    padded_str = '%'
    if pad_left:
        padded_str += '-'
    padded_str += '%d.%d' % (pad_len, pad_len)
    padded_str += 's'
    return padded_str % s

#----------------------------------------------------------------------
def is_sequence( value ):
    return ( value and ( not hasattr( value, 'strip') and
                         hasattr( value, '__getitem__' ) and
                         hasattr( value, '__iter__' ) ) )

#------------------------------------------------------------------
size_factors = Storage( K=1,
                        M=1024,
                        G=1024 * 1024 )
def sort_du( lines ):
    f_arr = []
    for l in lines:
        t = l.replace( '\t', ' ' ).split( ' ', 1 )
        str_size = t[0].strip()
        sizek = float( str_size[:-1] ) * size_factors[ str_size[-1 ] ]
        f_arr.append( (sizek, t[1].strip()) )
    return sorted( f_arr, reverse=True )

#------------------------------------------------------------------
def get_top_du( du_result, limit=6 ):
    lines = du_result.splitlines()
    sorted_lines = sort_du( lines )
    top_du = ''
    for l in sorted_lines[ : limit ]:
        size = l[0]
        if size > size_factors.G:
            du = '%.1fG' % ( size / size_factors.G )
        elif size > size_factors.M:
            du = '%.1fM' % ( size / size_factors.M )
        else:
            du = '%.1fK' % ( size )
        top_du += '%8.8s %s\n' % ( du, l[1] )
    return top_du

#------------------------------------------------------------------
