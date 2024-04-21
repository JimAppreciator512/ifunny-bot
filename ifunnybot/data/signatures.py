from typing import List

from pyfsig.constants import FileSignatureDict


IFUNNY_SIGS: List[FileSignatureDict] = [
    {
        "display_string": "GIF87a",
        "description": "Image file encoded in theGraphics Interchange Format (GIF)",
        "file_extension": "gif",
        "hex": [71, 73, 70, 56, 55, 97],
        "offset": 0,
    },
    {
        "display_string": "GIF89a",
        "description": "Image file encoded in theGraphics Interchange Format (GIF)",
        "file_extension": "gif",
        "hex": [71, 73, 70, 56, 57, 97],
        "offset": 0,
    },
    {
        "display_string": "II*.",
        "description": "Tagged Image File Format (little endian format)",
        "file_extension": "tif",
        "hex": [73, 73, 42, 0],
        "offset": 0,
    },
    {
        "display_string": "MM.*",
        "description": "Tagged Image File Format (big endian format)",
        "file_extension": "tif",
        "hex": [77, 77, 0, 42],
        "offset": 0,
    },
    {
        "display_string": "II*.....CR",
        "description": "Canon's RAW format is based on the TIFF file format",
        "file_extension": "cr2",
        "hex": [73, 73, 42, 0, 16, 0, 0, 0, 67, 82],
        "offset": 0,
    },
    {
        "display_string": "II*.....CR",
        "description": "Canon RAW Format Version 2",
        "file_extension": "cr2",
        "hex": [73, 73, 42, 0, 16, 0, 0, 0, 67, 82],
        "offset": 0,
    },
    {
        "display_string": ".*_×",
        "description": "Kodak Cineon image",
        "file_extension": "cin",
        "hex": [128, 42, 95, 215],
        "offset": 0,
    },
    {
        "display_string": "RNC.RNC.",
        "description": "Compressed file usingRob Northen Compression (version 1 and 2) algorithm",
        "file_extension": "",
        "hex": [82, 78, 67, 1, 82, 78, 67, 2],
        "offset": 0,
    },
    {
        "display_string": "SDPX",
        "description": "SMPTEDPX image (big endian format)",
        "file_extension": "dpx",
        "hex": [83, 68, 80, 88],
        "offset": 0,
    },
    {
        "display_string": "XPDS",
        "description": "SMPTEDPX image (little endian format)",
        "file_extension": "dpx",
        "hex": [88, 80, 68, 83],
        "offset": 0,
    },
    {
        "display_string": "v/1.",
        "description": "OpenEXR image",
        "file_extension": "exr",
        "hex": [118, 47, 49, 1],
        "offset": 0,
    },
    {
        "display_string": "BPGû",
        "description": "Better Portable Graphics format",
        "file_extension": "bpg",
        "hex": [66, 80, 71, 251],
        "offset": 0,
    },
    {
        "display_string": "ÿØÿÛ",
        "description": "JPEG raw or in theJFIF orExif file format",
        "file_extension": "jpg",
        "hex": [255, 216, 255, 219],
        "offset": 0,
    },
    {
        "display_string": "ÿØÿÛ",
        "description": "JPEG raw or in theJFIF orExif file format",
        "file_extension": "jpeg",
        "hex": [255, 216, 255, 219],
        "offset": 0,
    },
    {
        "display_string": "ÿØÿà..JFIF..",
        "description": "JPEG raw or in theJFIF orExif file format",
        "file_extension": "jpg",
        "hex": [255, 216, 255, 224, None, None, 74, 70, 73, 70, 0, 1],
        "offset": 0,
    },
    {
        "display_string": "ÿØÿà..JFIF..",
        "description": "JPEG raw or in theJFIF orExif file format",
        "file_extension": "jpeg",
        "hex": [255, 216, 255, 224, None, None, 74, 70, 73, 70, 0, 1],
        "offset": 0,
    },
    {
        "display_string": "ÿØÿá..Exif..",
        "description": "JPEG raw or in theJFIF orExif file format",
        "file_extension": "jpg",
        "hex": [255, 216, 255, 225, None, None, 69, 120, 105, 102, 0, 0],
        "offset": 0,
    },
    {
        "display_string": "ÿØÿá..Exif..",
        "description": "JPEG raw or in theJFIF orExif file format",
        "file_extension": "jpeg",
        "hex": [255, 216, 255, 225, None, None, 69, 120, 105, 102, 0, 0],
        "offset": 0,
    },
    {
        "display_string": ".PNG....",
        "description": "Image encoded in thePortable Network Graphics format",
        "file_extension": "png",
        "hex": [137, 80, 78, 71, 13, 10, 26, 10],
        "offset": 0,
    },
    {
        "display_string": "ï»¿",
        "description": "UTF-8 encodedUnicodebyte order mark, commonly seen in text files.",
        "file_extension": "",
        "hex": [239, 187, 191],
        "offset": 0,
    },
    {
        "display_string": "OggS",
        "description": "Ogg, anopen source media container format",
        "file_extension": "ogg",
        "hex": [79, 103, 103, 83],
        "offset": 0,
    },
    {
        "display_string": "OggS",
        "description": "Ogg, anopen source media container format",
        "file_extension": "oga",
        "hex": [79, 103, 103, 83],
        "offset": 0,
    },
    {
        "display_string": "OggS",
        "description": "Ogg, anopen source media container format",
        "file_extension": "ogv",
        "hex": [79, 103, 103, 83],
        "offset": 0,
    },
    {
        "display_string": "RIFF....WAVE",
        "description": "Waveform Audio File Format",
        "file_extension": "wav",
        "hex": [82, 73, 70, 70, None, None, None, None, 87, 65, 86, 69],
        "offset": 0,
    },
    {
        "display_string": "RIFF....AVI ",
        "description": "Audio Video Interleave video format",
        "file_extension": "avi",
        "hex": [82, 73, 70, 70, None, None, None, None, 65, 86, 73, 32],
        "offset": 0,
    },
    {
        "display_string": "ÿû",
        "description": "MPEG-1 Layer 3 file without anID3 tag or with anID3v1 tag (which's appended at the end of the "
        "file)",
        "file_extension": "mp3",
        "hex": [255, 251],
        "offset": 0,
    },
    {
        "display_string": "ID3",
        "description": "MP3 file with an ID3v2 container",
        "file_extension": "mp3",
        "hex": [73, 68, 51],
        "offset": 0,
    },
    {
        "display_string": "BM",
        "description": "BMP file, abitmap format used mostly in theWindows world",
        "file_extension": "bmp",
        "hex": [66, 77],
        "offset": 0,
    },
    {
        "display_string": "BM",
        "description": "BMP file, abitmap format used mostly in the Windows world",
        "file_extension": "dib",
        "hex": [66, 77],
        "offset": 0,
    },
    {
        "display_string": "BM",
        "description": "BMP file, abitmap format used mostly in theWindows world",
        "file_extension": "dib",
        "hex": [66, 77],
        "offset": 0,
    },
    {
        "display_string": "SIMPLE  =                    T",
        "description": "Flexible Image Transport System (FITS)",
        "file_extension": "fits",
        "hex": [
            83,
            73,
            77,
            80,
            76,
            69,
            32,
            32,
            61,
            32,
            32,
            32,
            32,
            32,
            32,
            32,
            32,
            32,
            32,
            32,
            32,
            32,
            32,
            32,
            32,
            32,
            32,
            32,
            32,
            84,
        ],
        "offset": 0,
    },
    {
        "display_string": "fLaC",
        "description": "Free Lossless Audio Codec",
        "file_extension": "flac",
        "hex": [102, 76, 97, 67],
        "offset": 0,
    },
    {
        "display_string": "MThd",
        "description": "MIDI sound file",
        "file_extension": "mid",
        "hex": [77, 84, 104, 100],
        "offset": 0,
    },
    {
        "display_string": "MThd",
        "description": "MIDI sound file",
        "file_extension": "midi",
        "hex": [77, 84, 104, 100],
        "offset": 0,
    },
    {
        "display_string": "KDM",
        "description": "VMDK files",
        "file_extension": "vmdk",
        "hex": [75, 68, 77],
        "offset": 0,
    },
    {
        "display_string": ".Eß£",
        "description": "Matroska media container, includingWebM",
        "file_extension": "mkv",
        "hex": [26, 69, 223, 163],
        "offset": 0,
    },
    {
        "display_string": "Ï..",
        "description": "Lepton compressed JPEG image",
        "file_extension": "lep",
        "hex": [207, 132, 1],
        "offset": 0,
    },
    {
        "display_string": "RIFF....",
        "description": "Google WebP image file",
        "file_extension": "webp",
        "hex": [82, 73, 70, 70, None, None, None, None],
        "offset": 0,
    },
    {
        "display_string": "WEBP",
        "description": "",
        "file_extension": "",
        "hex": [87, 69, 66, 80],
        "offset": 0,
    },
    {
        "display_string": "ftypisom",
        "description": "ISO Base Media file (MPEG-4)",
        "file_extension": "mp4",
        "hex": [0x66, 0x74, 0x79, 0x70, 0x69, 0x73, 0x6f, 0x6d],
        "offset": 4,
    },
    {
        "display_string": "ftypMSNV",
        "description": "MPEG-4 video file",
        "file_extension": "mp4",
        "hex": [0x66, 0x74, 0x79, 0x70, 0x4d, 0x53, 0x4e, 0x56],
        "offset": 4,
    }
]

