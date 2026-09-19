import struct,sys,os,json,hashlib

def align(x,p): return (x+p-1)//p*p

def parse(path):
 d=open(path,'rb').read(); assert d[:8]==b'VNDRBOOT'
 ver,page,kaddr,raddr,vrsz=struct.unpack_from('<5I',d,8); assert ver==4
 o=28; cmd=d[o:o+2048];o+=2048; tags=struct.unpack_from('<I',d,o)[0];o+=4; name=d[o:o+16];o+=16
 hs,ds=struct.unpack_from('<II',d,o);o+=8; da=struct.unpack_from('<Q',d,o)[0];o+=8
 ts,en,es,bs=struct.unpack_from('<4I',d,o);o+=16
 vroff=page; dtoff=vroff+align(vrsz,page); toff=dtoff+align(ds,page); boff=toff+align(ts,page)
 ents=[]
 for i in range(en):
  e=d[toff+i*es:toff+(i+1)*es]; sz,off,typ=struct.unpack_from('<III',e,0); nm=e[12:44]; bids=e[44:108]
  ents.append((sz,off,typ,nm,bids,d[vroff+off:vroff+off+sz]))
 return dict(d=d,ver=ver,page=page,kaddr=kaddr,raddr=raddr,cmd=cmd,tags=tags,name=name,hs=hs,dtb=d[dtoff:dtoff+ds],da=da,es=es,boot=d[boff:boff+bs],ents=ents)
def pack(x, payloads, out):
 page=x['page']; es=x['es']; offs=[]; pos=0
 for p in payloads: offs.append(pos); pos+=len(p)
 vrsz=pos; table=b''
 for i,p in enumerate(payloads):
  old=x['ents'][i]; table+=struct.pack('<III',len(p),offs[i],old[2])+old[3]+old[4]
 hdr=(b'VNDRBOOT'+struct.pack('<5I',4,page,x['kaddr'],x['raddr'],vrsz)+x['cmd']+struct.pack('<I',x['tags'])+x['name']+struct.pack('<IIQ4I',x['hs'],len(x['dtb']),x['da'],len(table),len(payloads),es,len(x['boot'])))
 assert len(hdr)==x['hs']
 blob=hdr+b'\0'*(page-len(hdr))
 vr=b''.join(payloads);blob+=vr+b'\0'*(align(len(vr),page)-len(vr))
 blob+=x['dtb']+b'\0'*(align(len(x['dtb']),page)-len(x['dtb']))
 blob+=table+b'\0'*(align(len(table),page)-len(table))+x['boot']
 open(out,'wb').write(blob)
x=parse(sys.argv[1]);pack(x,[e[5] for e in x['ents']],sys.argv[2])
print(len(open(sys.argv[2],'rb').read()),hashlib.sha256(open(sys.argv[2],'rb').read()).hexdigest())
