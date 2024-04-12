import nonchord
import random

FLOURISH = {
    'third-passing': 0.4,
    'third-16': 0.1,
    'same-neighbor-16': 0.0,
    'same-neighbor': 0.1,
    'second-jump': 0.2,
    'second-8-16-16': 0.1,
    'fourth-8-16-16': 0.1,
    'fifth-jump': 0.1,
    'fifth-16': 0.1,
}

def flourish(items, i, rhy_i, thresholds, ternary):
    rhy = rhy_i    
    lyr = []
    new_items = []
    
    if rhy not in ['4', '4.'] or i >= len(items)-1:
        return rhy, lyr, new_items 
    
    n1 = items[i]
    n2 = items[i+1]

    # Some passing notes between fifths
    if nonchord.interval_fifth_up(n1, n2):
        if random.random() < thresholds['fifth-16']:
            rhy = random.choice(['8 8 16 16', '8. 16 16 16']) if ternary else '16 16 16 16'
            lyr += ['-', '-', '-']
            new_items += [
                nonchord.note_direction(n1, n2, 1),
                nonchord.note_direction(n1, n2, 2),
                nonchord.note_direction(n1, n2, 3),
            ]
        if random.random() < thresholds['fifth-jump']:
            rhy =  '4 8' if ternary else '8 8'
            lyr += ['-']
            new_items += [
                nonchord.note_direction(n1, n2, 2)
            ]
            
    # Some passing notes between fourths
    elif nonchord.interval_fourth(n1, n2):
        if random.random() < thresholds['fourth-8-16-16']:
            rhy = random.choice(['8 8 8', '8. 16 8']) if ternary else '8 16 16'
            lyr += ['-', '-']
            new_items += [
                nonchord.note_direction(n1, n2, 1),
                nonchord.note_direction(n1, n2, 2)
            ]

    # Some passing notes between thirds
    elif nonchord.interval_third(n1, n2):
        if random.random() < thresholds['third-16']:
            rhy = '8 8 16 16' if ternary else '16 16 16 16'
            lyr += ['-', '-', '-']
            new_items += [
                nonchord.note_direction(n1, n2, 1),
                n2,
                nonchord.note_direction(n1, n2, 3),
                ]
        elif random.random() < thresholds['third-passing']:
            rhy = '4 8' if ternary else '8 8'
            lyr += ['-']
            new_items += [nonchord.note_nonchord(n1, n2)]

    # Some neighbor notes between same notes
    elif n1 == n2:
        if random.random() < thresholds['same-neighbor-16']:
            rhy = random.choice(['8 8 16 16', '8. 16 16 16']) if ternary else '16 16 16 16'
            lyr += ['-', '-', '-']
            dir = random.choice([-1, 1])
            new_items += [
                nonchord.note_projection(n1, dir, 1),
                nonchord.note_projection(n1, dir, 2) if random.choice([True, False]) else n1,
                nonchord.note_projection(n1, dir, 1),
            ]
        elif random.random() < thresholds['same-neighbor']:
            rhy = '4 8' if ternary else random.choice(['8 8', '8. 16'])
            lyr += ['-']
            new_items += [nonchord.note_nonchord(n1, n2, True)]

    # Some jump-passing notes between seconds
    elif nonchord.interval_second(n1, n2):
        if random.random() < thresholds['second-jump']:
            rhy = '4 8' if ternary else random.choice(['8 8', '8. 16'])
            lyr += ['-']
            new_items += [nonchord.note_direction(n1, n2, 2)]
        elif random.random() < thresholds['second-8-16-16']:
            rhy = random.choice(['8 8 8', '8. 16 8']) if ternary else '8 16 16'
            lyr += ['-', '-']
            new_items += [
                n2, 
                nonchord.note_direction(n1, n2, 2)
            ]
            
    return rhy, lyr, new_items 