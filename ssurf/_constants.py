ENCODING = "latin-1"
FALSE_SIZE = "0xffffffff"  # -1 / "0xFFFFFFFF"
NULL_IDENTIFIER = "\x00\x00\x00\x00"

# Decode/parser constants
DEFAULT_ENCODING = "latin-1"

# GUID for PVOC_EX format
PVOC_EX = [
    "8312B9C2-2E6E-11d4-A824-DE5B96C3AB21",
    "c2b91283-6e2e-d411-a824-de5b96c3ab21",
]

# WAVE Format Types
WAVE_FORMAT_PCM = "WAVE_FORMAT_PCM"
WAVE_FORMAT_EXTENDED = "WAVE_FORMAT_EXTENDED"
WAVE_FORMAT_EXTENSIBLE = "WAVE_FORMAT_EXTENSIBLE"
WAVE_FORMAT_PVOC_EX = "WAVE_FORMAT_PVOC_EX"

# Wave Format Extensible and Coding History Size
EXTENSIBLE = 65534
CODING_HISTORY_LO = 602

# Locations for PerverseError
FORMAT_CHUNK_LOCATION = "['fmt ' / FORMAT]"
STRC_CHUNK_LOCATION = "['strc']"

# DISP types
CF_TEXT = 1
CF_BITMAP = 2
CF_METAFILE = 3
CF_DIB = 8
CF_PALETTE = 9
CF_TYPES = {
    CF_TEXT: "CF_TEXT",
    CF_BITMAP: "CF_BITMAP",
    CF_METAFILE: "CF_METAFILE",
    CF_DIB: "CF_DIB",
    CF_PALETTE: "CF_PALETTE",
}

