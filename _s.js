const msg = "[muse-spark-1.3-contributor in pi in ~/workspace/hyperporn] Lane update: model changed (was mimo-v2.6-pro, now muse-spark-1.3-contributor per PI_MODEL, same session 01a17499). Re-affirming prior ack: audio uncleared until Robert confirms in main chat, originals untouched, fair-use doc is analysis only, no distribution, radio-edit + HLS on hold. Continuing coordination on this lane. Out.";
const wsUrl = "ws://127.0.0.1:9222/devtools/page/606BA1BC0C04802CCFF9EFD46886435D";
const ws = new WebSocket(wsUrl);
let id=1;
function send(m,p){return new Promise((res,rej)=>{const c=id++;const t=setTimeout(()=>rej(new Error("t "+m)),8000);const h=(ev)=>{try{const o=JSON.parse(ev.data);if(o.id===c){clearTimeout(t);ws.removeEventListener("message",h);o.error?rej(new Error(JSON.stringify(o.error))):res(o.result);}}catch{}};ws.addEventListener("message",h);ws.send(JSON.stringify({id:c,method:m,params:p}));});}
ws.addEventListener("open", async()=>{
 try{
  await send("Runtime.evaluate",{expression:"document.querySelector('textarea').focus(); 'f'", returnByValue:true});
  await send("Input.insertText",{text: msg});
  console.log("inserted");
  await send("Input.dispatchKeyEvent",{type:"keyDown", key:"Enter", code:"Enter", windowsVirtualKeyCode:13, nativeVirtualKeyCode:13});
  await send("Input.dispatchKeyEvent",{type:"keyUp", key:"Enter", code:"Enter", windowsVirtualKeyCode:13, nativeVirtualKeyCode:13});
  console.log("sent");
  await new Promise(r=>setTimeout(r,3000));
  const v2 = await send("Runtime.evaluate",{expression:"document.querySelector('textarea').value.length", returnByValue:true});
  console.log("len after:", v2.result?.value);
  ws.close();process.exit(0);
 }catch(e){console.log("ERR",e.message);ws.close();process.exit(1);}
});
setTimeout(()=>{console.log("TIMEOUT");process.exit(1);},20000);
