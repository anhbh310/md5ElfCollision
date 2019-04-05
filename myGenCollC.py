import md5
import binascii
import os


def buildElfFile():
    elfName = "elfFile"
    os.system("gcc c_demo.c -o {}".format(elfName))


def createCollision(prefix, middle, suffix, b0, b1):
    with open("goodFile", "wb") as fgood:
        fgood.write(prefix + b1 + middle + b1 + suffix)
    fgood.close()

    with open("evilFile", "wb") as fevil:
        fevil.write(prefix + b0 + middle + b1 + suffix)
    fevil.close()

    os.system("chmod +x goodFile evilFile")


def createCollisionBlock(prefix):
    digester = md5.MD5()
    digester.update(prefix)
    ihv = binascii.hexlify(digester.ihv()).decode()

    f0 = "block0"
    f1 = "block1"

    os.system("./fastcoll --ihv {} -o {} {}".format(ihv, f0, f1))

    with open(f0, 'rb') as f0d:
        b0 = f0d.read()

    with open(f1, 'rb') as f1d:
        b1 = f1d.read()

    os.system("rm {}".format(f0))
    os.system("rm {}".format(f1))

    return b0, b1


def main():
    buildElfFile()
    first = 0x680
    second = 0x748
    midlen = 0x48
    with open("elfFile", "rb") as elfF:
        elfFileData = elfF.read()
    elfF.close()

    prefix = elfFileData[:first]
    suffix = elfFileData[second + 128:]
    middle = elfFileData[first + 128:first + 128 + midlen]

    b0, b1 = createCollisionBlock(prefix)
    createCollision(prefix, middle, suffix, b0, b1)


if __name__ == "__main__":
    main()
