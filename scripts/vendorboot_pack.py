#!/usr/bin/env python3
import struct,sys,hashlib

def align(x,p): return (x+p-1)//p*p

def parse(path):
 d=open(path,'rb').read()
 if d[:8]!=b'VNDRBOOT': raise SystemExit('bad VNDRBOOT magic')
 ver,page,kaddr,raddr,vrsz=struct.unpack_from('<5I',d,8)
 if ver!=4 or page!=4096: raise SystemExit(f'unexpected header: v{ver} page={page}')
 o=28; cmd=d[o:o+2048];o+=2048; tags=struct.unpack_from('<I',d,o)[0];o+=4; name=d[o:o+16];o+=16
 hs,ds=struct.unpack_from('<II',d,o);o+=8; da=struct.unpack_from('<Q',d,o)[0];o+=8
 ts,en,es,bs=struct.unpack_from('<4I',d,o);o+=16
 if hs!=2128 or en!=2 or es!=108: raise SystemExit(f'unexpected stock table/header: hs={hs} en={en} es={es}')
 vroff=page; dtoff=vroff+align(vrsz,page); toff=dtoff+align(ds,page); boff=toff+align(ts,page)
 ents=[]
 for i in range(en):
  e=d[toff+i*es:toff+(i+1)*es]; sz,off,typ=struct.unpack_from('<III',e,0); nm=e[12:44]; bids=e[44:108]
  payload=d[vroff+off:vroff+off+sz]
  if len(payload)!=sz: raise SystemExit('truncated stock ramdisk')
  ents.append((sz,off,typ,nm,bids,payload))
 return dict(d=d,page=page,kaddr=kaddr,raddr=raddr,cmd=cmd,tags=tags,name=name,hs=hs,dtb=d[dtoff:dtoff+ds],da=da,es=es,boot=d[boff:boff+bs],ents=ents)

def pack(x, platform, recovery, out):
 payloads=[platform,recovery]; page=x['page']; offsets=[0,len(platform)]; total=sum(map(len,payloads))
 table=b''
 for i,p in enumerate(payloads):
  old=x['ents'][i]
  typ=1 if i==0 else 2
  name=old[3] if i==0 else b'recovery'+b'\0'*24
  table += struct.pack('<III',len(p),offsets[i],typ)+name+old[4]
 hdr=(b'VNDRBOOT'+struct.pack('<5I',4,page,x['kaddr'],x['raddr'],total)+x['cmd']+
      struct.pack('<I',x['tags'])+x['name']+
      struct.pack('<IIQ4I',x['hs'],len(x['dtb']),x['da'],len(table),2,x['es'],len(x['boot'])))
 if len(hdr)!=x['hs']: raise SystemExit(f'header size mismatch {len(hdr)}')
 blob=hdr+b'\0'*(page-len(hdr))
 vr=platform+recovery; blob+=vr+b'\0'*(align(len(vr),page)-len(vr))
 blob+=x['dtb']+b'\0'*(align(len(x['dtb']),page)-len(x['dtb']))
 blob+=table+b'\0'*(align(len(table),page)-len(table))+x['boot']
 open(out,'wb').write(blob)
 print(f'pre_avb_size={len(blob)}')
 print(f'platform_size={len(platform)} recovery_size={len(recovery)} total_ramdisks={total}')
 print(f'stock_cmdline={x["cmd"].split(bytes([0]),1)[0].decode(errors="replace")}')
 print(f'stock_dtb_sha256={hashlib.sha256(x["dtb"]).hexdigest()}')

if len(sys.argv)!=5: raise SystemExit('usage: vendorboot_pack.py stock.img platform.lz4 recovery.lz4 out.img')
x=parse(sys.argv[1]); p=open(sys.argv[2],'rb').read(); r=open(sys.argv[3],'rb').read()
if p[:4]!=b'\x02\x21\x4c\x18' or r[:4]!=b'\x02\x21\x4c\x18': raise SystemExit('both fragments must be legacy LZ4')
pack(x,p,r,sys.argv[4])
