from pyvisa import ResourceManager


gpib_addr = 22
rm = ResourceManager('@py')
dev = rm.open_resource('GPIB0::{:d}::INSTR'.format(gpib_addr))

dev.write('*RST')
dev.write("FUNC 'CURR'")
dev.write("SYST:ZCH ON")            # Enable zero check
dev.write("CURR:RANG 2E-9")              # Set range to 2nA
# Wait for user to verify open connection
input("Remove probes from DUT to perform zero-correction, "
      "then press Enter to continue.")
dev.write("INIT")                   # Start measurement for zero correction
dev.write("SYST:ZCOR:STAT OFF")     # Disable zero correction
dev.write("SYST:ZCOR:ACQ")          # Use previous reading for zero correction
dev.write("SYST:ZCOR ON")           # Perform zero correction
dev.write("CURR:RANG:AUTO ON")      # Enable auto range
dev.write("SYST:ZCH OFF")           # Disable zero checking
print("Calibration complete")
