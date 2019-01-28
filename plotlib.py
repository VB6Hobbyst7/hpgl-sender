import serial
import serial.tools.list_ports

def list_serial_ports():
    return serial.tools.list_ports.comports()

def plot(port, baud_rate, file):
    plotter = serial.Serial(port, baud_rate, xonxoff=False, rtscts=True, dsrdtr=False)
    success, file_content, etags = file.load_contents()
    if not success:
        raise RuntimeError('Could not read contents of input file')
    plotter.write(file_content)
    plotter.close()
