namespace Cspyshell.Frontend.Core.Net;

class MessageWriter(Stream innerStream) : IDisposable
{
    public Stream InnerStream { get; } = innerStream;

    private void WriteVarint(int number)
    {
        using BinaryWriter writer = new(InnerStream);

        while (number > 0)
        {
            byte b = (byte)(number & 127);

            if (number >= 128)
            {
                b |= 128;
            }

            writer.Write(b);

            number >>= 7;
        }
    }

    public void Write(byte[] buffer)
    {
        WriteVarint(buffer.Length);

        BinaryWriter writer = new(InnerStream);
        writer.Write(buffer);
    }

    public void Dispose()
    {
        InnerStream.Dispose();
        GC.SuppressFinalize(this);
    }
}
