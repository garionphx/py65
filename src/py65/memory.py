# this sparse array module only needed for large-memory CPU models
try:
    from blist import *
except ImportError:
    pass

class ObservableMemory:
    def __init__(self, subject=None, addrWidth=16):
        if subject is None:
            if addrWidth <= 16:
                subject = 0x10000 * [0x00]
            else:
                try:
                    subject = blist([0]) * (1 << addrWidth)
                except:
                    print "Fatal: failed to initialise large memory for this CPU"
                    exit (1)

        self._subject = subject

        self._read_subscribers  = {}
        self._write_subscribers = {}        

    def __setitem__(self, address, value):
        callbacks = self._write_subscribers.get(address, [])

        for callback in callbacks:
            result = callback(address, value)
            if result is not None:
                value = result

        self._subject[address] = value
        
    def __getitem__(self, address):
        callbacks = self._read_subscribers.get(address, [])
        final_result = None

        for callback in callbacks:
            result = callback(address)
            if result is not None:
                final_result = result

        if final_result is None:
            return self._subject[address]
        else:
            return final_result
    
    def __getattr__(self, attribute):
        return getattr(self._subject, attribute)

    def subscribe_to_write(self, address_range, callback):
        for address in address_range:
            callbacks = self._write_subscribers.setdefault(address, [])
            if callback not in callbacks:
                callbacks.append(callback)

    def subscribe_to_read(self, address_range, callback): 
        for address in address_range:
            callbacks = self._read_subscribers.setdefault(address, [])
            if callback not in callbacks:
                callbacks.append(callback)

    def write(self, start_address, bytes):
        self._subject[start_address:start_address+len(bytes)] = bytes
