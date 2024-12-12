import json
import argparse

def generate_ak_importance(input_file):
    input = json.load(open(input_file))
    ak_importance = {}

    # Each person has a score of 1 they distribute among their AKs equally
    for participant in input['participants']:
        for preference in participant['preferences']:
            ak_id = preference['ak_id']
            if ak_id not in ak_importance:
                ak_importance[ak_id] = 0
            ak_importance[ak_id] += 1 / len(participant['preferences'])
    
    ak_id_to_name = {}
    for ak in input['aks']:
        ak_id_to_name[ak['id']] = ak['info']['name']


    output = []
    for ak_id in ak_importance.keys():
        output.append([ak_id_to_name[ak_id], ak_importance[ak_id]])
    
    output.sort(key=lambda x: x[1], reverse=True)
    return output

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Generate AK importance from input JSON file.')
    parser.add_argument('input_json', type=str, help='Path to the input JSON file')
    args = parser.parse_args()

    ak_importance = generate_ak_importance(args.input_json)
    output_md = ""
    for ak in ak_importance:
        # Print name and importance rounded to two decimal places
        output_md += f"- {ak[0]}: {ak[1]:.2f}\n"
    print(output_md)
