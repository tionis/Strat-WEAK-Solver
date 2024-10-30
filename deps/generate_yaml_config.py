import yaml
import json
import sys

def generate_yaml_config(input_json_file, output_yaml_file):
    with open(input_json_file, 'r') as json_file:
        try:
            input_data = json.load(json_file)
        except json.JSONDecodeError as e:
            print(f"Error: {e}")
            return
    
    timeslot_id_to_name = {}
    ak_id_to_name = {}
    room_id_to_name = {}
    participant_id_to_name = {}

    config = {
        "timeslots": [],
        "rooms": [],
        "participants": [],
        "aks": []
    }

    for room in input_data["rooms"]:
        this_room = {
            "name": room["info"]["name"],
            "capacity": room["capacity"]
        }
        if len(room["time_constraints"]) > 0:
            this_room["time_constraints"] = room["time_constraints"]
        if len(room["fulfilled_room_constraints"]) > 0:
            this_room["fulfilled_room_constraints"] = room["fulfilled_room_constraints"]
        room_id_to_name[room["id"]] = room["info"]["name"]
        config["rooms"].append(this_room)

    for timelot in input_data["timeslots"]["blocks"][0]:
        this_timeslot = {
            "name": timelot["info"]["start"],
        }
        if len(timelot["fulfilled_time_constraints"]) > 0:
            this_timeslot["fulfilled_time_constraints"] = timelot["fulfilled_time_constraints"]
        timeslot_id_to_name[timelot["id"]] = timelot["info"]["start"]
        config["timeslots"].append(this_timeslot)

    for ak in input_data["aks"]:
        this_ak = {
            "name": ak["info"]["name"],
            "duration": ak["duration"],
        }
        if ak["info"]["head"] is not None:
            this_ak["head"] = ak["info"]["head"]
        if len(ak["time_constraints"]) > 0:
            this_ak["time_constraints"] = ak["time_constraints"]
        if len(ak["room_constraints"]) > 0:
            this_ak["room_constraints"] = ak["room_constraints"]
        ak_id_to_name[ak["id"]] = ak["info"]["name"]
        config["aks"].append(this_ak)
    
    for participant in input_data["participants"]:
        this_participant = {
            "name": participant["info"]["name"],
        }
        participant_id_to_name[participant["id"]] = participant["info"]["name"]
        if len(participant["time_constraints"]) > 0:
            this_participant["time_constraints"] = participant["time_constraints"]
        if len(participant["room_constraints"]) > 0:
            this_participant["room_constraints"] = participant["room_constraints"]
        this_participant["aks"] = []

        for ak in participant["preferences"]:
            print(participant)
            print(ak)
            this_ak = {
                "name": ak_id_to_name[ak["ak_id"]],
            }
            if "preference_score" in ak and ak["preference_score"] != 1:
                this_ak["preference_score"] = ak["preference_score"]

            if ak["required"]:
                this_ak["required"] = ak["required"]

            this_participant["aks"].append(this_ak)

        config["participants"].append(this_participant)

    with open(output_yaml_file, 'w') as yaml_file:
        yaml.dump(config, yaml_file)


if __name__ == "__main__":
    # argv[1] is the input json file
    # argv[2] is the output yaml file
    generate_yaml_config(sys.argv[1], sys.argv[2])
