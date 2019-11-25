import re
import collections
import subprocess
import traceback

from console_progressbar import ProgressBar
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
            input_func = raw_input
        except NameError:
            input_func = input

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

    # Method to find the compliance of the system
    def checkValidity(self, commandsAndResults):
        pb = ProgressBar(total=100, decimals=3, length=50, fill='#', zfill='-')
        success = 0
        for i in range(0, len(commandsAndResults[0])):
            commandLst = commandsAndResults[0]
            resultLst = commandsAndResults[1]

            try:
                process = subprocess.Popen(commandLst[i], shell=True, stderr=subprocess.PIPE,
                                           stdout=subprocess.PIPE)
                process = process.communicate()[0].strip()  # evaluate commands on system
                print('')
                # process = str(process).encode('utf-8').strip()
                if i == len(commandLst) - 1:
                    pb.print_progress_bar(100)
                else:
                    pb.print_progress_bar((100 / (len(commandLst))) * (i + 1))
                if process == resultLst[i]:
                    success += 1

            except subprocess.CalledProcessError as e:
                print(e.output)
                print("\n", FAIL + "Non Compliance" + ENDC)
                return "Non-Compliance"

        if success == len(commandsAndResults[0]):
            print(OKGREEN + "Compliance" + ENDC)  # Check whether all the commands are executed without errors
            return "Compliance"
        else:
            print(FAIL + "Non Compliance" + ENDC)
            return "Non-Compliance"

    def remedy(self, remediationDictionary, section):
        errorLog = open("logs/error.log", "a")
        remedyFlag = False
        for remediationSection, commands in remediationDictionary.items():
            if remediationSection == section:
                remedyFlag = True
                success = 0
                for i in range(len(commands[0])):
                    try:
                        process = subprocess.Popen(commands[0][i], shell=True, stderr=subprocess.PIPE,
                                                   stdout=subprocess.PIPE)  # execute remediation commands
                        success += 1
                        if process.stderr:
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
                validity = self.checkValidity(commandsAndResults)
                auditResultFile.write("%s : %s\n" % (section, validity))

            auditResultFile.close()

        else:  # remediation
            remedyAll = input_func("Do you want to remedy all (Y/N/E) : ")
            if remedyAll.lower() == "y":
                remediationDictionary = self.filePreConfigurator("conf/remediation.conf")
                for section, commandsAndResults in ruleDictionary.items():
                    print(OKBLUE + section + ENDC)
                    validity = self.checkValidity(commandsAndResults)
                    if validity == "Non-Compliance":
                        self.remedy(remediationDictionary, section)

            elif remedyAll.lower() == "n":
                remediationDictionary = self.filePreConfigurator("conf/remediation.conf")
                for section, commandsAndResults in ruleDictionary.items():
                    print(OKBLUE + section + ENDC)
                    validity = self.checkValidity(commandsAndResults)
                    if validity == "Non-Compliance":
                        needRemediation = input_func(
                            "Section is non compliance with benchmarks. Do you want a remediation "  # prompt to user asking a remediation
                            "(Y/N/E) : ")
                        if needRemediation.lower() == "y":
                            self.remedy(remediationDictionary, section)
                        elif needRemediation.lower() == "n":
                            print(WARNING + "Remediation skipped !" + ENDC)
                            continue
                        elif needRemediation.lower() == "e":
                            exit()
                        else:
                            print(WARNING + "Invalid Input. Section remediation not applied !" + ENDC)

            elif remedyAll.lower() == "e":
                exit()

            else:
                print(WARNING + "Invalid Input. Section remediation not applied !" + ENDC)
