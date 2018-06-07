import smbus
from time import *
 
class I2C_device:
 
   def __init__(self, addr, port=1):
      self.addr = addr
      self.bus = smbus.SMBus(port)
 
   # Read a single byte
   def read(self):
      return self.bus.read_byte(self.addr)
 
   # Read cmd
   def read_data(self, cmd):
      return self.bus.read_byte_data(self.addr, cmd)
 
   # Read a block of data
   def read_block_data(self, cmd):
      return self.bus.read_block_data(self.addr, cmd)
 
   # Write a single command
   def write_cmd(self, cmd):
      self.bus.write_byte(self.addr, cmd)
      sleep(0.01)
 
   # Write a command and argument
   def write_cmd_arg(self, cmd, data):
      self.bus.write_byte_data(self.addr, cmd, data)
      sleep(0.01)
 
   # Write a block of data
   def write_block_data(self, cmd, data):
      self.bus.write_block_data(self.addr, cmd, data)
      sleep(0.01)
