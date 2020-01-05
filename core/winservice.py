import os
import sys
import win32serviceutil
import win32service


class WindowsService(win32serviceutil.ServiceFramework):
    _svc_name_ = ''
    _svc_display_name_ = ''

    def SvcDoRun(self):
        bp = os.path.dirname(os.path.abspath(__file__))
        bp = bp.replace('\\', '/')
        if bp.endswith('/'):
            bp = bp[:-1]
        p = bp.rfind('/')
        bp = bp[:p]
        os.chdir(bp)

        import core.application
        core.application.Application.initialize()
        core.application.Application.load_instance(sys.argv[1])
        core.application.Application.start_servers()

    def SvcStop(self):
        import core.application
        self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
        core.application.Application.stop_servers()
        self.ReportServiceStatus(win32service.SERVICE_STOPPED)
