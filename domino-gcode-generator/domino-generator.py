#!/usr/bin/python3

import os
from datetime import datetime


PIP_DEPTH = -2.0        # How deep to drill the pip from the surface of the domino
PIP_DIA = 4.2           # The diameter of the pip at the PIP_DEPTH - could be different if using v-bit vs drill.
PIP_MAX_SQUARE = 17.5   # The pip pattern will fill to the extents of this boundary.
L_ORIGIN_X = 12.7       # X-coord for the center of the left half of the domino.
L_ORIGIN_Y = -12.7      # Y-coord for the center of the left half of the domino.
R_ORIGIN_X = 38.1       # X-coord for the center of the right half of the domino.
R_ORIGIN_Y = -12.7      # Y-coord for the center of the right half of the domino.

R_PLANE = 0.7           # mm above part
Z_RETRACT = 2.5         # mm above part
DRILL_FEED = 100.0      # mm/min

PART_CHANGE__X  = 5.0   # Location where we will change out to the next domino.
PART_CHANGE__Y  = 30.0

# Returns the maximum travel which keeps pips at the extremes of the pattern boundary
def max_pattern_dist(max_square, pip_dia_at_depth):
    return (max_square - pip_dia_at_depth)

# Go to part change location and pause. Swap part, then click resume in linuxcnc to go to next domino
def next_domino():
    ret_str = "\n(Put a new domino in the work holding.) ;\n"
    ret_str += f"G00 X{PART_CHANGE__X} Y{PART_CHANGE__Y} (Rapid to part change location.) ;\n"
    ret_str += "M0 (Pause for part change.) ;\n"
    return ret_str

def gcode_header():

    filename = os.path.basename(__file__)
    date_time = datetime.now().strftime("%Y/%m/%d, %H:%M:%S")

    ret_str = "%\n"
    ret_str += f"(Generated by {filename} on {date_time})\n"
    ret_str += "(G54 X0 Y0 is at the top-left of part) ;\n"
    ret_str += "(Z0 is on top of the part) ;\n"
    ret_str += f"(Tool produces a {PIP_DIA} diameter hole at domino top plane Z=0.0)\n"
    ret_str += "(BEGIN PREPARATION BLOCKS) ;\n"
    ret_str += "T1 M06 (Select tool 1) ;\n"
    ret_str += "G00 G90 G40 G49 G54 (Safe startup) ;\n"
    ret_str += "G21 (Programming in mm) ;\n"
    ret_str += f"G00 G90 Z{Z_RETRACT} (Rapid retract) ;\n"
    #ret_str += "G00 G54 X2. Y-2. (Rapid to 1st position) ;\n"
    #ret_str += "S1000 M03 (Spindle on CW) ;\n"
    #ret_str += "G43 H01 Z0.1 (Activate tool offset 1) ;\n"
    #ret_str += "M08 (Coolant on) ;\n"
    return ret_str

def gcode_footer():
    ret_str = "\n"
    ret_str += "(BEGIN COMPLETION BLOCKS) ;\n"
    #ret_str += f"G53 G49 M05 (spindle off) ;\n"
    #ret_str += f"G53 Y{PART_CHANGE__Y} ;\n"
    ret_str += f"G00 X{PART_CHANGE__X} Y{PART_CHANGE__Y} (Rapid to part change location.) ;\n"
    ret_str += "M30 (End program) ;\n"
    ret_str += "%\n"
    return ret_str

def one_pip(msg, pattern_x,pattern_y, pip_depth):
    ret_str = f"({msg} at X:{pattern_x:.2f},Y:{pattern_y:.2f}) ;\n"

    ret_str += f"G00 X{pattern_x:.2f} Y{pattern_y:.2f} (Rapid to pattern center.) ;\n"

    ret_str += f"G81 Z{pip_depth} R{R_PLANE} F{DRILL_FEED} (Begin drill cycle.) ;\n"

    ret_str += "G80 (Cancel drill cycle.) ;\n"
    ret_str += f"G00 G90 Z{Z_RETRACT} (Rapid retract) ;\n"

    return ret_str

