import yaml
from odsparsator import odsparsator
import sys
import os

def generate_yaml_config(input_ods_sheet_file, input_yaml_config_file, output_yaml_file):
    config = {
        "timeslots": [],
        "rooms": [],
        "participants": [],
        "aks": []
    }

    # read the input yaml config
    with open(input_yaml_config_file, 'r') as yaml_file:
        config = yaml.safe_load(yaml_file)

    aks=[]
    people={}

    sheet = odsparsator.ods_to_python(input_ods_sheet_file)
    tables = sheet["body"]
    AKtable = None
    ParticipantsTable = None
    for table in tables:
        if table["name"] == "AKs":
            AKtable = table["table"]
        elif table["name"] == "Menschen":
            ParticipantsTable = table["table"]

    if not AKtable:
        raise Exception("AKs table not found")

    # go over all rows in the AK table skipping the first row
    for raw_row in AKtable[1:]:
        row = raw_row["row"]
        cleanedCols = []
        colStyle = {}
        for col in row:
            # some cols have extra styling info, for these we take the 'value' key
            # TODO styling info defines wether a person is needed or not
            typ = type(col)
            if typ.__name__ == "dict" and "value" in col:
                cleanedCols.append(col["value"])
                colStyle[col["value"]] = col["style"]
            else:
                cleanedCols.append(col)
        if len(cleanedCols) == 0:
            break
        name = cleanedCols[0]
        if name == "" or name == "null":
            break
        duration = 1
        head_field = cleanedCols[1]
        if not head_field:
            head_field = ""
        heads = []
        if head_field != "" and head_field != "null":
            heads = [head_field]
        participants = []
        for x in cleanedCols[2:12]:
            if x and x != "null":
                if colStyle[x] == 'ce77': # GELB -> required
                    print(f"Found required person: {x}")
                    heads.append(x)
                else:
                    participants.append(x)
        protokoll = ""
        if len(cleanedCols) > 12:
            protokoll = cleanedCols[12]
        description = ""
        if len(cleanedCols) > 13:
            description = cleanedCols[13]
        room_constraints = []
        if len(cleanedCols) > 14:
            room_constraints = cleanedCols[14].split(",")
        time_constraints = []
        if len(cleanedCols) > 15:
            time_constraints = cleanedCols[15].split(",")
        aks.append({
            "name": name,
            "protokoll": protokoll,
            "description": description,
            "duration": duration,
            "head": head_field,
            "participants": participants+heads,
            "room_constraints": room_constraints,
            "time_constraints": time_constraints
        })
        for head in heads:
            if not head in people:
                people[head] = {"name": "head", "aks": []}
            people[head]["aks"].append({"name": name, "required": True})
        for participant in participants:
            if not participant in people:
                people[participant] = {"name": "participant", "aks": []}
            people[participant]["aks"].append({"name": name})

    # go over all rows in the participants table skipping the first row
    # for all rows where the third column doesn't contain a checkmark symbol "✔" add the time_constraint "nach_freitag_ankunft"
    for raw_row in ParticipantsTable[1:]:
        row = raw_row["row"]
        cleanedCols = []
        for col in row:
            # some cols have extra styling info, for these we take the 'value' key
            typ = type(col)
            if typ.__name__ == "dict" and "value" in col:
                cleanedCols.append(col["value"])
            else:
                cleanedCols.append(col)
        if len(cleanedCols) == 0:
            break
        if cleanedCols[1] is None or cleanedCols[1] == "" or cleanedCols[1] == "null":
            break
        name = cleanedCols[1]
        if name == "" or name == "null":
            break
        if cleanedCols[2] is None or cleanedCols[1] == "" or cleanedCols[1] == "null":
            print(f"{name} comes after friday noon")
            person = people.get(name, {"name": "participant", "aks": []})
            if not 'time_constraints' in person:
                person['time_constraints'] = []
            person['time_constraints'].append("nach_freitag_ankunft")
            people[name] = person
        else:
            person = people.get(name, {"name": "participant", "aks": []})
            if not 'time_constraints' in person:
                person['time_constraints'] = []
            people[name] = person

    config["aks"] = aks
    # Convert people from dict to list with key in name field
    config["participants"] = [{"name": key,
                               "aks": value["aks"],
                               "time_constraints": value["time_constraints"]}
                               for key, value in people.items()]


    os.makedirs(os.path.dirname(output_yaml_file), exist_ok=True)
    with open(output_yaml_file, 'w+') as yaml_file:
        yaml.dump(config, yaml_file)


if __name__ == "__main__":
    generate_yaml_config(sys.argv[1], sys.argv[2], sys.argv[3])
