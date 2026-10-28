const wsUrl = "ws://127.0.0.1:9222/devtools/page/606BA1BC0C04802CCFF9EFD46886435D";
const ws = new WebSocket(wsUrl);
let id=1;
function send(m,p){return new Promise((res,rej)=>{const c=id++;const t=setTimeout(()=>rej(new Error("t "+m)),8000);const h=(ev)=>{try{const o=JSON.parse(ev.data);if(o.id===c){clearTimeout(t);ws.removeEventListener("message",h);o.error?rej(new Error(JSON.stringify(o.error))):res(o.result);}}catch{}};ws.addEventListener("message",h);ws.send(JSON.stringify({id:c,method:m,params:p}));});}
ws.addEventListener("open", async()=>{
 try{
  const q=(e)=>send("Runtime.evaluate",{expression:e, returnByValue:true}).then(r=>r.result?.value);
  console.log("len:", await q("document.querySelector('textarea') ? document.querySelector('textarea').value.length : -1"));
  console.log("tail:", await q("document.body.innerText.slice(-600)"));
  ws.close();process.exit(0);
 }catch(e){console.log("ERR",e.message);ws.close();process.exit(1);}
});
setTimeout(()=>{console.log("TIMEOUT");process.exit(1);},15000);
