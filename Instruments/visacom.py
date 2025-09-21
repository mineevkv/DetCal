import logging
import time
import pyvisa

from System.logger import get_logger
logger = get_logger(__name__)

class VisaCom():
    def __init__(self):
        self.instr = None
        

    def send(self, command):
        """
            Send SCPI command to the instrument

            Does not work with response in binary (use query_binary_values instead)
        """

        try:     
            if "?" in command:
                response = self.instr.query(command).strip() # return ASCII string
                command_type = 'QUERY'        
            else:
                response = f"bytes written: {self.instr.write(command)}" # return INT (number of bytes written)
                command_type = 'WRITE'
            
            logger.info(f"{self.instr} sending {command_type} command >> {command} -> {response}")
            return response
            
        except pyvisa.errors.VisaIOError as e:
            logger.error(f"Error communicating with instrument: {e}")
            return

    @staticmethod
    def get_visa_string_ip(ip):
        """
            Create VISA string for LAN connection
        """
        return f'TCPIP0::{ip}::INSTR'

    @staticmethod
    def get_visa_resource(visa_string, alternative=False):
        """
        Check connect to remote instrument
        """
        if 'TCPIP' or 'USB' in visa_string:
            interface = visa_string.split('::')[0]
        else:
            logger.error("Invalid VISA string format")
            return

        try:
            # Create a resource manager
            rm = pyvisa.ResourceManager()
            
            try:
                logger.info(f"Trying to connect to: {interface}")
                
                inst = rm.open_resource(visa_string)
                logger.info(f'{inst}')
                inst.timeout = 5000  # 5-second timeout
                inst.read_termination = '\n'  # Common termination characters
                inst.write_termination = '\n'
                
                time.sleep(0.1)
                
                idn = inst.query('*IDN?').strip()
                logger.info(f"Instrument identified as: {idn}")
                
                return inst
                
            except pyvisa.errors.VisaIOError as e:
                logger.error(f"Error communicating with {interface}: {e}")
                if alternative:
                    logger.info("Trying alternative termination characters...")
                    
                    # Try different termination characters
                    for read_term, write_term in [('\r\n', '\r\n'), ('\r', '\r'), ('\n', '\n')]: # \r\n - Windows standard, \r - old \n - modern instruments
                        try:
                            if 'inst' in locals():
                                inst.close()
                            
                            inst = rm.open_resource(visa_string)
                            inst.timeout = 5000
                            inst.read_termination = read_term
                            inst.write_termination = write_term
                            
                            time.sleep(0.1)
                            idn = inst.query('*IDN?').strip()
                            logger.info(f"Success with termination {repr(read_term)}/{repr(write_term)}: {idn}")
                            return inst
                            
                        except pyvisa.errors.VisaIOError:
                            logger.error(f"All termination character combinations failed for {interface}")
                            raise
                        
            except Exception as e:
                logger.error(f"Unexpected error with {interface}: {e}")
                raise
        
        except Exception as e:
            logger.error(f"Failed to initialize resource manager: {e}") 
            logger.warning("Could not identify any instruments")
            raise