using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.IO;
using System.Text.RegularExpressions;
using System.Threading.Tasks;
using Microsoft.Dafny;
using static Microsoft.Dafny.DafnyMain;
using System.Linq;
using Std.Wrappers;

namespace DafnySketcherCli {
  class Program {
    static async Task<int> Main(string[] args) {
      if (args.Length < 2) {
        await Console.Error.WriteLineAsync("Usage: sketcher-cli <file.dfy> <SketchType> [<MethodName>] [\"optional prompt…\"]");
        return 1;
      }

      var filePath   = args[0];
      var sketchType = args[1];
      var methodName = args.Length >= 3 ? args[2] : null;
      if (methodName == "null") {
        methodName = null;
      }
      var prompt     = args.Length >= 4 ? args[3] : "";

      if (!File.Exists(filePath)) {
        await Console.Error.WriteLineAsync($"Error: file not found: {filePath}");
        return 1;
      }

      // 1) Read the source text
      var source = await File.ReadAllTextAsync(filePath);

      // 2) Parse & resolve using HandleDafnyFile and the new ParseCheck API
      var options = DafnyOptions.Default;
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
      /*
      if (!string.IsNullOrEmpty(error)) {
        await Console.Error.WriteLineAsync($"Dafny parse/resolve error: {error}");
        return 1;
      }
      */

      // 3) Look up the method by name
      Method? method = null;
      if (methodName is not null) {
        method = Utility.GetMethodByName(dafnyProgram, methodName);
      }

      // 4) Instantiate the sketcher and fire it
      if (sketchType == "errors") { 
        // 2) Invoke `dafny verify` normally and capture its text output
        var psi = new ProcessStartInfo("dafny", $"verify \"{filePath}\"") {
          RedirectStandardOutput = true,
          RedirectStandardError  = true,
          UseShellExecute        = false,
        };
        using var proc = Process.Start(psi)!;
        var stdout = await proc.StandardOutput.ReadToEndAsync();
        var stderr = await proc.StandardError.ReadToEndAsync();
        proc.WaitForExit();
        var allText = stdout + "\n" + stderr;

        // 3) Pull out lines like: file.dfy(line,col): Error: message
        var diagnostics = new List<(int line, int col, string msg)>();
        // Match any line containing "(line,col):" followed by an optional "Error:" and the message
        var regex = new Regex(@"\((\d+),(\d+)\):\s*(?:Error:)?\s*(.*)");
        foreach (var rawLine in allText.Split('\n')) {
          //await Console.Error.WriteLineAsync($"DEBUG LINE: {rawLine}");
          if (!rawLine.Contains("Error:")) {
            continue;
          }
          var line = rawLine.Trim();
          var m    = regex.Match(line);
          if (m.Success) {
            //await Console.Error.WriteLineAsync($"DEBUG MATCH: {line}");
            diagnostics.Add((
              int.Parse(m.Groups[1].Value),
              int.Parse(m.Groups[2].Value),
              m.Groups[3].Value
            ));
          }
        }

        // Remove duplicate errors
        diagnostics = diagnostics.Distinct().ToList();

        // 4) Map each error pos into the enclosing Dafny method and print
        foreach (var (ln, col, msg) in diagnostics) {
          var m = Utility.GetEnclosingMethodByPosition(
            dafnyProgram, ln, col
          );
          var name = m?.Name ?? "<global>";
          Console.WriteLine($"{name}:{ln}:{col} {msg}");
        }

      } else {
        var sketcher = ISketcher.Create(sketchType, reporter);
        if (sketcher is null) {
          await Console.Error.WriteLineAsync("Error: sketcher unavailable for type " + sketchType);
          return 1;
        }

        var req  = new SketchRequest(dafnyProgram, source, method, null, method?.StartToken.line, prompt);
        var resp = await sketcher.GenerateSketch(req);
        var sketch = resp.Sketch;
        var result = sketch;

        // 2) Read original lines
        var lines = File.ReadAllLines(filePath).ToList();

        // 3) Compute replace range
        int start, end;
        if (method != null) {
          start = method.Body.StartToken.line;
          end   = method.Body.EndToken.line - 1;
        } else {
          start = 0; // TODO
          end   = start;
        }

        // 4) Replace those lines
        var sketchLines = sketch.Split('\n');
        lines.RemoveRange(start, end - start);
        lines.InsertRange(start, sketchLines);

        // 5) Output
        result = string.Join("\n", lines);

        await Console.Out.WriteLineAsync(result);
      }
      return 0;
    }
  }
}