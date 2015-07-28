#! /usr/bin/python

#----------------------------------------------------------------------
class HgRepoStatusDetailed( object ):
    #----------------------------------------------------------------------
    def __init__( self, status_parts ):
        self.status = status_parts[0]
        self.filename = status_parts[1]

    #----------------------------------------------------------------------
    def __str__(self ):
        return '%s %s' % ( self.status,
                           self.filename )

    #----------------------------------------------------------------------

