import smbus

LCD_SET_DDRAM_ADDR = 0x80

class I2cLcd:
  i2c = ""
  address = ""
  register_setting = 0x00
  register_display = 0x40
  col_num = 16

  def __init__(self, bus_num, address):
    self.address = address
    self.i2c = smbus.SMBus(bus_num)
    # init
    self.i2c.write_i2c_block_data( self.address, self.register_setting, [0x38, 0x39, 0x14, 0x70, 0x56, 0x6c] )
    self.i2c.write_i2c_block_data( self.address, self.register_setting, [0x38, 0x0c, 0x01] )

  def setCursor(self, col, row):
    row_offset = [ 0x00, 0x40 ]
    self.i2c.write_byte_data( self.address, self.register_setting, LCD_SET_DDRAM_ADDR | (col + row_offset[row]) )

  def write(self, str):
    counter = 0
    for c in list(str):
      self.i2c.write_byte_data( self.address, self.register_display, ord(c) )
      counter += 1
      if counter >= self.col_num:
        break
