import yaml
import json
import sys
import os
import argparse

def validate_feasability(config):
    """
    Validate the input data for feasability.
    This currently checks the the amount of AKs is less or equal to the amount of timeslots.
    """
    timeslot_room_capacity = len(config['rooms'] * len(config['timeslots']['blocks'][0]))
    ak_capacity = len(config['aks'])
    if ak_capacity > timeslot_room_capacity:
        raise ValueError(f"Amount of AKs ({ak_capacity}) is greater than the amount of timeslot-room combinations ({timeslot_room_capacity}).")

def penalize_input(config, penalize_percentage=None):
    """
    penalize people with too many AKs
    per default only people with more aks than timeslots are penalized
    if penalize_percentage is set, people with more aks than aks * penalize_percentage are penalized
    """
    # Distribute penalties for people with too many AKs
    # Only modifies preference_score if none exists yet
    # Valid preference_scores
    # -1: required
    # 0: not interested
    # 1: weakly interested
    # 2: strongly interested

    # Penalize people that have more AKs than timeslots
    timeslot_count = len(config['timeslots']['blocks'][0])
    for participant in config['participants']:
        if len(participant['preferences']) > timeslot_count:
            for preference in participant['preferences']:
                print(f"Punished {participant['info']['name']} for having way too many AKs (more than timeslots available)")
                if 'preference_score' in preference:
                    continue
                else:
                    preference['preference_score'] = 0

    if penalize_percentage:
        # Penalize people that have more AKs than aks * penalize_percentage
        ak_count = len(config['aks'])
        for participant in config['participants']:
            if len(participant['preferences']) > ak_count * penalize_percentage:
                for preference in participant['preferences']:
                    print(f"Punished {participant['info']['name']} for having too many AKs")
                    if 'preference_score' in preference:
                        continue
                    else:
                        preference['preference_score'] = 1

    return config

def generate_input_json(input_file, output_file, penalize=None):
    with open(input_file, 'r') as stream:
        try:
            input_data = yaml.safe_load(stream)
        except yaml.YAMLError as exc:
            print(exc)

    timeslot_name_to_id = {}
    next_timeslot_id = 1
    ak_name_to_id = {}
    next_ak_id = 1
    room_name_to_id = {}
    next_room_id = 1
    participant_name_to_id = {}
    next_participant_id = 1

    output = {}
    output['info'] = {}

    output['rooms'] = []
    for room in input_data['rooms']:
        this_room = {}
        this_room['info'] = {"name": room.get("name")}
        if not room_name_to_id.get(room.get("name")):
            room_name_to_id[room.get("name")] = "Room" + str(next_room_id)
            next_room_id += 1
        this_room['id'] = room_name_to_id[room.get("name")]
        this_room['capacity'] = room.get("capacity")
        this_room['time_constraints'] = room.get("time_constraints", [])
        this_room['fulfilled_room_constraints'] = room.get("fulfilled_room_constraints", [])
        output['rooms'].append(this_room)

    output['timeslots'] = {"info": {"duration": "One Hour"},"blocks": []}
    blocks = []
    for timeslot in input_data['timeslots']:
        this_timeslot = {}
        this_timeslot['info'] = {"start": timeslot.get("name")}
        if not timeslot_name_to_id.get(timeslot.get("name")):
            timeslot_name_to_id[timeslot.get("name")] = "Slot" + str(next_timeslot_id)
            next_timeslot_id += 1
        this_timeslot['id'] = timeslot_name_to_id[timeslot.get("name")]
        this_timeslot['fulfilled_time_constraints'] = timeslot.get("fulfilled_time_constraints", [])
        blocks.append(this_timeslot)
    
    output['timeslots']['blocks'] = [blocks]

    output['aks'] = []
    for ak in input_data['aks']:
        this_ak = {}
        this_ak['info'] = {"name": ak.get("name"),
                           "reso": False, "description": "",
                           "head": ak.get("head", ""),
                           "description": ak.get("description", ""),
                           "protokoll": ak.get("protokoll", "")}
        if not ak_name_to_id.get(ak.get("name")):
            ak_name_to_id[ak.get("name")] = "AK" + str(next_ak_id)
            next_ak_id += 1
        this_ak['id'] = ak_name_to_id[ak.get("name")]
        this_ak['time_constraints'] = ak.get("time_constraints", [])
        this_ak['room_constraints'] = ak.get("room_constraints", [])
        this_ak['duration'] = ak.get("duration", 1)
        this_ak['properties'] = {}
        output['aks'].append(this_ak)

    output['participants'] = []
    for participant in input_data['participants']:
        this_participant = {}
        this_participant['info'] = {"name": participant.get("name")}
        if not participant_name_to_id.get(participant.get("name")):
            participant_name_to_id[participant.get("name")] = "User" + str(next_participant_id)
            next_participant_id += 1
        this_participant['id'] = participant_name_to_id[participant.get("name")]
        this_participant['preferences'] = []
        for ak in participant.get("aks", []):
            this_participant['preferences'].append({"ak_id": ak_name_to_id[ak.get("name")], "preference_score": ak.get("score", 1), "required": ak.get("required", False)})
        this_participant['time_constraints'] = participant.get("time_constraints", [])
        this_participant['room_constraints'] = participant.get("room_constraints", [])
        output['participants'].append(this_participant)
 
    output = penalize_input(output, penalize_percentage=penalize)

    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    with open(output_file, 'w+') as f:
        f.write(json.dumps(output, indent=4))

if __name__ == "__main__":

    parser = argparse.ArgumentParser(description='Generate input JSON from YAML.')
    parser.add_argument('input_file', type=str, help='The input YAML file')
    parser.add_argument('output_file', type=str, help='The output JSON file')
    parser.add_argument('--penalize', type=float, help='Penalize people with more AKs than aks * penalize_percentage')
    args = parser.parse_args()

    generate_input_json(args.input_file, args.output_file, penalize=args.penalize)
