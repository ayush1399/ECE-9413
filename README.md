# VMIPS Timing and Functional Simulators

## ECE-GY 9413 Course Project

Authors: Ayushman Singh (as16513) and Rachel Abreu (ra2466)

### How to Run

The timing simulator is located in the Phase2 folder.

```
python as16513_ra2466_timingsimulator.py --iodir <test-dir>
```

Timing Simulator

This tool that models the data path and control path of a microarchitecture to predict how long it will take to execute a program. It takes as input an assembly instruction file, and VDMEM and SDMEM files and a configuration file for the microarchitecture parameters and outputs the number of cycles required to execute the program.

### Test Cases

Tests can be found in separate folders within DotProduct and FullyConnected folders. The following tests are included:

| Folder         | Description                          |
| -------------- | ------------------------------------ |
| Dot Product    | Dot product implementation           |
| FullyConnected | Fully Connected Layer Implementation |
