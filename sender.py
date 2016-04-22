import socket, sys, segments,struct,threading, datetime,time


# Initializing Global Variables ------------------
segment_buffer = []
Max_payload = 556
sequence_number = 0

timeout_limit = 0.5
rtt_deviation = 0
estimated_RTT = 0.5

sending_filename = ""
remote_IP = ""
remote_port = 0
ack_port = 0
log_filename = ""
window_size = 0


retransmitted_segments = 0
segments_sent = 0

# Helper Methods --------------------

def send_packet_w_acks(send_socket, ack_socket, current_seg):
  send_socket.sendto(current_seg,(remote_IP, remote_port))
  send_date_time = datetime.datetime.now()
  send_time = time.time()

  #unpack for log
  packet_source_port, packet_destination_port,packet_seq_number, packet_ack_number, packet_header_size, packet_final, packet_ack, packet_checksum, packet_payload = segments.unpack_segment(current_seg)

  log_file_descriptor.write(str(send_date_time) + " | source port: " + str(packet_source_port) + " | destination port: " + str(packet_destination_port) + " | sequence number: " + str(packet_seq_number) + " | ack number: " + str(packet_ack_number) + " | " + "ACK: 0 | FIN: " + str(packet_final) + " SENT\n")

  global retransmitted_segments, segments_sent, timeout_limit, rtt_deviation, estimated_RTT


  try:
    ack_socket.settimeout(timeout_limit)
    ack_number = ack_socket.recv(16)

    ack_reception_date_time = datetime.datetime.now()
    ack_reception_time = time.time()

    #update timeout limit
    sampleRTT = ack_reception_time - send_time
    estimated_RTT = estimated_RTT*(0.875) + sampleRTT*(0.125)
    rtt_deviation = 0.75*(rtt_deviation) + 0.25*abs(sampleRTT - estimated_RTT)
    timeout_limit = estimated_RTT + 4*rtt_deviation

    #segments sent
    segments_sent += 1
    #log if correct
    log_file_descriptor.write(str(ack_reception_date_time) + " | source port: " + str(packet_source_port) + " | destination port: " + str(packet_destination_port) + " | sequence number: " + str(packet_seq_number) + " | ack number: " + str(ack_number) + " | " + "ACK: 1 | FIN: " + str(packet_final) + " RECEIVED\n")

  except socket.timeout:
    #print("timeout interval" + str(timeout_limit))
    log_file_descriptor.write(" source port: " + str(packet_source_port) + " | destination port: " + str(packet_destination_port) + " | sequence number: " + str(packet_seq_number) + " | ack number: " + str(packet_ack_number) + " | " + "ACK: 0 | FIN: " + str(packet_final) + "| PACKET DELIVERY WAS UNSUCCESFUL \n")
    #print(str(retransmitted_segments))

    #retransmitted segments
    retransmitted_segments += 1
    segments_sent += 1
    send_packet_w_acks(send_socket, ack_socket, current_seg)

def build_segment_buffer(sending_fd):

  sequence_number = 0
  expected_ACK_number = 0

  #print("reading the junglebook --------")
  current_payload = sending_fd.read(Max_payload)

  #loop until you everything is read
  while len(current_payload) > 0:


    #FIN
    if(len(current_payload) < Max_payload):
      current_segment = segments.make_segment(ack_port,remote_port,sequence_number,expected_ACK_number,0,1,window_size,current_payload)
      segment_buffer.append(current_segment)

    else:
      current_segment = segments.make_segment(ack_port,remote_port,sequence_number,expected_ACK_number,0,0,window_size,current_payload)
      segment_buffer.append(current_segment)


    current_payload = sending_fd.read(Max_payload)
    sequence_number += 1
    expected_ACK_number += 1

  #print("finished reading the junglebook")

# Main Method --------------------------------


# Reading Command line arguments--------------------
try:
  sending_filename = sys.argv[1]
  remote_IP = socket.gethostbyname(sys.argv[2])
  remote_port = int(sys.argv[3])
  ack_port = int(sys.argv[4])
  log_filename = sys.argv[5]
  window_size = int(sys.argv[6])


except IndexError, TypeError:
  exit("Please type: $ sender.py [sending_filename] [remote_IP] [remote_port] [ack_port] [log_filename] [window_size]")

  print sending_filename + ", " + remote_IP + ", " + str(remote_IP) + ", " + str(ack_port) + ", " + log_filename + ", " + str(window_size) + " ."



try:
  # Setting up sockets and files----------------------

  #UDP sockets for packet delivery
  sending_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

  #UDP socket for receiving ACK's
  ack_ip = socket.gethostname()
  ack_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
  ack_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
  ack_socket.bind((ack_ip , ack_port))

  #read channel for the sendfile
  try:
    sending_file_descriptor = open(sending_filename,'r')
  except IOError:
    print(sending_filename + " was not found.")
    ack_socket.close()
    sending_socket.close()
    sys.exit()

  #Write channel for the logfile
  if log_filename == "stdout":
    log_file_descriptor = sys.stdout
  else:
    try:
      log_file_descriptor = open(log_filename,'w')
    except IOError:
      print(log_filename + " was not found.")
      ack_socket.close()
      sending_socket.close()
      sys.exit()


  # Read the file to populate the segment Buffer ------------

  build_segment_buffer(sending_file_descriptor)


  while(sequence_number < len(segment_buffer)):
    #print(str(sequence_number) + ":" + str(len(segment_buffer)))
    send_packet_w_acks(sending_socket,ack_socket, segment_buffer[sequence_number])
    #print("packet " + str(sequence_number) +  "got sent" )
    sequence_number += 1
  print("")
  print("Delivery was completed succesfully --------------------")
  print("Estimated RTT = " + str(estimated_RTT)) + " seconds"
  print("Total bytes sent = " + str(segments_sent*576))
  print("Segments sent = " + str(segments_sent))
  print("Retransmitted Segments = ") + str(retransmitted_segments)
  percentage_of_retransmitted_segments = (float(retransmitted_segments) / segments_sent)*100
  print("Segments retransmitted = " + str(percentage_of_retransmitted_segments) + "%")



except KeyboardInterrupt:
    print " , CTRL + C command issued, sender socket closing ----------"
    ack_socket.close()
    sending_socket.close()
    sys.exit()