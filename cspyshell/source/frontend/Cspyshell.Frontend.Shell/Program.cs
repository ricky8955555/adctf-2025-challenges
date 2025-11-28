// See https://aka.ms/new-console-template for more information
using System.Diagnostics;
using System.IO.Pipes;
using System.Reflection;
using Cspyshell.Frontend.Shell;

using AnonymousPipeServerStream pipeServerStream = new(PipeDirection.In, HandleInheritability.Inheritable);

var processPath = Environment.ProcessPath ?? throw new UnreachableException();
ProcessStartInfo pipeClientStartInfo = new("python3", [processPath, pipeServerStream.GetClientHandleAsString()])
{
    UseShellExecute = false
};
using var pipeClient = Process.Start(pipeClientStartInfo) ?? throw new ShellStartupFailedException();
pipeServerStream.DisposeLocalCopyOfClientHandle();

using MemoryStream binpackStream = new();
pipeServerStream.CopyTo(binpackStream);

byte[] binpackData = binpackStream.ToArray();
Binpack binpack = new([110, 73, 99, 48, 78, 49, 107, 111, 55, 105, 45, 112, 51, 114, 82, 35]);
byte[] assemblyBinary = binpack.Unpack(binpackData);
var coreAssembly = Assembly.Load(assemblyBinary);

var application = coreAssembly.GetType("Cspyshell.Frontend.Core.Application") ?? throw new UnreachableException();
var entryMethod = application.GetMethod("Main", BindingFlags.Public | BindingFlags.Static) ?? throw new UnreachableException();

entryMethod.Invoke(null, null);

class ShellStartupFailedException : Exception { }
