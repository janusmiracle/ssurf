## ssurf

`ssurf` is an encoding, decoding, and reading library for WAVE files.

The library is designed to be simple for the user while maintaining high performance. 

Users can control reading performance by specifying which `chunk_data` to read when accessing a stream. For instance, in RF64 files, chunks like `data`, `JUNK`, `PAD`, `FILLR`, or certain ProTool chunks can be extremely large. By listing chunks to ignore, users can prevent these from being read.

### Reading

Reading supports RIFF, RF64, BW64, and PVOC-EX formats, including big-endian variants. Sony Wave64 is not currently supported.

Reading is done using the `Read` class. It takes in a `source` parameter and `options`. `source` can be a file, BufferedReader, BytesIO, or even raw bytes.

The `Read` class allows users to access any chunk in the stream, both in its raw form and parsed structure.

Below are all the `Read` properties and methods:

NOTE: The `get_chunk` and `get_chunk_raw` methods return a tuple `(size of data (int), chunk_data)`.

```py
# Initialize the class
source = 'test.wav'
reader = Read(source)  # Ignore options for now

# Properties:

# Stream-related properties
reader.stream          # Normalized ReadableStream
reader.file_size       # Stream size in bytes
reader.identity        # Stream format info
reader.byteorder       # Stream endianness
reader.chunk_list      # List of chunks (including ignored ones)
reader.ds64            # `ds64` chunk in dict format
reader.formtype        # Always returns 'WAVE'
reader.is_extensible   # Checks if the format is extensible
reader.master          # Master RIFF identifier (RIFF, RIFX, RF64, etc.)

# Methods:

# Chunk retrieval methods
reader.all()                            # Returns all parsed chunks in a dict
reader.all_raw()                        # Returns all raw chunks
reader.get_chunk(chunk_identifier)      # Returns a specified chunk or None if missing
reader.get_chunk_raw(chunk_identifier)  # Same as get_chunk() but for raw chunks
reader.get_summary()                    # Returns a summary of [fmt, data, fact]
reader.has_chunk(chunk_identifier)      # Checks if a specified chunk exists

# PCM Properties (basic WAVE info)
reader.audio_format    
reader.num_channels    
reader.sample_rate     
reader.byte_rate       
reader.block_align     
reader.bits_per_sample 
reader.bit_depth       
reader.encoding         

# Extended Properties
reader.extension_size

# Extensible Properties
reader.valid_bits_per_sample
reader.channel_mask
reader.speaker_layout
reader.guid             # Only available in Extensible format

# PVOC-EX Properties
reader.version          
reader.pvoc_size        
reader.word_format      
reader.analysis_format  
reader.source_format    
reader.window_type      
reader.num_analysis_bins
reader.bin_count        
reader.window_length    
reader.overlap          
reader.frame_align      
reader.analysis_rate    
reader.window_param      
reader.word_format_str  
reader.analysis_format_str
reader.source_format_str
reader.window_type_str  
reader.beta

```

The user can control the library's performance, especially when reading chunks from the stream. While the time spent in `stream.read()` is usually negligible, it can be significant in RF64 streams, particularly for large chunks like `data` or `JUNK`.

In this case, you can use `ReaderOptions`. Specifically, the `ignore_chunks` setting.

The below example will be using a 6 billion byte (roughly 6.2GB) RF64 file.

```py 
from ssurf import Read

# Without any optimizations..
source = "rf64-large.wav"
reader = Read(source)

print(reader.file_size)
>>> 6260008262
print(reader.get_chunk("data").size)
>>> 6227020800
```

As you can see, the size of the `data` chunk is obscene. Running this took around 2.24 seconds.

Now, lets ignore the large `data` chunk.

```py 
from ssurf import Read, ReaderOptions

source = "rf64-large.wav"
options = ReaderOptions(ignore_chunks["data", "JUNK", "FLLR", "PAD "])
reader = Read(source, options)

print(reader.file_size)
>>> 6260008262
print(reader.get_chunk("data").size)
>>> 6227020800
```

The process took around 5-14ms to run. You can still access the chunk's size even if it's ignored. Ignoring a chunk only skips reading its data, but be cautious when ignoring essential chunks like `fmt `, as this WILL cause errors. Only ignore chunks that are defaulted to `GenericChunk` or `data`.

Any unsupported/unknown/undocumented chunks will automatically default to `GenericChunk`, and return its identifier, size, and byte payload.

```py 
print(reader.get_chunk("minf"))
>>> GenericChunk(identifier='minf', size=16, payload=b'8z\x9fkw+\xd5\x01\x01\x00\x00\x00\x00\x00\x00\x00')
```
