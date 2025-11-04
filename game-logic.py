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
    adb_tap(456, 1775)
    print("tap")


def get_tubes_to_tap(all_tubes):
    tubes_to_tap = []
    colors_checked = {}
    tubes_being_poured_into = []
    for idx, tube in enumerate(all_tubes):
        if tube['colors'][0]['color'] != 'empty' and len(tube['colors']) < 2:
            continue
        if tube['colors'][0] == 'empty' and len(tube['colors']) == 2:
            continue
        t_color = tube['pour_color']['color'] 
        if t_color == 'empty':
            continue
        if t_color in colors_checked:
            continue
        if tube in tubes_being_poured_into:
            continue # We cant pour a tube that is about to be poured in.
        
        alike_colored_tubes = [tube, ]
        max_empty_space_tube = tube

        for idx2, tube2 in enumerate(all_tubes):
            if idx == idx2:
                continue
            if tube2 in tubes_being_poured_into:
                continue

            t2_color = tube2['pour_color']['color']
            t2_empty_space = int(tube2['colors'][0]['height']) if tube2['colors'][0]['color'] == 'empty' else 0

            current_empty_space = int(max_empty_space_tube['colors'][0]['height'] if tube['colors'][0]['color'] == 'empty' else 0)
            if t2_color == t_color or t2_color == 'empty':
                alike_colored_tubes.append(tube2)
                if t2_empty_space > current_empty_space:
                    max_empty_space_tube = tube2

        if len(alike_colored_tubes) == 1:
            continue

        if max_empty_space_tube in alike_colored_tubes:
            alike_colored_tubes.remove(max_empty_space_tube) # We dont want to pour the tube into itself...
        tubes_being_poured_into.append(max_empty_space_tube)


        available_space = int(max_empty_space_tube['colors'][0]['height']) if max_empty_space_tube['colors'][0]['color'] == 'empty' else 0
        sorted_tubes = sorted(alike_colored_tubes, key=lambda tube: tube['pour_color']['height']) # want to sort based on tube['pour_color']['height']

        if len(sorted_tubes) == 1:
            if available_space > sorted_tubes[0]['pour_color']['height']:
                tubes_to_tap.append((sorted_tubes[0], max_empty_space_tube))
                continue
            else:
                tubes_to_tap.append((max_empty_space_tube, sorted_tubes[0]))
                continue


        for x in sorted_tubes:
            if available_space >= x['pour_color']['height']:
                tubes_to_tap.append((x, max_empty_space_tube))
                print(f"pouring tube {x['tube_index']} into {max_empty_space_tube['tube_index']}")

        colors_checked[t_color] = 1
    return tubes_to_tap
            




        


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

        tubes_to_tap = get_tubes_to_tap(all_tube_colors)

        if len(tubes_to_tap) > 0:
            for x in tubes_to_tap:
                adb_tap(*get_tap_position(x[0]))
                adb_tap(*get_tap_position(x[1]))
        else:
            next_level()

        

    #     #Now that we know where everything is, we can designate 'pour tubes' (ones that are empty or contain 1 color) and 'working tubes' (tubes we need to get down to 1 color)
    #     working_tubes, pour_tubes = [], []

    #     for tube in all_tube_colors:
    #         if len(tube['colors']) == 1 or len(tube['colors']) == 2 and tube['top_color']['color'] == 'empty':
    #             pour_tubes.append(tube)
    #         else:
    #             working_tubes.append(tube)


    #     #Get a list of all colors that have a pour tube we can use so we don't mix colors up
    #     available_pouring_colors = [tube['colors'][-1]['color'] for tube in pour_tubes]
    #     #Now we can follow a simple pattern of scanning the working tubes for the largest color that we can put into a pour tube!
    #     tubes_to_pour = get_tubes_of_most_frequent_color(working_tubes, available_pouring_colors)

    #     if len(tubes_to_pour) == 0:
    #         # If we have no working tubes to pour, its time to combine any alike pour-tubes
    #         for x in pour_tubes:
    #             if len(x['colors'])==1 and x['top_color']['color'] == 'empty':
    #                 continue
    #             for y in pour_tubes:
    #                 if len(y['colors'])==1 and y['top_color']['color'] == 'empty':
    #                     continue
    #                 if x['tube_index'] == y['tube_index']:
    #                     continue
    #                 if x['colors'][-1]['color'] == y['colors'][-1]['color']:
    #                     tubes_to_pour = x

    #     if len(tubes_to_pour) == 0:
    #         # If we still haven't found one to pour, lets try combining 2 working tubes!
    #         for x in working_tubes:
    #             for y in working_tubes:
    #                 if x['tube_index'] == y['tube_index']:
    #                     continue
    #                 if y['top_color']['color'] != "empty":
    #                     continue   
    #                 if x['pour_color']['color'] == y['colors'][1]['color'] and y['colors'][0]['height'] >= x['pour_color']['height'] - 10: # margin of error
    #                     tubes_to_pour = [x,]
    #                     pour_tubes.append(y)
    #                     break
    #             if len(tubes_to_pour) != 0:
    #                 break

    #     if len(tubes_to_pour) == 0:
    #         next_level()
    #         continue

        
    #     for x in tubes_to_pour:
    #         if x in pour_tubes:
    #             pour_tubes.remove(x)


    #     #Now that we have the tube we want to pour, we need the tube to pour it into. we know 1 exists but not where! 
    #     color_to_pour = tubes_to_pour[0]['pour_color']['color']
    #     tube_to_pour_in = None
    #     for tube in pour_tubes:
    #         if tube['top_color']['color'] == color_to_pour or tube['colors'][-1]['color'] == 'empty' or (tube['colors'][0]['color'] == 'empty' and tube['colors'][1]['color'] == color_to_pour):
    #             if tube_to_pour_in is None or tube['top_color']['height'] > tube_to_pour_in['top_color']['height']: #Lets take the largest empty space we find
    #                 tube_to_pour_in = tube

    #     # Now we just tap on both tubes, and repeat!
    #     tube_1_pos_list = [get_tap_position(tube) for tube in tubes_to_pour]
    #     tube_2_tap_pos = get_tap_position(tube_to_pour_in)

    #     for pos in tube_1_pos_list:
    #         adb_tap(*pos)
    #         adb_tap(*tube_2_tap_pos)
    #     sleep(1.3)
    # sleep(1)

    # print("done?")