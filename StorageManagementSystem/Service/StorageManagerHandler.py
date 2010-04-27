########################################################################
# $Header: /tmp/libdirac/tmp.FKduyw2449/dirac/DIRAC3/DIRAC/StorageManagementSystem/Service/StorageManagerHandler.py,v 1.1 2009/10/30 19:38:56 acsmith Exp $
########################################################################
""" StorageManagerHandler is the implementation of the StorageManagementDB in the DISET framework """
__RCSID__ = "$Id: StorageManagerHandler.py,v 1.1 2009/10/30 19:38:56 acsmith Exp $"

from types import *
from DIRAC                                                 import gLogger, gConfig, S_OK, S_ERROR
from DIRAC.Core.DISET.RequestHandler                       import RequestHandler
from DIRAC.StorageManagementSystem.DB.StorageManagementDB  import StorageManagementDB
# This is a global instance of the StorageDB
storageDB = False

def initializeStorageManagerHandler(serviceInfo):
  global storageDB
  storageDB = StorageManagementDB()
  return S_OK()

class StorageManagerHandler(RequestHandler):

  ######################################################################
  #
  #  Example call back methods
  #

  types_updateTaskStatus = []
  def export_updateTaskStatus(self,sourceID,status, successful=[],failed=[]):
    """ An example to show the usage of the callbacks. """
    gLogger.info("updateTaskStatus: Received callback information for ID %s" % sourceID)
    gLogger.info("updateTaskStatus: Status = '%s'" % status)
    if successful:
      gLogger.info("updateTaskStatus: %s files successfully staged" % len(successful))
      for lfn,time in successful:
        gLogger.info("updateTaskStatus: %s %s" % (lfn.ljust(100),time.ljust(10)))
    if failed:
      gLogger.info("updateTaskStatus: %s files failed to stage" % len(successful))
      for lfn,time in failed:
        gLogger.info("updateTaskStatus: %s %s" % (lfn.ljust(100),time.ljust(10)))
    return S_OK()

  ######################################################################
  #
  #  Monitoring methods
  #

  types_getTaskStatus = [IntType]
  def export_getTaskStatus(self,taskID):
    """ Obtain the status of the stage task from the DB. """
    res = storageDB.getTaskStatus(taskID)
    if not res['OK']:
      gLogger.error('getTaskStatus: Failed to get task status',res['Message'])
    return res

  types_getTaskInfo = [IntType]
  def export_getTaskInfo(self,taskID):
    """ Obtain the metadata of the stage task from the DB. """
    res = storageDB.getTaskInfo(taskID)
    if not res['OK']:
      gLogger.error('getTaskInfo: Failed to get task metadata',res['Message'])
    return res

  types_getTaskSummary = [IntType]
  def export_getTaskSummary(self,taskID):
    """ Obtain the summary of the stage task from the DB. """
    res = storageDB.getTaskSummary(taskID)
    if not res['OK']:
      gLogger.error('getTaskSummary: Failed to get task summary',res['Message'])
    return res

  ####################################################################
  #
  # setRequest is used to initially insert tasks and their associated files. Leaves files in New status.
  #

  types_setRequest = [DictType,StringType,StringType,IntType]
  def export_setRequest(self,lfnDict,source,callbackMethod,taskID):
    """ This method allows stage requests to be set into the StagerDB """
    res = storageDB.setRequest(lfnDict,source,callbackMethod,taskID)
    if not res['OK']:
      gLogger.error('setRequest: Failed to set stage request',res['Message'])
    return res

  ####################################################################
  #
  # The state transition of the Replicas from New->Waiting
  #

  types_updateReplicaInformation = [ListType]
  def export_updateReplicaInformation(self,replicaTuples):
    """ This method sets the pfn and size for the supplied replicas """
    res = storageDB.updateReplicaInformation(replicaTuples)
    if not res['OK']:
      gLogger.error('updateRelicaInformation: Failed to update replica information',res['Message'])
    return res

  ####################################################################
  #
  # The state transition of the Replicas from Waiting->StageSubmitted
  #

  types_getWaitingReplicas = []
  def export_getWaitingReplicas(self):
    """ This method obtains the replicas for which all replicas in the task are Waiting """
    res = storageDB.getWaitingReplicas()
    if not res['OK']:
      gLogger.error('getWaitingReplicas: Failed to obtain Waiting replicas',res['Message'])
    return res

  types_getSubmittedStagePins = []
  def export_getSubmittedStagePins(self):
    """ This method obtains the number of files and size of the requests submitted for each storage element """
    res = storageDB.getSubmittedStagePins()
    if not res['OK']:
      gLogger.error('getSubmittedStagePins: Failed to obtain submitted request summary',res['Message'])
    return res

  types_insertStageRequest = [DictType,[IntType,LongType]]
  def export_insertStageRequest(self,requestReplicas,pinLifetime):
    """ This method inserts the stage request ID assocaited to supplied replicaIDs """
    res = storageDB.insertStageRequest(requestReplicas,pinLifetime)
    if not res['OK']:
      gLogger.error('insertStageRequest: Failed to insert stage request information',res['Message'])
    return res

  ####################################################################
  #
  # The state transition of the Replicas from StageSubmitted->Staged
  #

  types_getStageSubmittedReplicas = []
  def export_getStageSubmittedReplicas(self):
    """ This method obtains the replica metadata and the stage requestID for the replicas in StageSubmitted status """
    res = storageDB.getStageSubmittedReplicas()
    if not res['OK']:
      gLogger.error('getStageSubmittedReplicas: Failed to obtain StageSubmitted replicas',res['Message'])
    return res

  types_setStageComplete = [ListType]
  def export_setStageComplete(self,replicaIDs):
    """ This method updates the status of the stage request for the supplied replica IDs """
    res = storageDB.setStageComplete(replicaIDs)
    if not res['OK']:
      gLogger.error('setStageComplete: Failed to set StageRequest complete',res['Message'])
    return res

  ####################################################################
  #
  # The state transition of the Replicas from Staged->Pinned
  #

  types_getStagedReplicas = []
  def export_getStagedReplicas(self):
    """ This method obtains the replicas and SRM request information which are in the Staged status """
    res = storageDB.getStagedReplicas()
    if not res['OK']:
      gLogger.error('getStagedReplicas: Failed to obtain Staged replicas',res['Message'])
    return res

  types_insertPinRequest = [DictType,IntType]
  def export_insertPinRequest(self,requestReplicas,pinLifeTime):
    """ This method inserts pins for the supplied replicaIDs with the supplied lifetime """
    res = storageDB.insertPinRequest(requestReplicas,pinLifeTime)
    if not res['OK']:
      gLogger.error('insertPinRequest: Failed to insert pin information',res['Message'])
    return res

  ####################################################################
  #
  # The methods for finalization of tasks
  #

  types_updateStageCompletingTasks = []
  def export_updateStageCompletingTasks(self):
    """ This method checks whether the file for Tasks in 'StageCompleting' status are all Staged and updates the Task status to Staged """
    res = storageDB.updateStageCompletingTasks()
    if not res['OK']:
      gLogger.error('updateStageCompletingTasks: Failed to update StageCompleting tasks.',res['Message'])
    return res

  types_setTasksDone = [ListType]
  def export_setTasksDone(self,taskIDs):
    """ This method sets the status in the Tasks table to Done for the list of supplied task IDs """
    res = storageDB.setTasksDone(taskIDs)
    if not res['OK']:
      gLogger.error('setTasksDone: Failed to set status of tasks to Done',res['Message'])
    return res

  types_removeTasks = [ListType]
  def export_removeTasks(self,taskIDs):
    """ This method removes the entries from TaskReplicas and Tasks with the supplied task IDs """
    res = storageDB.removeTasks(taskIDs)
    if not res['OK']:
      gLogger.error('removeTasks: Failed to remove Tasks',res['Message'])
    return res

  types_removeUnlinkedReplicas = []
  def export_removeUnlinkedReplicas(self):
    """ This method removes Replicas which have no associated Tasks """
    res = storageDB.removeUnlinkedReplicas()
    if not res['OK']:
      gLogger.error('removeUnlinkedReplicas: Failed to remove unlinked Replicas',res['Message'])
    return res

  ####################################################################
  #
  # The state transition of the Replicas from *->Failed
  #

  types_updateReplicaFailure = [DictType]
  def export_updateReplicaFailure(self,replicaFailures):
    """ This method sets the status of the replica to failed with the supplied reason """
    res = storageDB.updateReplicaFailure(replicaFailures)
    if not res['OK']:
      gLogger.error('updateRelicaFailure: Failed to update replica failure information',res['Message'])
    return res

  ####################################################################
  #
  # General methods for obtaining Tasks, Replicas with supplied state
  #

  types_getTasksWithStatus = [StringType]
  def export_getTasksWithStatus(self,status):
    """ This method allows to retrieve Tasks with the supplied status """
    res = storageDB.getTasksWithStatus(status)
    if not res['OK']:
      gLogger.error('getTasksWithStatus: Failed to get tasks with %s status' % status,res['Message'])
    return res

  types_getReplicasWithStatus = [StringType]
  def export_getReplicasWithStatus(self,status):
    """ This method allows to retrieve replicas with the supplied status """
    res = storageDB.getReplicasWithStatus(status)
    if not res['OK']:
      gLogger.error('getReplicasWithStatus: Failed to get replicas with %s status' % status,res['Message'])
    return res