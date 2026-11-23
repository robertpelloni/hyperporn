import json
from websocket import create_connection
ts = json.load(open("C:/Users/hyper/tabs.json"))
t = [x for x in ts if "chatgpt.com/c/" in x.get("url", "")][0]
ws = create_connection(t["webSocketDebuggerUrl"], timeout=8, suppress_origin=True)
ws.settimeout(8)
ws.send(json.dumps({"id":1,"method":"Runtime.evaluate","params":{"expression":"document.title","returnByValue":True}}))
r = ws.recv()
ws.close()
open("C:/Users/hyper/workspace/hyperporn/cdp_recon3_out.txt", "w").write(r[:300])
