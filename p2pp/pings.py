__author__ = 'Tom Van den Eede'
__copyright__ = 'Copyright 2018-2022, Palette2 Splicer Post Processing Project'
__credits__ = ['Tom Van den Eede',
               'Tim Brookman'
               ]
__license__ = 'GPLv3'
__maintainer__ = 'Tom Van den Eede'
__email__ = 'P2PP@pandora.be'

import p2pp.gcode as gcode
import p2pp.variables as v
from p2pp.formatnumbers import hexify_float

# SECTION PPLUS PING GCODE

def acc_first_pause(retractCode, untractCode, feedRate):
    gcode.issue_code(";PING PAUSE 1 START", True)
    gcode.issue_code(retractCode)
    gcode.issue_code("G4 S0")
    gcode.issue_code("G4 P4000")
    gcode.issue_code("G1")
    gcode.issue_code("G4 P4000")
    gcode.issue_code("G1")
    gcode.issue_code("G4 P4000")
    gcode.issue_code("G1")
    gcode.issue_code("G4 P1000")
    gcode.issue_code("G1")
    gcode.issue_code(";PING PAUSE 1 END", True)
    gcode.issue_code(untractCode)
    gcode.issue_code("G1 F{}".format(feedRate))
acc_first_pauseOLD = """
;PING PAUSE 1 START
{}
G4 S0
G4 P4000
G1
G4 P4000
G1
G4 P4000
G1
G4 P1000
G1
;PING PAUSE 1 END
{}
G1 F{}
"""

def acc_second_pause(retractCode, untractCode, feedRate):
    gcode.issue_code(retractCode, True)
    gcode.issue_code(";PING PAUSE 2 START", True)
    gcode.issue_code(retractCode)
    gcode.issue_code("G4 S0")
    gcode.issue_code("G4 P4000")
    gcode.issue_code("G1")
    gcode.issue_code("G4 P3000")
    gcode.issue_code("G1")
    gcode.issue_code(untractCode)
    gcode.issue_code("G1 F{}".format(feedRate))
    gcode.issue_code(";PING PAUSE 2 END", True)

acc_second_pauseOLD = """
;PING PAUSE 2 START
{}
G4 S0
G4 P4000
G1
G4 P3000
G1
{}
G1 F{}
;PING PAUSE 2 END"""


# SECTION PING chk ACC/CONN

def check_first_ping_condition():
    return (v.total_material_extruded - v.last_ping_extruder_position) > (v.ping_interval-19.0)


def check_connected_ping():

    if (not v.accessory_mode or v.connected_accessory_mode) and check_first_ping_condition():
        v.ping_interval = v.ping_interval * v.ping_length_multiplier
        v.ping_interval = min(v.max_ping_interval, v.ping_interval)
        v.last_ping_extruder_position = v.total_material_extruded
        v.ping_extruder_position.append(v.last_ping_extruder_position)

        gcode.issue_code(
            "; --- P2PP - INSERT PING CODE {} after {:-10.4f}mm of extrusion".format(len(v.ping_extruder_position),
                                                                                     v.last_ping_extruder_position))
        # wait for the planning buffer to clear
        gcode.issue_code(v.finish_moves)


        # insert O31 commands format depending on device
        if v.palette3:
            if v.connected_accessory_mode:
                gcode.issue_code("; --- P2PP - The next line requires Octoprint printing with the P3PING plugin!!")
                gcode.issue_code("O40 L{:.2f} mm".format(v.last_ping_extruder_position + v.autoloadingoffset))
                #O40 will trigger octorpint plugin to send the ping command onto the P3 Directly
            else:
                gcode.issue_code("O31 L{:.2f} mm".format(v.last_ping_extruder_position + v.autoloadingoffset))
        else:
            gcode.issue_code("O31 {}".format(hexify_float(v.last_ping_extruder_position + v.autoloadingoffset)))

        gcode.issue_code("; --- P2PP - END PING CODE", True)

