const wsUrl = "ws://127.0.0.1:9222/devtools/page/79ACC9811DCA4E87E18C3A7F5DAE06D3";
const ws = new WebSocket(wsUrl);
ws.addEventListener("open", ()=>{
  ws.send(JSON.stringify({id:1, method:"Runtime.evaluate", params:{expression:"(document.querySelector('main')?document.querySelector('main').innerText:document.body.innerText).slice(-1200)", returnByValue:true}}));
});
ws.addEventListener("message",(ev)=>{
  try{
    const o=JSON.parse(ev.data);
    if(o.id===1){ console.log((o.result?.result?.value||'').slice(0,1400) || ev.data.slice(0,300)); }
  }catch(e){ console.log(ev.data.slice(0,300)); }
  try{ws.close();}catch(e){}
  setTimeout(()=>process.exit(0),500);
});
setTimeout(()=>{console.log("TIMEOUT");process.exit(1);},15000);
