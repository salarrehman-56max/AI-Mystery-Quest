import json, os
from models.case import Case

ROOT = os.path.dirname(os.path.dirname(__file__))
CASES_PATH = os.path.join(ROOT, "data", "cases.json")
HISTORY_PATH = os.path.join(ROOT, "data", "history.json")

DEFAULT_CASES = [
{
"id":"museum-heist","title":"The Midnight Sapphire","category":"Theft","difficulty":"Easy","location":"Blackthorn Museum",
"story":"At the museum's midnight gala, the priceless Star Sapphire vanished from a locked display. The alarm was disabled for twelve minutes. Three staff members had access to the east gallery.",
"solution":"Mara Voss","explanation":"Mara signed out the display maintenance key shortly before the theft and returned it after the alarm resumed. The gallery clock was manually reset during the same period, contradicting her claim that she stayed in the restoration lab.",
"suspects":[
{"name":"Mara Voss","role":"Head Conservator","background":"Knows the display mechanisms and maintains delicate exhibits.","motive":"Her restoration grant was about to be cancelled.","alibi":"Claims she remained in the restoration lab all evening."},
{"name":"Elias Reed","role":"Security Officer","background":"Monitors cameras and the alarm console.","motive":"Recently received a notice about gambling debts.","alibi":"Says he stayed in the security booth."},
{"name":"Nina Vale","role":"Event Coordinator","background":"Managed guest access and the gala schedule.","motive":"Wanted publicity after being passed over for promotion.","alibi":"Says she was greeting guests in the main hall."}],
"evidence":[
{"id":"clue-key","title":"Maintenance Key Log","description":"Mara signed out the east display key at 11:42 PM and returned it at 12:08 AM.","related":"Mara Voss"},
{"id":"clue-clock","title":"The Gallery Clock","description":"The east gallery clock stopped at 11:56 PM and was manually reset. Dust on its winding knob was disturbed.","related":"Mara Voss"},
{"id":"clue-alarm","title":"Alarm Console Record","description":"The alarm entered maintenance mode using an authorized staff code, not by force.","related":"Elias Reed"}],
"puzzle":{"question":"A detective sees the sequence 2, 4, 8, 16. What number comes next?","options":["18","24","32","64"],"answer":"32","explanation":"Each number is double the previous number."}
},
{
"id":"lighthouse-blackout","title":"The Lighthouse Blackout","category":"Suspicious Incident","difficulty":"Medium","location":"Greyhaven Lighthouse",
"story":"During a storm, the lighthouse beam went dark for seventeen minutes. A cargo vessel nearly struck the rocks. The generator was intact, but a brass fuse had disappeared from the control room.",
"solution":"Jonas Pike","explanation":"The missing brass fuse was found in Jonas's tool pouch. He claimed to be outside securing the railing, but protected interior stairs carried wet boot prints matching his work boots.",
"suspects":[
{"name":"Jonas Pike","role":"Maintenance Keeper","background":"Maintains the generator, wiring, and lighthouse structure.","motive":"Was angry that the maintenance contract was being transferred.","alibi":"Claims he was securing the eastern railing throughout the blackout."},
{"name":"Iris Bell","role":"Weather Observer","background":"Records storm conditions and communicates with ships.","motive":"Her storm warnings had recently been questioned.","alibi":"Says she remained in the observation room."},
{"name":"Caleb Moss","role":"Harbor Pilot","background":"Guides vessels through the coastal channel.","motive":"Had argued with the lighthouse authority over harbor fees.","alibi":"Says he was at the harbor radio station."}],
"evidence":[
{"id":"clue-fuse","title":"Missing Brass Fuse","description":"A brass fuse matching the control panel was found in Jonas's tool pouch.","related":"Jonas Pike"},
{"id":"clue-prints","title":"Boot Prints Indoors","description":"Wet boot prints appeared on an interior corridor protected from the storm.","related":"Jonas Pike"},
{"id":"clue-weather","title":"Weather Log","description":"The strongest gusts began after the lighthouse beam returned.","related":"Iris Bell"}],
"puzzle":{"question":"A ship flashes a signal of three short lights, then two short lights. How many flashes are in two complete repetitions?","options":["5","8","10","12"],"answer":"10","explanation":"There are five flashes in each repetition, so two repetitions contain ten."}
},
{
"id":"orchid-disappearance","title":"The Vanishing Orchid","category":"Missing Person","difficulty":"Hard","location":"Willowmere Conservatory",
"story":"Botanist Dr. Selene Hart vanished after announcing the discovery of a rare orchid. Her greenhouse was locked from inside, her tea was untouched, and a muddy footprint lay beside a ventilation hatch.",
"solution":"Peter Wren","explanation":"A delivery receipt showed Peter received a replacement vent grille that morning. The footprint matched greenhouse technician clogs, and the hatch could be opened from outside while the grille was removed.",
"suspects":[
{"name":"Peter Wren","role":"Greenhouse Technician","background":"Maintains vents, irrigation, and greenhouse equipment.","motive":"Feared losing his job after Selene questioned supply orders.","alibi":"Claims he was repairing the west irrigation line."},
{"name":"Dr. Anya Cole","role":"Research Partner","background":"Co-authored several papers with Selene.","motive":"Wanted sole credit for the orchid discovery.","alibi":"Says she was in the university library."},
{"name":"Ruth Dallow","role":"Conservatory Director","background":"Controls access to the research wing.","motive":"The discovery could expose unauthorized plant sales.","alibi":"Says she was meeting donors in the front office."}],
"evidence":[
{"id":"clue-receipt","title":"Ventilation Grille Receipt","description":"A replacement grille was delivered to Peter on the morning Selene disappeared.","related":"Peter Wren"},
{"id":"clue-footprint","title":"Muddy Footprint","description":"The tread matches the clogs issued to greenhouse technicians.","related":"Peter Wren"},
{"id":"clue-tea","title":"Untouched Tea","description":"The tea was still warm, suggesting Selene left suddenly rather than planning to leave.","related":"Dr. Anya Cole"}],
"puzzle":{"question":"I speak without a mouth and hear without ears. I have no body, but come alive with wind. What am I?","options":["Shadow","Echo","Clock","River"],"answer":"Echo","explanation":"An echo repeats sound without having a physical mouth or ears."}
}
]

