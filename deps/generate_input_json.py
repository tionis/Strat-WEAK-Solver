import yaml
import json
import sys

def make_name_safe(name):
    return name.replace(' ', '_')

def generate_input_json(input_file, output_file):
    with open(input_file, 'r') as stream:
        try:
            input_data = yaml.safe_load(stream)
        except yaml.YAMLError as exc:
            print(exc)

    output = {}
    output['info'] = {}

    output['rooms'] = []
    for room in input_data['rooms']:
        this_room = {}
        this_room['info'] = {"name": room.get("name")}
        this_room['id'] = make_name_safe(room.get("name"))
        this_room['capacity'] = room.get("capacity")
        this_room['time_constraints'] = room.get("time_constraints", [])
        this_room['fulfilled_room_constraints'] = room.get("fulfilled_room_constraints", [])
        output['rooms'].append(this_room)

    output['timeslots'] = {"info": {"duration": "One Hour"}, "blocks": []}
    for timeslot in input_data['timeslots']:
        this_timeslot = {}
        this_timeslot['info'] = {"start": timeslot.get("name")}
        this_timeslot['id'] = make_name_safe(timeslot.get("name"))
        this_timeslot['fulfilled_time_constraints'] = timeslot.get("fulfilled_time_constraints", [])
        output['timeslots']['blocks'].append(this_timeslot)

    output['aks'] = []
    for ak in input_data['aks']:
        this_ak = {}
        this_ak['info'] = {"name": ak.get("name"), "reso": False, "description": "", "head": ak.get("head", "")}
        this_ak['id'] = make_name_safe(ak.get("name"))
        this_ak['time_constraints'] = ak.get("time_constraints", [])
        this_ak['room_constraints'] = ak.get("room_constraints", [])
        this_ak['duration'] = ak.get("duration", 1)
        this_ak['properties'] = {}
        output['aks'].append(this_ak)

    output['participants'] = []
    for participant in input_data['participants']:
        this_participant = {}
        this_participant['info'] = {"name": participant.get("name")}
        this_participant['id'] = make_name_safe(participant.get("name"))
        this_participant['preferences'] = []
        for ak in participant.get("ak", []):
            this_participant['preferences'].append({"ak_id": make_name_safe(ak.get("name", "")), "preference_score": ak.get("score", 1), "required": ak.get("required", False)})
        this_participant['time_constraints'] = participant.get("time_constraints", [])
        this_participant['room_constraints'] = participant.get("room_constraints", [])
        output['participants'].append(this_participant)
    
    with open(output_file, 'w') as f:
        f.write(json.dumps(output, indent=4))

if __name__ == "__main__":
    # argv[1] is the input yaml file
    # argv[2] is the output json file
    generate_input_json(sys.argv[1], sys.argv[2])