def two_pips(msg, pattern_x,pattern_y, max_square, pip_depth, pip_dia_at_depth):
    ret_str = f"({msg} at X:{pattern_x:.2f},Y:{pattern_y:.2f}) ;\n"

    ret_str += f"G00 X{pattern_x:.2f} Y{pattern_y:.2f} (Rapid to pattern center.) ;\n"
    
    max_travel = max_pattern_dist(max_square, pip_dia_at_depth)
    half_max_travel = max_travel/2.0

    hole_0 = (pattern_x-half_max_travel, pattern_y+half_max_travel)
    hole_1 = (pattern_x+half_max_travel, pattern_y-half_max_travel)
    
    ret_str += f"G00 X{hole_0[0]:.2f} Y{hole_0[1]:.2f} (Rapid to top-left pip.) ;\n"

    ret_str += f"G81 Z{pip_depth} R{R_PLANE} F{DRILL_FEED} (Begin drill cycle.) ;\n"
    ret_str += f"X{hole_1[0]:.2f} Y{hole_1[1]:.2f} (2nd hole) ;\n"

    ret_str += "G80 (Cancel drill cycle.) ;\n"
    ret_str += f"G00 G90 Z{Z_RETRACT} (Rapid retract) ;\n"

    return ret_str

def four_pips(msg, pattern_x,pattern_y, max_square, pip_depth, pip_dia_at_depth):
    ret_str = f"({msg} at X:{pattern_x:.2f},Y:{pattern_y:.2f}) ;\n"

    ret_str += f"G00 X{pattern_x:.2f} Y{pattern_y:.2f} (Rapid to pattern center.) ;\n"
    
    max_travel = max_pattern_dist(max_square, pip_dia_at_depth)
    half_max_travel = max_travel/2.0

    hole_0 = (pattern_x-half_max_travel, pattern_y+half_max_travel)
    hole_1 = (pattern_x+half_max_travel, pattern_y+half_max_travel)
    hole_2 = (pattern_x+half_max_travel, pattern_y-half_max_travel)
    hole_3 = (pattern_x-half_max_travel, pattern_y-half_max_travel)

    ret_str += f"G00 X{hole_0[0]:.2f} Y{hole_0[1]:.2f} (Rapid to top-left pip.) ;\n"

    ret_str += f"G81 Z{pip_depth} R{R_PLANE} F{DRILL_FEED} (Begin drill cycle.) ;\n"
    ret_str += f"X{hole_1[0]:.2f} Y{hole_1[1]:.2f} (2nd hole) ;\n"
    ret_str += f"X{hole_2[0]:.2f} Y{hole_2[1]:.2f} (3rd hole) ;\n"
    ret_str += f"X{hole_3[0]:.2f} Y{hole_3[1]:.2f} (4th hole) ;\n"

    ret_str += "G80 (Cancel drill cycle.) ;\n"
    ret_str += f"G00 G90 Z{Z_RETRACT} (Rapid retract) ;\n"

    return ret_str

def six_pips(msg, pattern_x,pattern_y, max_square, pip_depth, pip_dia_at_depth):
    ret_str = f"({msg} at X:{pattern_x:.2f},Y:{pattern_y:.2f}) ;\n"

    ret_str += f"G00 X{pattern_x:.2f} Y{pattern_y:.2f} (Rapid to pattern center.) ;\n"
    
    max_travel = max_pattern_dist(max_square, pip_dia_at_depth)
    half_max_travel = max_travel/2.0

    hole_0 = (pattern_x-half_max_travel, pattern_y+half_max_travel)
    hole_1 = (pattern_x, pattern_y+half_max_travel)
    hole_2 = (pattern_x+half_max_travel, pattern_y+half_max_travel)
    hole_3 = (pattern_x+half_max_travel, pattern_y-half_max_travel)
    hole_4 = (pattern_x, pattern_y-half_max_travel)
    hole_5 = (pattern_x-half_max_travel, pattern_y-half_max_travel)

    ret_str += f"G00 X{hole_0[0]:.2f} Y{hole_0[1]:.2f} (Rapid to top-left pip.) ;\n"
    ret_str += f"G81 Z{pip_depth} R{R_PLANE} F{DRILL_FEED} (Begin drill cycle.) ;\n"
    ret_str += f"X{hole_1[0]:.2f} Y{hole_1[1]:.2f} (2nd hole) ;\n"
    ret_str += f"X{hole_2[0]:.2f} Y{hole_2[1]:.2f} (3rd hole) ;\n"
    ret_str += f"X{hole_3[0]:.2f} Y{hole_3[1]:.2f} (4th hole) ;\n"
    ret_str += f"X{hole_4[0]:.2f} Y{hole_4[1]:.2f} (5th hole) ;\n"
    ret_str += f"X{hole_5[0]:.2f} Y{hole_5[1]:.2f} (6th hole) ;\n"

    ret_str += "G80 (Cancel drill cycle.) ;\n"
    ret_str += f"G00 G90 Z{Z_RETRACT} (Rapid retract) ;\n"

    return ret_str