class GameService:
    def __init__(self):
        os.makedirs(os.path.dirname(CASES_PATH), exist_ok=True)
        if not os.path.exists(CASES_PATH):
            self._write(CASES_PATH, DEFAULT_CASES)
        if not os.path.exists(HISTORY_PATH):
            self._write(HISTORY_PATH, [])

    def _read(self, path, fallback):
        try:
            with open(path, encoding="utf-8") as f: return json.load(f)
        except (OSError, json.JSONDecodeError): return fallback

    def _write(self, path, data):
        tmp = path + ".tmp"
        with open(tmp, "w", encoding="utf-8") as f: json.dump(data, f, indent=2, ensure_ascii=False)
        os.replace(tmp, path)

    def all_cases(self): return self._read(CASES_PATH, DEFAULT_CASES)
    def get_case(self, case_id):
        data = next((c for c in self.all_cases() if c.get("id") == case_id), None)
        return Case.from_dict(data).to_dict() if data else None
    def list_case(self, c): return {k:c[k] for k in ("id","title","category","difficulty","location","story")}
    def list_cases(self): return [self.list_case(c) for c in self.all_cases()]
    def public_case(self, case):
        result = dict(case)
        result.pop("solution", None); result.pop("explanation", None)
        result["puzzle"] = {k:v for k,v in case["puzzle"].items() if k not in ("answer","explanation")}
        return result
    def save_history(self, record):
        history = self.history()
        history.insert(0, record)
        self._write(HISTORY_PATH, history[:100])
    def history(self): return self._read(HISTORY_PATH, [])
    def add_case(self, case):
        case["id"] = "ai-" + __import__("uuid").uuid4().hex[:10]
        cases = self.all_cases(); cases.insert(0, case); self._write(CASES_PATH, cases[:40])
        return case
