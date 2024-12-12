import json
import sys

def timeslot_id_to_numer(timeslot_id):
    # trim prefix "Slot"
    return int(timeslot_id[4:])

def generate_output_md_table(output_json, output_file):
    with open(output_json, "r") as f:
        output = json.load(f)
    
    output_md = ""

    ak_id_to_name = {}
    room_id_to_name = {}
    participant_id_to_name = {}
    timeslot_id_to_name = {}
    ak_id_to_room_id = {}
    ak_id_to_info = {}

    for ak in output["input"]["aks"]:
        ak_id_to_name[ak["id"]] = ak["info"]["name"]
        ak_id_to_info[ak["id"]] = ak["info"]
    
    for ak in output["scheduled_aks"]:
        ak_id_to_room_id[ak["ak_id"]] = ak["room_id"]

    for room in output["input"]["rooms"]:
        room_id_to_name[room["id"]] = room["info"]["name"]

    for participant in output["input"]["participants"]:
        participant_id_to_name[participant["id"]] = participant["info"]["name"]

    for timeslot in output["input"]["timeslots"]["blocks"][0]:
        timeslot_id_to_name[timeslot["id"]] = timeslot["info"]["start"]

    timeslots = {}
    for ak in output["scheduled_aks"]:
        for timeslot in ak["timeslot_ids"]:
            if timeslot not in timeslots:
                timeslots[timeslot] = []
            this_ak = {"name": ak_id_to_name[ak["ak_id"]], "room": room_id_to_name[ak["room_id"]], "participants": [participant_id_to_name[participant] for participant in ak.get("participant_ids",[])]}
            timeslots[timeslot].append(this_ak)

    sorted_timeslots = sorted(timeslots.keys(),key=timeslot_id_to_numer)

    aks_per_person_per_timeslot = {}
    for ak in output["scheduled_aks"]:
        for timeslot in ak["timeslot_ids"]:
            for participant in ak.get("participant_ids", []):
                if participant not in aks_per_person_per_timeslot:
                    aks_per_person_per_timeslot[participant] = {}
                if timeslot not in aks_per_person_per_timeslot[participant]:
                    aks_per_person_per_timeslot[participant][timeslot] = []
                aks_per_person_per_timeslot[participant][timeslot].append(ak["ak_id"])

    output_md="# Personal Plans\n"

    for participant in output["input"]["participants"]:
        output_md += f"## {participant['info']['name']}\n"
        if participant["id"] not in aks_per_person_per_timeslot:
            aks_per_person_per_timeslot[participant["id"]] = []
        max_concurrent_aks = 1
        for ak in aks_per_person_per_timeslot[participant["id"]].values():
            if len(ak) > max_concurrent_aks:
                max_concurrent_aks = len(ak)
        output_md += "| Time |"
        for i in range(max_concurrent_aks):
            output_md += f" AK {i+1} (Room) |"
        output_md += "\n"

        output_md += "| --- |"
        for i in range(max_concurrent_aks):
            output_md += " --- |"
        output_md += "\n"

        for timeslot in sorted_timeslots:
            output_md += f"| {timeslot_id_to_name[timeslot]} |"
            if timeslot in aks_per_person_per_timeslot[participant["id"]].keys():
                for ak_id in aks_per_person_per_timeslot[participant["id"]][timeslot]:
                    room = room_id_to_name[ak_id_to_room_id[ak_id]]
                    output_md += f" [{ak_id_to_name[ak_id]} ({room})]({ak_id_to_info[ak_id].get("protokoll", "")}) |"
                for i in range(max_concurrent_aks - len(aks_per_person_per_timeslot[participant["id"]])):
                    output_md += " |"
            else:
                for i in range(max_concurrent_aks):
                    output_md += " |"
            output_md += "\n"

    with open(output_file, "w") as f:
        f.write(output_md)
        

if __name__ == "__main__":
    # argv[1] is the output json file
    # argv[2] is the output md table file
    generate_output_md_table(sys.argv[1], sys.argv[2])