def main():
    with open("domino_set.ngc",'w',encoding = "utf-8") as f:
        f.write(gcode_header())

        f.write(next_domino())

        f.write("\n(~~~~~~~~~~ Start 0x1 Domino. ~~~~~~~~~~) ;\n")
        f.write(one_pip("BEGIN 1-PIP PATTERN", R_ORIGIN_X, R_ORIGIN_Y, PIP_DEPTH))
        f.write("(~~~~~~~~~~ End 0x1 Domino. ~~~~~~~~~~) ;\n")

        f.write(next_domino())

        f.write("\n(~~~~~~~~~~ Start 0x2 Domino. ~~~~~~~~~~) ;\n")
        f.write(two_pips("BEGIN 2-PIP PATTERN", R_ORIGIN_X, R_ORIGIN_Y, PIP_MAX_SQUARE, PIP_DEPTH,PIP_DIA))
        f.write("(~~~~~~~~~~ End 0x2 Domino. ~~~~~~~~~~) ;\n")

        f.write(next_domino())

        f.write("\n(~~~~~~~~~~ Start 0x3 Domino. ~~~~~~~~~~) ;\n")
        f.write(one_pip("BEGIN 1-PIP PATTERN", R_ORIGIN_X, R_ORIGIN_Y, PIP_DEPTH))
        f.write(two_pips("BEGIN 2-PIP PATTERN", R_ORIGIN_X, R_ORIGIN_Y, PIP_MAX_SQUARE, PIP_DEPTH,PIP_DIA))
        f.write("(~~~~~~~~~~ End 0x3 Domino. ~~~~~~~~~~) ;\n")

        f.write(next_domino())

        f.write("\n(~~~~~~~~~~ Start 0x4 Domino. ~~~~~~~~~~) ;\n")
        f.write(four_pips("BEGIN 4-PIP PATTERN", R_ORIGIN_X, R_ORIGIN_Y, PIP_MAX_SQUARE, PIP_DEPTH,PIP_DIA))
        f.write("(~~~~~~~~~~ End 0x4 Domino. ~~~~~~~~~~) ;\n")

        f.write(next_domino())

        f.write("\n(~~~~~~~~~~ Start 0x5 Domino. ~~~~~~~~~~) ;\n")
        f.write(one_pip("BEGIN 1-PIP PATTERN", R_ORIGIN_X, R_ORIGIN_Y, PIP_DEPTH))
        f.write(four_pips("BEGIN 4-PIP PATTERN", R_ORIGIN_X, R_ORIGIN_Y, PIP_MAX_SQUARE, PIP_DEPTH,PIP_DIA))
        f.write("(~~~~~~~~~~ End 0x5 Domino. ~~~~~~~~~~) ;\n")

        f.write(next_domino())

        f.write("\n(~~~~~~~~~~ Start 0x6 Domino. ~~~~~~~~~~) ;\n")
        f.write(six_pips("BEGIN 6-PIP PATTERN", R_ORIGIN_X, R_ORIGIN_Y, PIP_MAX_SQUARE, PIP_DEPTH,PIP_DIA))
        f.write("(~~~~~~~~~~ End 0x6 Domino. ~~~~~~~~~~) ;\n")

        f.write(next_domino())
        
        f.write("\n(~~~~~~~~~~ Start 1x1 Domino. ~~~~~~~~~~) ;\n")
        f.write(one_pip("BEGIN 1-PIP PATTERN", L_ORIGIN_X, L_ORIGIN_Y, PIP_DEPTH))
        f.write("\n")
        f.write(one_pip("BEGIN 1-PIP PATTERN", R_ORIGIN_X, R_ORIGIN_Y, PIP_DEPTH))
        f.write("(~~~~~~~~~~ End 1x1 Domino. ~~~~~~~~~~) ;\n")

        f.write(next_domino())

        f.write("\n(~~~~~~~~~~ Start 1x2 Domino. ~~~~~~~~~~) ;\n")
        f.write(one_pip("BEGIN 1-PIP PATTERN", L_ORIGIN_X, L_ORIGIN_Y, PIP_DEPTH))
        f.write("\n")
        f.write(two_pips("BEGIN 2-PIP PATTERN", R_ORIGIN_X, R_ORIGIN_Y, PIP_MAX_SQUARE, PIP_DEPTH,PIP_DIA))
        f.write("(~~~~~~~~~~ End 1x2 Domino. ~~~~~~~~~~) ;\n")

        f.write(next_domino())

        f.write("\n(~~~~~~~~~~ Start 1x3 Domino. ~~~~~~~~~~) ;\n")
        f.write(one_pip("BEGIN 1-PIP PATTERN", L_ORIGIN_X, L_ORIGIN_Y, PIP_DEPTH))
        f.write("\n")
        f.write(one_pip("BEGIN 1-PIP PATTERN", R_ORIGIN_X, R_ORIGIN_Y, PIP_DEPTH))
        f.write(two_pips("BEGIN 2-PIP PATTERN", R_ORIGIN_X, R_ORIGIN_Y, PIP_MAX_SQUARE, PIP_DEPTH,PIP_DIA))
        f.write("(~~~~~~~~~~ End 1x3 Domino. ~~~~~~~~~~) ;\n")

        f.write(next_domino())

        f.write("\n(~~~~~~~~~~ Start 1x4 Domino. ~~~~~~~~~~) ;\n")
        f.write(one_pip("BEGIN 1-PIP PATTERN", L_ORIGIN_X, L_ORIGIN_Y, PIP_DEPTH))
        f.write("\n")
        f.write(four_pips("BEGIN 4-PIP PATTERN", R_ORIGIN_X, R_ORIGIN_Y, PIP_MAX_SQUARE, PIP_DEPTH,PIP_DIA))
        f.write("(~~~~~~~~~~ End 1x4 Domino. ~~~~~~~~~~) ;\n")

        f.write(next_domino())

        f.write("\n(~~~~~~~~~~ Start 1x5 Domino. ~~~~~~~~~~) ;\n")
        f.write(one_pip("BEGIN 1-PIP PATTERN", L_ORIGIN_X, L_ORIGIN_Y, PIP_DEPTH))
        f.write("\n")
        f.write(one_pip("BEGIN 1-PIP PATTERN", R_ORIGIN_X, R_ORIGIN_Y, PIP_DEPTH))
        f.write(four_pips("BEGIN 4-PIP PATTERN", R_ORIGIN_X, R_ORIGIN_Y, PIP_MAX_SQUARE, PIP_DEPTH,PIP_DIA))
        f.write("(~~~~~~~~~~ End 1x5 Domino. ~~~~~~~~~~) ;\n")

        f.write(next_domino())

        f.write("\n(~~~~~~~~~~ Start 1x6 Domino. ~~~~~~~~~~) ;\n")
        f.write(one_pip("BEGIN 1-PIP PATTERN", L_ORIGIN_X, L_ORIGIN_Y, PIP_DEPTH))
        f.write("\n")
        f.write(six_pips("BEGIN 6-PIP PATTERN", R_ORIGIN_X, R_ORIGIN_Y, PIP_MAX_SQUARE, PIP_DEPTH,PIP_DIA))
        f.write("(~~~~~~~~~~ End 1x6 Domino. ~~~~~~~~~~) ;\n")

        f.write(next_domino())

        f.write("\n(~~~~~~~~~~ Start 2x2 Domino. ~~~~~~~~~~) ;\n")
        f.write(two_pips("BEGIN 2-PIP PATTERN", L_ORIGIN_X, L_ORIGIN_Y, PIP_MAX_SQUARE, PIP_DEPTH,PIP_DIA))
        f.write("\n")
        f.write(two_pips("BEGIN 2-PIP PATTERN", R_ORIGIN_X, R_ORIGIN_Y, PIP_MAX_SQUARE, PIP_DEPTH,PIP_DIA))
        f.write("(~~~~~~~~~~ End 2x2 Domino. ~~~~~~~~~~) ;\n")

        f.write(next_domino())

        f.write("\n(~~~~~~~~~~ Start 2x3 Domino. ~~~~~~~~~~) ;\n")
        f.write(two_pips("BEGIN 2-PIP PATTERN", L_ORIGIN_X, L_ORIGIN_Y, PIP_MAX_SQUARE, PIP_DEPTH,PIP_DIA))
        f.write("\n")
        f.write(one_pip("BEGIN 1-PIP PATTERN", R_ORIGIN_X, R_ORIGIN_Y, PIP_DEPTH))
        f.write(two_pips("BEGIN 2-PIP PATTERN", R_ORIGIN_X, R_ORIGIN_Y, PIP_MAX_SQUARE, PIP_DEPTH,PIP_DIA))
        f.write("(~~~~~~~~~~ End 2x3 Domino. ~~~~~~~~~~) ;\n")

        f.write(next_domino())

        f.write("\n(~~~~~~~~~~ Start 2x4 Domino. ~~~~~~~~~~) ;\n")
        f.write(two_pips("BEGIN 2-PIP PATTERN", L_ORIGIN_X, L_ORIGIN_Y, PIP_MAX_SQUARE, PIP_DEPTH,PIP_DIA))
        f.write("\n")
        f.write(four_pips("BEGIN 4-PIP PATTERN", R_ORIGIN_X, R_ORIGIN_Y, PIP_MAX_SQUARE, PIP_DEPTH,PIP_DIA))
        f.write("(~~~~~~~~~~ End 2x4 Domino. ~~~~~~~~~~) ;\n")

        f.write(next_domino())

        f.write("\n(~~~~~~~~~~ Start 2x5 Domino. ~~~~~~~~~~) ;\n")
        f.write(two_pips("BEGIN 2-PIP PATTERN", L_ORIGIN_X, L_ORIGIN_Y, PIP_MAX_SQUARE, PIP_DEPTH,PIP_DIA))
        f.write("\n")
        f.write(one_pip("BEGIN 1-PIP PATTERN", R_ORIGIN_X, R_ORIGIN_Y, PIP_DEPTH))
        f.write(four_pips("BEGIN 4-PIP PATTERN", R_ORIGIN_X, R_ORIGIN_Y, PIP_MAX_SQUARE, PIP_DEPTH,PIP_DIA))
        f.write("(~~~~~~~~~~ End 2x5 Domino. ~~~~~~~~~~) ;\n")

        f.write(next_domino())

        f.write("\n(~~~~~~~~~~ Start 2x6 Domino. ~~~~~~~~~~) ;\n")
        f.write(two_pips("BEGIN 2-PIP PATTERN", L_ORIGIN_X, L_ORIGIN_Y, PIP_MAX_SQUARE, PIP_DEPTH,PIP_DIA))
        f.write("\n")
        f.write(six_pips("BEGIN 6-PIP PATTERN", R_ORIGIN_X, R_ORIGIN_Y, PIP_MAX_SQUARE, PIP_DEPTH,PIP_DIA))
        f.write("(~~~~~~~~~~ End 2x6 Domino. ~~~~~~~~~~) ;\n")

        f.write(next_domino())

        f.write("\n(~~~~~~~~~~ Start 3x3 Domino. ~~~~~~~~~~) ;\n")
        f.write(one_pip("BEGIN 1-PIP PATTERN", L_ORIGIN_X, L_ORIGIN_Y, PIP_DEPTH))
        f.write(two_pips("BEGIN 2-PIP PATTERN", L_ORIGIN_X, L_ORIGIN_Y, PIP_MAX_SQUARE, PIP_DEPTH,PIP_DIA))
        f.write("\n")
        f.write(one_pip("BEGIN 1-PIP PATTERN", R_ORIGIN_X, R_ORIGIN_Y, PIP_DEPTH))
        f.write(two_pips("BEGIN 2-PIP PATTERN", R_ORIGIN_X, R_ORIGIN_Y, PIP_MAX_SQUARE, PIP_DEPTH,PIP_DIA))
        f.write("(~~~~~~~~~~ End 3x3 Domino. ~~~~~~~~~~) ;\n")

        f.write(next_domino())

        f.write("\n(~~~~~~~~~~ Start 3x4 Domino. ~~~~~~~~~~) ;\n")
        f.write(one_pip("BEGIN 1-PIP PATTERN", L_ORIGIN_X, L_ORIGIN_Y, PIP_DEPTH))
        f.write(two_pips("BEGIN 2-PIP PATTERN", L_ORIGIN_X, L_ORIGIN_Y, PIP_MAX_SQUARE, PIP_DEPTH,PIP_DIA))
        f.write("\n")
        f.write(four_pips("BEGIN 4-PIP PATTERN", R_ORIGIN_X, R_ORIGIN_Y, PIP_MAX_SQUARE, PIP_DEPTH,PIP_DIA))
        f.write("(~~~~~~~~~~ End 3x4 Domino. ~~~~~~~~~~) ;\n")

        f.write(next_domino())

        f.write("\n(~~~~~~~~~~ Start 3x5 Domino. ~~~~~~~~~~) ;\n")
        f.write(one_pip("BEGIN 1-PIP PATTERN", L_ORIGIN_X, L_ORIGIN_Y, PIP_DEPTH))
        f.write(two_pips("BEGIN 2-PIP PATTERN", L_ORIGIN_X, L_ORIGIN_Y, PIP_MAX_SQUARE, PIP_DEPTH,PIP_DIA))
        f.write("\n")
        f.write(one_pip("BEGIN 1-PIP PATTERN", R_ORIGIN_X, R_ORIGIN_Y, PIP_DEPTH))
        f.write(four_pips("BEGIN 4-PIP PATTERN", R_ORIGIN_X, R_ORIGIN_Y, PIP_MAX_SQUARE, PIP_DEPTH,PIP_DIA))
        f.write("(~~~~~~~~~~ End 3x5 Domino. ~~~~~~~~~~) ;\n")

        f.write(next_domino())

        f.write("\n(~~~~~~~~~~ Start 3x6 Domino. ~~~~~~~~~~) ;\n")
        f.write(one_pip("BEGIN 1-PIP PATTERN", L_ORIGIN_X, L_ORIGIN_Y, PIP_DEPTH))
        f.write(two_pips("BEGIN 2-PIP PATTERN", L_ORIGIN_X, L_ORIGIN_Y, PIP_MAX_SQUARE, PIP_DEPTH,PIP_DIA))
        f.write("\n")
        f.write(six_pips("BEGIN 6-PIP PATTERN", R_ORIGIN_X, R_ORIGIN_Y, PIP_MAX_SQUARE, PIP_DEPTH,PIP_DIA))
        f.write("(~~~~~~~~~~ End 3x6 Domino. ~~~~~~~~~~) ;\n")

        f.write(next_domino())

        f.write("\n(~~~~~~~~~~ Start 4x4 Domino. ~~~~~~~~~~) ;\n")
        f.write(four_pips("BEGIN 4-PIP PATTERN", L_ORIGIN_X, L_ORIGIN_Y, PIP_MAX_SQUARE, PIP_DEPTH,PIP_DIA))
        f.write("\n")
        f.write(four_pips("BEGIN 4-PIP PATTERN", R_ORIGIN_X, R_ORIGIN_Y, PIP_MAX_SQUARE, PIP_DEPTH,PIP_DIA))
        f.write("(~~~~~~~~~~ End 4x4 Domino. ~~~~~~~~~~) ;\n")

        f.write(next_domino())

        f.write("\n(~~~~~~~~~~ Start 4x5 Domino. ~~~~~~~~~~) ;\n")
        f.write(four_pips("BEGIN 4-PIP PATTERN", L_ORIGIN_X, L_ORIGIN_Y, PIP_MAX_SQUARE, PIP_DEPTH,PIP_DIA))
        f.write("\n")
        f.write(one_pip("BEGIN 1-PIP PATTERN", R_ORIGIN_X, R_ORIGIN_Y, PIP_DEPTH))
        f.write(four_pips("BEGIN 4-PIP PATTERN", R_ORIGIN_X, R_ORIGIN_Y, PIP_MAX_SQUARE, PIP_DEPTH,PIP_DIA))
        f.write("(~~~~~~~~~~ End 4x5 Domino. ~~~~~~~~~~) ;\n")

        f.write(next_domino())

        f.write("\n(~~~~~~~~~~ Start 4x6 Domino. ~~~~~~~~~~) ;\n")
        f.write(four_pips("BEGIN 4-PIP PATTERN", L_ORIGIN_X, L_ORIGIN_Y, PIP_MAX_SQUARE, PIP_DEPTH,PIP_DIA))
        f.write("\n")
        f.write(six_pips("BEGIN 6-PIP PATTERN", R_ORIGIN_X, R_ORIGIN_Y, PIP_MAX_SQUARE, PIP_DEPTH,PIP_DIA))
        f.write("(~~~~~~~~~~ End 4x6 Domino. ~~~~~~~~~~) ;\n")

        f.write(next_domino())

        f.write("\n(~~~~~~~~~~ Start 5x5 Domino. ~~~~~~~~~~) ;\n")
        f.write(one_pip("BEGIN 1-PIP PATTERN", L_ORIGIN_X, L_ORIGIN_Y, PIP_DEPTH))
        f.write(four_pips("BEGIN 4-PIP PATTERN", L_ORIGIN_X, L_ORIGIN_Y, PIP_MAX_SQUARE, PIP_DEPTH,PIP_DIA))
        f.write("\n")
        f.write(one_pip("BEGIN 1-PIP PATTERN", R_ORIGIN_X, R_ORIGIN_Y, PIP_DEPTH))
        f.write(four_pips("BEGIN 4-PIP PATTERN", R_ORIGIN_X, R_ORIGIN_Y, PIP_MAX_SQUARE, PIP_DEPTH,PIP_DIA))
        f.write("(~~~~~~~~~~ End 5x5 Domino. ~~~~~~~~~~) ;\n")

        f.write(next_domino())

        f.write("\n(~~~~~~~~~~ Start 5x6 Domino. ~~~~~~~~~~) ;\n")
        f.write(one_pip("BEGIN 1-PIP PATTERN", L_ORIGIN_X, L_ORIGIN_Y, PIP_DEPTH))
        f.write(four_pips("BEGIN 4-PIP PATTERN", L_ORIGIN_X, L_ORIGIN_Y, PIP_MAX_SQUARE, PIP_DEPTH,PIP_DIA))
        f.write("\n")
        f.write(six_pips("BEGIN 6-PIP PATTERN", R_ORIGIN_X, R_ORIGIN_Y, PIP_MAX_SQUARE, PIP_DEPTH,PIP_DIA))
        f.write("(~~~~~~~~~~ End 5x6 Domino. ~~~~~~~~~~) ;\n")

        f.write(next_domino())

        f.write("\n(~~~~~~~~~~ Start 6x6 Domino. ~~~~~~~~~~) ;\n")
        f.write(six_pips("BEGIN 6-PIP PATTERN", L_ORIGIN_X, L_ORIGIN_Y, PIP_MAX_SQUARE, PIP_DEPTH,PIP_DIA))
        f.write("\n")
        f.write(six_pips("BEGIN 6-PIP PATTERN", R_ORIGIN_X, R_ORIGIN_Y, PIP_MAX_SQUARE, PIP_DEPTH,PIP_DIA))
        f.write("(~~~~~~~~~~ End 6x6 Domino. ~~~~~~~~~~) ;\n")

        f.write(gcode_footer())

if __name__ == "__main__":
    main()