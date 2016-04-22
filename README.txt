README
--------------------------------
--------------------------------

I implemented my own version of TCP on top of UDP. My programs ensure an in order delivery of uncorrupted packets through my implementation packet loss recovery and the check sum function. This delivery works irrespective of any delays or losses in the link (as tested through the program newudpl_1.4, available at http://www.cs.columbia.edu/~hgs/research/projects/newudpl/newudpl-1.4/)


Sample Run *****

In order to run my code, I input the following commands on separate tabs in my localhost for the link emulator, sender and receiver respectively:

  LINK EMULATOR: $ ./newudpl -vv -oathens:4000 -iathens:* [FLAGS]

  FLAGS: I used the flags -O50 , -B50 , -d0.8 , -L10 . I recommend using these flags given the MSS and file size (69 packets
          each with a payload of 556 bytes maximum + 20 byte header)

  RECEIVER: $ python receiver.py received_file.txt 4000 athens 4001 stdout

            $ receiver.py [receiving_filename] [listening_port] [sender_IP] [sender_port] [log_filename]

  SENDER: $ python sender.py original_file.txt athens 41192 4001 stdout 1

          $ sender.py [sending_filename] [remote_IP] [remote_port] [ack_port] [log_filename] [window_size]

  VERIFY FILE TRANSMISSION WITH $ diff [sending_filename] [receiving_filename]



A) The TCP Segment Structure

  I used the Standard TCP Header to pack and unpack the payload of my packets. In other words, all my packets had 20 Byte headers that represented the packet's source port(2 bytes), destination port(2 bytes), sequence number(4 bytes), acknowledgement number(4 bytes), header size (1 byte), flags (1 byte), window size (2 bytes), checksum (2 bytes), urgent pointer (2 bytes)

B) The states typically visited by a sender and receiver

  I am unsure what to specify in this section, I shall provide an overview of the functioning of my program. Please execute the scripts as specified in the sample run IN THE SPECIFIED ORDER FROM TOP TO BOTTOM. My code works by first having both the sender and receiver setting up the receiving and destination sockets, as well as setting up other descriptors like log files and the original file which will be reconstructed from the packets sent by the sender to the receiver. Sender then divyyies the original file into segments and stores them in a tuple (or array) from which it will send later on. It then uses the UDP sockets to send them to the receiving side, only moving on to the next ones when an ack sent from the receiving side has been received. Once all the packets are sent, the sending side receives the statistics of the code (as specified in the original assignment)

C) Loss Recovery mechanism

  Each packet has its own timer (whose timeout limit is always updated through the TCP estimated RTT formulas, regardless if the packet gets acked or not). If an ack is received within the timeout window, its reception is logged at the sending side and prompts the next packets to be sent. However if an ACK is not received in the timeout window, my code calls the method send_packet_w_acks yet again to repeat this process.

D) Potential Bugs

  I checked my code in my local machine and the clic lab, however I am unsure whether my code works with IPv6 addresses. Beyond that the code should work as expected. Please make sure to follow the instructions that I wrote for the sample run to make sure you are running the code appropriately.

