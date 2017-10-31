import sys
import os

alphabet = [
"""
   
   
   
   
   
""",
"""
 ###
 ###
 ## 
    
 ## 
""",
""" 
 # #
    
    
    
    
""",
"""
  ##  ## 
 ########
  ##  ## 
 ########
  ##  ## 
""",
"""    
   ####
  # #  
   ##  
   # # 
 ####  
""",
"""      
 ##   #  
#  # #   
 ## # ## 
   # #  #
  #   ## 
""",
"""
 ####   
#    #  
 ## #  #
#    #  
 ###  # 
""",
"""
 #
  
  
  
  
""",
"""
   #
 #  
 #  
 #  
   #
""",
"""
 #  
   #
   #
   #
 #  
""",
"""
      
 # # #
  ### 
 # # #
      
""",
"""
       
   ##  
 ######
   ##  
       
""",
"""
    
    
    
  ##
 ## 
""",
"""
     
     
 ### 
     
     
""",
"""
   
   
   
   
 ##
""",
"""   
     #
    # 
   #  
  #   
 #    
""",
"""   
  ### 
 #  ##
 # # #
 ##  #
  ### 
""",
"""   
  ##  
 # #  
   #  
   #  
 #####
""",
"""
  ### 
 #   #
    # 
  #   
 #####
""",
"""
  ### 
 #   #
   ## 
 #   #
  ### 
""",
"""
 #   #
 #   #
 #####
     #
     #
""",
"""
 #####
 #    
 #####
     #
 #####
 """,
 """
 #####
 #    
 #####
 #   #
 #####
 """ ,
 """  
 #####
     #
    # 
   #  
  #   
 """,
 """  
 #####
 #   #
 #####
 #   #
 #####
 """ ,
 """
 #####
 #   #
 #####
     #
     #
 """,
"""
   
 ##
   
 ##
   
""",
"""
   
 ##
   
 ##
 # 
""",
"""   
     #
   #  
 #    
   #  
     #
""",
"""
      
 #####
      
 #####
      
""",
"""
 #    
   #  
     #
   #  
 #    
""",
"""
  ### 
 #   #
    # 
      
   #  
""",
"""
   #####  
  # ##  # 
 # #  #  #
  # ## ## 
   #####  
""",
"""
  ### 
 #   #
 #####
 #   #
 #   #
""",
"""
 #### 
 #   #
 #### 
 #   #
 #### 
""",
"""
  ####
 #    
 #    
 #    
  ####
"""    ,
"""
 ####  
 #    #
 #    #
 #    #
 ####  
""",
"""  
 ####
 #   
 ####
 #   
 ####
""",
"""  
 ####
 #   
 ####
 #   
 #   
""",
"""
  ####
 #    
 # ###
 #   #
  ####
""",
"""
 #   #
 #   #
 #####
 #   #
 #   #
""",
"""
 ###
  # 
  # 
  # 
 ###
""",
"""
  #####
    #  
    #  
 #  #  
  ###  
""",
"""
 #   #
 # #  
 ##   
 # #  
 #   #
""",
"""
 #    
 #    
 #    
 #    
 #####
""",
""" 
 ##    ##
 # #  # #
 #  ##  #
 #      #
 #      #
""",
"""
 #     #
 # #   #
 #  #  #
 #   # #
 #     #
""",
"""
  #### 
 #    #
 #    #
 #    #
  #### 
""",
"""
 #### 
 #   #
 #### 
 #    
 #    
""",
"""
  ####  
 #    # 
 #    # 
 #   ## 
  #### #
""",
"""
 ##### 
 #    #
 # ### 
 #   # 
 #    #
""",
"""
  ###
 #   
  ## 
    #
 ### 
""",
"""
 #####
   #  
   #  
   #  
   #  
""",
"""
 #    #
 #    #
 #    #
 #    #
  #### 
""",
"""
 #      #
 #      #
  #    # 
   #  #  
    ##   
""",
"""
 #       #
 #       #
 #   #   #
  # # # # 
   #   #  
""",
"""
 #   #
  # # 
   #  
  # # 
 #   #
""",
"""
 #   #
  # # 
   #  
   #  
   #  
""",
"""
 #####
    # 
   #  
  #   
 #####
""",
"""
 ###
 #  
 #  
 #  
 ###
""",
"""
 #    
  #   
   #  
    # 
     #
""",
"""
 ###
   #
   #
   #
 ###
""",
"""
   #  
 #   #
      
      
      
""",
"""
     
     
     
     
 ####
""",
"""
  ##
    
    
    
    
""",
"","","","","","","","","","","","","",
"","","","","","","","","","","","","",
 """
   ##
  #  
 ##  
  #  
   ##
 """,
 """
  #
  #
  #
  #
  #
 """,
 """
 ##  
   # 
   ##
   # 
 ##  
 """,
 """
          
  ###     
 #   #   #
      ### 
          
 """,
 """
 #######
 # # # #
 #  #  #
 # # # #
 #######
 """
]

def _getTerminalSize():
    env = os.environ
    def ioctl_GWINSZ(fd):
        try:
            import fcntl, termios, struct, os
            cr = struct.unpack('hh', fcntl.ioctl(fd, termios.TIOCGWINSZ,
        '1234'))
        except:
            return
        return cr
    cr = ioctl_GWINSZ(0) or ioctl_GWINSZ(1) or ioctl_GWINSZ(2)
    if not cr:
        try:
            fd = os.open(os.ctermid(), os.O_RDONLY)
            cr = ioctl_GWINSZ(fd)
            os.close(fd)
        except:
            pass
    if not cr:
        cr = (env.get('LINES', 25), env.get('COLUMNS', 100))

    return int(cr[0]), int(cr[1])

class ShoutOut():

  def __init__(self, letters="", token="#"):
    self.letters = letters
    self.token = token

  def __str__(self):
    return self.__repr__()

  def __repr__(self):
    return self.loudify(self.letters)

  def change_to(self, new_token):
    self.token = new_token

  def loud(self, letters):
    return self.loudify(letters)

  def loudify(self, letters):
    width = _getTerminalSize()[1]
    global alphabet
    arr_line = []
    arr = []
    special_tokens = [10]
    for ch in str(letters).upper():
      # print "[" + ch + "]" + str(ord(ch))
      if ord(ch) in special_tokens:
        # do special
        if ord(ch) == 10: # new line
          arr_line.append(arr)
          arr = list()
        elif ord(ch) == 11:
          pass
        continue  

      idx = ord(ch)-ord(' ')
      try:
        arr.append(alphabet[idx])
      except Exception as e:
        arr.append(alphabet[-1])
      if len(arr) * 9 > width:
          arr_line.append(arr)
          arr = list()
    arr_line.append(arr)
      # arr = list()

    aa_line = []
    aa = []
    for line in arr_line:
      for _ in line:
        aa.append(_.split("\n"))
      aa_line.append(aa)
      aa = list()

    contents = ""
    for aa in aa_line:
      content = ""
      if self.token == "#":
        for ll in (zip(*aa)):
          content += " ".join(ll) + "\n"
      else:
        for ll in (zip(*aa)):
          content += " ".join(ll).replace("#", self.token) + "\n"
      contents += content
    return contents

shoutout = ShoutOut()
def loud(letters):
  return shoutout.loud(letters)

def change_to(token):
  shoutout.change_to(token)


if __name__ == "__main__":
  loud(sys.argv[1])

