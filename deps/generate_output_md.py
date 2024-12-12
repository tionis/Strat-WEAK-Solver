import json
import sys

def timeslot_id_to_numer(timeslot_id):
    # trim prefix "Slot"
    return int(timeslot_id[4:])

def generate_output_md(output_json, output_file):
    with open(output_json, "r") as f:
        output = json.load(f)
    
    output_md = ""

    ak_id_to_name = {}
    ak_id_to_info = {}
    room_id_to_name = {}
    participant_id_to_name = {}
    timeslot_id_to_name = {}

    for ak in output["input"]["aks"]:
        ak_id_to_name[ak["id"]] = ak["info"]["name"]
        ak_id_to_info[ak["id"]] = ak["info"]

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
            this_ak = {
                "name": ak_id_to_name[ak["ak_id"]],
                "room": room_id_to_name[ak["room_id"]],
                "participants": [participant_id_to_name[participant] for participant in ak.get("participant_ids",[])],
                "protokoll": ak_id_to_info[ak["ak_id"]].get("protokoll", "")
            }
            timeslots[timeslot].append(this_ak)

    sorted_timeslots = sorted(timeslots.keys(),key=timeslot_id_to_numer)
    for timeslot_id in sorted_timeslots:
        output_md += f"# {timeslot_id_to_name[timeslot_id]}\n"
        for ak in timeslots[timeslot_id]:
            output_md += f"## [{ak['name']} ({ak['room']})]({ak['protokoll']})\n"
            for participant in ak["participants"]:
                output_md += f"- {participant}\n"

    with open(output_file, "w") as f:
        f.write(output_md)

if __name__ == "__main__":
    # argv[1] is the output json file
    # argv[2] is the output md file
    generate_output_md(sys.argv[1], sys.argv[2])
