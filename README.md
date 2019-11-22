# Cis Auditor
This project is to audit and remedy a system according to the benchmarks supplied using configuration file

## Setup
- Install all the dependencies in dependency.txt
- run cis_benchmarks.py

## Edit Benchmarks
There are two configuration files in conf/ directory.       
  - audit.conf contains all the commands and their results that needs to do auditing       
    > Note: Don't change the file structure. sections should be in []. After defining a section add audit commands line by line. After one empty line add respective results of the commands to audit. **IMPORTANT** Only use empty lines to seperate commands from there results        
    eg: 
    `[section 1]`        
    `command1`        
    `command2`        
    `command3`        
    `        `        
    `result1`        
    `result2`        
    `result3`        
    `[section 2]`        
    `........`        
  - remediation.conf containts remediation commands for sections. 
    > Note: After defining sections as audit.conf add all the shell commands need to execute line by line as before. **IMPORTANT** There should not be empty lines        
    eg: `[section 1]`        
        `command1`        
        `command2`        
        `command3`        
        `[section 2]`        
        `........`
