# https://www.udemy.com/python-programming-for-real-life-networking-use/learn/v4/overview

import random
import sys

def check_ip(ip_address):

    #Checking octets            
    a = ip_address.split('.')

    if (len(a) == 4) and (1 <= int(a[0]) <= 223) and (int(a[0]) != 127) and (int(a[0]) != 169 or int(a[1]) != 254) and (0 <= int(a[1]) <= 255 and 0 <= int(a[2]) <= 255 and 0 <= int(a[3]) <= 255):
        pass

    else:
        raise ValueError 
def check_mask(subnet_mask):

    masks = [255, 254, 252, 248, 240, 224, 192, 128, 0]
      
    #Checking octets            
    b = subnet_mask.split('.')
    
    if (len(b) == 4) and (int(b[0]) == 255) and (int(b[1]) in masks) and (int(b[2]) in masks) and (int(b[3]) in masks) and (int(b[0]) >= int(b[1]) >= int(b[2]) >= int(b[3])):
        pass
    else:
        raise ValueError
    
def convert_address_to_binary(subnet_mask):
    #Convert mask to binary string
    mask_octets_padded = []
    mask_octets_decimal = subnet_mask.split(".")
    
    for octet_index in range(0, len(mask_octets_decimal)):
        
        binary_octet = bin(int(mask_octets_decimal[octet_index])).split("b")[1]

        if len(binary_octet) == 8:
            mask_octets_padded.append(binary_octet)
        
        elif len(binary_octet) < 8:
            binary_octet_padded = binary_octet.zfill(8)
            mask_octets_padded.append(binary_octet_padded)
            
    decimal_mask = "".join(mask_octets_padded)
    return decimal_mask
    
def get_no_of_zeros(decimal_mask):
    return decimal_mask.count("0")

def get_no_of_ones(decimal_mask):
    return  32 - get_no_of_zeros(decimal_mask)

def get_nb_host(subnet_mask):
    try:
        check_mask(subnet_mask)
        decimal_mask=convert_address_to_binary(subnet_mask)
        no_of_zeros=get_no_of_zeros(decimal_mask)  
        no_of_ones=get_no_of_ones(decimal_mask)
        no_of_hosts = abs(2 ** no_of_zeros - 2) #return positive value for mask /32
          
        return no_of_hosts
        
    except ValueError:
        print("error subnet mask")

def get_wildcard_mask(subnet_mask):

    try:
        check_mask(subnet_mask)
        #Obtaining wildcard mask
        wildcard_octets = []
        mask_octets_decimal = subnet_mask.split(".")
        for w_octet in mask_octets_decimal:
            wild_octet = 255 - int(w_octet)
            wildcard_octets.append(str(wild_octet))
         
        wildcard_mask = ".".join(wildcard_octets)
        return wildcard_mask
        
    except ValueError:
        print("error subnet mask")
        
def get_network_address_binary_and_broadcast_address_binary(ip_address,subnet_mask):
    binary_ip=convert_address_to_binary(ip_address)
    
    decimal_mask = convert_address_to_binary(subnet_mask)
    no_of_zeros=get_no_of_zeros(decimal_mask)
    no_of_ones=get_no_of_ones(decimal_mask)
    
    network_address_binary = binary_ip[:(no_of_ones)] + "0" * no_of_zeros
    broadcast_address_binary = binary_ip[:(no_of_ones)] + "1" * no_of_zeros 
    
    return network_address_binary,broadcast_address_binary

def get_net_ip_address(network_address_binary):
    net_ip_octets = []
    for octet in range(0, len(network_address_binary), 8):
        net_ip_octet = network_address_binary[octet:octet+8]
        net_ip_octets.append(net_ip_octet)
    
    net_ip_address = []
    for each_octet in net_ip_octets:
        net_ip_address.append(str(int(each_octet, 2)))
    
    network_address = ".".join(net_ip_address)
    return net_ip_address

def get_bst_ip_address(broadcast_address_binary):
    bst_ip_octets = []
    for octet in range(0, len(broadcast_address_binary), 8):
        bst_ip_octet = broadcast_address_binary[octet:octet+8]
        bst_ip_octets.append(bst_ip_octet)
    
    bst_ip_address = []
    for each_octet in bst_ip_octets:
        bst_ip_address.append(str(int(each_octet, 2)))
    
    return bst_ip_address
        
def get_broadcast_address(ip_address,subnet_mask):

    #Obtain the network address and broadcast address from the binary strings obtained above
    check_ip(ip_address)
    check_mask(subnet_mask)

    
    network_address_binary,broadcast_address_binary=get_network_address_binary_and_broadcast_address_binary(ip_address,subnet_mask)
    
    
    bst_ip_address=get_bst_ip_address(broadcast_address_binary)
    
        
    broadcast_address = ".".join(bst_ip_address)
    return broadcast_address


            

def generate_random_ip_address_from_subnet(ip_address,subnet_mask):
#Part 4: Generation of random IP in subnet

    generated_ip = []
    network_address_binary,broadcast_address_binary=get_network_address_binary_and_broadcast_address_binary(ip_address,subnet_mask)
    bst_ip_address=get_bst_ip_address(broadcast_address_binary)
    net_ip_address=get_net_ip_address(network_address_binary)
    #Obtain available IP address in range, based on the difference between octets in broadcast address and network address
    for indexb, oct_bst in enumerate(bst_ip_address):
        for indexn, oct_net in enumerate(net_ip_address):
            if indexb == indexn:
                if oct_bst == oct_net:
                    #Add identical octets to the generated_ip list
                    generated_ip.append(oct_bst)
                else:
                    #Generate random number(s) from within octet intervals and append to the list
                    generated_ip.append(str(random.randint(int(oct_net), int(oct_bst))))
    
    #IP address generated from the subnet pool
    y_iaddr = ".".join(generated_ip)
    
    return y_iaddr
    

'''      
print(get_nb_host("255.255.255.0"))
print(get_no_of_ones("255.255.255.0"))
print(get_wildcard_mask("255.255.255.0"))
print(get_broadcast_address("1.1.1.1","255.255.255.0"))
print(generate_random_ip_address_from_subnet("1.1.1.1","255.255.255.0"))
'''
