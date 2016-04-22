import socket, sys, segments,struct,datetime

# Initializing Global Variables ------------------
Max_payload_size = 556

# Reading Command line arguments---------------------------------
try:
  receiving_filename = sys.argv[1]
  listening_port = int(sys.argv[2])
  sender_IP = socket.gethostbyname(sys.argv[3])
  sender_port = int(sys.argv[4])
  log_filename = sys.argv[5]

except IndexError, TypeError:
  exit("Please type: $ receiver.py [receiving_filename] [listening_port] [sender_IP] [sender_port] [log_filename] ")

  print receiving_filename + ", " + listening_port + ", " + str(sender_IP) + ", " + str(sender_port) + ", " + log_filename + ". "


# Main Method---------------------------------------
try:

# Setting up sockets and files----------------------

  #UDP socket to receive packets
  receiving_ip = socket.gethostname()
  receiving_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
  receiving_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR,1)
  receiving_socket.bind((receiving_ip, listening_port))


  #udp socket for acknowledgements, bind when handshaking is finished
  ack_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
  ack_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR,1)


  # write channel to rebuild file
  try:
    receiving_file_descriptor = open(receiving_filename, 'w')
  except IOError:
    print(receiving_filename + " was not found.")
    ack_socket.close()
    sending_socket.close()
    sys.exit()

  # write channel for the logfile
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



  # sequence of packets expected
  expected_seq_number = 0

  while True:
      try:
        packet, addr = receiving_socket.recvfrom(576)

        if packet:

          #unpack packet
          packet_source_port, packet_destination_port,packet_seq_number, packet_ack_number, packet_header_size, packet_final, packet_ack, packet_checksum, packet_payload = segments.unpack_segment(packet)


          #check if packet is corrupt by checking checksum
          #strip null chars, fin doesnt have the correct checksum ---------------
          if(str(packet_checksum).rstrip(' \t\r\n\0') == str(segments.checksum_function(packet_source_port, packet_destination_port, packet_seq_number, packet_ack_number, packet_final, packet_ack, packet_payload)).rstrip(' \t\r\n\0')):

            if(packet_seq_number == expected_seq_number):

              #log packet, write data to receiving file
              #timestamp, source, destination, Sequence #, ACK #, and the flags
              if packet_final:
                receiving_file_descriptor.write(packet_payload.rstrip(' \t\r\n\0'))
                time_of_reception = datetime.datetime.now()
                log_file_descriptor.write(str(time_of_reception) + " | source port: " + str(packet_source_port) + " | destination port: " + str(packet_destination_port) + " | sequence number: " + str(packet_seq_number) + " | ack number: " + str(packet_ack_number) + " | " + "ACK: 0 | FIN: " + str(packet_final) + " RECEIVED\n")

                #print("final packet")
              else:
                receiving_file_descriptor.write(packet_payload)
                time_of_reception = datetime.datetime.now()
                log_file_descriptor.write(str(time_of_reception) + " | source port: " + str(packet_source_port) + " | destination port: " + str(packet_destination_port) + " | sequence number: " + str(packet_seq_number) + " | ack number: " + str(packet_ack_number) + " | " + "ACK: 0 | FIN: " + str(packet_final) + " RECEIVED\n")
              #print(packet_payload)

              #ack the pocket
              log_file_descriptor.write(str(time_of_reception) + " | source port: " + str(packet_source_port) + " | destination port: " + str(packet_destination_port) + " | sequence number: " + str(packet_seq_number) + " | ack number: " + str(packet_ack_number) + " | " + "ACK: 1 | FIN: " + str(packet_final) + " ACK SENT\n")
              expected_seq_number += 1
              ack_socket.sendto(str(packet_ack_number),(sender_IP,sender_port))


      except KeyboardInterrupt:
        receiving_socket.close()
        sys.exit()

  print "exited inner loop"

except KeyboardInterrupt:
  print " , CTRL + C command issued, sender socket closing ----------"
  receiving_socket.close()
  ack_socket.close()
  sys.exit()
