import json

data_dir = "./data/chatCD"


def read_json() -> dict:
    try:
        with open(data_dir + "usercd.json", "r") as f_in:
            data = json.load(f_in)
            f_in.close()
            return data
    except FileNotFoundError:
        try:
            import os

            os.makedirs(data_dir)
        except FileExistsError:
            pass
        with open(data_dir + "usercd.json", mode="w") as f_out:
            json.dump({}, f_out)

        return {}


def write_json(qid: str, time: int, mid: int, data: dict):
    data[qid] = [time, mid]
    with open(data_dir + "usercd.json", "w") as f_out:
        json.dump(data, f_out)
        f_out.close()


def remove_json(qid: str):
    with open(data_dir + "usercd.json", "r") as f_in:
        data = json.load(f_in)
        f_in.close()
    data.pop(qid)
    with open(data_dir + "usercd.json", "w") as f_out:
        json.dump(data, f_out)
        f_out.close()
