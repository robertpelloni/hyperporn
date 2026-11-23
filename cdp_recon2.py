import json
from websocket import create_connection
tabs = json.load(open("C:/Users/hyper/tabs.json"))
targets = [t for t in tabs if t.get("type") == "page" and ("chatgpt.com" in t.get("url", "") or "gemini.google.com" in t.get("url", "") or "muse.ai" in t.get("url", ""))]
js = """JSON.stringify(Array.from(document.querySelectorAll("[contenteditable=true],textarea")).map(function(e){return e.tagName+":"+e.id+":"+((e.className||"").toString().slice(0,50))+":"+(e.offsetParent!==null)}).slice(-8))"""
out = []
for t in targets:
    try:
        ws = create_connection(t["webSocketDebuggerUrl"], timeout=5, suppress_origin=True)
        ws.settimeout(5)
        ws.send(json.dumps({"id":1,"method":"Runtime.evaluate","params":{"expression":js,"returnByValue":True}}))
        out.append(t["url"][:55] + " => " + ws.recv()[:700])
        ws.close()
    except Exception as e:
        out.append(t["url"][:55] + " !! " + type(e).__name__)
open("C:/Users/hyper/workspace/hyperporn/cdp_recon_out.txt", "w").write(chr(10).join(out))
print("done")
