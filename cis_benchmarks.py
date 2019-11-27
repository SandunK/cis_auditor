import traceback
import subprocess
from EvaluationLogic import *


input_func = None
try:
    input_func = raw_input
except NameError:
    input_func = input

try:
    from art import *
    from console_progressbar import ProgressBar
except ImportError:
    rc = subprocess.call("./configure.sh")
    from art import *
    from console_progressbar import ProgressBar


tprint("CIS Benchmark Auditor")
mode = input_func("Audit or Remediation (A/R) :")
logic = EvaluationLogic()

if mode.lower() == 'a':
    print("Audit started...")
    try:
        logic.auditOrRemediate(False)   # Flag is to indicate whether need a remediation
    except Exception as e:
        traceback.print_exc()
elif mode.lower() == 'r':
    print("Remediation started...")
    try:
        logic.auditOrRemediate(True)  # Flag is to indicate whether need a remediation
    except Exception as e:
        traceback.print_exc()
else:
    print("Invalid input")