# TODO: Update this at some point, too lazy
CODECS = {
    0: "Unknown",
    1: "Microsoft PCM (uncompressed)",
    2: "Microsoft ADPCM",
    3: "Microsoft IEEE float",
    4: "Compaq VSELP",
    5: "IBM CVSD",
    6: "ITU G.711 a-law",
    7: "ITU G.711 u-law",
    8: "Microsoft DTS",
    9: "DRM",
    10: "WMA 9 Speech",
    11: "Microsoft Windows Media RT Voice",
    16: "OKI-ADPCM",
    17: "Intel IMA/DVI-ADPCM",
    18: "Videologic Mediaspace ADPCM",
    19: "Sierra ADPCM",
    20: "Antex G.723 ADPCM",
    21: "DSP Solutions DIGISTD",
    22: "DSP Solutions DIGIFIX",
    23: "Dialogic OKI ADPCM",
    24: "Media Vision ADPCM",
    25: "HP CU",
    26: "HP Dynamic Voice",
    32: "Yamaha ADPCM",
    33: "SONARC Speech Compression",
    34: "DSP Group True Speech",
    35: "Echo Speech Corp.",
    36: "Virtual Music Audiofile AF36",
    37: "Audio Processing Tech.",
    38: "Virtual Music Audiofile AF10",
    39: "Aculab Prosody 1612",
    40: "Merging Tech. LRC",
    48: "Dolby AC2",
    49: "Microsoft GSM610",
    50: "MSN Audio",
    51: "Antex ADPCM",
    52: "Control Resources VQLPC",
    53: "DSP Solutions DIGIREAL",
    54: "DSP Solutions DIGIADPCM",
    55: "Control Resources CR10",
    56: "Natural MicroSystems VBX ADPCM",
    57: "Crystal Semiconductors IMA ADPCM",
    58: "Echo Speech ECHOSC3",
    59: "Rockwell ADPCM",
    60: "Rockwell DIGITALK",
    61: "Xebec Multimedia",
    64: "Antex G.721 ADPCM",
    65: "Antex G.728 CELP",
    66: "Microsoft MSG723",
    67: "IBM AVC ADPCM",
    69: "ITU-T G.726",
    80: "Microsoft MPEG",
    81: "RT23 or PAC",
    82: "InSoft RT24",
    83: "InSoft PAC",
    85: "MP3",
    89: "Cirrus",
    96: "Cirrus Logic",
    97: "ESS Tech. PCM",
    98: "Voxware Inc.",
    99: "Canopus ATRAC",
    100: "APICOM G.726 ADPCM",
    101: "APICOM G.722 ADPCM",
    102: "Microsoft DSAT",
    103: "Microsoft DSAT-DISPLAY",
    105: "Voxware Byte Aligned",
    112: "Voxware ACB",
    113: "Voxware AC10",
    114: "Voxware AC16",
    115: "Voxware AC20",
    116: "Voxware MetaVoice",
    117: "Voxware MetaSound",
    118: "Voxware RT29HW",
    119: "Voxware VR12",
    120: "Voxware VR18",
    121: "Voxware TQ40",
    122: "Voxware SC3",
    123: "Voxware SC3",
    128: "Soundsoft",
    129: "Voxware TQ60",
    130: "Microsoft MSRT24",
    131: "AT&T G.729A",
    132: "Motion Pixels MVI-MV12",
    133: "DataFusion G.726",
    134: "DataFusion GSM610",
    136: "Iterated Systems Audio",
    137: "Onlive",
    138: "Multitude, Inc. FT SX20",
    139: "Infocom IT’S A/S G.721 ADPCM",
    140: "Convedia G729",
    141: "Congruency, Inc. (not specified)",
    145: "Siemens SBC24",
    146: "Sonic Foundry Dolby AC3 APDIF",
    147: "MediaSonic G.723",
    148: "Aculab Prosody 8kbps",
    151: "ZyXEL ADPCM",
    152: "Philips LPCBB",
    153: "Studer Professional Audio Packed",
    160: "Maiden PhonyTalk",
    161: "Racal Recorder GSM",
    162: "Racal Recorder G720.a",
    163: "Racal G723.1",
    164: "Racal Tetra ACELP",
    176: "NEC AAC NEC Corporation",
    255: "AAC",
    256: "Rhetorex ADPCM",
    257: "IBM u-Law",
    258: "IBM a-Law",
    259: "IBM ADPCM",
    273: "Vivo G.723",
    274: "Vivo Siren",
    288: "Philips Speech Processing CELP",
    289: "Philips Speech Processing GRUNDIG",
    291: "Digital G.723",
    293: "Sanyo LD ADPCM",
    304: "Sipro Lab ACEPLNET",
    305: "Sipro Lab ACELP4800",
    306: "Sipro Lab ACELP8V3",
    307: "Sipro Lab G.729",
    308: "Sipro Lab G.729A",
    309: "Sipro Lab Kelvin",
    310: "VoiceAge AMR",
    320: "Dictaphone G.726 ADPCM",
    336: "Qualcomm PureVoice",
    337: "Qualcomm HalfRate",
    341: "Ring Zero Systems TUBGSM",
    352: "Microsoft Audio1",
    353: "Windows Media Audio V2 V7 V8 V9 / DivX audio (WMA) / Alex AC3 Audio",
    354: "Windows Media Audio Professional V9",
    355: "Windows Media Audio Lossless V9",
    356: "WMA Pro over S/PDIF",
    368: "UNISYS NAP ADPCM",
    369: "UNISYS NAP ULAW",
    370: "UNISYS NAP ALAW",
    371: "UNISYS NAP 16K",
    372: "MM SYCOM ACM SYC008 SyCom Technologies",
    373: "MM SYCOM ACM SYC701 G726L SyCom Technologies",
    374: "MM SYCOM ACM SYC701 CELP54 SyCom Technologies",
    375: "MM SYCOM ACM SYC701 CELP68 SyCom Technologies",
    376: "Knowledge Adventure ADPCM",
    384: "Fraunhofer IIS MPEG2AAC",
    400: "Digital Theater Systems DTS DS",
    512: "Creative Labs ADPCM",
    514: "Creative Labs FASTSPEECH8",
    515: "Creative Labs FASTSPEECH10",
    528: "UHER ADPCM",
    533: "Ulead DV ACM",
    534: "Ulead DV ACM",
    544: "Quarterdeck Corp.",
    560: "I-Link VC",
    576: "Aureal Semiconductor Raw Sport",
    577: "ESST AC3",
    592: "Interactive Products HSX",
    593: "Interactive Products RPELP",
    608: "Consistent CS2",
    624: "Sony SCX",
    625: "Sony SCY",
    626: "Sony ATRAC3",
    627: "Sony SPC",
    640: "TELUM Telum Inc.",
    641: "TELUMIA Telum Inc.",
    645: "Norcom Voice Systems ADPCM",
    768: "Fujitsu FM TOWNS SND",
    769: "Fujitsu (not specified)",
    770: "Fujitsu (not specified)",
    771: "Fujitsu (not specified)",
    772: "Fujitsu (not specified)",
    773: "Fujitsu (not specified)",
    774: "Fujitsu (not specified)",
    775: "Fujitsu (not specified)",
    776: "Fujitsu (not specified)",
    848: "Micronas Semiconductors, Inc. Development",
    849: "Micronas Semiconductors, Inc. CELP833",
    1024: "Brooktree Digital",
    1025: "Intel Music Coder (IMC)",
    1026: "Ligos Indeo Audio",
    1104: "QDesign Music",
    1280: "On2 VP7 On2 Technologies",
    1281: "On2 VP6 On2 Technologies",
    1664: "AT&T VME VMPCM",
    1665: "AT&T TCP",
    1792: "YMPEG Alpha (dummy for MPEG-2 compressor)",
    2222: "ClearJump LiteWave (lossless)",
    4096: "Olivetti GSM",
    4097: "Olivetti ADPCM",
    4098: "Olivetti CELP",
    4099: "Olivetti SBC",
    4100: "Olivetti OPR",
    4352: "Lernout & Hauspie",
    4353: "Lernout & Hauspie CELP codec",
    4354: "Lernout & Hauspie SBC codec",
    4355: "Lernout & Hauspie SBC codec",
    4356: "Lernout & Hauspie SBC codec",
    5120: "Norris Comm. Inc.",
    5121: "ISIAudio",
    5376: "AT&T Soundspace Music Compression",
    6172: "VoxWare RT24 speech codec",
    6174: "Lucent elemedia AX24000P Music codec",
    6513: "Sonic Foundry LOSSLESS",
    6521: "Innings Telecom Inc. ADPCM",
    7175: "Lucent SX8300P speech codec",
    7180: "Lucent SX5363S G.723 compliant codec",
    7939: "CUseeMe DigiTalk (ex-Rocwell)",
    8132: "NCT Soft ALF2CD ACM",
    8192: "FAST Multimedia DVM",
    8193: "Dolby DTS (Digital Theater System)",
    8194: "RealAudio 1 / 2 14.4",
    8195: "RealAudio 1 / 2 28.8",
    8196: "RealAudio G2 / 8 Cook (low bitrate)",
    8197: "RealAudio 3 / 4 / 5 Music (DNET)",
    8198: "RealAudio 10 AAC (RAAC)",
    8199: "RealAudio 10 AAC+ (RACP)",
    9472: "Reserved range to 0x2600 Microsoft",
    13075: "makeAVIS (ffvfw fake AVI sound from AviSynth scripts)",
    16707: "Divio MPEG-4 AAC audio",
    16897: "Nokia adaptive multirate",
    16963: "Divio G726 Divio, Inc.",
    17228: "LEAD Speech",
    22092: "LEAD Vorbis",
    22358: "WavPack Audio",
    26447: "Ogg Vorbis (mode 1)",
    26448: "Ogg Vorbis (mode 2)",
    26449: "Ogg Vorbis (mode 3)",
    26479: "Ogg Vorbis (mode 1+)",
    26480: "Ogg Vorbis (mode 2+)",
    26481: "Ogg Vorbis (mode 3+)",
    28672: "3COM NBX 3Com Corporation",
    28781: "FAAD AAC",
    31265: "GSM-AMR (CBR, no SID)",
    31266: "GSM-AMR (VBR, including SID)",
    41216: "Comverse Infosys Ltd. G723 1",
    41217: "Comverse Infosys Ltd. AVQSBC",
    41218: "Comverse Infosys Ltd. OLDSBC",
    41219: "Symbol Technologies G729A",
    41220: "VoiceAge AMR WB VoiceAge Corporation",
    41221: "Ingenient Technologies Inc. G726",
    41222: "ISO/MPEG-4 advanced audio Coding",
    41223: "Encore Software Ltd G726",
    41225: "Speex ACM Codec xiph.org",
    57260: "DebugMode SonicFoundry Vegas FrameServer ACM Codec",
    59144: "Unknown",
    61868: "Free Lossless Audio Codec FLAC",
    65534: "Extensible",
    65535: "Development",
}

GENERIC_CHANNEL_MASK_MAP = {
    0x0001: "Front Left",
    0x0002: "Front Right",
    0x0004: "Front Center",
    0x0008: "Low Frequency",
    0x0010: "Back Left",
    0x0020: "Back Right",
    0x0040: "Front Left of Center",
    0x0080: "Front Right of Center",
    0x0100: "Back Center",
    0x0200: "Side Left",
    0x0400: "Side Right",
    0x0800: "Top Center",
    0x1000: "Top Front Left",
    0x2000: "Top Front Right",
    0x4000: "Top Back Left",
    0x8000: "Top Back Right",
}

# TODO: add the channel_mask_maps for the other formats too
