import csv
import io
import pandas as pd
import InputLog

class SignatureDetector:

    EVENT_TGT = "4768"
    EVENT_ST="4769"
    EVENT_PRIV = "4672"
    EVENT_PROCESS = "4688"
    EVENT_PRIV_SERVICE = "4673"
    EVENT_PRIV_OPE = "4674"
    EVENT_SHARE = "5140"
    SYSTEM_DIR = "c:\windows";
    SYSTEM_DIR2 = "c:\program files";
    PSEXESVC = "psexesvc";
    ADMINSHARE="\c$"
    RESULT_NORMAL="normal"
    RESULT_PRIV="attack: Unexpected privilege is used"
    RESULT_CMD="attack: command on blackList is used"
    RESULT_MAL_CMD = "attack: Abnormal command or tool is used"
    RESULT_ADMINSHARE = "attack: Admin share is used"
    RESULT_NOTGT="attack: Golden Ticket is used"

    df=pd.DataFrame(data=None, index=None, columns=["datetime","eventid","accountname","clientaddr","servicename","processname","objectname"], dtype=None, copy=False)
    df_admin = pd.DataFrame(data=None, index=None, columns=[ "accountname"], dtype=None, copy=False)
    df_cmd = pd.DataFrame(data=None, index=None, columns=["processname"], dtype=None, copy=False)


    def __init__(self):
        print("constructor called")

    def is_attack(self):
        print("is_attack called")

    @staticmethod
    def signature_detect(datetime, eventid, accountname, clientaddr, servicename, processname, objectname,sharedname):
        """ Detect attack using signature based detection.
        :param datetime: Datetime of the event
        :param eventid: EventID
        :param accountname: Accountname
        :param clientaddr: Source IP address
        :param servicename: Service name
        :param processname: Process name(command name)
        :param objectname: Object name
        :return : True(1) if attack, False(0) if normal
        """

        inputLog = InputLog.InputLog(datetime, eventid, accountname, clientaddr, servicename, processname, objectname,sharedname)
        return SignatureDetector.signature_detect(inputLog)

    @staticmethod
    def signature_detect(inputLog):
        """ Detect attack using signature based detection.
        :param inputLog: InputLog object of the event
        :return : True(1) if attack, False(0) if normal
        """

        #print(SignatureDetector.df)

        #SignatureDetector.df["accountname"] = SignatureDetector.df["accountname"].str.lower()

        result=SignatureDetector.RESULT_NORMAL


        if (inputLog.get_eventid()==SignatureDetector.EVENT_ST) :
            result=SignatureDetector.hasNoTGT(inputLog)

        elif (inputLog.get_eventid() == SignatureDetector.EVENT_PRIV):
            result =SignatureDetector.isNotAdmin(inputLog)

        elif (inputLog.get_eventid() == SignatureDetector.EVENT_PRIV_OPE
                or inputLog.get_eventid() == SignatureDetector.EVENT_PRIV_SERVICE
                or inputLog.get_eventid() == SignatureDetector.EVENT_PROCESS):
            result = SignatureDetector.isSuspiciousProcess(inputLog)

        elif (inputLog.get_eventid() == SignatureDetector.EVENT_SHARE):
            result =SignatureDetector.isAdminshare(inputLog)

        series = pd.Series([inputLog.get_datetime(),inputLog.get_eventid(),inputLog.get_accountname(),inputLog.get_clientaddr(),
                      inputLog.get_servicename(),inputLog.get_processname(),inputLog.get_objectname()], index=SignatureDetector.df.columns)
        SignatureDetector.df=SignatureDetector.df.append(series, ignore_index = True)

        return result

    @staticmethod
    def hasNoTGT(inputLog):
        SignatureDetector.df["eventid"]=SignatureDetector.df["eventid"].astype(str)
        logs=SignatureDetector.df[(SignatureDetector.df.accountname == inputLog.get_accountname())
                                  &(SignatureDetector.df.clientaddr==inputLog.get_clientaddr())
                                  & (SignatureDetector.df.eventid == SignatureDetector.EVENT_TGT)
        ]
        if len(logs)==0:
            print("Signature D: " + SignatureDetector.RESULT_NOTGT)
            return SignatureDetector.RESULT_NOTGT
        else:
            return SignatureDetector.RESULT_NORMAL

    @staticmethod
    def isNotAdmin(inputLog):
        logs = SignatureDetector.df_admin[(SignatureDetector.df_admin.accountname == inputLog.get_accountname())]
        if len(logs) == 0:
            print("Signature A: " + SignatureDetector.RESULT_PRIV)
            return SignatureDetector.RESULT_PRIV
        else:
            return SignatureDetector.RESULT_NORMAL

    @staticmethod
    def isSuspiciousProcess(inputLog):

        logs = SignatureDetector.df[(SignatureDetector.df.accountname == inputLog.get_accountname())
                                    & (SignatureDetector.df.eventid == SignatureDetector.EVENT_ST)
                                    ]
        latestlog=logs.tail(1)
        if(len(latestlog)>0):
            clientaddr=latestlog.clientaddr.values[0]
            inputLog.set_clientaddr(clientaddr)

        #print(inputLog.get_clientaddr()+","+inputLog.get_accountname())

        if (inputLog.get_processname().find(SignatureDetector.SYSTEM_DIR)==-1 and inputLog.get_processname().find(SignatureDetector.SYSTEM_DIR2)==-1):
            print("Signature B: "+SignatureDetector.RESULT_MAL_CMD)
            return SignatureDetector.RESULT_MAL_CMD
        cmds=inputLog.get_processname().split("\\")
        cmd=cmds[len(cmds)-1]
        logs = SignatureDetector.df_cmd[SignatureDetector.df_cmd.processname.str.contains(cmd)]
        if len(logs)>0:
            print("Signature B: " + SignatureDetector.RESULT_CMD)
            return SignatureDetector.RESULT_CMD

        if inputLog.get_objectname().find(SignatureDetector.PSEXESVC)>=0:
            print("Signature B: " + SignatureDetector.RESULT_CMD)
            return SignatureDetector.RESULT_CMD

        return SignatureDetector.RESULT_NORMAL

    @staticmethod
    def isAdminshare(inputLog):
        if inputLog.get_sharedname().find(SignatureDetector.ADMINSHARE)>=0:
            print("Signature C: " + SignatureDetector.RESULT_ADMINSHARE)
            return SignatureDetector.RESULT_ADMINSHARE

        return SignatureDetector.RESULT_NORMAL

