#!/usr/bin/env python
########################################################################
# $HeadURL$
########################################################################
__RCSID__ = "$Id$"
import DIRAC
from DIRAC.Core.Base                                   import Script

read  = True
write = True
check = True
site  = ''

Script.setUsageMessage( """
Ban one or more Storage Elements for usage

Usage:
   %s SE1 [SE2 ...]
""" % Script.scriptName )

Script.registerSwitch( "r" , "BanRead" , "      Ban only reading from the storage element" )
Script.registerSwitch( "w" , "BanWrite", "     Ban writing to the storage element" )
Script.registerSwitch( "k" , "BanCheck", "    Ban check access to the storage element" )
Script.registerSwitch( "S:", "Site="   , "      Ban all SEs associate to site (note that if writing is allowed, check is always allowed)" )
Script.parseCommandLine( ignoreErrors = True )

ses = Script.getPositionalArgs()
for switch in Script.getUnprocessedSwitches():
  if switch[0].lower() == "r" or switch[0].lower() == "banread":
    write = False
    check = False
  if switch[0].lower() == "w" or switch[0].lower() == "banwrite":
    read = False
    check = False
  if switch[0].lower() == "k" or switch[0].lower() == "bancheck":
    read = False
    write = False
  if switch[0] == "S" or switch[0].lower() == "site":
    site = switch[1]

#from DIRAC.ConfigurationSystem.Client.CSAPI           import CSAPI
from DIRAC                                           import gConfig, gLogger
from DIRAC.ConfigurationSystem.Client.Helpers        import ResourceStatus 
from DIRAC.Core.Security.ProxyInfo                   import getProxyInfo
from DIRAC.Core.Utilities.List                       import intListToString
from DIRAC.FrameworkSystem.Client.NotificationClient import NotificationClient
#csAPI = CSAPI()

res = getProxyInfo()
if not res[ 'OK' ]:
  gLogger.error( 'Failed to get proxy information', res[ 'Message' ] )
  DIRAC.exit( 2 )

userName = res[ 'Value' ][ 'username' ]
group    = res[ 'Value' ][ 'group' ]

if not type( ses ) == type( [] ):
  Script.showHelp()
  DIRAC.exit( -1 )

if site:
  res = gConfig.getOptionsDict( '/Resources/Sites/LCG/%s' % site )
  if not res[ 'OK' ]:
    gLogger.error( 'The provided site (%s) is not known.' % site )
    DIRAC.exit( -1 )
  ses.extend( res[ 'Value' ][ 'SE' ].replace( ' ', '' ).split( ',' ) )

if not ses:
  gLogger.error( 'There were no SEs provided' )
  DIRAC.exit()

readBanned  = []
writeBanned = []
checkBanned = []

storageCFGBase = "/Resources/StorageElements"
for se in ses:
  
  #res = ResourceStatus.getStorageElementStatus( se )
  res = gConfig.getOptionsDict( "%s/%s" % ( storageCFGBase, se ) )
  if not res['OK']:
    gLogger.error( "Storage Element %s does not exist" % se )
    continue
  
  existingOptions = res[ 'Value' ]
  reason          = 'Forced with dirac-admin-ban-se by %s' % userName
  
  # Eventually, we will get rid of the notion of InActive, as we always write Banned. 
  if read and existingOptions[ 'Read' ] in [ 'Active', 'Bad' ]:  
  #if read and existingOptions['ReadAccess'] == "Active":
    resR = ResourceStatus.setStorageElementStatus( se, 'Read', 'Banned', reason, userName )
    #res = csAPI.setOption( "%s/%s/ReadAccess" % ( storageCFGBase, se ), "InActive" )
    if not resR['OK']:
      gLogger.error( 'Failed to update %s read access to Banned' % se )
    else:
      gLogger.debug( 'Successfully updated %s read access to Banned' % se )
      readBanned.append( se )
      
  # Eventually, we will get rid of the notion of InActive, as we always write Banned. 
  if write and existingOptions[ 'Write' ] in [ 'Active', 'Bad' ]:    
  #if write and existingOptions['WriteAccess'] == "Active":
    resW = ResourceStatus.setStorageElementStatus( se, 'Write', 'Banned', reason, userName )
    #res = csAPI.setOption( "%s/%s/WriteAccess" % ( storageCFGBase, se ), "InActive" )
    if not resW['OK']:
      gLogger.error( "Failed to update %s write access to Banned" % se )
    else:
      gLogger.debug( "Successfully updated %s write access to Banned" % se )
      writeBanned.append( se )
      
  # Eventually, we will get rid of the notion of InActive, as we always write Banned. 
  if check and existingOptions[ 'Check' ] in [ 'Active', 'Bad' ]:    
  #if check and existingOptions['CheckAccess'] == "Active":
    resC = ResourceStatus.setStorageElementStatus( se, 'Check', 'Banned', reason, userName )
    #res = csAPI.setOption( "%s/%s/CheckAccess" % ( storageCFGBase, se ), "InActive" )
    if not resC['OK']:
      gLogger.error( "Failed to update %s check access to Banned" % se )
    else:
      gLogger.debug( "Successfully updated %s check access to Banned" % se )
      checkBanned.append( se )
 
  if not resR['OK'] or not resW['OK'] or not resC['OK']:
    gLogger.error( "Failed to commit changes to CS", res['Message'] )
    DIRAC.exit( -1 ) 
      
#res = csAPI.commitChanges()
#if not res['OK']:
#  gLogger.error( "Failed to commit changes to CS", res['Message'] )
#  DIRAC.exit( -1 )

if not ( writeBanned or readBanned or checkBanned ):
  gLogger.notice( "No storage elements were banned" )
  DIRAC.exit( -1 )

subject = '%s storage elements banned for use' % len( ses )
address = gConfig.getValue( '/Operations/EMail/Production', 'lhcb-grid@cern.ch' )
body = ''
if read:
  body = "%s\n\nThe following storage elements were banned for reading:" % body
  for se in readBanned:
    body = "%s\n%s" % ( body, se )
if write:
  body = "%s\n\nThe following storage elements were banned for writing:" % body
  for se in writeBanned:
    body = "%s\n%s" % ( body, se )
if check:
  body = "%s\n\nThe following storage elements were banned for check access:" % body
  for se in checkBanned:
    body = "%s\n%s" % ( body, se )

NotificationClient().sendMail( address, subject, body, '%s@cern.ch' % userName )
DIRAC.exit( 0 )
