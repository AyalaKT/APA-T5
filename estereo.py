#! /usr/bin/python3

"""
    T5 : Sonido estéreo y ficheros WAVE

    Nombre y apellidos: Eric Ayala
"""

import struct as st

def Bits2fmt(BitsPerSample):
    """ Convierte los bits en formato WAVE """
    if BitsPerSample == 8:
        return 'b'
    elif BitsPerSample == 16:
        return 'h'
    elif BitsPerSample == 32:
        return 'i'
    else:
        raise ValueError('Bits no válidos: debe ser 8, 16 o 32')

def leeWave(ficWave):
    """ Lee un archivo WAVE PCM lineal y devuelve metadatos + datos """
    with open(ficWave, 'rb') as f:
        header_fmt = '4sI4s4sIH'
        header = f.read(st.calcsize(header_fmt))
        ChunkID, ChunkSize, Format, SubchunkID, SubChunkSize, AudioFormat = st.unpack(header_fmt, header)

        if Format == b'WAVE' and AudioFormat == 1:
            fmt_fmt = '<HIIHH4sI'
            fmt_data = f.read(st.calcsize(fmt_fmt))
            (numChannels, SampleRate, ByteRate, BlockAlign,
             BitsPerSample, SubChunk2Id, SubChunk2Size) = st.unpack(fmt_fmt, fmt_data)

            numSamples = SubChunk2Size // BlockAlign
            fmtData = '<' + str(numSamples * numChannels) + Bits2fmt(BitsPerSample)
            raw_data = f.read(st.calcsize(fmtData))
            data = st.unpack(fmtData, raw_data)
        else:
            raise ValueError('Fichero no es PCM WAVE')

    return (numChannels, SampleRate, BitsPerSample, data)

def escrWave(ficWave, /, *, numChannels=2, SampleRate=44100, BitsPerSample=16, data=[]):
    """ Escribe una señal PCM en formato WAVE """
    with open(ficWave, 'wb') as f:
        NumSamples = len(data)
        SubChunk1Size = 16
        SubChunk2Size = NumSamples * numChannels * (BitsPerSample // 8)
        ChunkSize = 4 + (8 + SubChunk1Size) + (8 + SubChunk2Size)
        ByteRate = SampleRate * numChannels * (BitsPerSample // 8)
        BlockAlign = numChannels * BitsPerSample // 8

        fmt = '<4sI4s4sIHHIIHH4sI' + str(NumSamples) + Bits2fmt(BitsPerSample)
        estructura = st.pack(fmt, b'RIFF', ChunkSize, b'WAVE', b'fmt ', SubChunk1Size, 1,
                             numChannels, SampleRate, ByteRate, BlockAlign,
                             BitsPerSample, b'data', SubChunk2Size, *data)
        f.write(estructura)

def estereo2mono(ficEste, ficMono, canal=2):
    """ Convierte una señal estéreo a mono según canal (0: L, 1: R, 2: L+R/2, 3: L–R/2) """
    numCh, fs, bps, data = leeWave(ficEste)
    data += (0,)  # Evita errores de índice

    if canal == 0:
        datosMono = data[0::2]
    elif canal == 1:
        datosMono = data[1::2]
    elif canal == 2:
        datosMono = [(l + r) // 2 for l, r in zip(data[::2], data[1::2])]
    elif canal == 3:
        datosMono = [(l - r) // 2 for l, r in zip(data[::2], data[1::2])]
    else:
        raise ValueError("Canal no válido. Usa 0, 1, 2 o 3.")

    escrWave(ficMono, numChannels=1, SampleRate=fs, BitsPerSample=bps, data=datosMono)

def mono2estereo(ficIzq, ficDer, ficEste):
    """ Combina dos ficheros mono en un fichero estéreo """
    ncL, fsL, bpsL, dataL = leeWave(ficIzq)
    ncR, fsR, bpsR, dataR = leeWave(ficDer)

    dataStereo = [val for pair in zip(dataL, dataR) for val in pair]
    escrWave(ficEste, numChannels=2, SampleRate=fsL, BitsPerSample=bpsL, data=dataStereo)

def codEstereo(ficEste, ficCod):
    """ Codifica señal estéreo como una señal mono de 32 bits con (L+R)/2 y (L–R)/2 """
    nch, fs, bps, data = leeWave(ficEste)
    codificada = []

    for i in range(0, len(data), 2):
        L = data[i]
        R = data[i + 1]
        codificada.append((L + R) // 2)
        codificada.append((L - R) // 2)

    escrWave(ficCod, numChannels=1, SampleRate=fs, BitsPerSample=32, data=codificada)

def decEstereo(ficCod, ficDec):
    """ Decodifica señal mono de 32 bits en dos canales estéreo (reconstrucción L y R) """
    nch, fs, bps, data = leeWave(ficCod)
    L_rec = []
    R_rec = []

    for i in range(0, len(data), 2):
        suma = data[i]
        dif = data[i + 1]
        L_rec.append((suma + dif) // 2)
        R_rec.append((suma - dif) // 2)

    dataOut = [val for pair in zip(L_rec, R_rec) for val in pair]
    escrWave(ficDec, numChannels=2, SampleRate=fs, BitsPerSample=16, data=dataOut)
