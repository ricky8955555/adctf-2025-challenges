using System.Diagnostics;
using System.Net;
using System.Net.Sockets;
using System.Reflection;
using System.Text;
using Cspyshell.Frontend.Core.Net;
using NSec.Cryptography;

namespace Cspyshell.Frontend.Core;

class BackendStartupFailedException : Exception { }

public class Application
{
    private static Process RunBackend(IPEndPoint endpoint)
    {
        var executingAssembly = Assembly.GetExecutingAssembly();
        using var backendStream = executingAssembly.GetManifestResourceStream("backend") ?? throw new UnreachableException();

        string backendPath = Path.GetTempFileName();

        try
        {
            using var backendFile = File.Create(backendPath);

#pragma warning disable CA1416 // Validate platform compatibility
            File.SetUnixFileMode(backendPath, UnixFileMode.UserRead | UnixFileMode.UserWrite | UnixFileMode.UserExecute);  // rwx
#pragma warning restore CA1416 // Validate platform compatibility

            backendStream.CopyTo(backendFile);
            backendFile.Close();

            ProcessStartInfo backendStartInfo = new(backendPath, [endpoint.Address.ToString(), endpoint.Port.ToString()])
            {
                UseShellExecute = false,
                RedirectStandardError = true,  // silent stderr
            };

            Process backendProcess = new() { StartInfo = backendStartInfo };
            backendProcess.Start();

            return backendProcess;
        }
        catch
        {
            File.Delete(backendPath);
            throw;
        }
    }

    private static string? ReadCode()
    {
        StringBuilder sb = new();

        Console.Write(">>> ");

        while (true)
        {
            string? line = Console.ReadLine();

            if (line is null && sb.Length == 0)
            {
                return null;
            }

            if (string.IsNullOrEmpty(line))
            {
                break;
            }

            sb.AppendLine(line);

            Console.Write("... ");
        }

        return sb.ToString().TrimEnd();
    }

    public static void Main()
    {
        using TcpListener listener = new(IPAddress.Loopback, 0);
        listener.Start();

        using var backendProcess = RunBackend((IPEndPoint)listener.LocalEndpoint);

        using var socket = listener.AcceptSocket();
        using RpcSocket rpcSocket = new(socket);

        rpcSocket.Initiate(Key.Create(KeyAgreementAlgorithm.X25519));

        while (true)
        {
            string? code = ReadCode();

            if (code is null || code == "exit")
            {
                break;
            }

            byte[] codeBytes = Encoding.UTF8.GetBytes(code);
            rpcSocket.Send(codeBytes);

            try
            {
                byte[] retvalBytes = rpcSocket.Receive();
                string retval = Encoding.UTF8.GetString(retvalBytes);

                if (!string.IsNullOrEmpty(retval))
                {
                    Console.WriteLine(retval);
                }
            }
            catch (EndOfStreamException)
            {
                break;
            }
        }
    }
}
