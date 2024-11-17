#Project: BlenderFacadeExporter
#Author: Connor Russell
#Date: 11/9/2024
#Purpose: Provide simple single function call to open a blender file, call the export function, and compare it with a known good file

import bpy
import sys
import argparse

def test(test_dir):
    b_pass = False

    #Open the test file, which is in the test_dir/Exporter.blend
    print("Opening test file: " + test_dir + "/Exporter.blend")
    bpy.ops.wm.open_mainfile(filepath=test_dir + "/Exporter.blend")

    #Call the operator blender_utils.export_facade
    print("Exporting facade")
    bpy.ops.blender_utils.export_facade()

    #Define paths for the files to compare
    new_file = test_dir + "/Exporter.fac"
    known_good_file = test_dir + "/Exporter.good.fac"
    exporter_output = test_dir + "/Test Results.csv"

    #Check if this is Blender version 3.6 or greater. If so we need to check against a different file as there are tiny coordinate differences between the versions
    if bpy.app.version[0] >= 4 and bpy.app.version[1] >= 0:
        known_good_file = test_dir + "/Exporter.good.40.fac"
    elif bpy.app.version[0] >= 3 and bpy.app.version[1] >= 6:
        known_good_file = test_dir + "/Exporter.good.36.fac"

    print("Comparing files" + new_file + " and " + known_good_file)

    #Compare the exported file with the known good file
    b_pass = True
    chr_same = 0
    chr_total = 0
    with open(new_file, 'r') as new, open(known_good_file, 'r') as good:
        f_new = new.read()
        f_good = good.read()

        #Iterate through every character
        for i in range(len(f_new)):
            try:
                if f_new[i] == f_good[i]:
                    chr_same += 1
                else:
                    b_pass = False                    
                chr_total += 1
            except:
                b_pass = False
                print("ERROR at " + str(i) + " in file " + new_file)
                break
        
    try:
        similarity = chr_same / chr_total
    except:
        similarity = 0

    #Append the test results to the exporter_output file
    with open(exporter_output, 'a') as output:
        if b_pass:
            output.write("Exporter,PASS," + "{:.{precision}f}".format(similarity * 100, precision=4) + "%\n")
        else:
            output.write("Exporter,FAIL," + "{:.{precision}f}".format(similarity * 100, precision=4) + "%\n")

#Program entry point. Here we get the test directory, and call the test function
if __name__ == "__main__":

    #Parse the command line arguments
    try:
        for i in range(len(sys.argv)):
            if sys.argv[i] == "--test-dir":
                test_dir = sys.argv[i+1]
    except:
        print("Error parsing command line arguments")
        sys.exit(1)

    test(test_dir)


