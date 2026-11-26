import json
from websocket import create_connection
url = "ws://localhost:9222/devtools/page/226D380644DCDB10A171A1BA66D8D0C5"
out = []
for kw in ({"suppress_origin":True}, {"origin":"http://localhost"}, {}):
    try:
        ws = create_connection(url, timeout=4, **kw)
        ws.settimeout(4)
        ws.send(json.dumps({"id":1,"method":"Runtime.evaluate","params":{"expression":"document.title","returnByValue":True}}))
        out.append(str(sorted(kw.keys())) + " => " + ws.recv()[:200])
        ws.close()
        break
    except Exception as e:
        out.append(str(sorted(kw.keys())) + " !! " + type(e).__name__ + ": " + str(e)[:120])
open("C:/Users/hyper/workspace/hyperporn/cdp_result.txt", "w").write(chr(10).join(out))
print("done")
