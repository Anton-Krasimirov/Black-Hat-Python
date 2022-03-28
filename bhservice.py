import os
import servicemanager
import shutil
import subprocess
import sys

import win32event
import win32service
import win32serviceutil

SRCDIR = 'C:\\Users\\tim\\work' # задаваме изходната директория за скриптовия файл 
TGTDIR = 'C:\\Windows\\TEMP' # целевата директория, от която ще бъде стартирана от услугата


class BHServerSvc(win32serviceutil.ServiceFramework):
    _svc_name_ = "BlackHatService"
    _svc_display_name_ = "Black Hat Service"
    _svc_description_ = ("Executes VBScripts at regular intervals." + " What could possibly go wrong?")

    '''В метода __init__ инициализираме ServiceFramework, 
    намираме скрипта, който трябва да се изпълни, задаваме времето за изчакване на 1 минута и създаваме обекта на събитието '''

    def __init__(self, args):  # 1
        self.vbs = os.path.join(TGTDIR, 'bhservice_task.vbs')
        self.timeout = 1000 * 60

        win32serviceutil.ServiceFramework.__init__(self, args)
        self.hWaitStop = win32event.CreateEvent(None, 0, 0, None)

    '''В метода SvcStop ние посочваме състоянието на услугата и спираме нейното изпълнение '''

    def SvcStop(self):  # 2

        self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
        win32event.SetEvent(self.hWaitStop)

    '''В метода SvcDoRun стартираме услугата и извикваме основния метод, в който ще се изпълняват нашите задачи '''

    def SvcDoRun(self):  # 3
        self.ReportServiceStatus(win32service.SERVICE_RUNNING)
        self.main()

    '''Тук инициираме цикъл 1, който се изпълнява веднъж в минута (според параметъра self.timeout), 
    докато услугата получи сигнал за спиране 2. По време на изпълнение копираме скрипта в целевата директория, 
    изпълняваме го и изтриваме файла 3'''
    def main(self):
        while True:  # 1
            ret_code = win32event.WaitForSingleObject(self.hWaitStop, self.timeout)

            if ret_code == win32event.WAIT_OBJECT_0:  # 2
                servicemanager.LogInfoMsg("Service is stopping")
                break
        src = os.path.join(SRCDIR, 'bhservice_task.vbs')
        shutil.copy(src, self.vbs)
        subprocess.call("cscript.exe %s" % self.vbs, shell=False)  # 3
        os.unlink(self.vbs)

if __name__ == '__main__':
    if len(sys.argv) == 1:
        servicemanager.Initialize()
        servicemanager.PrepareToHostSingle(BHServerSvc)
        servicemanager.StartServiceCtrlDispatcher()
    else:
        win32serviceutil.HandleCommandLine(BHServerSvc)
