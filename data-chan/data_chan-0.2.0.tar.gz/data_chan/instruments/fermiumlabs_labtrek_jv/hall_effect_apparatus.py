import data_chan
import struct
from cffi import FFI
dchan = data_chan.init()

# the current correction values can be specified
#a = 0.008019432
#b = 0.9397528

a = 0.0
b = 1.0

ffi = FFI()

def init():
    """Initialize data-chan"""
    return dchan.datachan_init()

def acquire(vid,pid):
    """acquires a device given USB VID and PID"""
    
    scan = dchan.datachan_device_acquire(vid,pid)
    
    if scan.result is 0xFF:
        return scan
    
    elif scan.result is 0x04:
      class DataChanDeviceUknownError(Exception):
        pass
      raise DataChanDeviceUknownError("Data-chan acquire returned 0x04, meaning the device is uknown")
    
    elif scan.result is 0x03:
      raise MemoryError("Data-chan acquire returned 0x03, meaning it failed to malloc()")
    
    elif scan is 0x02:
      class DataChanDeviceCannotClaimError(Exception):
        pass
      raise DataChanDeviceCannotClaimError("Data-chan acquire returned 0x02, meaning it could not claim the device, but found it")
    
    elif scan.result is 0x01:
      class DataChanDeviceNotFoundOrInaccessibleError(Exception):
        pass
      raise DataChanDeviceNotFoundOrInaccessibleError("Data-chan acquire returned 0x01, meaning it did not found the device of given VID/PID. Could also be a permission problem on Unix/Linux ")  
    
    elif scan.result is 0x00:
      class DataChanUninitializedError(Exception):
        pass
      raise DataChanUninitializedError("Data-chan was not initialized.")  
    
    else:
      return scan
      
def enable(scan):
    """enable measurements in the data-chan device"""
    return dchan.datachan_device_enable(scan.device)

def queue_size(scan):
    """returns the number of measures in the host queue, ready to be popped"""
    return dchan.datachan_device_enqueued_measures(scan.device)

def pop_measure(scan):
    """pop and returns one measure"""
    d = None
    if(queue_size(scan)):
        measure = dchan.datachan_device_dequeue_measure(scan.device)
        if(measure != ffi.NULL):
            d = { 'ch'+str(measure.channels[i]) : measure.values[i] for i in range(len(measure.channels)) }
            d['time']=measure.time*1000+measure.millis
            dchan.datachan_clean_measure(measure)
    return d

def set_current_lockin(scan,current):
    """set the current generator in lock-in (AC) mode given the absolute value of a current"""
    d = struct.pack('ff'*1, *[a-float(current)/b,a+float(current)/b])
    dchan.datachan_send_async_command(scan.device,0x01,d,len(d))

def set_current_fixed(scan,current):
    """set the current generator in CC mode given a current"""
    d = struct.pack('f'*1, *[float(current)])
    dchan.datachan_send_async_command(scan.device,0x02,d,len(d))

def set_current_raw(scan,current):
    """set the current generator in CC mode given the raw DAC value. To be used only for testing"""
    d = struct.pack('H'*1, *[int(current)])
    dchan.datachan_send_async_command(scan.device,0x03,d,len(d))

def set_heater_state(scan,power):
    """set the heater given an input value from 0 to 255"""
    if int(power) < 0 or int(power) > 255:
        raise ValueError("The heater power needs to be between 0 and 255")
    d = struct.pack('B'*len([int(power)]), *[int(power)])
    dchan.datachan_send_async_command(scan.device,0x04,d,len(d))

def set_channel_gain(scan,channel,gain):
    """set the gain for the specified channel"""
    d = struct.pack('BB'*1, *[channel,int(gain)])
    dchan.datachan_send_async_command(scan.device,0x05,d,len(d))

def reset_device(scan):
    """reset the device"""
    d = struct.pack('B'*len([0]), *[0])
    dchan.datachan_send_async_command(scan.device,0x06,d,len(d))

def disconnect_device(scan):
    """disconnect the device and releases it from data-chan's usb control"""
    dchan.datachan_device_release(scan.device)

def shutdown_device():
    """soft device shutdown"""
    dchan.datachan_shutdown()
