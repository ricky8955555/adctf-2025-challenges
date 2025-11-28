namespace Cspyshell.Frontend.Core.Net;

class MessageReader(Stream innerStream) : IDisposable
{
    public Stream InnerStream { get; } = innerStream;

    private int ReadVarint()
    {
        BinaryReader reader = new(InnerStream);
        int number = 0;

        for (int i = 0; ; i++)
        {
            byte b = reader.ReadByte();

            number |= (b & 127) << (i * 7);
            if (b < 128)
            {
                break;
            }
        }

        return number;
    }

    public byte[] Read()
    {
        int size = ReadVarint();

        BinaryReader reader = new(InnerStream);
        return reader.ReadBytes(size);
    }

    public void Dispose()
    {
        InnerStream.Dispose();
        GC.SuppressFinalize(this);
    }
}
