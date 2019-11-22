import traceback

from art import *
from EvaluationLogic import *

tprint("CIS Benchmark Auditor")

mode = raw_input("Audit or Remediation (A/R/E) :")
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
elif mode.lower() == 'e':
    exit()
else:
    print("Invalid input")


