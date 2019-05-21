
from uiputils.uiptools.cast import formated_json
import json

if __name__ == '__main__':
    with open('./opintents2.json', 'r') as fp:
        print(formated_json(json.load(fp)))
