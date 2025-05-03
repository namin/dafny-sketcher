using System.Collections.Generic;
using System.IO; // for TextReader
using System;
using Microsoft.Dafny;
using static Microsoft.Dafny.DafnyMain;

namespace DafnySketcherCli {
  class Program {
    static async Task<int> Main(string[] args) {
      if (args.Length < 3) {
        await Console.Error.WriteLineAsync("Usage: sketcher-cli <file.dfy> <SketchType> <MethodName> [\"optional prompt…\"]");
        return 1;
      }

      var filePath   = args[0];
      var sketchType = args[1];
      var methodName = args[2];
      var prompt     = args.Length >= 4 ? args[3] : "";

      if (!File.Exists(filePath)) {
        await Console.Error.WriteLineAsync($"Error: file not found: {filePath}");
        return 1;
      }

      // 1) Read the source text
      var source = await File.ReadAllTextAsync(filePath);

      // 2) Parse & resolve using HandleDafnyFile and the new ParseCheck API
      var options = DafnyOptions.DefaultImmutableOptions;
      var reporter = new ConsoleErrorReporter(options);
      // Load the file through the DafnyMain helper, so it respects search paths, includes, etc.
      var dafnyFile = DafnyFile.HandleDafnyFile(
        OnDiskFileSystem.Instance,
        reporter,
        options,
        new Uri(Path.GetFullPath(filePath)),
        Token.NoToken
      );
      var files = new List<DafnyFile> { dafnyFile };
      var (dafnyProgram, error) = await ParseCheck(
        TextReader.Null,
        files,
        "sketcher-cli",
        options
      );
      if (!string.IsNullOrEmpty(error)) {
        await Console.Error.WriteLineAsync($"Dafny parse/resolve error: {error}");
        return 1;
      }

      // 3) Look up the method by name
      var method = Utility.GetMethodByName(dafnyProgram, methodName);
      /*if (method is null) {
        await Console.Error.WriteLineAsync($"Error: method “{methodName}” not found in {filePath}");
        return 1;
      }*/

      // 4) Instantiate the sketcher and fire it
      var sketcher = ISketcher.Create(sketchType, reporter);
      if (sketcher is null) {
        await Console.Error.WriteLineAsync("Internal error: sketcher unavailable for type " + sketchType);
        return 1;
      }

      var req  = new SketchRequest(dafnyProgram, source, method, "inductive", method.StartToken.line, prompt);
      var resp = await sketcher.GenerateSketch(req);

      await Console.Out.WriteLineAsync(resp.Sketch);
      return 0;
    }
  }
}