import yaml
from odsparsator import odsparsator
import sys

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
        duration = 2
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
        aks.append({
            "name": name,
            "duration": duration,
            "head": head_field,
            "participants": participants+heads
        })
        for head in heads:
            if not head in people:
                people[head] = {"name": "head", "aks": []}
            people[head]["aks"].append({"name": name, "required": True})
        for participant in participants:
            if not participant in people:
                people[participant] = {"name": "participant", "aks": []}
            people[participant]["aks"].append({"name": name})


    config["aks"] = aks
    # Convert people from dict to list with key in name field
    config["participants"] = [{"name": key, "aks": value["aks"]} for key, value in people.items()]

    with open(output_yaml_file, 'w') as yaml_file:
       yaml.dump(config, yaml_file)


if __name__ == "__main__":
    generate_yaml_config(sys.argv[1], sys.argv[2], sys.argv[3])
