import json
import argparse

def generate_aks_possible_on_thursday(input_json):
    with open(input_json, "r") as f:
        input = json.load(f)
    
    aks = set()

    ak_id_to_name = {}
    for ak in input["aks"]:
        ak_id_to_name[ak["id"]] = ak["info"]["name"]

    for ak in input['aks']:
        aks.add(ak['id'])

    for participant in input["participants"]:
        if 'nach_freitag_ankunft' in participant.get('time_constraints', []):
            for ak in participant["preferences"]:
                aks.discard(ak["ak_id"])

    out = []
    for ak in aks:
        out.append(ak_id_to_name[ak])
    return out

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Generate AK importance from input JSON file.')
    parser.add_argument('input_json', type=str, help='Path to the input JSON file')
    args = parser.parse_args()

    aks = generate_aks_possible_on_thursday(args.input_json)
    for ak in aks:
        print(ak)
