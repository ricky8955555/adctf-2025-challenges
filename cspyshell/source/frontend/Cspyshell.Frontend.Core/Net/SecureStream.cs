using System.Security.Cryptography;
using NSec.Cryptography;

namespace Cspyshell.Frontend.Core.Net;

public class InitiationFailedException : Exception { }

public class SecureStream(Stream innerStream) : Stream
{
    private Stream InnerStream { get; } = innerStream;

    private AesGcm? cipher = null;

    public bool Initiated => cipher is not null;

    private byte[] buffer = new byte[256];

    private int bufferPosition = 0;

    private int bufferAvailable = 0;

    public void Initiate(Key privateKey)
    {

        byte[] myPublicKeyBytes = privateKey.PublicKey.Export(KeyBlobFormat.RawPublicKey);
        InnerStream.Write(myPublicKeyBytes);
        InnerStream.Flush();

        byte[] otherPublicKeyBytes = new byte[32];
        InnerStream.Read(otherPublicKeyBytes);
        var otherPublicKey = PublicKey.Import(KeyAgreementAlgorithm.X25519, otherPublicKeyBytes, KeyBlobFormat.RawPublicKey);

        using var sharedSecret = KeyAgreementAlgorithm.X25519.Agree(privateKey, otherPublicKey) ?? throw new InitiationFailedException();
        var symmetricKey = KeyDerivationAlgorithm.HkdfSha512.DeriveKey(sharedSecret, [], [], AeadAlgorithm.Aes256Gcm, new() { ExportPolicy = KeyExportPolicies.AllowPlaintextExport });

        byte[] symmetricKeyBytes = symmetricKey.Export(KeyBlobFormat.RawSymmetricKey);

        cipher = new(symmetricKeyBytes, 16);
    }

    private static byte[] EncryptNonce(byte[] nonce)
    {
        if (nonce.Length == 0)
        {
            return [];
        }

        byte[] result = new byte[nonce.Length];

        result[0] = nonce[0];
        foreach (var (ch, i) in nonce.Select((it, i) => (it, i)).Skip(1))
        {
            result[i] = (byte)(ch ^ result[i - 1]);
        }

        return result;
    }

    private static byte[] DecryptNonce(byte[] nonce)
    {
        if (nonce.Length == 0)
        {
            return [];
        }

        byte[] result = [nonce[0], .. nonce.Zip(nonce.Skip(1), (a, b) => (byte)(a ^ b))];
        return result;
    }

    public override bool CanRead => Initiated && InnerStream.CanRead;

    public override bool CanSeek => false;

    public override bool CanWrite => Initiated && InnerStream.CanWrite;

    public override long Length => InnerStream.Length;

    public override long Position { get => throw new NotImplementedException(); set => throw new NotImplementedException(); }

    public override void Flush() => InnerStream.Flush();

    public override int Read(byte[] buffer, int offset, int count)
    {
        int nbytes = count;

        if (bufferPosition < bufferAvailable)
        {
            int remaining = bufferAvailable - bufferPosition;
            int size = remaining < nbytes ? remaining : nbytes;

            this.buffer[bufferPosition..(bufferPosition + size)].CopyTo(buffer, offset);

            offset += size;
            nbytes -= size;

            bufferPosition += size;
        }

        while (nbytes > 0)
        {
            BinaryReader reader = new(InnerStream);

            if (cipher is null)
            {
                throw new InvalidOperationException();
            }

            byte[] nonce = reader.ReadBytes(12);
            nonce = DecryptNonce(nonce);

            bufferAvailable = reader.ReadByte();

            byte[] ciphertext = reader.ReadBytes(bufferAvailable);
            byte[] tag = reader.ReadBytes(16);

            cipher.Decrypt(nonce, ciphertext, tag, this.buffer.AsSpan()[..bufferAvailable]);

            bufferPosition = nbytes < bufferAvailable ? nbytes : bufferAvailable;
            this.buffer[..bufferPosition].CopyTo(buffer, offset);

            offset += bufferPosition;
            nbytes -= bufferPosition;
        }

        return count - nbytes;
    }

    public override long Seek(long offset, SeekOrigin origin) => throw new NotSupportedException();

    public override void SetLength(long value) => InnerStream.SetLength(value);

    public override void Write(byte[] buffer, int offset, int count)
    {
        if (cipher is null)
        {
            throw new InvalidOperationException();
        }

        BinaryWriter writer = new(InnerStream);

        int end = offset + count;

        for (int i = offset; i < end; i += 255)
        {
            byte[] nonce = new byte[12];
            RandomNumberGenerator.Fill(nonce);

            int size = end - i;
            if (size > 255)
            {
                size = 255;
            }

            byte[] ciphertext = new byte[size];
            byte[] tag = new byte[16];
            cipher.Encrypt(nonce, buffer[i..(i + size)], ciphertext, tag);

            nonce = EncryptNonce(nonce);

            writer.Write([.. nonce, (byte)size, .. ciphertext, .. tag]);
        }
    }
}
