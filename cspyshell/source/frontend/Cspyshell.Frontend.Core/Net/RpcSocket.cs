using System.IO.Compression;
using System.Net.Sockets;
using System.Reflection;
using NSec.Cryptography;

namespace Cspyshell.Frontend.Core.Net;

public class RpcSocket(Socket innerSocket) : IDisposable
{
    private readonly SecureStream stream = new(new NetworkStream(innerSocket));

    public Socket InnerSocket { get; } = innerSocket;

    public void Initiate(Key privateKey) => stream.Initiate(privateKey);

    public void Send(byte[] data)
    {
        using MemoryStream compressedStream = new();

        using ZLibStream zlibStream = new(compressedStream, CompressionMode.Compress);
        zlibStream.Write(data);
        zlibStream.Close();

        byte[] compressedData = compressedStream.ToArray();

        MessageWriter writer = new(stream);
        writer.Write(compressedData);
    }

    public byte[] Receive()
    {
        MessageReader reader = new(stream);
        byte[] compressedData = reader.Read();

        using MemoryStream compressedDataStream = new(compressedData);
        using ZLibStream zlibStream = new(compressedDataStream, CompressionMode.Decompress);

        using MemoryStream dataStream = new();
        zlibStream.CopyTo(dataStream);

        return dataStream.ToArray();
    }

    public void Dispose()
    {
        stream.Dispose();
        GC.SuppressFinalize(this);
    }
}
