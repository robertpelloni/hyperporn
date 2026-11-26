import json
from websocket import create_connection
ws = create_connection("ws://localhost:9222/devtools/page/226D380644DCDB10A171A1BA66D8D0C5", timeout=10, suppress_origin=True)
ws.send(json.dumps({"id":1,"method":"Runtime.evaluate","params":{"expression":"document.title","returnByValue":True}}))
print(ws.recv()[:300])
ws.close()
