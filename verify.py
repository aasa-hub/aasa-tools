import json,urllib.request,sys
ENDPOINTS=["https://bsc-rpc.publicnode.com","https://bsc-dataseed.binance.org","https://1rpc.io/bnb"]
TOKEN="0x90c8889f428F9Ebb77BB8f15CAD3a50a9aC680df"
TREASURY="0x7C34E9e21eE28A49Ff0b84B61774119E6633359f"
POOLS=[("FLAPJAX/WBNB 1%","0xca93ec685b8623688e6b236f9068034b298c2150"),
       ("FLAPJAX/BTCB 1%","0x740a3b4a91cb8fa47e85d7f9713ca6ec2f8a037e")]
DANGER={"0x40c10f19":"mint(address,uint256)","0xa0712d68":"mint(uint256)","0x8456cb59":"pause()",
"0x3f4ba83a":"unpause()","0xf9f92be4":"blacklist(address)","0x0ecb93c0":"addBlackList(address)",
"0xc6d69a30":"setTaxRate(uint256)","0x2e5bb6ff":"setTax(uint256)","0x69fe0e2d":"setFee(uint256)",
"0x437823ec":"excludeFromFee(address)","0xea2f0b37":"includeInFee(address)","0x3659cfe6":"upgradeTo(address)",
"0x4f1ef286":"upgradeToAndCall(address,bytes)","0x153b0d1e":"setBlacklist(address,bool)",
"0xec28438a":"setMaxTxAmount(uint256)","0xc2e5ec04":"setTradingEnabled(bool)"}
def rpc(url,method,params,retry=0):
    d=json.dumps({"jsonrpc":"2.0","id":1,"method":method,"params":params}).encode()
    r=urllib.request.Request(url,d,{"Content-Type":"application/json","User-Agent":"flapjax-verify/1.0"})
    return json.loads(urllib.request.urlopen(r,timeout=30).read())["result"]
def pick():
    for u in ENDPOINTS:
        try:
            rpc(u,"eth_blockNumber",[]); return u
        except Exception: continue
    raise SystemExit("no endpoint")
U=pick()
blk=int(rpc(U,"eth_blockNumber",[]),16)
def call(to,data,block=blk):
    return rpc(U,"eth_call",[{"to":to,"data":data},hex(block)])
def word(h):
    h=h[2:] if h.startswith("0x") else h
    return int(h[:64] or "0",16)
def dec_str(h):
    h=h[2:]; ln=int(h[64:128],16); return bytes.fromhex(h[128:128+ln*2]).decode()
res={"endpoint":U,"block":blk,"checks":[]}
def add(name,status,detail): res["checks"].append({"name":name,"status":status,"detail":detail})
code=rpc(U,"eth_getCode",[TOKEN,hex(blk)])
add("token has code","PASS" if len(code)>2 else "FAIL",f"{len(code)//2-1} bytes at block {blk}")
sym=dec_str(call(TOKEN,"0x95d89b41")); dec=word(call(TOKEN,"0x313ce567")); sup=word(call(TOKEN,"0x18160ddd"))
add("symbol/decimals",f"PASS" if sym=="FLAPJAX" and dec==18 else "FAIL",f"{sym}, {dec} decimals, totalSupply {sup/10**dec:,.0f} (as-is, no price)")
own=call(TOKEN,"0x8da5cb5b"); add("owner() burned","PASS" if word(own)==0 else "FAIL",own)
impl=rpc(U,"eth_getStorageAt",[TOKEN,"0x360894a13ba1a3210667c828492db98dca3e2076cc3735a920a3ca505d382bbc",hex(blk)])
adm=rpc(U,"eth_getStorageAt",[TOKEN,"0xb53127684a568b3173ae13b9f8a6016e243e63b6e8ee1178d6a717850b5d6103",hex(blk)])
add("not a proxy (EIP-1967)",("PASS" if word(impl)==0 and word(adm)==0 else "FAIL"),
    f"impl slot {impl} · admin slot {adm}")
found=[s for s in DANGER if s in code.lower()]
add("admin selectors absent","PASS" if not found else "FAIL",", ".join(DANGER[s] for s in found) or "none of 16 privileged selectors in runtime bytecode")
tre=word(call(TOKEN,"0x70a08231"+"0"*24+TREASURY[2:].lower()))
add("treasury FLAPJAX read","PASS",f"{tre/1e18:,.0f} FJ at block {blk} (balance read only)")
for label,p in POOLS:
    pc=rpc(U,"eth_getCode",[p,hex(blk)])
    if len(pc)<=2:
        add(f"pool {label}","FAIL","no code"); continue
    t0="0x"+call(p,"0x0dfe1681")[-40:]; t1="0x"+call(p,"0xd21220a7")[-40:]
    fee=word(call(p,"0xddca3f43")); liq=word(call(p,"0x1a686502")); s0=call(p,"0x3850c7bd")
    has_fj = TOKEN.lower() in (t0.lower(),t1.lower())
    add(f"pool {label}",("PASS" if has_fj else "FAIL"),
        f"token0 {t0} token1 {t1} fee {fee} liquidity {liq} sqrtPriceX96 {word(s0)}")
res["unmeasured"]=["LP lock ownership (needs the locker contract's own state)",
 "holder distribution and top-holder concentration","off-chain bounty claims and their review status"]
print(json.dumps(res,indent=1))
