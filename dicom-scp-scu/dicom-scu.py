import matplotlib.pyplot as plt
from dataclasses import dataclass
from pynetdicom import AE
from pydicom import dcmread

CONTEXT = '1.2.840.10008.1.1'

@dataclass
class Modality:
    addr: str
    port: int
    ae_title: str

class Association:
    def __init__(self, modality, context):
        self.modality = modality
        self.context = context

    def __enter__(self):
        ae = AE()
        ae.add_requested_context(self.context)
        self._association = ae.associate(**vars(self.modality))
        return self._association

    def __exit__(self, *args):
        self._association.release()
        self._association = None

def import_dicom_file(path):
    ds = dcmread(path)
    return ds

    

if __name__ == '__main__':
    modality = Modality('127.0.0.1', 11112, 'DISCOVERY')

    with Association(modality, CONTEXT) as assoc:
        resp = assoc.send_c_echo()
        print(f'Modality responded with status (C_ECHO): {resp.Status}')
    
    ds = import_dicom_file('./img/case1_010.dcm')
    arr = ds.pixel_array
    plt.imshow(arr, cmap='gray')
    plt.show()