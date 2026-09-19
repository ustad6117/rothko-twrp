#!/usr/bin/env python3
import os,re,subprocess,stat,sys,shutil
if len(sys.argv)!=3: raise SystemExit('usage: make_delta.py STOCK_PLATFORM_ROOT TWRP_RECOVERY_ROOT')
stock=os.path.abspath(sys.argv[1]); root=os.path.abspath(sys.argv[2])
libdirs=[os.path.join(root,'system/lib64'),os.path.join(root,'vendor/lib64')]
def needed(path):
 try: out=subprocess.check_output(['readelf','-d',path],stderr=subprocess.DEVNULL,text=True)
 except (subprocess.CalledProcessError,OSError): return []
 return re.findall(r'Shared library: \[(.*?)\]',out)
def resolve(name):
 for d in libdirs:
  p=os.path.join(d,name)
  if os.path.isfile(p): return p
 return None
# Preserve TWRP and the Android-16 recovery services whose ABI must stay matched to its libraries.
seed_names=['recovery','init','keystore2','fastbootd','adbd','update_engine_sideload','snapuserd',
            'vold_prepare_subdirs','mitee_helper','servicemanager','hwservicemanager','vndservicemanager',
            'logd','watchdogd','charger']
seen=set()
for n in seed_names:
 p=os.path.join(root,'system/bin',n)
 if os.path.isfile(p): seen.add(p)
q=list(seen)
while q:
 p=q.pop()
 for n in needed(p):
  r=resolve(n)
  if r and r not in seen: seen.add(r); q.append(r)
keep={os.path.relpath(p,root) for p in seen}
# TWRP-specific tools not guaranteed to exist in stock PLATFORM.
for n in ['twrp','busybox','bash','magiskboot','resetprop','lptools','lpdump','lpdumpd','fscryptpolicyget','minadbd']:
 p=os.path.join(root,'system/bin',n)
 if os.path.isfile(p): keep.add(os.path.relpath(p,root))
removed_n=removed_b=0
for base,dirs,files in os.walk(root):
 for f in files:
  p=os.path.join(base,f); rel=os.path.relpath(p,root); s=os.path.join(stock,rel)
  try: a=os.lstat(p); b=os.lstat(s)
  except OSError: continue
  if stat.S_ISREG(a.st_mode) and stat.S_ISREG(b.st_mode) and rel not in keep:
   os.remove(p); removed_n+=1; removed_b+=a.st_size
# Stock PLATFORM is authoritative for its kernel modules; only modules absent from stock survive.
mods=os.path.join(root,'lib/modules')
if os.path.isdir(mods):
 for base,dirs,files in os.walk(mods):
  for f in files:
   p=os.path.join(base,f); rel=os.path.relpath(p,root); s=os.path.join(stock,rel)
   if os.path.isfile(p) and os.path.isfile(s): os.remove(p)
# English-only build does not need CJK font payload or language packs.
shutil.rmtree(os.path.join(root,'twres/languages'),ignore_errors=True)
cjk=os.path.join(root,'twres/fonts/wqy-microhei.ttf')
if os.path.exists(cjk): os.remove(cjk)
print(f'abi_closure_files={len(keep)}')
print(f'overlap_files_removed={removed_n}')
print(f'overlap_bytes_removed={removed_b}')
