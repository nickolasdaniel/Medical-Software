# Notes regarding **DICOM PROTOCOL** and **ORTHANC SERVER/LISTENER**

## What is *DICOM* ?
 
**DICOM** stands for *Digital Imaging and Communications in Medicine* and is the standard protocol for the communication and management of medical imaging information and related data. 

### It can be split in 2 parts:
-  File format
-  Network protocol

The file format is similar to popular formats such as *JPEG*, *PNG* etc. The DICOM file is responsible for encoding the medical images (through the so-called **pixel data**), as well as embedding medical data. 

The medical data in a DICOM file is encoded as a *key-value associative array*. Each key is called **DICOM tag** and each value can itself be a list of data sets (**sequence**) which resembles well-known formats such as *XML* and *JSON*.

The so called standard **DICOM tags** are normalized by an official dictionary, each tag being identified by two 16-bit hex numbers. The naming convention is camel case (*PatientName*, *StudyDescription*). This standard associates the tag with a data type (string, date, float...) also known as **value representation** (of the hex format).

The DICOM file format also specifies the set of DICOM tags that are mandatory or optional for each kind of imaging modality (CT, MR, NM, CBCT, PET...). This is called **storage service-object pair** (storage SOP).

Ranks of tags:
- Type 1 -> Mandatory
- Type 2 -> Mandatory (but can have null value)
- Type 3 -> Optional

Proprietary tags specific for each user can be implemented due to DICOM standard. Proprietary tags can be identified by the fact that their first hexadecimal number is odd *(e.g. (0x0009, 0x0010))*. Obviously, such proprietary tags should be avoided for maximal interoperability.

## Pixel data

The image itself is associated with the DICOM tag PixelData **_(0x7fe0, 0x0010)_**. The content of image can be compressed using many image formats, such as **JPEG**, **Lossless JPEG** or **JPEG 2000**. Obviously, non-destructive (lossless) compression should always be favored to avoid any loss of medical information. Note that a DICOM file can also act as a wrapper around a video encoded using **MPEG-2** or **H.264**.

The image compression algorithm can be identified by inspecting the *transfer syntax* that is associated with the DICOM file in its header.

There are few devices in a hospital that can support image compression so in order to get the full detailed overview, usually there aren't any algorithms applied on DICOM files. So in order for the transfer to be done, the **image** is encoded as a **raw buffer** that has a *width*, *height*, *pixel type(int/float)*, *color depth* and *photometric interpretation (grayscale/RGB)*. The most common case regarding the transfer syntex, is the **little_endian** altough the deprecated way was **big_endian**.

The process of converting one DICOM instance from some transfer syntax to another one is referred to as **transcoding**.

A DICOM image can be **multi-frame**, meaning that it encodes an array of different image frames. This is for instance used to encode uncompressed video sequences, that are often referred to as cine or **2D+t** images (e.g. for *ultrasound imaging*)

The **Orthanc** software can receive, store and send any kind of DICOM images and it can furthermore convert most uncompressed images to PNG. Orthanc chose PNG as it is losless, natively supported by many browsers, software and programming frameworks, and is able to encode up to 16bpp int pixels. This on-the-fly conversion to PNG images is what happens when previewing a DICOM image within Orthanc Explorer

The so called DICOM model of the real world is composed of 4 layers:
- Patient
- Study
- Series
- Instance

and the hierarchy goes as such: Patient benefits from a set of medical imaging *studies*. Each study is made of a set of *series* which is then composed of a set of *instances* **the latter being a synonym for a single DICOM file**.

Any imaging study can be associated with multiple series of images. Any **PET-CT-scan** study will contain at least two separate series: the *CT* series and the *PET* series. 

Any kind of imaging study will usually generate a set of separate series. In general, a series can be thought of as either a single 2D image (digital radiography), a 3D volume (CT-scan) or a 2D+t cine sequence. 

A series might also encode a single PDF report, a structured report, or a temporal sequence of 3D images. 

The actual pixel data of a given series is spread across multiple DICOM instances. This allows to split a huge image (medical imaging commonly deals with 4GB images) into hundres of small files of several megabytes, each of which can entirely fit in the computer memory, at the price of a severe redundancy of the medical infromation that is embedded within these files.

The DICOM stamndard specifies a module as a set of DICOM tags that describe these 4 resources. For instance, the DICOM tag PatientName is part of the patient module, whereas SeriesDescription is part of the series module. 

Any SOP can be decomposed into a set of modules that make sense for its associated type of modality, anmd whose conjuction forms encodes all the medical information.

According to this model of the real world, the default Web interface of Orthanc allows to browse from the **patient level** to the **instance level**.

## DICOM identifiers

Very importantly, the DICOM standard specifies DICOM tags that allow to index each single DICOM resource:

- Patients are indexed with PatientID **(0x0010, 0x0020)** (part of the patient module).
- Studies are indexed with StudyInstanceUID **(0x0020, 0x000d)** (part of the study module).
- Series are indexed with SeriesInstanceUID **(0x0020, 0x000e)** (part of the series module).
- Instances are indexed with SOPInstanceUID **(0x0008, 0x0018)** (part of the SOP module).

The DICOM standard orders *StudyInstanceUID*, *SeriesInstanceUID* and *SOPInstanceUID* to be **globally unique**.

Importantly, even if the PatientID must be unique inside a given hospital, it is not guaranteed to be globally unique. This means that different patients imaged in different hospitals might share the same PatientID. For this reason, you should always browse from the study level (and not from the patient level) as soon as you deal with an application that handles patients from different hospitals.

In any case, the core engine Orthanc keeps an index of all these DICOM identifiers (*PatientID, AccessionNumber, StudyInstanceUID, SeriesInstanceUID* and *SOPInstanceUID*) and is able to quickly maps them to its own internal identifiers. This lookup is implemented by the ```/tools/lookup``` URI of the REST API of Orthanc.

## DICOM network protocol

The DICOM protocol is actually one of the earliest example of **Web services**, long before **SOAP** and **REST**.
Through this protocol you can:
- **Test the connection** between two devices (*C-Echo*).
- **Send images** from the local imaging device to a remote device (*C-Store*).
- **Search the content** of a remote device (*C-Find*). 
- **Retrieve images** from a remote device (*C-Move* or *C-Get*)

In the DICOM terminology, the client of a DICOM service is called a **service class user** (SCU) and the server that provides the requests is called a **service class provider** (SCP). The client sends a request that is encoded as a DICOM file (the **command**). and the server answers with a DICOM file.

Connection between SCU and SCP is called an **association**. This association starts with a handshake between the client and the server agreeing on the commands that can be exchanged between them and as well as which *transfer syntaxes* are supported.
