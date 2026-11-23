import json,pathlib
p=pathlib.Path(r"C:\Users\hyper\.pi\agent\sessions\--C--Users-hyper-workspace-hyperporn--\2026-10-25T19-46-05-696Z_01a17499-4afc-720a-889f-0eb564861ab6.jsonl")
users=[]
assists=[]
for line in p.read_text(encoding="utf-8",errors="ignore").splitlines():
  try:
    o=json.loads(line)
  except: continue
  if o.get("type")!="message": continue
  m=o.get("message",{})
  role=m.get("role")
  content=m.get("content",[])
  texts=[]
  if isinstance(content,list):
    for c in content:
      if isinstance(c,dict) and c.get("type")=="text" and c.get("text"):
        texts.append(c["text"][:2000])
  if role=="user" and texts:
    users.append((o.get("timestamp",""), texts[0][:800]))
  if role=="assistant" and texts:
    assists.append((o.get("timestamp",""), texts[0][:1200]))
print(f"USERS={len(users)} ASSISTS={len(assists)}")
for ts,tx in users:
  print("====USER",ts,"====")
  print(tx[:800].replace(chr(13),\" \").replace(chr(10),\" | \"))
print("====ASSIST-LAST15====")
for ts,tx in assists[-15:]:
  print("----ASSIST",ts,"----")
  print(tx[:1200].replace(chr(13),\" \").replace(chr(10),\" | \"))

