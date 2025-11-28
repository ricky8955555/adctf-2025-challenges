using System.IO.Compression;

namespace Cspyshell.Frontend.Shell;

class Binpack
{
    private byte[] vector;

    public Binpack(byte[] iv)
    {
        if (iv.Length != 16)
        {
            throw new ArgumentException("Invalid iv size.", nameof(iv));
        }

        vector = iv;
    }

    private void Next()
    {
        byte[] newVector = [.. vector.Select((value, i) => (byte)(((value + (i * 7)) >> 5) | (((value + (i * 5)) & 31) << 3)))];

        foreach (var (value, source) in vector.Select((value, i) => (value, i)))
        {
            int target = value & 0xf;
            (newVector[source], newVector[target]) = (newVector[target], newVector[source]);
        }

        vector = newVector;
    }

    public byte[] Crypt(byte[] plaintext)
    {
        using MemoryStream stream = new();

        for (int i = 0; i < plaintext.Length; i += 16)
        {
            byte[] block = [.. plaintext.Skip(i).Zip(vector, (ch, k) => (byte)(ch ^ k))];
            stream.Write(block);

            Next();
        }

        return stream.ToArray();
    }

    public byte[] Unpack(byte[] ciphertext)
    {
        using MemoryStream ciphertextStream = new(ciphertext);
        using ZLibStream zlibStream = new(ciphertextStream, CompressionMode.Decompress);

        using MemoryStream stream = new();
        zlibStream.CopyTo(stream);

        byte[] decompressed = stream.ToArray();

        byte[] plaintext = Crypt(decompressed);
        return plaintext;
    }
}
