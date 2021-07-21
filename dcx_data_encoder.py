
''' DCX2496 sends and receives presets from PC via COM-Port
    The escaping tecnique used ensures that basically bit 0x80 (MSB) is only set
    in magic bytes handling communication control. So, 0x80  must be escaped in the data stream.
    
    Assume we have raw preset data. To create the escaped stream ready to send via COM 
    the following is done:
    -We read data in chuncks of 7 bytes, delete bit8 (MSB), and write them to our output stream
    -WE collect the original 7 MSB's from the just written 7 bytes, collect them to a new byte, and write that to output stream

    This DCXDecoder can encode a preset file("Save Set") from the DCX2496-remote program for COM communication
                    can decode a preset file received via COM so the DCX2496-remote program can read it    

'''
class DCXDataDecoder( ):
    def __init__(self):
        pass
    def encode(self,byte_array):
        out=bytearray()
        
        for stride in range(0,len(byte_array),7):#read data in groups of 7 bytes
            high_bits=0 #contains the high bits of the seven bytes before it
            for byte in range(7): #read seven bytes
                b=0
                if(stride+byte < len(byte_array)):#secure that last group of bytes is filled with zeroes, and last byte is hig_bit byte
                    b=byte_array[stride+byte]
                out.extend( (b&0x7F).to_bytes(1,byteorder="little")) #cut high bit and save byte
                high_bits= high_bits |(((b&0x80)>>7)<<byte) # extract high bit and transfer high bit to its position in high_byte 
        
            out.extend(high_bits.to_bytes(1,byteorder="little")) #append high_byte as the eight byte of this group
        return out

    def decode(self,byte_array,is_preset_file=True):
        out=bytearray()
        if(len(byte_array)%8 !=0):
            print("len not divisible by 8 - format does not match")
            return out
        for stride in range(0,len(byte_array),8):
            high_bits=byte_array[stride+7]
            for byte in range (7):
                
                b=byte_array[stride+byte] | ((high_bits&(1<<byte))>>byte) << 7
                out.extend(b.to_bytes(1,byteorder="little"))
        ##WARNING: HACK INCOMING
        if is_preset_file:
            out=out[:-6]    #We cannot recreate original file size because we have no len info, 
                            #and encoding makes data always divisible by eight. however, file size is fixed for preset files, so cut last 6 zero bytes, and call it a day
        ##END HACK
        print("decoded size: "+str(len(out)))
        return out



dcxdecoder=DCXDataDecoder()

##check encoding
genfile="30_WOHNZIMM.xpc"
gen=open(genfile,"rb")

encoded_file=open("ENCODED_"+genfile,"wb")
genb=bytearray(gen.read())

enc_bytes=dcxdecoder.encode(genb)

encoded_file.write(enc_bytes)

gen.close()
encoded_file.close()


##check decoding
encoded_file_from_dcx="READ_PRESET_WOHNZ_CLIPPED3.bin"
decoded_file= "DECODED_"+encoded_file_from_dcx

enc_dcx=open(encoded_file_from_dcx,"rb")
dec_dcx=open(decoded_file,"wb")

enc_dcx_bytes=bytearray(enc_dcx.read())

dec_bytes=dcxdecoder.decode(enc_dcx_bytes)

dec_dcx.write(dec_bytes)

enc_dcx.close()
dec_dcx.close()





