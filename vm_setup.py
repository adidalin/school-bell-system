"""Complete VoiceMeeter Banana setup for dual-zone output"""
import ctypes, time, sys

bits = 64 if sys.maxsize > 2**32 else 32
dll_path = f"C:/Program Files (x86)/VB/Voicemeeter/VoicemeeterRemote{bits}.dll"
vm = ctypes.windll.LoadLibrary(dll_path)

result = vm.VBVMR_Login()
if result != 0:
    print(f"Login failed: {result}")
    sys.exit(1)

print("=== VoiceMeeter Banana Configuration ===\n")

# Step 1: Configure bus output devices
# A1 -> WDM device 1 (扬声器 - Speakers)
vm.VBVMR_SetParameters(b"Bus[0].device.wdm=1\0")
time.sleep(0.1)
print("A1 (Bus[0]) -> WDM device 1 (扬声器)")

# A2 -> KS device 1 (try both 0 and 1 to see which works)
# KS 0 = Speakers (WDM-KS), KS 1 = Headphones (WDM-KS) probably
vm.VBVMR_SetParameters(b"Bus[1].device.ks=1\0")
time.sleep(0.1)
print("A2 (Bus[1]) -> KS device 1")

# Step 2: Configure strip routing
# Strip[3] = Virtual Input 1 (Voicemeeter VAIO) -> A1 only (Speakers)
vm.VBVMR_SetParameters(b"Strip[3].A1=1\0")
vm.VBVMR_SetParameters(b"Strip[3].A2=0\0")
vm.VBVMR_SetParameters(b"Strip[3].A3=0\0")
vm.VBVMR_SetParameters(b"Strip[3].B1=0\0")
vm.VBVMR_SetParameters(b"Strip[3].B2=0\0")
time.sleep(0.1)
print("Virtual Input 1 (Strip[3]) -> A1 only")

# Strip[4] = Virtual Input 2 (Aux VAIO) -> A2 only (Headphones)
vm.VBVMR_SetParameters(b"Strip[4].A1=0\0")
vm.VBVMR_SetParameters(b"Strip[4].A2=1\0")
vm.VBVMR_SetParameters(b"Strip[4].A3=0\0")
vm.VBVMR_SetParameters(b"Strip[4].B1=0\0")
vm.VBVMR_SetParameters(b"Strip[4].B2=0\0")
time.sleep(0.1)
print("Virtual Input 2 (Strip[4]) -> A2 only")

# Step 3: Verify by reading back
buf = ctypes.create_string_buffer(512)

params = [
    "Bus[0].device.wdm",
    "Bus[1].device.ks",
    "Strip[3].A1",
    "Strip[3].A2",
    "Strip[4].A1",
    "Strip[4].A2",
]
for p in params:
    # Use GetParameterStringW
    wbuf = ctypes.create_unicode_buffer(512)
    try:
        func = vm.VBVMR_GetParameterStringW
        func.argtypes = [ctypes.c_char_p, ctypes.c_wchar_p]
        func.restype = ctypes.c_long
        res = func(p.encode(), wbuf)
        print(f"  {p} = {wbuf.value} (res={res})")
    except:
        try:
            fbuf = ctypes.c_float()
            func = vm.VBVMR_GetParameterFloat
            func.restype = ctypes.c_long
            func.argtypes = [ctypes.c_char_p, ctypes.POINTER(ctypes.c_float)]
            res = func(p.encode(), ctypes.byref(fbuf))
            print(f"  {p} = {fbuf.value} (res={res})")
        except Exception as e2:
            print(f"  {p}: could not read ({e2})")

vm.VBVMR_Logout()
print("\nDone! VoiceMeeter configured.")
