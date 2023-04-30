import datetime

def find_indices(lst, condition):
    return [i for i, elem in enumerate(lst) if condition(elem)]

def get_elapsed_time(start_time, end_time):
    elapsed_time = end_time - start_time
    hours, remainder = divmod(elapsed_time.total_seconds(), 3600)
    minutes, seconds = divmod(remainder, 60)
    formatted_time = '{:02}:{:02}:{:02}'.format(int(hours), int(minutes), int(seconds))
    return formatted_time

def extract_play_list_from_scene_list(scenes):
    res = []

    for scene in scenes:
        res.append(scene.split(":")[0])

    return res