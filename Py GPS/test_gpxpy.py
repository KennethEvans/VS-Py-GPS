import xml.etree.ElementTree as ET
import tempfile

def test(file_name):
        ET.register_namespace('', "http://www.topografix.com/GPX/1/1")
        #ET.register_namespace('tpex', "http://www.garmin.com/xmlschemas/TrackPointExtension/v2")
        print(f'Reading {file_name}')
        tree = ET.parse(file_name)
        if True:
            temp = tempfile.NamedTemporaryFile(prefix='PyGPS-')
            print(f'Writing {temp.name}')
            tree.write(temp)
            temp.close()
        else:
            default_out_name = 'C:/Users/evans/AppData/Local/Temp/TestPyGpx.gpx'
            print(f'Writing {default_out_name}')
            tree.write(default_out_name)

        # Get a string representation
        root = tree.getroot();
        xml = ET.tostring(root, encoding='unicode');
        print(xml[0:128])
    
def main():
    default_file_name = 'C:/Users/evans/Documents/GPSLink/Polar/Kenneth_Evans_2021-12-12_13-21-52_Walking_Rehab.gpx'
    test(default_file_name)

if __name__ == "__main__":
    main()

