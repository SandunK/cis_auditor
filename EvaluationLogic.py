import re
import collections
import subprocess
import traceback
import shlex
from console_progressbar import ProgressBar

"""
@Author Sandun Gunasekara
Created on 11/20/2019
"""

try:
    # For Python 3.0 and later
    from urllib.request import urlopen
except ImportError:
    # Fall back to Python 2's urllib2
    from urllib2 import urlopen
from datetime import datetime


class EvaluationLogic:
    def __init__(self):
        global OKGREEN
        global WARNING  # global variable for colors
        global FAIL
        global ENDC
        global OKBLUE
        global input_func

        OKGREEN = '\033[92m'  # Green color start
        WARNING = '\033[93m'  # Yellow color
        FAIL = '\033[91m'  # Red color start
        OKBLUE = '\033[94m'  # Blue color
        ENDC = '\033[0m'  # End of colors

        input_func = None
        try:
            # for python 2
            input_func = raw_input
        except NameError:
            # for python 3
            input_func = input

    # configure file data according to a pre defined structure
    def filePreConfigurator(self, filePath):
        sectionLst = []  # Benchmark sections
        commandLst = []  # All the commands and their output
        sectionIndexLst = []  # index of the sections in file
        ruleDictionary = collections.OrderedDict()  # ordered dictionary key = sections, value = commands for section
        try:
            # confFile = urlopen('https://raw.githubusercontent.com/SandunK/git-demo-160176A/master/section.conf')      # file open from remote server
            confFile = open(filePath, "r")
            content = confFile.read().strip().splitlines()
        except IOError:
            traceback.print_exc()
        else:
            for i in content:
                sectionMatch = re.match(r'^\[.*\]', i)  # pattern to find sections
                if sectionMatch:
                    sectionLst.append(sectionMatch.group())
                    sectionIndexLst.append(content.index(i))

            for i in range(0, len(sectionIndexLst)):
                if i == len(sectionIndexLst) - 1:
                    commandLst.append(content[sectionIndexLst[i] + 1:])  # filter commands of each section
                else:
                    commandLst.append(content[sectionIndexLst[i] + 1:sectionIndexLst[i + 1]])

            for k in range(0, len(commandLst)):
                size = len(commandLst[k])
                separatorIndexLst = []  # Index of seperators
                separatorFound = False
                for idx, val in enumerate(commandLst[k]):
                    if separatorFound and val.strip() == '':  # find separators. separator used to seperate
                        continue  # commands from their results
                    elif val.strip() == '':
                        separatorIndexLst.append(idx)  # empty line used as seperator
                        separatorFound = True

                if len(separatorIndexLst) == 0:
                    result = [commandLst[k][i + 1:j] for i, j in
                              zip([-1] + separatorIndexLst, [size])]  # devide commands and respective results
                else:  # using seperator
                    result = [commandLst[k][i + 1:j] for i, j in zip([-1] + separatorIndexLst, separatorIndexLst + (
                        [size] if separatorIndexLst[-1] != size else []))]

                ruleDictionary[sectionLst[k]] = result

            return ruleDictionary

    # Method to find whether compliance or not
    def checkValidity(self, commandsAndResults, section):
        errorLog = open("logs/audit_error.log", "a")
        pb = ProgressBar(total=100, decimals=3, length=50, fill='#', zfill='-')
        success = 0

        for i in range(0, len(commandsAndResults[0])):
            commandLst = commandsAndResults[0]
            resultLst = commandsAndResults[1]

            try:
                if i == len(commandLst) - 1:  # Print progressbar
                    pb.print_progress_bar(100)
                else:
                    pb.print_progress_bar((100 / (len(commandLst))) * (i + 1))

                process = subprocess.Popen(commandLst[i], shell=True, stderr=subprocess.PIPE,  # execute the command
                                           stdout=subprocess.PIPE)

                outContent = process.stdout.readlines()         # command output
                errContent = process.stderr.readlines()         # command error output
                process.wait()
                if len(outContent)>0:
                    out = outContent[-1]                        # if output exists get last line
                else:
                    out = ''
                if len(errContent)>0:                           # if error exists get last line
                    err = errContent[-1]
                else:
                    err = ''
                errorState = process.poll()                     # get command error state
                process.wait()

                if resultLst[i].strip() == "errStderr":  # if definitely there should be any output
                    if err:
                        print(FAIL + "Non Compliance" + ENDC)
                        return "Non-compliance"
                    else:
                        if errorState != 0:  # state of the last bash output 0= no error 1 = error
                            print(FAIL + "Non Compliance" + ENDC)
                            return "Non-compliance"
                        else:
                            success += 1

                elif resultLst[i].strip() == "err":  # There should be any output. But errors will be errors
                    if err:
                        print(err)
                        errorLog.write(str(
                            datetime.utcnow()) + "UTC. Error occurred when auditing %s on %s command "
                                                 "with error \"%s\"\n" % (
                                           section, commandLst[i], err.strip()))
                        print(FAIL + "Error" + ENDC)
                        return "Error"
                    else:
                        if errorState != 0:  # state of the last bash output 0= no error 1 = error
                            print(FAIL + "Non Compliance" + ENDC)
                            return "Non-compliance"
                        else:
                            success += 1
                else:
                    # if process.stderr:
                    if err:                 # output defined but error occurred
                        print("\n" + err)
                        errorLog.write(str(
                            datetime.utcnow()) + "UTC. Error occurred when auditing %s on %s command "
                                                 "with error \"%s\"\n" % (
                                           section, commandLst[i], err.strip()))
                        print(FAIL + "Error" + ENDC)
                        return "Error"
                    else:
                        processStr = out.strip()
                        print('')
                        if processStr == resultLst[i]:  # compare the output with expected result
                            success += 1

            except subprocess.CalledProcessError as e:
                print(FAIL + e.output + ENDC)
                print(FAIL + "Error occurred when auditing " + section + " on " + commandLst[i][
                    i] + " command." + ENDC)
                errorLog.write(str(
                    datetime.utcnow()) + "UTC. Error occurred when Auditing %s on %s command "
                                         "with error \"%s\"\n" % (section, commandLst[i], e.output.strip()))
                return "Error"
            except IndexError:
                print(FAIL + "Error occurred when auditing " + section + " on " + commandLst[i][
                    i] + " command." + ENDC)
                errorLog.write(str(
                    datetime.utcnow()) + "UTC. Error occurred when Auditing %s on %s command "
                                         "with error \"%s\"\n" % (section, commandLst[i], traceback.print_exc()))
                return "Error"

        if success == len(commandsAndResults[0]):
            print(OKGREEN + "Compliance" + ENDC)  # Check whether all the commands are executed without errors
            return "Compliance"
        else:
            print(FAIL + "Non Compliance" + ENDC)
            return "Non-Compliance"

    # Remedy a section
    def remedy(self, remediationDictionary, section):
        errorLog = open("logs/remediation_error.log", "a")
        remedyFlag = False  # flag to identify whether remediation available

        for remediationSection, commands in remediationDictionary.items():  # loop through remediation
            if remediationSection == section:
                remedyFlag = True
                success = 0  # number of success executions
                for i in range(len(commands[0])):
                    try:
                        process = subprocess.Popen(commands[0][i], shell=True, stderr=subprocess.PIPE,
                                                   # execute the commands
                                                   stdout=subprocess.PIPE)  # execute remediation commands
                        success += 1
                        if process.stderr:  # if error occurred
                            for line in process.stderr:
                                print(line)
                                errorLog.write(str(
                                    datetime.utcnow()) + "UTC. Error occurred when remedying %s on %s command "
                                                         "with error \"%s\"\n" % (
                                                   section, commands[0][i], line.strip()))

                    except subprocess.CalledProcessError as e:
                        print(FAIL + e.output + ENDC)
                        print(FAIL + "Error occurred when remedying " + section + " on " + commands[0][
                            i] + " command." + ENDC)
                        errorLog.write(str(
                            datetime.utcnow()) + "UTC. Error occurred when remedying %s on %s command "
                                                 "with error \"%s\"\n" % (section, commands[0][i], e.output.strip()))

                if success == len(commands):
                    print(OKGREEN + 'Remediation success' + ENDC)  # check whether all the commands are executed
                else:
                    print(
                        FAIL + 'Remediation failed. For more info check error.log file in project_directory/error.log' + ENDC)
        if not remedyFlag:
            print(WARNING + "Remediation not available" + ENDC)  # check whether remediation defined
        errorLog.close()

    def auditOrRemediate(self, isRemedy):
        ruleDictionary = self.filePreConfigurator("conf/audit.conf")

        # Only audit
        if not isRemedy:
            auditResultFile = open("Audit_result.txt", "w")  # file that records audit results
            auditResultFile.write("Audit started at " + str(datetime.utcnow()) + " on UTC time.\n \n")
            for section, commandsAndResults in ruleDictionary.items():  # loop through sections
                print(OKBLUE + section.strip() + ENDC)
                validity = self.checkValidity(commandsAndResults, section)  # Check validity of the section
                auditResultFile.write("%s : %s\n" % (section, validity))

            auditResultFile.close()

        else:
            remediationDictionary = self.filePreConfigurator(
                "conf/remediation.conf")  # read commands to remedy each section
            remedyAll = False  # flag to define remedy all or not
            for section, commandsAndResults in ruleDictionary.items():
                print(OKBLUE + section + ENDC)
                validity = self.checkValidity(commandsAndResults, section)  # check validity of the section

                if validity == "Non-Compliance":
                    if remedyAll:
                        self.remedy(remediationDictionary, section)  # remedy the section
                    else:
                        needRemediation = input_func(
                            "Section is non compliance with benchmarks. Do you want a remediation "  # prompt to user asking a remediation
                            "(Y/N/A) : ")
                        if needRemediation.lower() == "y":
                            self.remedy(remediationDictionary, section)
                        elif needRemediation.lower() == "n":
                            print(WARNING + "Remediation skipped !" + ENDC)
                            continue
                        elif needRemediation.lower() == "a":
                            remedyAll = True
                        else:
                            print(WARNING + "Invalid Input. Section remediation not applied !" + ENDC)
