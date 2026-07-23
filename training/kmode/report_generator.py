import json


def save_report(path, results):
    with open(path, 'w', encoding='utf-8') as file:
        json.dump(results, file, indent=2)


def create_report(results):
    return {
        'accuracy': results.get('accuracy', 0),
        'loss': results.get('loss', 0),
    }
