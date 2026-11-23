import json
from websocket import create_connection
tabs = json.load(open("C:/Users/hyper/tabs.json"))
targets = [t for t in tabs if t.get("type") == "page" and ("chatgpt.com" in t.get("url", "") or "gemini.google.com" in t.get("url", "") or "muse.ai" in t.get("url", ""))]
print(len(targets))
js = """JSON.stringify(Array.from(document.querySelectorAll("[contenteditable=true],textarea")).map(function(e){return e.tagName+":"+e.id+":"+(e.offsetParent!==null)}).slice(-6))"""
for t in targets:
    print(t.get("url", "")[:60])
    ws = create_connection(t["webSocketDebuggerUrl"], timeout=10)
    ws.send(json.dumps({"id":1,"method":"Runtime.evaluate","params":{"expression":js,"returnByValue":True}}))
    print(ws.recv()[:500])
    ws.close()
