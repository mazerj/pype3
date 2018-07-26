# -*- Mode: Python; tab-width: 4; py-indent-offset: 4; -*-

"""Exception classes for errors

These are are the standard errors that pype and the pype libraries
functions might throw during task execution.

Author -- James A. Mazer (mazerj@gmail.com)

"""

class FatalPypeError(Exception): pass
class FatalComediError(Exception): pass
class PypeStartupError(Exception): pass
class DepreciatedError(Exception): pass
class MonkError(Exception): pass
class MonkNoStart(Exception): pass
class TimeoutError(Exception): 	pass
class NoProblem(Exception): pass
class UserAbort(Exception): pass
class UserExit(Exception): pass
class TaskAbort(Exception): pass
class RunTimeError(Exception): pass

class BarTransition(Exception): pass
class JoyTransition(Exception): pass
class FixBreak(Exception): pass
class Alarm(Exception): pass
class EmergencyAbort(Exception): pass

# for obsolete function calls
class Obsolete(Exception): pass


def obsolete_fn(*args):
    raise Obsolete
