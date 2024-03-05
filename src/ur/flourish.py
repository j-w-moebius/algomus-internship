import nonchord
import random

FLOURISH = {
    'third-passing': 0.5,
    'third-16': 0.1,
    'same-neighbor': 0.1,
    'second-jump': 0.2,
    'second-8-16-16': 0.1,
}

def flourish(items, i, rhy_i, thresholds):
    rhy = rhy_i    
    lyr = []
    new_items = []
    
    if rhy != '4' or i >= len(items)-1:
        return rhy, lyr, new_items 
    
    n1 = items[i]
    n2 = items[i+1]

    # Some passing notes between thirds
    if nonchord.interval_third(n1, n2):
        if random.random() < thresholds['third-16']:
            rhy = '16 16 16 16'
            lyr += ['-', '-', '-']
            new_items += [
                nonchord.note_direction(n1, n2, 1),
                n2,
                nonchord.note_direction(n1, n2, 3),
                ]
        elif random.random() < thresholds['third-passing']:
            rhy = '8 8'
            lyr += ['-']
            new_items += [nonchord.note_nonchord(n1, n2)]

    # Some neighbor notes between same notes
    if n1 == n2:
        if random.random() < thresholds['same-neighbor']:
            rhy = '8 8'
            lyr += ['-']
            new_items += [nonchord.note_nonchord(n1, n2, True)]

    # Some jump-passing notes between seconds
    if nonchord.interval_second(n1, n2):
        if random.random() < thresholds['second-jump']:
            rhy = '8 8'
            lyr += ['-']
            new_items += [nonchord.note_direction(n1, n2, 2)]
        if random.random() < thresholds['second-8-16-16']:
            rhy = '8 16 16'
            lyr += ['-', '-']
            new_items += [
                n2, 
                nonchord.note_direction(n1, n2, 2)
            ]
            
    return rhy, lyr, new_items 