# SECTION ACC MODE PING 1 and 2

def get_ping_retract_code():
    if v.absolute_extruder or True:
        v.acc_ping_left -= v.retraction
        return "G1 E{} F7200".format(-v.ping_retraction_amount - v.retraction), "G1 E{} F7200".format(v.ping_retraction_amount)
    else:
        return "G1 E-3.000 F7200", "G1 E3.000 F7200"

def check_accessorymode_first():
    if (v.accessory_mode and not v.connected_accessory_mode) and check_first_ping_condition():
        v.acc_ping_left = 20
        rt, urt = get_ping_retract_code()
        v.last_ping_extruder_position = v.total_material_extruded
        v.ping_extruder_position.append(v.total_material_extruded)
        gcode.issue_code(";Ping start: {}".format(v.total_material_extruded), True)
        gcode.issue_code("; ------------------------------------", True)
        gcode.issue_code("; --- P2PP - ACCESSORY MODE PING PART 1", True)
        gcode.issue_code(";Current absolute position: " + str(v.total_material_extruded))
        acc_first_pause(rt, urt, v.keep_speed)
        gcode.issue_code("; -------------------------------------", True)


def interpollate(_from, _to, _part):
    if _part == 0:
        return _from
    else:
        return _from + (_to - _from) * _part

inPing = False
counter = 0
def check_accessorymode_second(e):
    visited = False
    global inPing
    global counter
    nextline = None
    rval = False
    if (v.accessory_mode and not v.connected_accessory_mode) and (v.acc_ping_left > 0):
        if v.acc_ping_left >= e:
            v.acc_ping_left -= e
            counter += e
            print("{:7.5f},{:7.5f},{:7.5f}".format(e, counter, v.acc_ping_left))
            if inPing:
                gcode.issue_code("; acc_ping_left: {}".format(v.acc_ping_left), True)
                gcode.issue_code(";START OF EXTRUSIONPING: " + str(v.total_material_extruded + e), True)
                inPing = False
            visited = True
        else:
            print("SPLIT")
            proc = v.acc_ping_left / e
            int_x = interpollate(v.previous_position_x, v.current_position_x, proc)
            int_y = interpollate(v.previous_position_y, v.current_position_y, proc)
            gcode.issue_code("G1 X{:.4f} Y{:.4f} E{:.4f}; SPLIT START;PING".format(int_x, int_y, v.acc_ping_left))
            e -= v.acc_ping_left
            v.acc_ping_left = 0
            counter = 20
            nextline = "G1 X{:.4f} Y{:.4f} E{:.4f}; SPLIT END;PING".format(v.current_position_x, v.current_position_y, e)
            rval = True
        if v.acc_ping_left <= 0.1:
            if visited:
                gcode.issue_code("G1 X{:.4f} Y{:.4f} E{:.4f}; Extra;PING".format(v.current_position_x, v.current_position_y, e))
                rval = True
            gcode.issue_code("; -------------------------------------", True)
            gcode.issue_code("; --- P2PP - ACCESSORY MODE PING PART 2", True)
            rt, urt = get_ping_retract_code()
            gcode.issue_code(";END OF EXTRUSIONPING: {}mm".format(20 - v.acc_ping_left), True)
            gcode.issue_code("ExtrusionCC: {:10f}   :   SOFAR:".format(v.total_material_extruded), True)
            acc_second_pause(rt, urt, v.keep_speed)
            gcode.issue_code("ExtrusionDD: {:10f}   :   SOFAR:".format(v.total_material_extruded), True)

            gcode.issue_code("; -------------------------------------", True)
            v.ping_interval = v.ping_interval * v.ping_length_multiplier
            v.ping_interval = min(v.max_ping_interval, v.ping_interval)
            print(20 - v.acc_ping_left)
            v.ping_extrusion_between_pause.append(20 - v.acc_ping_left)
            v.acc_ping_left = 0
            counter = 0
            inPing = True
            if nextline:
                gcode.issue_code(nextline)

    return rval
