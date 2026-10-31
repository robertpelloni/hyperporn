const wsUrl = "ws://127.0.0.1:9222/devtools/page/79ACC9811DCA4E87E18C3A7F5DAE06D3";
const ws = new WebSocket(wsUrl);
ws.addEventListener("open", ()=>{
  const expr = "(()=>{const t=document.body.innerText;return t.slice(-1800);})()";
  ws.send(JSON.stringify({id:1, method:"Runtime.evaluate", params:{expression:expr, returnByValue:true}}));
});
ws.addEventListener("message",(ev)=>{
  try{
    const o=JSON.parse(ev.data);
    if(o.id===1){ console.log(o.result?.result?.value || ev.data.slice(0,500)); ws.close(); process.exit(0); }
  }catch(e){ console.log(ev.data.slice(0,800)); }
});
setTimeout(()=>{console.log("TIMEOUT");process.exit(1);},15000);
