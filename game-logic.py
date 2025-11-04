import sys
from color_detection import analyze_all_tubes
from adb import adb_tap
from time import sleep
from adb import capture_screen, has_devices
import subprocess

def get_tap_position(tube):
    tap_x = tube['top_color']['scan_x']
    tap_y = tube['top_color']['start_y'] + (tube['top_color']['height'] / 2)
    return (tap_x, tap_y)

def get_largest_continuous_top_color_tube(working_tubes, available_pouring_colors):
    colors = {}
    for tube in working_tubes:
            pour_color = tube['pour_color']['color']

            if pour_color in available_pouring_colors or 'empty' in available_pouring_colors:
                if pour_color in colors:
                    colors[pour_color] += tube['pour_color']['height']
                else:
                    colors[pour_color] = tube['pour_color']['height']
    if colors:
        most_color = max(colors, key=colors.get)
    else:
        return None
    for tube in working_tubes:
        if tube['pour_color']['color'] == most_color:
            return tube
        
def get_tubes_of_most_frequent_color(working_tubes, available_pouring_colors):
    colors = {}
    tubes_to_pour = []
    for tube in working_tubes:
            pour_color = tube['pour_color']['color']

            if pour_color in available_pouring_colors or 'empty' in available_pouring_colors:
                if pour_color in colors:
                    colors[pour_color] += tube['pour_color']['height']
                else:
                    colors[pour_color] = tube['pour_color']['height']
    if colors:
        most_color = max(colors, key=colors.get)
    else:
        return []
    for tube in working_tubes:
        if tube['pour_color']['color'] == most_color:
            tubes_to_pour.append(tube)
    return tubes_to_pour

def next_level():
    sleep(2)
    adb_tap(456, 1775)
    print("tap")
    sleep(1)

# Example usage
if __name__ == "__main__":
    # while not has_devices():
    #     print('waiting for device...')
    #     sleep(5)
    screenrecord_proc = subprocess.Popen(
        ["adb", "shell", "screenrecord", "/sdcard/bot_recording.mp4"]
    )
    playing = True
    while playing:
        image = capture_screen()

        #Level begins, we need to first analyze all tubes to get the lists of colors and empty spaces
        all_tube_colors, img = analyze_all_tubes(image, scan_offset=40)

        #Now that we know where everything is, we can designate 'pour tubes' (ones that are empty or contain 1 color) and 'working tubes' (tubes we need to get down to 1 color)
        working_tubes, pour_tubes = [], []

        for tube in all_tube_colors:
            if len(tube['colors']) == 1 or len(tube['colors']) == 2 and tube['top_color']['color'] == 'empty':
                pour_tubes.append(tube)
            else:
                working_tubes.append(tube)


        #Get a list of all colors that have a pour tube we can use so we don't mix colors up
        available_pouring_colors = [tube['colors'][-1]['color'] for tube in pour_tubes]
        #Now we can follow a simple pattern of scanning the working tubes for the largest color that we can put into a pour tube!
        tubes_to_pour = get_tubes_of_most_frequent_color(working_tubes, available_pouring_colors)

        if len(tubes_to_pour) == 0:
            # If we have no working tubes to pour, its time to combine any alike pour-tubes
            for x in pour_tubes:
                if len(x['colors'])==1 and x['top_color']['color'] == 'empty':
                    continue
                for y in pour_tubes:
                    if len(y['colors'])==1 and y['top_color']['color'] == 'empty':
                        continue
                    if x['tube_index'] == y['tube_index']:
                        continue
                    if x['colors'][-1]['color'] == y['colors'][-1]['color']:
                        tubes_to_pour = x

        if len(tubes_to_pour) == 0:
            # If we still haven't found one to pour, lets try combining 2 working tubes!
            for x in working_tubes:
                for y in working_tubes:
                    if x['tube_index'] == y['tube_index']:
                        continue
                    if y['top_color']['color'] != "empty":
                        continue   
                    if x['pour_color']['color'] == y['colors'][1]['color'] and y['colors'][0]['height'] >= x['pour_color']['height'] - 10: # margin of error
                        tubes_to_pour = [x,]
                        pour_tubes.append(y)
                        break
                if len(tubes_to_pour) != 0:
                    break

        if len(tubes_to_pour) == 0:
            next_level()
            continue

        
        for x in tubes_to_pour:
            if x in pour_tubes:
                pour_tubes.remove(x)


        #Now that we have the tube we want to pour, we need the tube to pour it into. we know 1 exists but not where! 
        color_to_pour = tubes_to_pour[0]['pour_color']['color']
        tube_to_pour_in = None
        for tube in pour_tubes:
            if tube['top_color']['color'] == color_to_pour or tube['colors'][-1]['color'] == 'empty' or (tube['colors'][0]['color'] == 'empty' and tube['colors'][1]['color'] == color_to_pour):
                if tube_to_pour_in is None or tube['top_color']['height'] > tube_to_pour_in['top_color']['height']: #Lets take the largest empty space we find
                    tube_to_pour_in = tube

        # Now we just tap on both tubes, and repeat!
        tube_1_pos_list = [get_tap_position(tube) for tube in tubes_to_pour]
        tube_2_tap_pos = get_tap_position(tube_to_pour_in)

        for pos in tube_1_pos_list:
            adb_tap(*pos)
            adb_tap(*tube_2_tap_pos)
        sleep(1.3)
    sleep(1)

    print("done?")