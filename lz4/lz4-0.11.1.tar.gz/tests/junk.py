import lz4.frame as lz4frame

context = lz4frame.create_compression_context()
input_data = b"2099023098234882923049823094823094898239230982349081231290381209380981203981209381238901283098908123109238098123" * 4096 * 1000
chunk_size = int((len(input_data)/2)+1)
compressed = lz4frame.compress_begin(context, source_size=len(input_data))
compressed += lz4frame.compress_update(context, input_data[:chunk_size])
compressed += lz4frame.compress_update(context, input_data[chunk_size:])
compressed += lz4frame.compress_end(context)

with open('t.lz4', 'w') as file:
    file.write(compressed)
