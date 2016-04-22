import socket,sys,struct

# Declaring global variables
header_size = 5
Max_payload = 556
header_format = 'HHIIBBHHH'

def make_segment(source_port,destination_port,sequence_num,ack_num, ack, final,  window_size, payload):

  checksum = checksum_function(source_port,destination_port,sequence_num,ack_num,final,ack,payload)

  # add padding to payload if the payload has less than the Max_payload as data
  #padded_payload = payload + (' '*(Max_payload - len(payload)))

  if final:
    flags = 1
  else:
    flags = 0

  if ack:
    flags += 16

  #make segment and return it
  #print("packing checksum: " + str(checksum))
  header = struct.pack(header_format,source_port,destination_port,sequence_num,ack_num,header_size,flags, window_size, checksum, 0)
  segment = header + payload
  return segment

def unpack_segment(segment):
  header = segment[:20]
  #print(len(header))
  #print header

  source_port, destination_port, sequence_number, ack_number, header_size, flags, window_size, checksum, urgent  = struct.unpack(header_format,header)
  #print("unpacking checksum:" + str(checksum))
  ack = 0
  final = 0

  if ((flags >> 4) == 1):
    ack = 1
  else:
    ack = 0

  if (int(flags % 2 == 1)):
    final =  1
  else:
    final = 0

  payload = segment[20:]

  return source_port, destination_port, sequence_number, \
  ack_number, header_size, final, ack, checksum, \
  payload

# checksum not being computed according to the algorithm
def checksum_function(source_p,dest_p,seq_n,ack_n,final_f,ack_f,payl):
  entire_segment = str(source_p) + str(dest_p) + str(seq_n) + str(ack_n) \
  + str(header_size) + str(final_f) + str(ack_f) + payl

  total_sum = 0
  for i in range((0), len(entire_segment) - 1, 2):
    #compute the sum with the byte value of each pair
    current_sum = ord(entire_segment[i]) + (ord(entire_segment[i+1]) << 8)
    #totalling the sum and wrapping around
    total_sum = ((total_sum + current_sum) & 0xffff) + ((total_sum + current_sum) >> 16)
  #print entire_segment
  #print("computed checksum: " + str(total_sum))
  return total_sum