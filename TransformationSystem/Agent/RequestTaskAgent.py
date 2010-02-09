########################################################################
# $HeadURL: svn+ssh://svn.cern.ch/reps/dirac/DIRAC/trunk/DIRAC/TransformationSystem/Agent/RequestTaskAgent.py $
########################################################################
"""  The Request Task Agent takes request tasks created in the transformation database and submits to the request management system. """
__RCSID__ = "$Id: ReplicationSubmissionAgent.py 20001 2010-01-20 12:47:38Z acsmith $"

from DIRAC                                                          import S_OK, S_ERROR, gConfig, gMonitor, gLogger, rootPath
from DIRAC.TransformationSystem.Agent.TaskManagerAgentBase          import TaskManagerAgentBase
from DIRAC.TransformationSystem.Client.TaskManager                  import RequestTasks

AGENT_NAME = 'TransformationSystem/RequestTaskAgent'

class RequestTaskAgent(TaskManagerAgentBase,RequestTasks):

  #############################################################################
  def initialize(self):
    """ Sets defaults """
    TaskManagerAgentBase.initialize()
    RequestTasks.__init__(self)
    return S_OK()